# Anvil — Backlog

Lightweight capture of mid-session observations and deferred work. Each entry is a candidate for a future plan, not a plan itself.

---

## Open

### 2026-06-08 — Enforce project_id scoping invariant on health_scores-joining finding queries

**Context:** Bellows cycle 1 (first multi-project run) leaked invoice-pulse chunks into bellows findings — `find_coverage_gaps` and `find_coupling_hotspots` filtered on `cycle_id` alone, and `cycle_id` is per-project (not globally unique, `cycle.py` `MAX(cycle_number WHERE project_id)+1`), so cycle N collides across projects sharing it. Fixed in `executable-anvil-lab-project-scope-fix-v2-2026-06-08` (commit `ff00ab8`): added `cc.project_id = ?` to both; regression test `test_finding_functions_project_scoped` added; validated by cycle 2 (commit `7e70af9` — 0 coverage gaps for bellows, 47 would-be-leaked rows all project_id=1). The SA audit confirmed the other 9 query surfaces already scoped.

**Residual (Low):** the root — `cycle_id` is not globally unique — remains; the fix defangs it by requiring `project_id` everywhere. No automated guard prevents a *future* finding query from joining `health_scores` on `cycle_id` without a `project_id` constraint. **Fix when picked up:** a lint/test asserting every `health_scores`-joining query in `lab.py` also constrains `code_chunks.project_id`. Priority: Low (regression test covers the two current offenders; this guards new ones).

### 2026-06-08 — Scan files_total inflation: non-source dirs walked

Cycle 2 scan reported `files_total=3088` for bellows, a 42-`.py` repo. `.bellows-worktrees`/`.bellows-cache` are now excluded (commit `4f65e8d`) but `logs/`, `knowledge/`, `.pytest_cache`, `.claude` are still walked and registered in `files` (only `.py` are extracted, so findings are unaffected — purely metric inflation). **Fix when picked up:** exclude non-source dirs from SCAN discovery, or restrict registration to extractable extensions. Priority: Low.

### 2026-06-08 — Mono-role `utility` classification for non-invoice-pulse projects

Both bellows cycles classified all 155 chunks as `utility` — the role taxonomy/weights are invoice-pulse-derived, so bellows roles (watcher/dispatcher/gate/verdict-lifecycle) aren't recognized and composites are effectively role-blind for bellows. Structural findings (coverage/coupling/clone/staleness/complexity/co-change) are sound; role-weighted prioritization is not. **Fix only if bellows becomes a recurring target:** add bellows role definitions + a `PROJECT_BRIEF.md`/`domain-glossary.md` (the latter also activates the intent layer). Priority: Low (deferred — exploratory target only). Note: bellows cycle 1's coverage gaps were contaminated (pre-fix); cycle 2 is the valid baseline.

### 2026-06-05 — (d2) volatility floor is not persisted; cycle 18–19 QA floor-invariant check was wrong-layer and never evaluated

Surfaced during the cycle-plan-template review (BACKLOG 2026-06-02, closed). The (d2) floor (`scorer.py:332`: `if coverage >= 0.99: volatility = max(volatility, ZERO_COVERAGE_VOLATILITY_FLOOR)`, floor=0.5) is applied as a **local variable inside `compute_composite`** and fed to the weighted composite — but the raised value is **never written back to `health_scores.volatility_score`**. The persisted column keeps the raw percentile-normalized volatility.

Consequence: the per-cycle QA check carried in the cycle-18 and cycle-19 executables — `SELECT COUNT(*) FROM health_scores WHERE project='invoice-pulse' AND cycle_number=N AND coverage_score >= 0.99 AND volatility_score < 0.5`, asserted "Expected: 0" — is wrong on two counts. (a) It targets the raw `volatility_score` column, which by design retains sub-0.5 values for floored chunks; run correctly against cycle 20 it returns **1235**, not 0. (b) It never actually evaluated in cycles 18–19: the query references a non-existent `project` column (real key is `project_id`) and `cycle_number` (absent from `health_scores`; the column is `cycle_id`), so it threw `no such column: project` and the traceback sat in the evidence file unverified. The new template drops this check entirely — the floor logic is covered by the scorer unit suite, which the QA `pytest tests/` gate runs.

**Decision fork (CEO), not a bug to auto-fix:** do we want a *persisted* floored-volatility signal at all? Options: (a) leave as-is — floor stays a composite-time transform, unit-tested, no DB invariant (status quo, zero work); (b) persist a separate `composite_volatility` (floored) column on `health_scores` so downstream consumers and a correct per-cycle invariant become possible; (c) add a correct composite-layer invariant to QA without a schema change (assert no coverage≥0.99 chunk has a composite below its floored-volatility lower bound). **Recommendation:** (a) — the floor's only job is to keep zero-coverage chunks from ranking artificially safe in the composite, which it does and which the unit suite already protects. Revisit only if a downstream consumer needs the floored value directly.

**Priority:** Low (documentation/methodology; no active failure — the only artifact was a silently-erroring QA check now removed).

### 2026-06-05 — Scanner creates duplicate module rows for the same file_path across cycles

**Closed 2026-06-05:** Diagnostic found no ongoing bug — `detect_changes()` already guards against duplication. The 1,182 excess rows were a historical one-time double-insert (contiguous ID block starting at 5754, all adjacent pairs, all `cycle_id=None`). One-time dedup DELETE removed all 1,182 duplicates (5,213 → 4,031 module chunks, 0 FK violations). No code change needed. Backup at `backups/anvil-backup-dedup-20260605-175815.db`.

### 2026-06-03 — File-set reconciliation: prune chunks for deleted files (DB hygiene)

**Closed 2026-06-05:** Fixed by `executable-anvil-orphan-chunk-reconciliation-2026-06-05.md`. Prune of deleted-file orphans implemented in `scanner.py:prune_deleted_file_orphans()`, called after `discover_files()`. 2,652 orphan chunks (2,400 modules + 252 children across 1,601 file_paths) pruned with clean cascade. Pre-prune timestamped backup, idempotent re-run. Commit `aa7c4c8`. QA PASS (238/238 tests).

The intent-gap phantom fix (last_seen_cycle, 2026-06-03) handles deleted-file orphans at the *filter* level — the extractor `continue`s on missing files, so their chunks never get stamped and are excluded from scoring/findings. But the rows persist. The (a2) sizing during that fix found **1,599 orphan module chunks** for invoice-pulse (files no longer on disk): 1,560 JSON, 22 md/html, 17 .py (16 test files, 1 production: `web/training.py` with 20 child chunks). None currently surface as findings (filtered), so this is DB hygiene, not correctness. **Fix when picked up:** after `discover_files()` in SCAN, compute DB-module-chunks minus on-disk-files and DELETE (or flag) the orphans + their children. Coordinate with the non-destructive philosophy — if deleting, handle `chunk_dependencies`/`similarities`/`symbol_bindings`/`provenance` cascades. **Priority:** Low.

### 2026-06-03 — `find_clone_candidates` reads `chunk_similarities`, not `health_scores` — residual phantom surface

**Closed 2026-06-05:** Fixed by `executable-anvil-orphan-chunk-reconciliation-2026-06-05.md`. Added `last_seen_cycle = ?` filter to `find_clone_candidates` (both sides: `a.last_seen_cycle` and `b.last_seen_cycle`), `find_best_practice_deviations`, and all 7 `generate_specialist_update_data` queries. Full bypass-surface audit confirmed no other unprotected readers produce findings. Commit `aa7c4c8`. QA PASS (238/238 tests).

The phantom fix scoped the scorer and `find_intent_gaps()` to `last_seen_cycle = current`, which transitively fixes every Lab finding type that flows through `health_scores`. But `find_clone_candidates` (`lab.py:193-194`) reads `chunk_similarities` directly and does NOT go through `health_scores`, so dead/orphan chunks can still surface as clone candidates. Lower-impact (different finding type, not the high-traffic intent-gap surface) but it's the same class of bug the phantom fix closed elsewhere. **Fix when picked up:** add a `last_seen_cycle = current` join/filter to `find_clone_candidates` (and audit role/chunk stats at `lab.py:322,763` for the same issue). **Priority:** Low.

### 2026-06-03 — Cycle-20 population discontinuity (characterized; no scoring-methodology decision warranted)

**Closed 2026-06-03:** Diagnostic `knowledge/research/scoring-population-discontinuity-2026-06-03.md` characterized this. The premise was largely a QA measurement artifact: the real scored-population delta was **4,175 → 3,688 (487, 11.7%)**, not the ~2,000/35% the cycle-20 QA narrative implied (which conflated total chunk count with scored count). The "5 displaced coupling findings" (`execute`/`commit`/`close`, `_get_db`, `get_connection`) were never findings — they are noise-filtered by `_is_noise_chunk()` (`lab.py:29-44`) and absent from `find_intent_gaps()` at both cycles; the QA delta used raw SQL without the noise filter. Dropped orphans were overwhelmingly inert (64% zero coupling, 74% zero volatility); percentile drift was modest and non-directional (max coupling 0.083, max volatility 0.042, no threshold crossings). The two sibling bugs are orthogonal to population composition — self-resolve is handled by the d2 floor (shipped `155f3d1`), inversion is driven by inter-cycle gaps + activity collapse. **No CEO scoring-methodology decision warranted from this discontinuity.** Cycle 20 is the correct clean baseline.

**Residual (Low):** Cycle 20 is a structural breakpoint for `compare_cycles()` — any cross-boundary comparison (cycle ≤19 vs ≥20) reports ~487 spurious "removed" chunks (orphan exclusions, not code deletions). One-time step, not cumulative; post-fix (20+ vs 20+) comparisons are clean. Optional: annotate the cycle-20 `cycle_reports` record, or have cross-boundary consumers discount the ~487 — only worth doing if cross-boundary comparisons are actually performed.

### 2026-06-02 — Anvil cycle plan template needs 3 fixes for clean Bellows dispatch

**Closed 2026-06-05:** Canonical template authored at `knowledge/architecture/cycle-plan-template.md` (commit `019e028`), replacing the copy-the-prior-cycle habit. All 3 fixes landed: (1) `**Dispatch Mode:** bellows` in header (Rule 35), (2) audit-findings + cycle-report deposits declared with the UTC date (gate `_resolve_deposit_path` matches literally — no glob — so local-date declarations fail; authoring rule 2 covers the boundary), (3) canonical cycle report declared as a DEV deposit + Planner wrap-commits it on main before the terminal close verdict (it's a tracked artifact, not gitignored). Review also fixed broken `WHERE project=...` queries inherited from cycle-18/19 (real column is `project_id`; no `cycle_date`; `health_scores` joins via `chunk_id`) and dropped a wrong-layer floor-invariant check — see new Open entry below.

Cycle 19 was dispatched via Bellows (first since the F8 ANVIL_ROOT fix). The run succeeded but tripped 3 claim/teardown gates, all from authoring the plan off the cycle-18 template:
1. **Missing `**Dispatch Mode:**` field** — Rule 35 (`validate_at_claim`) rejects plans lacking it, moving them to `halted-`. The cycle-18 template predates Rule 35.
2. **UTC date mismatch** — `run_cycle` names output files by UTC (e.g. `audit-findings-2026-06-03.md`), but the plan declared the local date (`...-06-02`), failing `deposit_exists` + `rule_22_verification`.
3. **Canonical-path cycle report dirties main** — `run_cycle` writes `knowledge/research/cycle-N-findings-{utc}.md` to the canonical anvil path (F8); it lands untracked in main and blocks the worktree-teardown cherry-pick.

**Fix when picked up:** update the Anvil cycle plan template to (a) include `**Dispatch Mode:** bellows`, (b) declare the audit-findings + cycle-report deposits with the UTC date (or a date-agnostic match), and (c) pre-commit the canonical cycle report (or declare it an expected main-tree artifact) so teardown doesn't treat it as a dirty-tree blocker. Reference: cycle 19 manual-close recovery, 2026-06-02.

### 2026-05-18 — Intent-gap findings include functions that no longer exist (volatility window > function lifetime)

**Closed 2026-06-03:** Fixed via philosophy A — added `last_seen_cycle INTEGER` to `code_chunks`, stamped on every scan (extractor, 4 paths incl. the unchanged-chunk trap), with the scorer and all 3 `find_intent_gaps()` buckets scoped to the current snapshot. Commit `2421f83`; plan `executable-anvil-intent-gap-phantom-fix-2026-06-03.md`; blueprint `knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md`; diagnostic `knowledge/research/intent-gap-phantom-mechanism-2026-06-03.md`. The diagnostic confirmed the mechanism is **(a1) stale orphan chunks in surviving files**, uniform across all phantoms — NOT git-history scoring (b). Cycle 20 validated: 0/5 phantoms surfaced, all five chunk_ids unstamped. **Corrections to the analysis below:** live table names are `code_chunks` / `git_changes` / `health_scores` (not `chunks` / `commits` / `volatility_scores`); `cycle_reports` has no `cycle_date` column (date derives from `started_at`); and `rates_grid` was NOT deleted in Phase 4 — `web/rates.py` was *rebuilt* (commit `769e420`) with the function dropped, so it was an (a1) surviving-file case, not a deleted-file (a2) case. (a2) is structurally possible but was not the active mechanism (sized at 1,599 orphan module chunks, only 1 production .py — see Open follow-up). **Follow-ups opened (Open):** file-set reconciliation; `find_clone_candidates` residual surface; cycle-20 population discontinuity + 5 displaced coupling findings.

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
