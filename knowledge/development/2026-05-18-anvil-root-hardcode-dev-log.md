# Dev Log — ANVIL_ROOT Hardcode (F8 close-out)

**Date:** 2026-05-18
**Plan:** executable-anvil-root-hardcode-2026-05-18
**Agent:** Anvil Developer

## Change Summary

Replaced the dynamic `ANVIL_ROOT` resolution in `src/config.py` line 6 with a hardcoded canonical path. This is symmetric with the F1/F4 fixes that hardcoded `SCAN_TARGETS` and `DEV_LOG_PATHS`.

**Before:** `ANVIL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`
**After:** `ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"`

## Files Changed

- `src/config.py` line 6 — replaced dynamic `__file__`-based resolution with hardcoded path

## Audit Findings (Step 1.1)

### Production usage of ANVIL_ROOT
| File | Line | Usage |
|---|---|---|
| `src/config.py` | 6 | Definition (changed) |
| `src/config.py` | 8 | `ANVIL_DB_PATH = os.path.join(ANVIL_ROOT, "anvil.db")` |
| `src/lab.py` | 18 | Import of `ANVIL_ROOT` |
| `src/lab.py` | 94 | `os.path.join(ANVIL_ROOT, "knowledge", "research", ...)` for cycle report path |

**No production code requires dynamic resolution.** All usages are simple path concatenation with the constant.

### Test monkey-patches of ANVIL_ROOT
| File | Line | Usage |
|---|---|---|
| `tests/test_lab.py` | 279 | `monkeypatch.setattr("src.lab.ANVIL_ROOT", str(tmp_path))` |
| `tests/test_cycle.py` | 89 | `monkeypatch.setattr("src.lab.ANVIL_ROOT", str(cycle_project))` |

Both tests use `monkeypatch.setattr` to redirect report writes to temp directories. This mechanism works identically on a hardcoded constant — `setattr` replaces the module-level attribute regardless of how the original value was computed.

### `os` import check
`os.path.join` is still used on line 8 (`ANVIL_DB_PATH`). The `import os` remains necessary.

## Runtime Verification (Step 1.4)

```
>>> from src.config import ANVIL_ROOT, ANVIL_DB_PATH
>>> repr(ANVIL_ROOT)
'/Users/marklehn/Developer/GitHub/anvil'
>>> repr(ANVIL_DB_PATH)
'/Users/marklehn/Developer/GitHub/anvil/anvil.db'
```

Both resolve to the canonical main-repo path, not the worktree path. Confirmed correct.

## Test Results

```
219 passed in 0.96s
```

Full suite passes, identical to the F9-follow recovery baseline of 219 tests.

## Prompt Feedback

No prompt issues encountered. The plan instructions were clear and unambiguous.

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** Step 1
**Status:** Complete

### What Was Done
Hardcoded `ANVIL_ROOT` in `src/config.py` to `/Users/marklehn/Developer/GitHub/anvil`, replacing the dynamic `__file__`-based resolution that produced worktree paths inside Bellows worktrees. Audited all production and test usages — no blockers found.

### Files Deposited
- `knowledge/development/2026-05-18-anvil-root-hardcode-dev-log.md` — this dev log

### Files Created or Modified (Code)
- `src/config.py` line 6 — replaced dynamic ANVIL_ROOT with hardcoded canonical path

### Decisions Made
- Kept `import os` since `os.path.join` is still used for `ANVIL_DB_PATH`
- No test changes needed — monkey-patch approach works on hardcoded constants

### Flags for CEO
- None

### Flags for Next Step
- Two tests monkey-patch `ANVIL_ROOT` via `monkeypatch.setattr("src.lab.ANVIL_ROOT", ...)` — QA should confirm both still pass (they do as of this run)
