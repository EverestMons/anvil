# QA Report — ANVIL_ROOT Hardcode (F8 close-out)

**Date:** 2026-05-18
**Plan:** executable-anvil-root-hardcode-2026-05-18
**Agent:** Anvil QA Analyst
**Dev Log:** knowledge/development/2026-05-18-anvil-root-hardcode-dev-log.md
**Commit:** 86ba5fd `fix(config): hardcode ANVIL_ROOT to canonical main-repo path (F8 close-out)`

---

## Verification Table

| # | Check | Expected | Status | Evidence |
|---|-------|----------|--------|----------|
| 1 | Hardcode landed in `src/config.py` line 6 | `ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"` | ✅ | `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/grep_anvil_root.txt` |
| 2 | No dynamic `os.path.dirname(__file__)` resolution remains | Zero matches, exit code 1 | ✅ | `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/grep_no_dynamic.txt` |
| 3 | Runtime values resolve to canonical main-repo path | ROOT: `/Users/marklehn/Developer/GitHub/anvil`, DB: `.../anvil.db` | ✅ | `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/runtime_values.txt` |
| 4 | Scope limited to `src/config.py` + dev log | 2 files changed: `src/config.py`, dev log | ✅ | `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/git_diff_stat.txt` |
| 5 | Full test suite passes | 219 tests pass | ✅ | `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/pytest_full.txt` |
| 6 | Fix commit present in HEAD ancestry | SHA `86ba5fd` at HEAD | ✅ | `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/git_log.txt` |

---

## Observations

- The DEV audit (Step 1.1) identified two tests that monkey-patch `ANVIL_ROOT`: `tests/test_lab.py:279` and `tests/test_cycle.py:89`. Both use `monkeypatch.setattr("src.lab.ANVIL_ROOT", ...)` to redirect report writes to temp directories. This mechanism works identically on a hardcoded constant — `setattr` replaces the module-level attribute regardless of how the original value was computed. Both tests pass in the full suite run (check 5).
- The `import os` statement is retained because `os.path.join` is still used on line 8 for `ANVIL_DB_PATH`.
- The change is symmetric with the F1/F4 hardcodes for `SCAN_TARGETS` and `DEV_LOG_PATHS`, completing the triangle of worktree-safe path constants.

---

## Verdict

**PASS** — All six checks verified. The hardcode is correct, scoped, and test-safe.

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/anvil-root-hardcode-2026-05-18/knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/
Files verified: 6
```

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** Step 2
**Status:** Complete

### What Was Done
Verified the ANVIL_ROOT hardcode fix across six checks: literal value in config, absence of dynamic resolution, runtime correctness, scope audit, full test suite (219 passed), and commit presence in HEAD. All checks pass.

### Files Deposited
- `knowledge/qa/2026-05-18-anvil-root-hardcode-qa.md` — this QA report
- `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/` — six evidence files

### Files Created or Modified (Code)
- None (QA step — read-only verification)

### Decisions Made
- PASS verdict issued — all six verification checks satisfied

### Flags for CEO
- None

### Flags for Next Step
- None
