"""
Anvil Stage 4 — Lab analysis and actionable output generation.

Reads scored data and produces findings (coverage gaps, coupling hotspots,
clone candidates, staleness alerts, complexity hotspots, co-change patterns),
Planner constraints, specialist update data, and cycle reports.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timezone

from src import db
from src.config import (
    ANVIL_ROOT,
    HIGH_RISK_THRESHOLD,
    COVERAGE_GAP_THRESHOLD,
    COUPLING_HOTSPOT_THRESHOLD,
    STALENESS_THRESHOLD,
    COMPLEXITY_THRESHOLD,
    COCHANGE_MIN_COUNT,
    ROLE_THRESHOLDS,
)
from src.detector import check_best_practice


def run_lab(conn, project_name: str, cycle_id: int) -> dict:
    """
    Main entry point for Lab analysis.

    Runs all finding functions, generates report and constraints.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]
    started_at = datetime.now(timezone.utc).isoformat()

    coverage_gaps = find_coverage_gaps(conn, project_id, cycle_id)
    coupling_hotspots = find_coupling_hotspots(conn, project_id, cycle_id)
    clone_candidates = find_clone_candidates(conn, project_id, cycle_id)
    staleness_alerts = find_staleness_alerts(conn, project_id, cycle_id)
    complexity_hotspots = find_complexity_hotspots(conn, project_id, cycle_id)
    cochange_patterns = find_cochange_patterns(conn, project_id)
    bp_deviations = find_best_practice_deviations(conn, project_id)

    findings = {
        "coverage_gaps": coverage_gaps,
        "coupling_hotspots": coupling_hotspots,
        "clone_candidates": clone_candidates,
        "staleness_alerts": staleness_alerts,
        "complexity_hotspots": complexity_hotspots,
        "cochange_patterns": cochange_patterns,
        "best_practice_deviations": bp_deviations,
    }

    constraints = generate_planner_constraints(
        conn, project_name, cycle_id, findings
    )
    specialist_data = generate_specialist_update_data(conn, project_id)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = os.path.join(
        ANVIL_ROOT, "knowledge", "research",
        f"cycle-{cycle_id}-findings-{today}.md",
    )

    write_cycle_report(
        conn, project_name, cycle_id, findings, constraints,
        specialist_data, report_path, started_at,
    )

    total = sum(len(v) for v in findings.values())

    return {
        "findings": {k: len(v) for k, v in findings.items()},
        "total_findings": total,
        "constraints_generated": len(constraints),
        "report_path": report_path,
    }


def find_coverage_gaps(conn, project_id: int, cycle_id: int) -> list[dict]:
    """Find untested high-risk chunks."""
    cur = conn.execute(
        "SELECT cc.id, cc.file_path, cc.name, cc.chunk_type, "
        "hs.composite_score, hs.coverage_score, hs.volatility_score "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE hs.cycle_id = ? AND hs.coverage_score >= ? "
        "AND hs.composite_score >= ? AND cc.chunk_type != 'test_case' "
        "ORDER BY hs.composite_score DESC",
        (cycle_id, COVERAGE_GAP_THRESHOLD, HIGH_RISK_THRESHOLD),
    )
    return [
        {
            "chunk_id": r[0], "file_path": r[1], "name": r[2],
            "chunk_type": r[3], "composite_score": r[4],
            "coverage_score": r[5], "volatility_score": r[6],
        }
        for r in cur.fetchall()
    ]


def find_coupling_hotspots(conn, project_id: int, cycle_id: int) -> list[dict]:
    """Find highly coupled chunks, using role-specific thresholds."""
    min_threshold = min(
        (rt.get("coupling_hotspot_threshold", COUPLING_HOTSPOT_THRESHOLD)
         for rt in ROLE_THRESHOLDS.values()),
        default=COUPLING_HOTSPOT_THRESHOLD,
    )
    cur = conn.execute(
        "SELECT cc.id, cc.file_path, cc.name, hs.coupling_score, "
        "hs.composite_score, cc.functional_role "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE hs.cycle_id = ? AND hs.coupling_score >= ? "
        "ORDER BY hs.coupling_score DESC",
        (cycle_id, min_threshold),
    )
    results = []
    for r in cur.fetchall():
        role = r[5]
        role_thresh = ROLE_THRESHOLDS.get(role, {})
        threshold = role_thresh.get(
            "coupling_hotspot_threshold", COUPLING_HOTSPOT_THRESHOLD
        )
        if r[3] < threshold:
            continue

        chunk_id = r[0]
        in_cur = conn.execute(
            "SELECT COUNT(*) FROM chunk_dependencies WHERE target_chunk_id = ?",
            (chunk_id,),
        )
        out_cur = conn.execute(
            "SELECT COUNT(*) FROM chunk_dependencies WHERE source_chunk_id = ?",
            (chunk_id,),
        )
        inbound = in_cur.fetchone()[0]
        outbound = out_cur.fetchone()[0]

        results.append({
            "chunk_id": chunk_id, "file_path": r[1], "name": r[2],
            "coupling_score": r[3], "composite_score": r[4],
            "inbound": inbound, "outbound": outbound,
        })
    return results


def find_clone_candidates(conn, project_id: int, cycle_id: int) -> list[dict]:
    """Find near-duplicate chunk pairs."""
    cur = conn.execute(
        "SELECT cs.chunk_a_id, cs.chunk_b_id, cs.similarity_score, "
        "a.file_path, a.name, b.file_path, b.name "
        "FROM chunk_similarities cs "
        "JOIN code_chunks a ON cs.chunk_a_id = a.id "
        "JOIN code_chunks b ON cs.chunk_b_id = b.id "
        "WHERE cs.cycle_id = ? AND a.project_id = ? "
        "ORDER BY cs.similarity_score DESC",
        (cycle_id, project_id),
    )
    return [
        {
            "chunk_a_id": r[0], "chunk_b_id": r[1],
            "similarity_score": r[2],
            "file_a": r[3], "name_a": r[4],
            "file_b": r[5], "name_b": r[6],
        }
        for r in cur.fetchall()
    ]


def find_staleness_alerts(conn, project_id: int, cycle_id: int) -> list[dict]:
    """Find chunks whose dependencies are newer than the chunk itself."""
    cur = conn.execute(
        "SELECT cc.id, cc.file_path, cc.name, hs.staleness_score, "
        "hs.composite_score "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE hs.cycle_id = ? AND hs.staleness_score >= ? "
        "AND cc.project_id = ? "
        "ORDER BY hs.staleness_score DESC",
        (cycle_id, STALENESS_THRESHOLD, project_id),
    )
    return [
        {
            "chunk_id": r[0], "file_path": r[1], "name": r[2],
            "staleness_score": r[3], "composite_score": r[4],
        }
        for r in cur.fetchall()
    ]


def find_complexity_hotspots(conn, project_id: int, cycle_id: int) -> list[dict]:
    """Find overly complex functions, using role-specific thresholds."""
    # Pre-filter at minimum possible threshold (0.50 for utility)
    min_threshold = min(
        (rt.get("complexity_threshold", COMPLEXITY_THRESHOLD)
         for rt in ROLE_THRESHOLDS.values()),
        default=COMPLEXITY_THRESHOLD,
    )
    cur = conn.execute(
        "SELECT cc.id, cc.file_path, cc.name, cc.structural_metadata, "
        "hs.complexity_score, hs.composite_score, cc.functional_role "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE hs.cycle_id = ? AND hs.complexity_score >= ? "
        "AND cc.project_id = ? "
        "ORDER BY hs.complexity_score DESC",
        (cycle_id, min_threshold, project_id),
    )
    results = []
    for r in cur.fetchall():
        role = r[6]
        role_thresh = ROLE_THRESHOLDS.get(role, {})
        threshold = role_thresh.get("complexity_threshold", COMPLEXITY_THRESHOLD)
        if r[4] < threshold:
            continue

        meta = {}
        if r[3]:
            try:
                meta = json.loads(r[3])
            except (json.JSONDecodeError, TypeError):
                pass
        results.append({
            "chunk_id": r[0], "file_path": r[1], "name": r[2],
            "complexity_score": r[4], "composite_score": r[5],
            "cyclomatic_complexity": meta.get("cyclomatic_complexity", 0),
            "nesting_depth": meta.get("nesting_depth", 0),
            "parameter_count": meta.get("parameter_count", 0),
        })
    return results


def find_cochange_patterns(conn, project_id: int) -> list[dict]:
    """Find files that frequently change together in git commits."""
    # Get all commits with their files
    cur = conn.execute(
        "SELECT commit_hash, file_path FROM git_changes "
        "WHERE project_id = ? AND file_path != ''",
        (project_id,),
    )
    commit_files = defaultdict(set)
    file_commits = defaultdict(set)
    for commit_hash, file_path in cur.fetchall():
        commit_files[commit_hash].add(file_path)
        file_commits[file_path].add(commit_hash)

    # Count co-changes per file pair
    pair_counts = defaultdict(int)
    for commit_hash, files in commit_files.items():
        files_list = sorted(files)
        for i in range(len(files_list)):
            for j in range(i + 1, len(files_list)):
                pair = (files_list[i], files_list[j])
                pair_counts[pair] += 1

    # Filter and compute Jaccard
    results = []
    for (file_a, file_b), count in pair_counts.items():
        if count >= COCHANGE_MIN_COUNT:
            union = len(file_commits[file_a] | file_commits[file_b])
            jaccard = count / union if union > 0 else 0.0
            results.append({
                "file_a": file_a,
                "file_b": file_b,
                "cochange_count": count,
                "jaccard_score": round(jaccard, 4),
            })

    results.sort(key=lambda x: x["cochange_count"], reverse=True)
    return results


def find_best_practice_deviations(conn, project_id: int) -> list[dict]:
    """Find chunks that deviate from best practices for their functional role."""
    # Get all classified chunks
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT id, file_path, name, content, structural_metadata, functional_role "
        "FROM code_chunks WHERE project_id = ? AND functional_role IS NOT NULL "
        "AND chunk_type NOT IN ('module', 'test_case')",
        (project_id,),
    )
    chunks = cur.fetchall()
    conn.row_factory = None

    # Cache practices by role
    practices_cache = {}
    results = []

    for chunk in chunks:
        role = chunk["functional_role"]
        if role not in practices_cache:
            practices_cache[role] = db.get_best_practices_by_role(conn, role)

        for practice in practices_cache[role]:
            result = check_best_practice(chunk, practice)
            if not result["compliant"]:
                results.append({
                    "chunk_id": chunk["id"],
                    "file_path": chunk["file_path"],
                    "name": chunk["name"],
                    "functional_role": role,
                    "practice_name": practice["pattern_name"],
                    "practice_description": practice["description"],
                    "practice_severity": practice["severity"],
                    "observation": result["observation"],
                    "recommendation": (
                        f'"{chunk["name"]}" is a {role}. '
                        f'Best practice: {practice["pattern_name"]} -- '
                        f'{practice["description"]}. '
                        f'Current: {result["observation"]}.'
                    ),
                })

    results.sort(key=lambda x: (
        {"high": 0, "medium": 1, "low": 2}.get(x["practice_severity"], 1),
        x["functional_role"],
    ))
    return results


def generate_planner_constraints(conn, project_name: str, cycle_id: int,
                                 findings: dict) -> list[dict]:
    """Assemble findings into structured Planner constraints."""
    constraints = []

    for gap in findings.get("coverage_gaps", []):
        severity = "high" if gap["composite_score"] >= 0.7 else "medium"
        constraints.append({
            "type": "coverage_required",
            "target": f"{gap['file_path']}::{gap['name']}",
            "reason": (f"Composite score {gap['composite_score']:.2f}, "
                       f"no test coverage, volatility {gap['volatility_score']:.2f}"),
            "severity": severity,
        })

    for hotspot in findings.get("coupling_hotspots", []):
        severity = "high" if hotspot["inbound"] >= 10 else "medium"
        constraints.append({
            "type": "verify_dependents",
            "target": f"{hotspot['file_path']}::{hotspot['name']}",
            "reason": (f"Coupling score {hotspot['coupling_score']:.2f}, "
                       f"{hotspot['inbound']} inbound + {hotspot['outbound']} outbound deps"),
            "severity": severity,
        })

    for clone in findings.get("clone_candidates", [])[:20]:  # Cap at 20
        constraints.append({
            "type": "refactor_candidate",
            "target": f"{clone['file_a']}::{clone['name_a']} ↔ {clone['file_b']}::{clone['name_b']}",
            "reason": f"Similarity {clone['similarity_score']:.2f} — potential duplicate",
            "severity": "medium",
        })

    for alert in findings.get("staleness_alerts", []):
        severity = "high" if alert["staleness_score"] >= 0.8 else "medium"
        constraints.append({
            "type": "investigation_needed",
            "target": f"{alert['file_path']}::{alert['name']}",
            "reason": f"Staleness score {alert['staleness_score']:.2f} — dependencies updated but chunk unchanged",
            "severity": severity,
        })

    for hotspot in findings.get("complexity_hotspots", [])[:20]:  # Cap at 20
        constraints.append({
            "type": "refactor_candidate",
            "target": f"{hotspot['file_path']}::{hotspot['name']}",
            "reason": (f"Complexity score {hotspot['complexity_score']:.2f}, "
                       f"cyclomatic={hotspot['cyclomatic_complexity']}, "
                       f"depth={hotspot['nesting_depth']}"),
            "severity": "medium",
        })

    for dev in findings.get("best_practice_deviations", [])[:30]:  # Cap at 30
        constraints.append({
            "type": "pattern_recommendation",
            "target": f"{dev['file_path']}::{dev['name']}",
            "reason": (f"{dev['functional_role']} deviates from "
                       f"{dev['practice_name']}: {dev['observation']}"),
            "severity": dev["practice_severity"],
        })

    return constraints


def generate_specialist_update_data(conn, project_id: int) -> dict:
    """Generate aggregate stats for specialist file sync."""
    counts = {}
    cur = conn.execute(
        "SELECT chunk_type, COUNT(*) FROM code_chunks "
        "WHERE project_id = ? GROUP BY chunk_type",
        (project_id,),
    )
    for ctype, cnt in cur.fetchall():
        counts[ctype] = cnt

    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_dependencies cd "
        "JOIN code_chunks cc ON cd.source_chunk_id = cc.id "
        "WHERE cc.project_id = ?",
        (project_id,),
    )
    total_deps = cur.fetchone()[0]

    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_similarities cs "
        "JOIN code_chunks cc ON cs.chunk_a_id = cc.id "
        "WHERE cc.project_id = ?",
        (project_id,),
    )
    total_sims = cur.fetchone()[0]

    cur = conn.execute(
        "SELECT AVG(composite_score) FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE cc.project_id = ?",
        (project_id,),
    )
    avg_score = cur.fetchone()[0] or 0.0

    cur = conn.execute(
        "SELECT COUNT(*) FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE cc.project_id = ? AND hs.composite_score >= ?",
        (project_id, HIGH_RISK_THRESHOLD),
    )
    high_risk = cur.fetchone()[0]

    # Top 10 complex
    cur = conn.execute(
        "SELECT cc.name, cc.file_path, hs.complexity_score "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE cc.project_id = ? "
        "ORDER BY hs.complexity_score DESC LIMIT 10",
        (project_id,),
    )
    top_complex = [
        {"name": r[0], "file": r[1], "complexity_score": r[2]}
        for r in cur.fetchall()
    ]

    # Top 10 coupled
    cur = conn.execute(
        "SELECT cc.name, cc.file_path, hs.coupling_score "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE cc.project_id = ? "
        "ORDER BY hs.coupling_score DESC LIMIT 10",
        (project_id,),
    )
    top_coupled = [
        {"name": r[0], "file": r[1], "coupling_score": r[2]}
        for r in cur.fetchall()
    ]

    return {
        "total_files": counts.get("module", 0),
        "total_functions": counts.get("function", 0),
        "total_classes": counts.get("class", 0),
        "total_methods": counts.get("method", 0),
        "total_test_cases": counts.get("test_case", 0),
        "total_dependencies": total_deps,
        "total_similarity_pairs": total_sims,
        "avg_composite_score": round(avg_score, 4),
        "high_risk_count": high_risk,
        "top_10_complex": top_complex,
        "top_10_coupled": top_coupled,
    }


def write_cycle_report(conn, project_name: str, cycle_id: int,
                       findings: dict, constraints: list[dict],
                       specialist_data: dict, report_path: str,
                       started_at: str) -> None:
    """Generate markdown report and create cycle_reports DB row."""
    project = db.get_project(conn, project_name)
    project_id = project["id"]
    completed_at = datetime.now(timezone.utc).isoformat()

    total_findings = sum(len(v) for v in findings.values())

    # Build markdown
    lines = []
    lines.append(f"# Anvil Cycle Report — {project_name} — Cycle {cycle_id}")
    lines.append(f"**Date:** {completed_at[:10]}")
    lines.append("")

    # Executive summary
    lines.append("## Executive Summary")
    sd = specialist_data
    lines.append(f"- **Total files:** {sd['total_files']}")
    lines.append(f"- **Total chunks:** {sd['total_functions'] + sd['total_classes'] + sd['total_methods'] + sd['total_test_cases']}")
    lines.append(f"- **High risk chunks:** {sd['high_risk_count']}")
    lines.append(f"- **Average composite score:** {sd['avg_composite_score']:.4f}")
    lines.append(f"- **Total findings:** {total_findings}")
    lines.append("")

    # Coverage gaps
    gaps = findings.get("coverage_gaps", [])
    lines.append(f"## Coverage Gaps ({len(gaps)} findings)")
    if gaps:
        lines.append("| File | Name | Type | Composite | Coverage | Volatility |")
        lines.append("|---|---|---|---|---|---|")
        for g in gaps[:30]:
            lines.append(
                f"| {g['file_path']} | {g['name']} | {g['chunk_type']} | "
                f"{g['composite_score']:.3f} | {g['coverage_score']:.2f} | "
                f"{g['volatility_score']:.2f} |"
            )
    else:
        lines.append("No coverage gaps found.")
    lines.append("")

    # Coupling hotspots
    hotspots = findings.get("coupling_hotspots", [])
    lines.append(f"## Coupling Hotspots ({len(hotspots)} findings)")
    if hotspots:
        lines.append("| File | Name | Coupling | Inbound | Outbound | Composite |")
        lines.append("|---|---|---|---|---|---|")
        for h in hotspots[:30]:
            lines.append(
                f"| {h['file_path']} | {h['name']} | {h['coupling_score']:.3f} | "
                f"{h['inbound']} | {h['outbound']} | {h['composite_score']:.3f} |"
            )
    else:
        lines.append("No coupling hotspots found.")
    lines.append("")

    # Clone candidates
    clones = findings.get("clone_candidates", [])
    lines.append(f"## Clone Candidates ({len(clones)} pairs)")
    if clones:
        lines.append("| File A | Name A | File B | Name B | Similarity |")
        lines.append("|---|---|---|---|---|")
        for c in clones[:30]:
            lines.append(
                f"| {c['file_a']} | {c['name_a']} | {c['file_b']} | "
                f"{c['name_b']} | {c['similarity_score']:.3f} |"
            )
    else:
        lines.append("No clone candidates found.")
    lines.append("")

    # Staleness alerts
    stale = findings.get("staleness_alerts", [])
    lines.append(f"## Staleness Alerts ({len(stale)} findings)")
    if stale:
        lines.append("| File | Name | Staleness | Composite |")
        lines.append("|---|---|---|---|")
        for s in stale[:30]:
            lines.append(
                f"| {s['file_path']} | {s['name']} | "
                f"{s['staleness_score']:.3f} | {s['composite_score']:.3f} |"
            )
    else:
        lines.append("No staleness alerts found.")
    lines.append("")

    # Complexity hotspots
    complex_h = findings.get("complexity_hotspots", [])
    lines.append(f"## Complexity Hotspots ({len(complex_h)} findings)")
    if complex_h:
        lines.append("| File | Name | Score | Cyclomatic | Depth | Params |")
        lines.append("|---|---|---|---|---|---|")
        for ch in complex_h[:30]:
            lines.append(
                f"| {ch['file_path']} | {ch['name']} | {ch['complexity_score']:.3f} | "
                f"{ch['cyclomatic_complexity']} | {ch['nesting_depth']} | "
                f"{ch['parameter_count']} |"
            )
    else:
        lines.append("No complexity hotspots found.")
    lines.append("")

    # Co-change patterns
    cochange = findings.get("cochange_patterns", [])
    lines.append(f"## Co-Change Patterns ({len(cochange)} pairs)")
    if cochange:
        lines.append("| File A | File B | Co-changes | Jaccard |")
        lines.append("|---|---|---|---|")
        for cc_item in cochange[:30]:
            lines.append(
                f"| {cc_item['file_a']} | {cc_item['file_b']} | "
                f"{cc_item['cochange_count']} | {cc_item['jaccard_score']:.3f} |"
            )
    else:
        lines.append("No co-change patterns found.")
    lines.append("")

    # Research Recommendations (best practice deviations)
    bp_devs = findings.get("best_practice_deviations", [])
    roles_with_devs = defaultdict(list)
    for d in bp_devs:
        roles_with_devs[d["functional_role"]].append(d)
    lines.append(f"## Research Recommendations ({len(bp_devs)} deviations across {len(roles_with_devs)} roles)")
    if bp_devs:
        for role in sorted(roles_with_devs.keys()):
            devs = roles_with_devs[role]
            lines.append(f"\n### {role} ({len(devs)} deviations)")
            for d in devs[:15]:
                lines.append(
                    f"- **[{d['practice_severity']}]** `{d['file_path']}::{d['name']}` "
                    f"-- {d['practice_name']}: {d['observation']}"
                )
    else:
        lines.append("No best practice deviations found.")
    lines.append("")

    # Planner constraints
    lines.append(f"## Planner Constraints ({len(constraints)} total)")
    if constraints:
        by_type = defaultdict(list)
        for c in constraints:
            by_type[c["type"]].append(c)
        for ctype, clist in by_type.items():
            lines.append(f"\n### {ctype} ({len(clist)})")
            for c in clist[:15]:
                lines.append(f"- **[{c['severity']}]** `{c['target']}` — {c['reason']}")
    lines.append("")

    # Specialist update data
    lines.append("## Specialist Update Data")
    lines.append(f"- Functions: {sd['total_functions']}")
    lines.append(f"- Classes: {sd['total_classes']}")
    lines.append(f"- Methods: {sd['total_methods']}")
    lines.append(f"- Test cases: {sd['total_test_cases']}")
    lines.append(f"- Dependencies: {sd['total_dependencies']}")
    lines.append(f"- Similarity pairs: {sd['total_similarity_pairs']}")
    lines.append(f"- Average health score: {sd['avg_composite_score']:.4f}")
    lines.append(f"- High risk count: {sd['high_risk_count']}")
    lines.append("")

    content = "\n".join(lines)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write(content)

    # DB row
    db.create_cycle_report(
        conn, project_id,
        cycle_number=cycle_id,
        started_at=started_at,
        completed_at=completed_at,
        files_scanned=sd["total_files"],
        chunks_extracted=sd["total_functions"] + sd["total_classes"] + sd["total_methods"] + sd["total_test_cases"],
        chunks_scored=sd["total_functions"] + sd["total_classes"] + sd["total_methods"] + sd["total_test_cases"],
        findings_count=total_findings,
        report_path=report_path,
    )


def research_best_practices(conn, role_name: str) -> dict:
    """
    Generate a research prompt for Claude Code to discover new best practices.

    Returns dict with role info, existing practices, and a structured prompt.
    Not automated — called by Claude Code during Lab sessions.
    """
    # Get role description
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT * FROM functional_roles WHERE name = ?", (role_name,)
    )
    role = cur.fetchone()
    conn.row_factory = None

    if not role:
        return {"error": f"Role not found: {role_name}"}

    existing = db.get_best_practices_by_role(conn, role_name)
    existing_names = [p["pattern_name"] for p in existing]

    prompt = (
        f"Research established software engineering best practices for "
        f"a '{role_name}' ({role['description']}). "
        f"Current known patterns: {', '.join(existing_names) or 'none'}. "
        f"Find 2-3 additional patterns not already listed. "
        f"For each, provide: pattern_name (snake_case), description (1-2 sentences), "
        f"detection_hint (how to detect violations), severity (low/medium/high)."
    )

    return {
        "role_name": role_name,
        "role_description": role["description"],
        "existing_practices": existing,
        "research_prompt": prompt,
    }
