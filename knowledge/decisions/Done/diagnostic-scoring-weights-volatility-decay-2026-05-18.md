# Anvil — Diagnostic: Scoring Weights & Volatility-Decay Population Audit
**Date:** 2026-05-18 | **Tier:** Diagnostic | **Test Scope:** none (read-only) | **Execution:** Step 1 (ANVIL SA) | **Priority:** 1

**auto_close:** false

## Context

Per `anvil/knowledge/BACKLOG.md` (2026-05-18 entry "Volatility-weighted composite scores cause findings to self-resolve"): two 04-14 CRITICAL findings (`dispute_brief`, `run_validation` in invoice-pulse `app.py`) dropped from the cycle-17 top-N solely because their volatility scores fell from 1.000 → 0.111 between cycles 16 and 17. Coverage and complexity were unchanged. The functions remain zero-coverage, high-complexity. The "improvement" was an artifact of Anvil's scoring weights, not remediation.

This diagnostic generalizes the finding from a two-function vignette to a population audit: across the cycle-10 top-20 trajectory through cycle-17, what fraction of dropped findings were dropped via real remediation (coverage_score or complexity_score moved) vs. fake volatility-decay (only volatility moved)? The output frames the four scoring-weight options listed in the BACKLOG entry against actual data so the CEO can make a weight-change decision (which is gated to CEO authority per the SA's decision matrix).

**This is a read-only diagnostic.** Do NOT modify scoring weights, do NOT run a new audit cycle, do NOT touch `anvil/src/scorer.py` or `anvil/src/config.py`. The output is a characterization + recommendation memo; no code lands.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file, executes Step 1 ONLY — a read-only SQL audit against `anvil/anvil.db` and a recommendation memo against the four scoring-weight options — deposits findings, and stops.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/diagnostic-scoring-weights-volatility-decay-2026-05-18.md. Execute Step 1 ONLY. After completing Step 1, STOP and report. Do NOT modify any source code, do NOT run a new audit cycle, do NOT modify the DB — this is a read-only diagnostic.
```

---
---

## STEP 1 — ANVIL SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/diagnostic-scoring-weights-volatility-decay-2026-05-18.md", "anvil/knowledge/decisions/in-progress-diagnostic-scoring-weights-volatility-decay-2026-05-18.md")`.
>
> Read your specialist file and domain glossary first. **You are the Anvil Systems Analyst.** Working directory is `/Users/marklehn/Developer/GitHub/`. **Context:** This diagnostic produces a population-scale characterization of how findings drop out of Anvil's top-N rankings between audit cycles — specifically distinguishing **real remediation** (coverage or complexity improved) from **fake volatility-decay** (only volatility moved, while coverage and complexity were unchanged). The BACKLOG entry that motivates this audit cites n=2 (`dispute_brief`, `run_validation`). Two functions cannot answer "is this systemic." This diagnostic does the population work.
>
> **Critical data-model context to internalize before writing queries:**
> - Canonical table names are `code_chunks` and `health_scores` (NOT `chunks` or `chunk_scores` — that older naming caused a query failure in the 2026-04-14 coupling-hotspots diagnostic per agent-prompt-feedback.md). Verify table names with `PRAGMA table_info` against `anvil/anvil.db` BEFORE writing any analysis query.
> - DB-recorded cycle numbers may differ from the filename-cycle numbers in `knowledge/research/cycle-N-findings-*.md`. PROJECT_STATUS records that the cycle-13 run was DB cycle 17; cycle-files exist for 14/15/16/17 (timestamps may give clues). Query `SELECT MAX(cycle_number), MIN(cycle_number), COUNT(*) FROM cycle_reports` to anchor the cycle range. Use DB cycle_number for everything; treat filename-cycle numbering as advisory only.
> - **Volatility is percentile-normalized per cycle**, not raw. Per `anvil/src/scorer.py` lines 178-181: `vol_ranks = {v: i / max(len(vol_values) - 1, 1) for i, v in enumerate(vol_values)}`. This means a function's volatility score moving from 1.0 to 0.11 between cycles can reflect either (a) the function's underlying raw volatility dropped while others stayed stable (genuine relative-decay), OR (b) other functions' raw volatility climbed while this one stayed stable (relative displacement). The audit needs to disambiguate these where possible. The raw volatility behind each percentile-normalized score is NOT stored in `health_scores`; only the normalized score is persisted. The audit can still characterize "did this function's percentile-rank drop while its coverage/complexity were unchanged" — which is the operationally useful question — but should be clear about what the data does and does not show.
> - Role-specific weight overrides exist in `anvil/src/config.py` (`ROLE_SCORING_WEIGHTS` at line 70+). The global `SCORING_WEIGHTS` is volatility 0.25. Different roles get different weight sets; route handlers may have a different weight profile than the global default. The audit must report which role each tracked function carried and which weight set actually applied.
>
> **Do exactly this:**
>
> **(1) Anchor the cycle range.** Query `anvil/anvil.db` for `SELECT cycle_number, cycle_date, project_name FROM cycle_reports ORDER BY cycle_number`. Report the full list. Identify the DB cycle_number corresponding to the 2026-04-14 cycle (Phase 2.1 first production run with intent gaps) — this is the "anchor cycle" for the audit. Identify the DB cycle_number for the most recent cycle (2026-05-17 cycle-13 plan, expected DB cycle 17). Report both. The audit window is anchor_cycle → most_recent_cycle.
>
> **(2) Build the population.** From the anchor cycle, identify the **top-20 invoice-pulse chunks** by composite_score where coverage_score = 1.0 (i.e., zero-test-coverage findings — the class the BACKLOG question is about). Query shape: `SELECT c.id, c.name, c.file_path, c.functional_role, hs.volatility_score, hs.coverage_score, hs.complexity_score, hs.coupling_score, hs.staleness_score, hs.composite_score FROM code_chunks c JOIN health_scores hs ON c.id = hs.chunk_id WHERE hs.cycle_id = (SELECT id FROM cycle_reports WHERE cycle_number = <anchor>) AND c.project_id = (SELECT id FROM projects WHERE name = 'invoice-pulse') AND hs.coverage_score >= 0.99 ORDER BY hs.composite_score DESC LIMIT 20`. Verify column names against `PRAGMA table_info(code_chunks)` and `PRAGMA table_info(health_scores)` before running — adapt column names if the schema differs from this sketch (e.g., if `cycle_id` is `cycle_number` directly, or if the join column is named differently). Report the literal output as a markdown table.
>
> **(3) Track the population across cycles.** For each of the 20 chunks from step (2), pull its health_scores row at every cycle in the audit window. Query shape: `SELECT cycle_number, volatility_score, coverage_score, complexity_score, composite_score FROM health_scores hs JOIN cycle_reports cr ON hs.cycle_id = cr.id WHERE hs.chunk_id = ? ORDER BY cycle_number`. Note that not every chunk may exist in every cycle (chunks can be deleted between cycles if their source code was removed). Report each chunk's full trajectory as a markdown table. If a chunk is missing from some cycles, note "absent" rather than fabricating a row.
>
> **(4) Classify each chunk's anchor→latest trajectory.** For each of the 20 chunks, classify into one of these buckets based on the delta from anchor_cycle to most_recent_cycle:
> - **REMEDIATED-COVERAGE** — coverage_score at most_recent < 0.5 (tests added). Real remediation.
> - **REMEDIATED-COMPLEXITY** — complexity_score at most_recent decreased by ≥ 0.1 vs. anchor. Real remediation (function was refactored).
> - **REMEDIATED-BOTH** — both above.
> - **VOLATILITY-DECAYED** — volatility_score dropped by ≥ 0.5 vs. anchor, while coverage_score and complexity_score moved by < 0.05 each. Fake remediation; the function is no safer than at anchor but its composite dropped.
> - **STALE-NOISE** — coverage_score and complexity_score unchanged, volatility_score also roughly unchanged, but composite drifted slightly via other dimensions (coupling/staleness). Marginal noise; not a methodology finding.
> - **DELETED** — chunk no longer present in latest cycle. Source code was removed.
> - **OTHER** — anything not fitting the above. Describe in prose.
>
> Report the classification as a markdown table: `Chunk | File | Role | Anchor Composite | Latest Composite | Δ Composite | Coverage Δ | Complexity Δ | Volatility Δ | Bucket`. Sum the buckets at the bottom: how many in each.
>
> **(5) Role-weight cross-check.** For each chunk, look up its `functional_role` and identify which weight set applied at most_recent_cycle. Cross-reference `anvil/src/config.py` `ROLE_SCORING_WEIGHTS` to determine each role's weight tuple. Report a small table: `Role | # of tracked chunks with this role | Weight tuple (vol, cov, comp, coup, stale)`. Flag any role where volatility weight ≥ 0.25 AND coverage weight ≤ 0.25 — these are the roles most susceptible to volatility-decay obscuring genuine zero-coverage findings.
>
> **(6) Top-N displacement check.** Independently of the tracked population, at most_recent_cycle, what is the cycle-17 invoice-pulse top-20 composite list? Same query shape as step (2) but at most_recent cycle. How many of the 20 chunks from step (2) (the anchor top-20) are still in the most_recent top-20? Of those that fell out, how many fell out via REMEDIATION-class buckets vs. VOLATILITY-DECAYED class buckets? This is the headline ratio the audit was commissioned to produce.
>
> **(7) Evaluate the four BACKLOG options against the data.** The BACKLOG entry lists four candidate weight-change directions:
> - **(a) Reduce volatility weight.** Quantify: if volatility weight had been 0.15 instead of 0.25 (a 0.10 reduction), and the additional 0.10 weight were redistributed evenly across coverage and complexity (0.05 each), how would the most_recent top-20 have ranked? Recompute composite for the 20 tracked chunks under the alternative weights and report the resulting rank order alongside the actual rank order. Same exercise but reducing volatility to 0.10 (0.15 reduction).
> - **(b) Sticky flag for high-impact findings.** Describe what "sticky" would mean operationally — does it mean a finding stays in top-N for N cycles after first appearing, regardless of composite drop? Does it mean a finding stays until coverage_score actually moves? Sketch the SQL or Python that would implement each variant. Do NOT propose a specific implementation; the goal is to make the design space explicit for CEO evaluation.
> - **(c) Secondary ranking by `coverage * complexity`.** What does the top-20 look like if sorted by `coverage_score * complexity_score` at most_recent cycle? Report this ranking. Are the BACKLOG-cited functions (`dispute_brief`, `run_validation`) in this ranking, and where? This is the cheapest option to characterize because it requires no weight change.
> - **(d) Conditional volatility decay** — treat volatility differently when coverage_score = 1.0. Sketch: if coverage_score = 1.0, multiply volatility_score's contribution to composite by 0.5 (or set it to a floor of, say, 0.5). Report the alternative-weights top-20 under this rule.
>
> The output for each option is a table or rank list, NOT a recommendation of which option to pick. The CEO decides. Your job is to make the four options legible against the data.
>
> **(8) Surface any additional options the data suggests.** If the audit reveals a fifth option the BACKLOG didn't anticipate — for example, decoupling the role-specific weights from the global ones, or a different normalization scheme for volatility — describe it briefly and quantify its effect on the most_recent top-20 if cheap to do so. If nothing additional surfaces, state that explicitly.
>
> **(9) Methodology limitations.** Explicitly state what this audit cannot answer:
> - Does the audit have access to raw (pre-percentile-normalization) volatility values? No — only normalized scores are stored. So "did the function's underlying volatility actually decay or did other functions become more volatile" is unanswerable from `health_scores` alone. (Could potentially be reconstructed from `git_changes` if commit dates are stored — note whether they are.)
> - Does the audit cover any project other than invoice-pulse? No, by design — invoice-pulse is the only project with multi-cycle history.
> - Does the audit account for chunks that were ADDED to the top-20 between cycles? No — the audit tracks the anchor top-20 forward only. New entrants are out of scope.
>
> **Deposit findings to** `anvil/knowledge/research/scoring-weights-volatility-decay-audit-2026-05-18.md` using `Filesystem:write_file` (NOT bash heredoc, NOT `with open()` if the MCP tool is available). Structure the deposit with sections matching items (1)–(9), plus a one-paragraph **Executive Summary** at the top stating the headline ratio (real remediation : volatility decay) and which of the four BACKLOG options the data most favors (or which the data is insufficient to choose between). Commit: `docs: diagnostic — scoring-weights volatility-decay population audit`.
>
> Standard prompt feedback protocol — append any prompt issues to `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/research/scoring-weights-volatility-decay-audit-2026-05-18.md`
