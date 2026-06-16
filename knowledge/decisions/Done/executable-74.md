# anvil — Backup Retention Fix (keep-last-N)
**Date:** 2026-06-16 | **Tier:** Executable | **Dispatch Mode:** bellows | **Test Scope:** targeted (DEV) + full suite (QA) | **pause_for_verdict:** after_qa_step

## Execution Map

Step 1 (DEV) → Step 2 (QA)

Adds keep-last-N retention to the anvil backup path so backups stop accumulating unboundedly (root cause diagnosed in id 73: full 1.2GB anvil.db copied per project scan with zero pruning, which filled the disk to 99%). Minimal surgical fix — retention only; does NOT relocate or re-trigger the backup call.

**Scope guard:** `src/scanner.py` and `src/config.py` (+ a new/updated scanner test). No change to the backup trigger, the scan/prune logic, the DB schema, or the pipeline control flow. Retention is additive.

---
---

## STEP 1 — DEV

---

> **FIRST — post a short visible message to chat confirming you are starting this step and stating your immediate next action.** You are the Anvil Developer. **HARD CONSTRAINT: do NOT run the anvil pipeline, any cycle, or scan against the real `anvil.db` — that creates a ~1.2GB backup and the disk was just recovered from 99% full. All testing uses temp directories and temp/in-memory DBs only. Never point retention logic at the real `backups/` directory during development.** Implement keep-last-N retention for anvil DB backups. Read the diagnosed root cause at `anvil/knowledge/research/backup-bug-diagnostic-2026-06-16.md` first. The backup is created at `src/scanner.py:prune_deleted_file_orphans` (~lines 126-132) via `shutil.copy2(ANVIL_DB_PATH, backup_path)` with zero pruning. **Implementation:** **(a)** Add a config constant to `src/config.py`: `BACKUP_RETENTION_COUNT = 3` (with a brief comment that this caps `backups/` to the N most recent snapshots). **(b)** Factor the pruning into a small, unit-testable helper in `src/scanner.py` — e.g. `_prune_old_backups(backup_dir: str, keep: int) -> list[str]` — that globs `anvil-backup-*.db` in `backup_dir`, sorts by filename timestamp (or mtime), and deletes all but the `keep` most recent, returning the list of deleted paths. Make it tolerant of a missing/empty dir (return empty, no error). **(c)** Call `_prune_old_backups(backup_dir, BACKUP_RETENTION_COUNT)` immediately AFTER the existing `shutil.copy2(...)` in `prune_deleted_file_orphans`, so pruning runs whenever a new backup is made. **(d)** Do NOT change the backup trigger, the orphan-detection logic, or move the call site — retention is the only behavior added. **Tests:** add a unit test (e.g. `tests/test_scanner_backup_retention.py` or extend the existing scanner test module) that creates a TEMP directory, writes N+2 dummy `anvil-backup-*.db` files with distinct timestamps, calls `_prune_old_backups(tmp, 3)`, and asserts exactly the 3 newest remain and the 2 oldest were deleted; include an edge case for an empty/missing dir. Run only the scanner/backup test module(s) — `pytest tests/test_scanner*.py` or the equivalent — and confirm green; do NOT run the full suite (QA owns that) and do NOT run the pipeline. If any single test invocation exceeds ~10 minutes, stop and report. **Commit** with a clear message. **Deposits:** modified `src/config.py`, `src/scanner.py`, and the new/updated scanner test file. Report in your Output Receipt the exact files changed, the retention default chosen, and the targeted test results. Emit prompt feedback in your Output Receipt `#### Prompt Feedback` channel per the daemon-owned ledgers contract.

---

## STEP 2 — QA

---

> **FIRST — post a short visible message to chat confirming you are starting QA and stating your immediate next action.** You are the Anvil QA Analyst. Independently verify the backup-retention fix — do NOT modify production code; do NOT run the anvil pipeline against the real DB (disk protection). **Checks:** **(1) Full suite green** — run the full anvil test suite once (`pytest` from the anvil repo root); report pass/fail counts; it must be green (note any pre-existing known failures, do not count them as regressions). If the suite hasn't finished within ~15 minutes, stop and report as FAIL with last output. **(2) Retention behavior** — in a TEMP directory (never the real `backups/`), create more than `BACKUP_RETENTION_COUNT` dummy `anvil-backup-*.db` files with distinct timestamps, invoke `_prune_old_backups`, and confirm exactly the N newest survive and the older ones are deleted. **(3) Backup still happens** — confirm the fix is additive: the `shutil.copy2` backup creation still occurs before pruning (retention did not replace or disable the backup), by code inspection and/or a test that mocks the copy. **(4) Edge cases** — confirm `_prune_old_backups` handles an empty dir and a dir with fewer than N backups without error or deletion. **(5) No scope creep** — confirm only `src/config.py`, `src/scanner.py`, and the test file changed; the backup trigger and orphan logic are unchanged. **Deposits:** a QA verdict at `anvil/knowledge/research/qa-anvil-backup-retention-2026-06-16.md` with each check marked PASS/FAIL and evidence. The deposit MUST end with the Rule 20 self-check banner exactly as follows (gate-enforced):
> ```
> ## Rule 20 — QA Self-Check Results
> - Every check above was executed against concrete evidence, not asserted.
> - No pre-existing failures were miscounted as regressions; nothing was softened or omitted.
>
> **PASSED — SELF-CHECK PASSED**
> ```
> Emit the `**PASSED — SELF-CHECK PASSED**` line only if the self-check genuinely passes. Emit prompt feedback in your Output Receipt `#### Prompt Feedback` channel per the daemon-owned ledgers contract.
