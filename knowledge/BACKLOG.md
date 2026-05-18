# Anvil — Backlog

Lightweight capture of mid-session observations and deferred work. Each entry is a candidate for a future plan, not a plan itself.

---

## Open

### 2026-05-18 — `ANVIL_ROOT` resolves to worktree path inside Bellows worktrees, breaking `cycle_reports.report_path`

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
