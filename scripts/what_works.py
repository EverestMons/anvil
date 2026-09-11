"""
What Works entry generator CLI.
Read-only over the checkout and all governance files.
Writes only to paths under --tmp or a directory named 'research'.
⛔ Refuses any --out-* path whose basename is GLOSSARY.md, that lies under
   a knowledge/decisions directory, or that is not under 'research' or --tmp.
Writers never called by name: run_cycle, run_lab, write_intent_audit,
write_cycle_report, ingest_test_results.
"""
import argparse
import os
import sqlite3
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ANVIL_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _ANVIL_ROOT)


def _guard_output_path(path, tmp_root):
    """
    Guard rule: refuse any output path whose basename is GLOSSARY.md, that
    lies under a knowledge/decisions directory, or that is not under a
    directory named 'research' or under tmp_root.
    Returns an error string if refused, else None.
    """
    if path is None:
        return None
    basename = os.path.basename(path)
    real = os.path.realpath(path)
    real_tmp = os.path.realpath(tmp_root) if tmp_root else None

    if basename == "GLOSSARY.md":
        return (
            "GUARD: output path refused — basename is GLOSSARY.md. "
            "The generator never writes the glossary."
        )

    # Reject knowledge/decisions paths
    norm = path.replace("\\", "/")
    if "knowledge/decisions" in norm:
        return (
            "GUARD: output path refused — path lies under a knowledge/decisions "
            "directory. Only research/ and tmp are valid output locations."
        )

    # Must be under 'research' or under tmp_root
    under_research = any(
        part == "research"
        for part in os.path.dirname(real).replace("\\", "/").split("/")
    )
    under_tmp = real_tmp is not None and real.startswith(real_tmp)
    if not (under_research or under_tmp):
        return (
            "GUARD: output path refused — path is not under a directory named "
            "'research' or under --tmp. Rule: write only to research/ or tmp."
        )
    return None


def main():
    ap = argparse.ArgumentParser(
        description="Generate 'what works' entries for production defs."
    )
    ap.add_argument(
        "--checkout",
        default=None,
        help="Path to the checkout to analyse (default: bellows path from SCAN_TARGETS)",
    )
    ap.add_argument(
        "--tmp", required=True,
        help="Temp dir for scratch DB; must be under /tmp or $TMPDIR",
    )
    ap.add_argument(
        "--definition", choices=["a", "b", "c"], default="c",
        help="Scoring definition to use (default: c)",
    )
    ap.add_argument("--top", type=int, default=20, metavar="K",
                    help="Number of top entries to emit (default: 20)")
    ap.add_argument("--out-md", default=None, metavar="PATH",
                    help="Write markdown output to this path")
    ap.add_argument("--out-tsv", default=None, metavar="PATH",
                    help="Write TSV output to this path")
    ap.add_argument(
        "--reference", default=None, metavar="FILE",
        help="File of 'file::name' lines; prints P@|ref| R@|ref| P@20 R@20",
    )
    args = ap.parse_args()

    # --- Guard output paths BEFORE any work ---
    for path in [args.out_md, args.out_tsv]:
        err = _guard_output_path(path, args.tmp)
        if err:
            print(err, file=sys.stderr)
            sys.exit(2)

    # --- Resolve checkout ---
    import src.config as cfg
    checkout = args.checkout or cfg.SCAN_TARGETS.get("bellows", {}).get("path")
    if not checkout or not os.path.isdir(checkout):
        print(f"ERROR: checkout not found: {checkout!r}", file=sys.stderr)
        sys.exit(1)

    # --- Build scratch DB ---
    from scripts.reprice_bellows_build import build_scratch_db
    try:
        db_path = build_scratch_db(checkout, args.tmp)
    except Exception as exc:
        print(f"ERROR building scratch DB: {exc}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")

    from src.what_works import (
        production_defs, verified_inbound, survived, rank,
        precision_recall, entry, render_markdown, render_tsv,
        ROLE_WEIGHTS,
    )
    from datetime import date
    today = date.today().isoformat()

    # --- Score ---
    defs = production_defs(checkout)
    vi = verified_inbound(conn, checkout, defs)

    surv_rows = survived(checkout, defs, today, conn=conn)
    for row in surv_rows:
        key = f"{row['file']}::{row['name']}"
        row["score_a"] = vi.get(key, 0)
        role_row = conn.execute(
            "SELECT functional_role FROM code_chunks WHERE file_path=? AND name=? LIMIT 1",
            (row["file"], row["name"]),
        ).fetchone()
        role = (role_row[0] if role_row else None) or "utility"
        row["role"] = role
        weight = ROLE_WEIGHTS.get(role, 1.0)
        row["score_c"] = row["score_a"] * weight

    ranked = rank(surv_rows, args.definition)

    # --- Reference stats ---
    if args.reference:
        ref_lines = open(args.reference, encoding="utf-8").read().splitlines()
        reference = {line.strip() for line in ref_lines if line.strip()}
        k_ref = len(reference)
        p_ref, r_ref = precision_recall(ranked, reference, k=k_ref)
        p20, r20 = precision_recall(ranked, reference, k=20)
        print(
            f"P@{k_ref}={p_ref:.3f} R@{k_ref}={r_ref:.3f} "
            f"P@20={p20:.3f} R@20={r20:.3f}"
        )

    top = ranked[:args.top]

    # --- Build entries ---
    entries = [entry(conn, checkout, row) for row in top]
    for i, (row, e) in enumerate(zip(top, entries)):
        e["score_a"] = row.get("score_a", 0)
        e["score_b"] = row.get("score_b", 0)
        e["score_c"] = row.get("score_c", 0.0)
        e["age_days"] = row.get("age_days", 0)
        e["stable_commits"] = row.get("stable_commits", 0)

    meta = {
        "definition": args.definition,
        "top_k": args.top,
        "checkout": checkout,
        "today": today,
    }

    # --- Write outputs ---
    if args.out_md:
        md = render_markdown(entries, meta)
        os.makedirs(os.path.dirname(os.path.abspath(args.out_md)), exist_ok=True)
        open(args.out_md, "w", encoding="utf-8").write(md)
        print(f"Wrote markdown: {args.out_md}")

    if args.out_tsv:
        tsv = render_tsv(entries)
        os.makedirs(os.path.dirname(os.path.abspath(args.out_tsv)), exist_ok=True)
        open(args.out_tsv, "w", encoding="utf-8").write(tsv)
        print(f"Wrote TSV: {args.out_tsv}")

    conn.close()


if __name__ == "__main__":
    main()
