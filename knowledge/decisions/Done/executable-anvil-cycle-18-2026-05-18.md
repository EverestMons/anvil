# Anvil Cycle 18 — validate F9-follow scoring fix in production
**Date:** 2026-05-18 | **Tier:** Cycle | **Test Scope:** smoke | **Execution:** Step 1 (DEV) → Step 2 (SA) → Step 3 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_each_step

## Context

The F9-follow scoring methodology fix shipped earlier today (commit `155f3d1` on main): (d2) volatility floor at 0.5 when coverage ≥ 0.99, and (c) new "Untested Complexity" cycle-report section. The fix passed unit tests + targeted regression but has only synthetic validation. A real Anvil cycle run will produce the first production exercise of both changes.

Additionally, F8 (`ANVIL_ROOT` hardcode, commit `86ba5fd`) shipped this session — cycle 18 will be the first cycle to write reports to the canonical main-repo path rather than a worktree-local path.

**Validation questions:**
1. Do zero-coverage chunks that had vol < 0.5 at cycle 17 now have composite scores reflecting the floor?
2. Does the "Untested Complexity" section appear in the cycle report between Coverage Gaps and Coupling Hotspots?
3. Is the section populated with reasonable top-20 by `coverage × complexity`?
4. Are coupling/staleness/complexity findings stable relative to cycle 17 (no unintended regressions)?
5. Does the secondary finding (percentile-normalization inversion) show up or get ruled out in real data?

**Production validation, not test validation.** This plan is the first real-data check of the F9-follow fix.

## How to Run This Plan

Bellows dispatches each step. Agent stops after each step; CEO confirms before the daemon advances.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-anvil-cycle-18-2026-05-18.md. Execute the next unexecuted step ONLY. After completing the step, STOP and wait for my confirmation.
```

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-anvil-cycle-18-2026-05-18.md", "anvil/knowledge/decisions/in-progress-executable-anvil-cycle-18-2026-05-18.md")`.
>
> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, `knowledge/research/domain-glossary.md`, `PROJECT_STATUS.md` (cycle 17 was 2026-05-17; this is cycle 18), and the prior cycle plan `knowledge/decisions/Done/executable-anvil-cycle-13-2026-05-20.md` (template for cycle execution).
>
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/anvil-cycle-18-2026-05-18/`; the worktree IS the anvil root from your perspective. For Anvil source imports use relative paths (e.g., `from src.cycle import run_cycle`). **For DB access use the absolute canonical path** `/Users/marklehn/Developer/GitHub/anvil/anvil.db` — the cycle writes to and reads from the main-repo DB, not a worktree-local one. The F8 hardcode (commit `86ba5fd`, this session) ensures `ANVIL_DB_PATH` resolves to this canonical path automatically.
>
> **Task:** Run Anvil Cycle 18 against invoice-pulse.
>
> **Pre-cycle snapshot.** Run this first and record output:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> baseline = {}
> baseline["chunks"] = conn.execute("SELECT COUNT(*) FROM code_chunks WHERE project='invoice-pulse'").fetchone()[0]
> baseline["last_cycle"] = conn.execute("SELECT MAX(cycle_number) FROM cycle_reports WHERE project='invoice-pulse'").fetchone()[0]
> baseline["last_cycle_date"] = conn.execute("SELECT cycle_date FROM cycle_reports WHERE project='invoice-pulse' AND cycle_number = (SELECT MAX(cycle_number) FROM cycle_reports WHERE project='invoice-pulse')").fetchone()[0]
> baseline["git_changes"] = conn.execute("SELECT COUNT(*) FROM git_changes WHERE project='invoice-pulse'").fetchone()[0]
> print(baseline)
> conn.close()
> ```
>
> Expected: `last_cycle: 17`, `last_cycle_date: 2026-05-17` (approximately).
>
> **Run the cycle.**
>
> ```python
> import sys, sqlite3
> sys.path.insert(0, ".")
> from src.cycle import run_cycle
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> result = run_cycle(conn, "invoice-pulse")
> print(result)
> conn.close()
> ```
>
> Note: `run_cycle` takes 2 args per the 2026-04-14 feedback log entry — `(conn, project_name)`. Path is resolved internally via config.
>
> **Post-cycle verification (after `run_cycle` returns).**
>
> (1) Capture post-cycle snapshot using the same queries as baseline; compute deltas. Confirm `cycle_number` bumped to 18.
>
> (2) Locate the new audit findings file. Per F8 fix, it should be at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-05-18.md` (canonical path, NOT a worktree-local path). Confirm file exists at that path. If it instead landed at `.bellows-worktrees/.../invoice-pulse/...`, FLAG for CEO — the F8 fix is not working as expected and the cycle data is in the wrong location.
>
> (3) From the audit findings file: print all CRITICAL findings verbatim, count findings by severity.
>
> (4) Test-file filter regression check: grep the findings file for `tests/` in `file_path` lines — expect zero matches.
>
> (5) Mission context check: grep for `Given that` — expect ≥1 match.
>
> (6) **NEW for cycle 18 — Untested Complexity section verification.** Grep the findings file for the literal string `Untested Complexity`. Expect exactly one match (the section header). Print the section's row count (count of bullet/table rows between `Untested Complexity` and the next `##` heading). Expected: up to 20 rows.
>
> (7) **NEW for cycle 18 — Volatility floor sanity.** Query `health_scores` for cycle 18 rows where `coverage_score >= 0.99` and `volatility_score < 0.5`. Expected count: zero. Run:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> r = conn.execute("""
>     SELECT COUNT(*) FROM health_scores
>     WHERE project='invoice-pulse' AND cycle_number=18
>     AND coverage_score >= 0.99 AND volatility_score < 0.5
> """).fetchone()[0]
> print(f"Floor violations: {r}")
> conn.close()
> ```
>
> If non-zero, the floor is not being applied — FLAG for CEO.
>
> (8) Top-10 highest-composite findings as a table (function name, file, composite score, finding type). This is the raw triage surface for SA in Step 2.
>
> **Constraints:** Do NOT modify Anvil source. Do NOT modify invoice-pulse source. If `run_cycle` raises, capture the full traceback and STOP — do not patch as Developer. If findings count is suspiciously low (<5) or high (>200), flag without speculating.
>
> **Deposit:** `knowledge/development/cycle-18-run-2026-05-18.md`. Must include: baseline snapshot, post-cycle snapshot with deltas, audit findings file path (confirming canonical not worktree), total findings, findings by severity, all CRITICAL findings verbatim, top-10 highest-composite findings table, test-file-filter result, mission-context result, Untested Complexity row count, floor violations count, `run_cycle` return value, end-to-end runtime in seconds.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/cycle-18-run-2026-05-18.md`
> - `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-05-18.md` (produced by `run_cycle`)
>
> **STOP. Wait for CEO confirmation.**

---
---

## STEP 2 — ANVIL SYSTEMS ANALYST

---

> Before starting, read `knowledge/development/cycle-18-run-2026-05-18.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil Systems Analyst. **Reads (in order):** `agents/ANVIL_SYSTEMS_ANALYST.md`, `knowledge/research/domain-glossary.md`, the cycle 18 dev log just deposited, the cycle 17 findings at `knowledge/research/cycle-17-findings-2026-05-17.md`, and the F9-follow attribution replay at `knowledge/research/volatility-attribution-replay-2026-05-18.md` (this is the audit that motivated the (d2) and (c) fixes — essential context).
>
> **Working directory note:** Same as Step 1 — worktree root IS anvil/, use absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB queries.
>
> **Task:** Produce a one-page comparison memo of cycle 18 vs cycle 17, focused on validating the F9-follow fix in production data.
>
> **Comparison axes (all five required):**
>
> **(A) Top-20 churn.** From cycle 17 findings (top 20 by composite) and cycle 18 findings (same), produce a table showing:
> - Functions present in BOTH top-20 → note rank change and composite delta
> - Functions in cycle-17 top-20 but NOT cycle-18 → were they fixed, did volatility decay them, or did the floor preserve them somewhere lower?
> - Functions newly in cycle-18 top-20 → likely candidates: the 9 displaced anchors from F9-follow if the floor recovered them
>
> **(B) Floor recovery audit.** For the 20 anchor chunks identified in `volatility-attribution-replay-2026-05-18.md` (full list in that file), query their cycle 18 composite scores. Compare to their cycle 17 composite scores. For each, classify:
> - RECOVERED: cycle-18 composite ≥ floor-implied composite (volatility ≥ 0.5 applied at the score level)
> - STILL_LOW: cycle-18 composite below where floor would imply (floor not applied — investigate why)
> - UNCHANGED: composite roughly identical to cycle 17 (floor didn't apply because volatility was already ≥ 0.5 or coverage < 0.99)
>
> Use this query shape:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> rows = conn.execute("""
>     SELECT h17.chunk_id, h17.volatility_score AS v17, h17.coverage_score AS c17, h17.composite_score AS comp17,
>            h18.volatility_score AS v18, h18.coverage_score AS c18, h18.composite_score AS comp18
>     FROM health_scores h17
>     LEFT JOIN health_scores h18 ON h17.chunk_id = h18.chunk_id
>         AND h18.project = h17.project AND h18.cycle_number = 18
>     WHERE h17.project = 'invoice-pulse' AND h17.cycle_number = 17
>     AND h17.chunk_id IN (<20 anchor chunk_ids from F9-follow audit>)
> """).fetchall()
> ```
>
> Read the chunk_ids from the F9-follow audit file — do not invent them.
>
> **(C) Untested Complexity section content review.** Open the cycle 18 audit findings file. Read the entire "Untested Complexity" section. Assess: (1) Are the entries plausible (high complexity × low coverage code that an engineer would care about)? (2) Are any obvious-noise patterns from prior cycles present (session lifecycle, getters, etc.)? (3) Do any entries overlap with Coverage Gaps section — and is that overlap useful or redundant? Recommend whether the section is delivering value as-shipped, or whether refinements are needed.
>
> **(D) Percentile-inversion check.** The F9-follow attribution replay surfaced that percentile normalization can invert direction during quiet periods (action_queue raw vol dropped 79% but normalized vol increased 0.83 → 1.00). In cycle 18 data, query for chunks with similar shape: raw volatility (use `volatility_raw_count` or whatever the persisted raw column is — check schema if uncertain) decreased ≥30% vs cycle 17 AND percentile-normalized `volatility_score` increased OR stayed flat. Count occurrences. If non-trivial (>5), this is a real population-level effect worth a BACKLOG entry; if rare (≤2), the inversion is an edge case mostly affecting extreme quiet periods.
>
> **(E) Coupling/staleness/complexity stability.** Compare cycle 17 vs cycle 18 totals for each. Expected: no large swings (these are not affected by the F9-follow fix). Large swings (>20% delta) would suggest a regression from the F9-follow changes touching code paths they shouldn't have.
>
> **Deliverable:** One-page comparison memo at `knowledge/research/cycle-18-comparison-memo-2026-05-18.md`. Structure: TL;DR (3-5 sentences with verdict on each of A-E), then one section per axis with the data + interpretation. Conclude with a "Fix verdict" line: PASS (fix working as designed), PARTIAL (some checks pass, some need investigation), or FAIL (fix not delivering or regressing).
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/research/cycle-18-comparison-memo-2026-05-18.md`
>
> **STOP. Wait for CEO confirmation.**

---
---

## STEP 3 — ANVIL QA ANALYST

---

> Before starting, read `knowledge/research/cycle-18-comparison-memo-2026-05-18.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the Step 1 dev log, the Step 2 comparison memo, and the cycle 18 audit findings file at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-05-18.md`.
>
> **Working directory note:** Worktree root IS anvil/. Use absolute path for DB access.
>
> **Do exactly this:**
>
> **(1) Cycle 18 DB row landed.** Run `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT cycle_number, findings_count, cycle_date FROM cycle_reports WHERE project=\"invoice-pulse\" AND cycle_number=18').fetchone(); print(r); conn.close()" 2>&1`. Capture to `knowledge/qa/evidence/executable-anvil-cycle-18-2026-05-18/cycle_18_row.txt`. Expected: non-null tuple with cycle_number=18 and today's date.
>
> **(2) Audit findings file at canonical path.** Run `ls -la /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-05-18.md 2>&1`. Capture to `findings_file_path.txt`. Expected: file exists, modified today. Mark ❌ if missing or in wrong location.
>
> **(3) Untested Complexity section present.** Run `grep -n "^## .*Untested Complexity" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-05-18.md 2>&1`. Capture to `untested_complexity_grep.txt`. Expected: exactly one match.
>
> **(4) Floor invariant holds.** Run the same floor-violations query from Step 1 check (7). Capture to `floor_violations.txt`. Expected: `Floor violations: 0`.
>
> **(5) Test-file filter regression check.** Run `grep -c "file_path.*tests/" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-05-18.md 2>&1`. Capture to `test_filter_check.txt`. Expected: 0.
>
> **(6) Comparison memo present and complete.** Verify `knowledge/research/cycle-18-comparison-memo-2026-05-18.md` exists, contains all five axes (A-E), and ends with a "Fix verdict" line. Capture grep output of section headers via `grep -n "^## \|^### " knowledge/research/cycle-18-comparison-memo-2026-05-18.md 2>&1` to `memo_structure.txt`.
>
> **(7) Full test suite.** Run `python3 -m pytest tests/ -v 2>&1` and capture to `pytest_full.txt`. Expected: 219 tests pass. This is the Rule 21 session-touched-tests check — the cycle run exercises lab.py and scorer.py.
>
> **(8) Write QA report** to `knowledge/qa/2026-05-18-cycle-18-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence |`. Six rows for checks (1)-(6) plus row for check (7). Brief "Observations" section noting the Fix verdict from the comparison memo (PASS/PARTIAL/FAIL). NO hedging keywords in ✅ rows.
>
> **(9) Rule 20 self-check.** Run the canonical Rule 20 self-check from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use these values:
> - `plan_slug`: `executable-anvil-cycle-18-2026-05-18`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-05-18-cycle-18-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-cycle-18-2026-05-18/`
> - `required_evidence_files`: `["cycle_18_row.txt", "findings_file_path.txt", "untested_complexity_grep.txt", "floor_violations.txt", "test_filter_check.txt", "memo_structure.txt", "pytest_full.txt"]`
>
> Include the literal stdout of the block in the QA report. If `FAILED`, halt and report.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-05-18-cycle-18-qa.md`
> - `knowledge/qa/evidence/executable-anvil-cycle-18-2026-05-18/`
