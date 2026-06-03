# Anvil — Backlog

Lightweight capture of mid-session observations and deferred work. Each entry is a candidate for a future plan, not a plan itself.

---

## Open

### 2026-06-02 — Anvil cycle plan template needs 3 fixes for clean Bellows dispatch

Cycle 19 was dispatched via Bellows (first since the F8 ANVIL_ROOT fix). The run succeeded but tripped 3 claim/teardown gates, all from authoring the plan off the cycle-18 template:
1. **Missing `**Dispatch Mode:**` field** — Rule 35 (`validate_at_claim`) rejects plans lacking it, moving them to `halted-`. The cycle-18 template predates Rule 35.
2. **UTC date mismatch** — `run_cycle` names output files by UTC (e.g. `audit-findings-2026-06-03.md`), but the plan declared the local date (`...-06-02`), failing `deposit_exists` + `rule_22_verification`.
3. **Canonical-path cycle report dirties main** — `run_cycle` writes `knowledge/research/cycle-N-findings-{utc}.md` to the canonical anvil path (F8); it lands untracked in main and blocks the worktree-teardown cherry-pick.

**Fix when picked up:** update the Anvil cycle plan template to (a) include `**Dispatch Mode:** bellows`, (b) declare the audit-findings + cycle-report deposits with the UTC date (or a date-agnostic match), and (c) pre-commit the canonical cycle report (or declare it an expected main-tree artifact) so teardown doesn't treat it as a dirty-tree blocker. Reference: cycle 19 manual-close recovery, 2026-06-02.

### 2026-05-18 — Intent-gap findings include functions that no longer exist (volatility window > function lifetime)

**Symptom:** Anvil cycle 17 and cycle 18 audits of invoice-pulse flagged 5 functions in `web/action_queue.py` as zero-coverage, high-volatility (composite scores 0.85, 0.80, 0.66, 0.65, 0.63). The Planner authored a workflow-mapping diagnostic to triage all five as a single cluster. The diagnostic discovered that **3 of the 5 flagged functions do not exist in the current codebase** — `record_response`, `_auto_route_after_response`, and `confirm_carrier` were removed on 2026-04-01 in commit `abaaa3f` as part of a dead-code sweep (31 dead routes across 9 files). The functions remain in Anvil's git history within the volatility scoring window, but they are not in the current `web/action_queue.py`. The effective intent-gap surface for that file is 2 functions, not 5.

**Evidence:** `invoice-pulse/knowledge/architecture/action-queue-workflow-2026-05-18.md` ("Critical Finding" section near top) names the three removed functions and cites commit `abaaa3f`. `invoice-pulse/knowledge/research/dead-code-sweep-2026-04-01.md` is the original deletion record. Anvil cycle 17 findings file lists all 5 with composite ≥ 0.63; cycle 18 (run after the deletion was already in main for ~6 weeks) still lists all 5 with substantially the same scores.

**Root cause:** Volatility scoring uses a git-history window (likely 60–90 days based on cycle 18 still flagging functions deleted 47 days prior). Function-level findings derive their identity from `chunks` table rows, which are produced by the SCAN phase from the current codebase — so a deleted function should not produce a chunk on a fresh scan. The hypothesis is that either (a) the chunk for the deleted function persisted in the DB across cycles (stale chunk not pruned), or (b) the EXTRACT/SCORE phase reads from git history rather than current-state chunks for high-volatility lookups. Diagnosis requires inspecting how `find_intent_gaps()` joins `chunks` against `commits` / `volatility_scores`. The audit didn't go deep enough to identify which mechanism produced the phantom — the diagnostic was scoped to invoice-pulse workflow, not Anvil internals.

**Impact assessment (current):** Misleads downstream triage. The 2026-05-17 invoice-pulse anvil-findings-backlog scoped the action_queue cluster as Actionable #1 with the framing "5 of 14 intent gaps in one file is a density Anvil hasn't surfaced before." That framing drove session-prioritization decisions and the diagnostic deposit. The substantive finding (2 functions need integration test coverage) is correct; the cluster-size argument that escalated it was 60% noise. Future Anvil consumers (the Planner doing curation, the CEO making prioritization calls) cannot trust intent-gap counts as a density signal.

**Suggested fix (SA diagnostic + DEV plan when picked up):** First, identify the mechanism — is it stale chunks or git-history-driven scoring? Diagnostic against the Anvil DB: for each cycle 18 finding, run `SELECT * FROM chunks WHERE name='<function_name>' AND file_path='<file_path>'` and check whether the chunk has a `last_seen_cycle` field, a `deleted_at` flag, or is being scored despite not being produced by the most recent SCAN. Once the mechanism is known: either (a) add a chunk-existence join to `find_intent_gaps()` so deleted chunks don't surface as findings, or (b) prune stale chunks during SCAN if the underlying file no longer contains the function.

**Update 2026-06-02 (cycle 19):** Still live. Cycle 19's invoice-pulse audit again surfaced 2 phantom functions in the top-10 — `rates_grid` (deleted in Phase 4) and `import_contract_setup` (renamed to `_import_contract_setup_section`). Confirms persistence cycle 18 -> 19. Per-finding existence check applied at triage (see `invoice-pulse/knowledge/research/anvil-findings-backlog-2026-06-03.md` Excluded section). Raises priority: every cycle currently requires manual phantom filtering.

**Connection to other Anvil methodology issues:** This is the third volatility-related finding-quality issue in the last week. (1) Morning 2026-05-18 F9-follow attribution replay: volatility-weighted composites caused 9 anchor chunks to appear to "self-decay" due to population collapse, not real improvement. (2) Existing BACKLOG entry above ("Volatility-weighted composite scores cause findings to 'self-resolve' when commit activity tapers"): same class of bug, opposite direction — functions get safer-looking just because activity tapered. (3) This entry: functions surface as high-volatility despite no longer existing. **Pattern:** volatility-as-currently-implemented operates on a temporal window that doesn't align with the chunk-existence window, producing findings whose temporal context disagrees with their structural context. A unified fix may be possible — e.g., scope all scoring (volatility + freshness + staleness) to chunks that exist in the most recent SCAN snapshot, never reach into git history beyond what those chunks reference.

**Cross-reference:** `invoice-pulse/knowledge/architecture/action-queue-workflow-2026-05-18.md` (the diagnostic that surfaced this). The existing "Volatility-weighted composite scores cause findings to 'self-resolve'" BACKLOG entry below (same metric, different failure mode).

**Risk:** Methodology. Like the self-resolve issue, this affects every audit Anvil produces and degrades the value of the findings file as a triage input. No urgency — the Planner can mitigate via per-finding chunk-existence verification at curation time — but that mitigation is manual and lossy.

**Priority:** Medium — third instance of the same class of bug in one week. Worth bundling with the self-resolve fix when scoring methodology gets revisited.

---

### 2026-05-18 — `ANVIL_ROOT` resolves to worktree path inside Bellows worktrees, breaking `cycle_reports.report_path`

**Closed 2026-05-18:** Fix shipped at commit `86ba5fd` (`src/config.py:6` hardcoded to `/Users/marklehn/Developer/GitHub/anvil`). Production-validated by cycle 18 — audit findings file deposited at canonical main-repo path, not worktree-local. 219/219 tests pass. See `PROJECT_STATUS.md` 2026-05-18 (afternoon) F8 entry.

**Symptom:** Cycle 17 (ran inside a Bellows worktree on 2026-05-17) wrote `report_path = /Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/anvil-cycle-13-2026-05-20/knowledge/research/cycle-17-findings-2026-05-17.md` to the DB. The worktree is torn down after the cycle completes, so the path is dead-on-arrival — points at a file that no longer exists.

**Root cause:** `src/config.py` defines `ANVIL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` — derived from `config.py`'s file location at runtime. When Anvil runs from a `.bellows-worktrees/...` checkout, `__file__` resolves inside the worktree, and `ANVIL_ROOT` becomes the worktree path. `lab.py:93–96` then joins that with `knowledge/research/cycle-N-findings-DATE.md` to build the deposit path — which the writer happens to honor for the actual file write (deposit lands inside worktree, gets merged back via Bellows teardown), but the path string recorded in the DB is the pre-merge worktree location.

**Impact assessment (current):** Cosmetic. As of 2026-05-18 Planner audit, nothing reads `cycle_reports.report_path` — grep across Anvil source/tests, Forge, Bellows, and ai-career-digest found only writers, no readers. The same Planner audit performed a one-shot UPDATE rewriting 16 Desktop paths to Developer paths (closing the 2026-05-14 iCloud-migration drift on cycles 1–16). Cycle 17's path was left as-is pending the source fix described below — rewriting the worktree path via SQL would mask the underlying bug.

**Suggested fix (DEV plan when picked up):** Hardcode `ANVIL_ROOT` to `/Users/marklehn/Developer/GitHub/anvil` in `src/config.py`, symmetric with yesterday's F1 fix that hardcoded `SCAN_TARGETS["invoice-pulse"]` and `DEV_LOG_PATHS["invoice-pulse"]`. Pattern: Anvil's canonical paths are not portable — they live in one specific filesystem location, and runtime derivation introduces drift modes (worktrees, copies, symlinks) without buying any portability benefit. Tests-after: confirm `ANVIL_ROOT` value, confirm a fresh cycle records the canonical path in `cycle_reports.report_path`, confirm existing import paths still resolve.

**Tests at risk:** Any test that monkey-patches `ANVIL_ROOT` to a `tmp_path` for isolation. Hardcoding the constant value will not break monkey-patching, but the test surface should be enumerated before the DEV plan ships.

**Risk:** Low. One-line change in a constant. No behavior change for non-worktree runs.

**Cross-reference:** F1 fix (2026-05-17, commit `74c6dce`) handled the same class of drift for `SCAN_TARGETS` and `DEV_LOG_PATHS`. This entry closes the third corner of the same triangle.

**Priority:** Low — purely cosmetic until something reads `cycle_reports.report_path`. Bundle with the next Anvil session that opens `config.py`.

---

### 2026-05-18 — Volatility-weighted composite scores cause findings to "self-resolve" when commit activity tapers

**Symptom:** Two 2026-04-14 backlog CRITICAL findings (`dispute_brief`, `run_validation` in invoice-pulse `app.py`) dropped out of the cycle 17 top-14, even though no remediation occurred. Targeted DB query at cycle 17:

| Function | Coverage | Complexity | Volatility | Composite |
|---|---|---|---|---|
| `dispute_brief` | 1.000 | 0.989 | **0.111** | 0.630 |
| `run_validation` | 1.000 | 0.939 | **0.111** | 0.597 |

vs. cycle 16:

| Function | Coverage | Complexity | Volatility | Composite |
|---|---|---|---|---|
| `dispute_brief` | 1.000 | 0.989 | 1.000 | 0.806 |
| `run_validation` | 1.000 | 0.939 | 1.000 | 0.772 |

Zero coverage gap unchanged. High complexity unchanged. Only volatility moved — and that moved purely because `app.py` saw fewer commits in the 4-week window leading up to cycle 17. The composite drop is real arithmetic; it is also misleading. The functions are no safer than they were on 04-14.

**Why this matters:** Anvil's audit reports give the impression that findings get "better" or "worse" between cycles. They do — but the dynamic is dominated by a metric (volatility) that is uncorrelated with the underlying risk for zero-coverage, high-complexity code. A function with no tests and cyclomatic complexity of 89 doesn't become safer because nobody touched it for a month; if anything, the staleness compounds the risk. The current scoring weights amplify this: volatility carries 0.25 weight (per `config.py:SCORING_WEIGHTS`), so a 0.9 volatility drop directly subtracts ~0.22 from the composite — enough to demote a CRITICAL finding off the top-N.

**Suggested investigation (SA diagnostic when picked up):** characterize how many of the 04-14 actionable items dropped out via "real" remediation (tests added, function refactored, coverage_score or complexity_score moved) vs. "fake" volatility-decay. If the ratio is high, the scoring weights need revisiting. Options to consider: (a) reduce volatility weight, (b) introduce a "sticky" flag that retains a finding in the top-N for N cycles after composite peak even if score decays, (c) report findings sorted by `coverage * complexity` separately from composite to surface coverage-gap-on-complex-code regardless of volatility, (d) treat volatility decay differently when coverage_score stays at 1.0 (no tests = no improvement, period).

**Cross-reference:** Captured in `invoice-pulse/knowledge/research/anvil-findings-backlog-2026-05-17.md` as the 2026-05-18 addendum, with full health-score deltas for the two specific functions.

**Risk:** Methodology, not code. No urgency, but every audit cycle that runs without this fix produces a report that overstates progress. Worth picking up when there's appetite for tuning the scoring engine — likely paired with the Phase 2.x refinements that introduced role-specific thresholds.

**Priority:** Medium — affects every audit report Anvil produces.

---

### 2026-05-18 — Percentile normalization can invert volatility direction during extreme population collapse

**Symptom:** During the F9-follow attribution replay, the `action_queue` function (web/action_queue.py) demonstrated a percentile-normalization inversion: raw volatility dropped 79% (weighted score 9.32 → 2.00, commits 13 → 3 in the 4-week window) yet the percentile-normalized `volatility_score` *increased* from 0.83 to 1.00. The function's true change-frequency risk dropped substantially, but the scorer ranked it as maximally volatile.

**Root cause:** Percentile normalization is a *relative* ranking. The scorer computes `volatility_score` as the percentile rank of `volatility_raw` within the cycle's population — there is no absolute scale anchor. When the population distribution collapses (most files go quiet while a few maintain modest activity), surviving files rank higher in percentile terms even if their absolute activity dropped. In the action_queue case, 83% of the population had zero commits by cycle 17 (down from only 4% at cycle 10), so 3 commits was enough to reach the 100th percentile despite being an absolute decline.

**Impact assessment:** Edge case, not a population-level effect. The cycle 17→18 comparison (1-day inter-cycle gap) showed **zero inversions** across the full chunk population. The 1-day gap shifted the 4-week rolling window by ~1 day, producing no meaningful population distribution shift. The action_queue inversion was driven specifically by the 33-day gap between cycles 10→17, during which the invoice-pulse project's overall commit activity collapsed from 212/220 files active (96%) to 38/225 files active (17%). Under normal inter-cycle intervals (days, not weeks), the effect does not manifest. See `knowledge/research/cycle-18-comparison-memo-2026-05-18.md`, axis D.

**Triggering condition:** Inversion is expected when (a) the inter-cycle gap exceeds ~14 days AND (b) the project's overall commit activity is collapsing or has collapsed (>50% of the file population dropping to zero raw volatility between the two cycles). Future scoring decisions should not rely on percentile stability under either condition. The 33-day gap that produced the observed inversion far exceeded the ~14-day threshold; a 1-day gap produced zero inversions.

**Suggested mitigations if pursued:**
- (a) **Cap percentile drift between cycles** — e.g., max ±0.3 change per cycle, preventing single-cycle normalization jumps from obscuring the raw signal direction.
- (b) **Persist absolute raw-volatility scale** — raw volatility is already computed (`compute_volatility` in scorer.py) but not persisted as a separate column in `health_scores`. Storing it alongside the percentile-normalized score would allow downstream consumers to detect inversions directly.
- (c) **Z-score normalization option** — offer an alternative scoring mode that uses Z-scores instead of percentile ranks for long-gap cycles, preserving directional fidelity when the population distribution is non-stationary.
- (d) **Population-collapse warning** — emit a warning when a cycle is being scored against a population that has collapsed by >50% vs the prior cycle, alerting the operator that percentile scores may not be directionally comparable.

**Risk:** Documentation only. Adding this entry does not change any code or scoring behavior. If a future plan addresses any of the suggested mitigations, that plan's risk would be evaluated separately.

**Priority:** Low. The (d2) volatility floor and (c) Untested Complexity backup view (shipped 2026-05-18 morning as part of the F9-follow scoring fix) already address the practical problem of zero-coverage chunks being incorrectly displaced. The inversion case is now diagnostic context for future scoring methodology decisions, not an active failure mode.

**Cross-reference:**
- `knowledge/research/volatility-attribution-replay-2026-05-18.md` — originating audit; section (5) documents the action_queue inversion, section (6) documents the population-wide collapse.
- `knowledge/research/cycle-18-comparison-memo-2026-05-18.md` — production confirmation; axis D confirms zero inversions under a 1-day inter-cycle gap.
