# Anvil — BACKLOG entry: percentile-normalization edge case
**Date:** 2026-05-18 | **Tier:** small | **Test Scope:** none | **Execution:** Step 1 (DOCS) → Step 2 (QA) | **Priority:** 3

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

The F9-follow attribution replay (2026-05-18 morning, `knowledge/research/volatility-attribution-replay-2026-05-18.md`) surfaced a secondary finding: percentile normalization can invert volatility signal direction during population collapse. The action_queue case had raw volatility drop 79% (commits 13→3) yet normalized `volatility_score` *increased* from 0.83 to 1.00 because the rest of the population collapsed harder.

Cycle 18 production validation (2026-05-18 afternoon, `knowledge/research/cycle-18-comparison-memo-2026-05-18.md`, axis D) refined the framing significantly: **zero inversions occurred between cycles 17 and 18 (a 1-day gap)**. The 4-week rolling window shifted by ~1 day, so commit counts for most files changed by at most 1 commit. There was no population distribution shift.

The inversion is therefore an **edge case specific to long inter-cycle gaps**, not a population-level effect. The 33-day gap between cycles 10→17 produced it; a 1-day gap does not.

This BACKLOG entry captures the methodology question on the active triage surface so it surfaces during Planner Phase 1.5 reads, and documents the triggering condition so future scoring decisions don't rely on percentile stability across long gaps.

**This is not a fix plan.** It is a methodology note. The deliverable is a new "Open" entry in `anvil/knowledge/BACKLOG.md`.

## How to Run This Plan

Bellows dispatches each step. Agent stops after step 1; CEO confirms before step 2.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-percentile-inversion-backlog-entry-2026-05-18.md. Execute the next unexecuted step ONLY. After completing the step, STOP and wait for my confirmation.
```

---
---

## STEP 1 — ANVIL DOCUMENTATION AGENT

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-percentile-inversion-backlog-entry-2026-05-18.md", "anvil/knowledge/decisions/in-progress-executable-percentile-inversion-backlog-entry-2026-05-18.md")`.
>
> **Identity:** You are the Anvil Documentation Agent (or, if no dedicated Documentation specialist exists in `agents/`, the Anvil Systems Analyst acting in a documentation capacity — read the agents/ directory and choose whichever is closest). **Reads (in order):** the chosen specialist file, `knowledge/research/domain-glossary.md`, `knowledge/BACKLOG.md` (existing structure to match), `knowledge/research/volatility-attribution-replay-2026-05-18.md` (the originating audit — section on "Secondary methodology finding" or similar), and `knowledge/research/cycle-18-comparison-memo-2026-05-18.md` (axis D, percentile-inversion check).
>
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/percentile-inversion-backlog-entry-2026-05-18/`. The worktree IS the anvil root; use worktree-relative paths (e.g., `knowledge/BACKLOG.md`, not `anvil/knowledge/BACKLOG.md`).
>
> **Task:** Add a new "Open" entry to `knowledge/BACKLOG.md` documenting the percentile-normalization edge case. Match the structural conventions of existing entries in the file (Symptom, Root cause, Impact, Suggested fix or "Suggested mitigation if pursued", Risk, Priority, Cross-reference).
>
> **Place the new entry AFTER the existing 2026-05-18 ANVIL_ROOT entry and AFTER the existing 2026-05-18 volatility-weighted-composite entry, but BEFORE any earlier-dated entries.** Use today's date as the entry header date: `### 2026-05-18 — Percentile normalization can invert volatility direction during extreme population collapse`.
>
> **Required content (you may adapt phrasing for fit, but cover all points):**
>
> 1. **Symptom:** Reference the action_queue case from the F9-follow audit — raw volatility dropped 79% (13 commits → 3 commits in the 4-week window) yet percentile-normalized `volatility_score` *increased* from 0.83 to 1.00. The function's true risk dropped substantially, but the scorer ranked it equally or more prominent.
>
> 2. **Root cause:** Percentile normalization is a *relative* ranking. When the population distribution collapses (most files go quiet while a few maintain modest activity), surviving files rank higher in percentile terms even if their absolute activity dropped. The scorer's `volatility_score` is computed as the percentile rank of `volatility_raw` within the cycle's population — there is no absolute scale anchor.
>
> 3. **Impact assessment:** Edge case, not a population-level effect. The cycle 17→18 comparison (1-day gap) showed zero inversions across the full chunk population. The action_queue case was driven by the 33-day gap between cycles 10→17, during which most invoice-pulse files lost their commit-window coverage entirely. Under normal inter-cycle intervals (days, not weeks), the effect does not manifest. Cite the cycle-18 comparison memo's axis D finding.
>
> 4. **Triggering condition (the value-add of this entry):** State explicitly that inversion is expected when (a) inter-cycle gap exceeds ~14 days AND (b) the project's overall commit activity is collapsing or has collapsed. Future scoring decisions should not rely on percentile stability under either condition.
>
> 5. **Suggested mitigations if pursued (NOT a fix plan, just options):** (a) Cap percentile drift between cycles (e.g., max ±0.3 change per cycle), (b) preserve absolute raw-volatility scale alongside the percentile (already partially done — raw is computed but not persisted as a separate column), (c) add a Z-score normalization option as an alternative scoring mode for long-gap cycles, (d) emit a warning when a cycle is being scored against a population that has collapsed by >50% vs the prior cycle.
>
> 6. **Risk:** Documentation only. Adding the entry does not change behavior. If a future plan addresses any of the suggested mitigations, that plan's risk would be evaluated separately.
>
> 7. **Priority:** Low. The (d2) volatility floor and (c) Untested Complexity backup view (shipped 2026-05-18 morning) already address the practical problem of zero-coverage chunks being incorrectly displaced. The inversion case is now diagnostic context, not an active failure.
>
> 8. **Cross-reference:** Link to `knowledge/research/volatility-attribution-replay-2026-05-18.md` (originating audit) AND `knowledge/research/cycle-18-comparison-memo-2026-05-18.md` (production confirmation of edge-case status).
>
> **Constraints:** Do NOT modify any source file. Do NOT modify or reorder existing BACKLOG entries. Append-and-position only. Single coherent entry — do not split into multiple entries.
>
> **Deposit:** The modified `knowledge/BACKLOG.md`. No separate dev log required for a documentation-only entry, but include a brief Output Receipt at the end of this step's response noting the entry's location (line range) in the modified file.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/BACKLOG.md`
>
> **STOP. Wait for CEO confirmation.**

---
---

## STEP 2 — ANVIL QA ANALYST

---

> Before starting, read the deposited `knowledge/BACKLOG.md` and confirm the Step 1 agent's Output Receipt was Complete. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the modified `knowledge/BACKLOG.md`, and the two source documents the entry must cross-reference: `knowledge/research/volatility-attribution-replay-2026-05-18.md` and `knowledge/research/cycle-18-comparison-memo-2026-05-18.md`.
>
> **Working directory note:** Worktree root IS anvil/.
>
> **Do exactly this:**
>
> **(1) Entry exists with the expected header.** Run `grep -n "Percentile normalization can invert" knowledge/BACKLOG.md 2>&1`. Capture to `knowledge/qa/evidence/executable-percentile-inversion-backlog-entry-2026-05-18/header_grep.txt`. Expected: exactly one match in the Open section.
>
> **(2) Entry covers all required content points.** Open the new entry and grep for each of the seven required fields/sections: `Symptom`, `Root cause`, `Impact`, `Triggering condition`, `Suggested mitigation`, `Risk`, `Priority`, `Cross-reference`. Capture grep results to `content_coverage.txt`. Mark ❌ if any field is missing.
>
> **(3) Triggering condition specificity check.** Grep the new entry for the literal substrings `14 days` (or `~14 days`) AND `population` AND `collapse` (or similar). Capture to `triggering_condition_check.txt`. Mark ❌ if the entry does not name a quantitative gap threshold and a qualitative population-collapse condition.
>
> **(4) Cross-reference targets exist.** Confirm both referenced files exist: `ls -la knowledge/research/volatility-attribution-replay-2026-05-18.md knowledge/research/cycle-18-comparison-memo-2026-05-18.md 2>&1`. Capture to `cross_reference_targets.txt`. Mark ❌ if either is missing.
>
> **(5) Entry placement.** Confirm the new entry sits AFTER both existing 2026-05-18 entries (ANVIL_ROOT and volatility-weighted-composite) and BEFORE any earlier-dated entries. Run `grep -n "^### " knowledge/BACKLOG.md 2>&1` and capture to `entry_order.txt`. Verify visually in the QA report that the chronological ordering (most recent first by date) is preserved.
>
> **(6) Scope creep audit.** Run `git --no-pager diff HEAD 2>&1 | head -200` (or `git --no-pager show --stat HEAD` if the entry has already been committed). Capture to `git_diff.txt`. Expected: only `knowledge/BACKLOG.md` modified. No other files touched. Mark ❌ if any other file appears.
>
> **(7) Write QA report** to `knowledge/qa/2026-05-18-percentile-inversion-backlog-entry-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence |`. Six rows for checks (1)-(6). Brief Observations section noting the entry's line range in BACKLOG.md and confirming the cross-references resolve. NO hedging keywords in ✅ rows.
>
> **(8) Rule 20 self-check.** Run the canonical Rule 20 self-check from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use these values:
> - `plan_slug`: `executable-percentile-inversion-backlog-entry-2026-05-18`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-05-18-percentile-inversion-backlog-entry-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-percentile-inversion-backlog-entry-2026-05-18/`
> - `required_evidence_files`: `["header_grep.txt", "content_coverage.txt", "triggering_condition_check.txt", "cross_reference_targets.txt", "entry_order.txt", "git_diff.txt"]`
>
> Include the literal stdout of the block in the QA report. If `FAILED`, halt and report.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-05-18-percentile-inversion-backlog-entry-qa.md`
> - `knowledge/qa/evidence/executable-percentile-inversion-backlog-entry-2026-05-18/`
