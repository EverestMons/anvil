# Anvil BACKLOG Cutover — Step 1 Dev Log (2026-06-12)
**Plan:** 15 — FORWARD Register Cutover (Reporting Phase 3, Stage 2 of 5)
**Agent:** Anvil Developer
**Step:** 1 (registers)

---

## Part A — Per-Entry Classification Table

Source: `knowledge/BACKLOG.md` (15 `###` entries in the `## Open` section)
Diagnostic reference: Section 1 of `governance/knowledge/research/reporting-phase-3-pre-cutover-unknowns-2026-06-12.md` (survey: 8 truly-open, 7 closed-inline)

| # | Date | Short title | Classification | Justification (inline marker) |
|---|---|---|---|---|
| 1 | 2026-06-09 | QA worktree RULE_20 read | truly-open | No Closed annotation; deferred fix with two options |
| 2 | 2026-06-08 | resolve_dependencies decoupling | truly-open | No Closed annotation; "Fix before any non-Python head" |
| 3 | 2026-06-08 | project_id scoping invariant | shipped-with-open-residual | Fix shipped (commit ff00ab8) but explicit "**Residual (Low):**" marker |
| 4 | 2026-06-08 | Scan files_total inflation | shipped-with-open-residual | Partial fix shipped (commit 4f65e8d) but "**Fix when picked up:**" marker — remaining dirs still walked |
| 5 | 2026-06-08 | Mono-role utility classification | truly-open | No Closed annotation; deferred unless bellows recurring |
| 6 | 2026-06-05 | (d2) volatility floor persistence | truly-open | No Closed annotation; "**Decision fork (CEO)**" marker |
| 7 | 2026-06-05 | Scanner duplicate module rows | closed-inline | "**Closed 2026-06-05:**" — one-time dedup, no residual |
| 8 | 2026-06-03 | File-set reconciliation | closed-inline | "**Closed 2026-06-05:**" — orphan-reconciliation executable; pre-closure Fix text retained |
| 9 | 2026-06-03 | find_clone_candidates residual phantom | closed-inline | "**Closed 2026-06-05:**" — last_seen_cycle filter added |
| 10 | 2026-06-03 | Cycle-20 population discontinuity | closed-inline | "**Closed 2026-06-03:**" — QA measurement artifact; optional residual |
| 11 | 2026-06-02 | Cycle plan template 3 fixes | closed-inline | "**Closed 2026-06-05:**" — canonical template authored |
| 12 | 2026-05-18 | Intent-gap phantom functions | closed-inline | "**Closed 2026-06-03:**" — last_seen_cycle fix; follow-ups are separate entries |
| 13 | 2026-05-18 | ANVIL_ROOT worktree path | closed-inline | "**Closed 2026-05-18:**" — fix shipped commit 86ba5fd |
| 14 | 2026-05-18 | Volatility self-resolve | truly-open | No Closed annotation; methodology issue, every audit report |
| 15 | 2026-05-18 | Percentile normalization inversion | truly-open | No Closed annotation; documented edge case |

### Totals

- **Open-class:** 8 (6 truly-open + 2 shipped-with-open-residual)
- **Closed-inline:** 7
- **Divergence from diagnostic survey:** None — 8/7 matches exactly

---

## Part B — Register Creation Confirmations

### FORWARD.md
- **Path:** `knowledge/FORWARD.md`
- **Format:** diagnostic Section 4 verbatim — title, standing-queue preamble blockquote, 6-column table
- **Rows:** 8 (one per open-class entry, chronological order, numbered 1–8)
- **Residual entries (#5, #6):** state the residual itself with `(context in BACKLOG-ARCHIVE.md)` appended
- **Types:** 7 deferred-work, 1 ceo-decision-fork (entry #3, d2 volatility floor)
- **Plan-id links:** all "—" (no deferred/halted plan ids named in the entries)
- **Status:** all "open"

### BACKLOG-ARCHIVE.md
- **Path:** `knowledge/BACKLOG-ARCHIVE.md`
- **Header:** `# Anvil — BACKLOG Archive (frozen 2026-06-12)` + blockquote + `---`
- **Body:** byte-identical to `knowledge/BACKLOG.md` (verified via Python byte comparison)
- **Original BACKLOG.md size:** 32,435 bytes

---

## BACKLOG.md Untouched Confirmation

```
$ git status
On branch bellows-wt/15
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	knowledge/BACKLOG-ARCHIVE.md
	knowledge/FORWARD.md

nothing added to commit but untracked files present (use "git add" to track)
```

BACKLOG.md does not appear in `git status` — it has not been modified, staged, or deleted. Only the two new register files appear as untracked.
