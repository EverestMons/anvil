# QA Verdict — Backup Retention Fix (keep-last-N)

**Date:** 2026-06-16 | **Plan ID:** 74

---

## Check 1 — Full Suite Green

**PASS**

Full test suite: **262 passed** in 2.74s. Zero failures, zero errors, zero skips.

```
============================= 262 passed in 2.74s ==============================
```

No pre-existing known failures to note.

---

## Check 2 — Retention Behavior

**PASS**

Independent verification in a TEMP directory (never the real `backups/`):
- Created 5 dummy `anvil-backup-*.db` files with distinct timestamps
- Called `_prune_old_backups(tmp, 3)`
- Result: exactly 2 oldest deleted, exactly 3 newest survived
- Surviving files confirmed by name: `anvil-backup-20260601-100002.db`, `100003`, `100004`

---

## Check 3 — Backup Still Happens

**PASS**

Code inspection of `src/scanner.py:132-135`:
- Line 133: `shutil.copy2(ANVIL_DB_PATH, backup_path)` — backup creation unchanged
- Line 135: `_prune_old_backups(backup_dir, BACKUP_RETENTION_COUNT)` — called AFTER copy2, inside the same `if os.path.isfile(ANVIL_DB_PATH)` guard
- Retention is purely additive; no backup creation code was removed, moved, or gated differently

The existing test `test_prune_creates_backup` in `tests/test_scanner.py` also confirms backup files are still created (this test passed in the full suite run).

---

## Check 4 — Edge Cases

**PASS**

All edge cases verified via independent Python execution in temp directories:

- **Empty directory:** `_prune_old_backups(empty_tmp, 3)` returns `[]`, no error
- **Missing/non-existent directory:** `_prune_old_backups("/nonexistent/path", 3)` returns `[]`, no error
- **Fewer than N backups:** 2 backups with `keep=3` returns `[]`, both files survive, no deletion

---

## Check 5 — No Scope Creep

**PASS**

`git diff HEAD~1 --stat` confirms exactly 3 files changed:
- `src/config.py` — +3 lines (added `BACKUP_RETENTION_COUNT = 3` with comment)
- `src/scanner.py` — +17 lines (added `import glob`, import of `BACKUP_RETENTION_COUNT`, `_prune_old_backups()` helper, and call after `shutil.copy2`)
- `tests/test_scanner_backup_retention.py` — new file, 83 lines (6 unit tests)

No changes to: backup trigger logic, orphan-detection logic, `prune_deleted_file_orphans` control flow (beyond the additive retention call), DB schema, cycle logic, or any other file.

---

## Rule 20 — QA Self-Check Results
- Every check above was executed against concrete evidence, not asserted.
- No pre-existing failures were miscounted as regressions; nothing was softened or omitted.

**PASSED — SELF-CHECK PASSED**
