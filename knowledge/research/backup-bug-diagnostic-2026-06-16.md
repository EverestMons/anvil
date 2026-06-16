# Backup Bloat Bug — Diagnostic Findings

**Date:** 2026-06-16 | **Type:** Static code-tracing audit (read-only)

---

## (1) Where is the backup created?

**Single site:** `src/scanner.py:prune_deleted_file_orphans:126-132`

```python
backup_dir = os.path.join(ANVIL_ROOT, "backups")
os.makedirs(backup_dir, exist_ok=True)
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
backup_path = os.path.join(backup_dir, f"anvil-backup-{timestamp}.db")
if os.path.isfile(ANVIL_DB_PATH):
    shutil.copy2(ANVIL_DB_PATH, backup_path)
```

This is the only code path in the entire codebase that writes to `backups/`. No other `shutil.copy`/`copy2`/`copyfile` of the DB, no sqlite `.backup()`, no `snapshot` function exists.

---

## (2) What triggers a backup, and how often?

**Trigger:** a backup is created every time `prune_deleted_file_orphans()` finds at least one orphan file (a file path in `code_chunks` that no longer exists on disk).

**Call chain:**
- `src/cycle.py:run_cycle:74` calls `scan_project(conn, project_name)`
- `src/scanner.py:scan_project:51` calls `prune_deleted_file_orphans(conn, project_id, on_disk_paths)`
- `src/scanner.py:prune_deleted_file_orphans:122-132` — if `orphan_fps` is non-empty (line 123), the backup fires unconditionally

**Frequency:** one backup per project scan that has any orphan files. In an actively-developed codebase where files are regularly renamed/moved/deleted, orphans are common — so effectively **one backup per scan, per project**.

There is no gate, flag, cooldown, or deduplication. Every qualifying scan copies the full ~1.2 GB database.

---

## (3) Why PAIRS seconds apart?

`SCAN_TARGETS` in `src/config.py:12-23` defines **two projects**: `"invoice-pulse"` and `"bellows"`. Both share the same `anvil.db` (at `ANVIL_DB_PATH`, `src/config.py:10`).

When the pipeline runs both projects in sequence (e.g., `run_cycle(conn, "invoice-pulse")` then `run_cycle(conn, "bellows")`), each call triggers its own `scan_project` → `prune_deleted_file_orphans`. If **both** projects have at least one orphan file, each independently copies the same `anvil.db` to `backups/` — producing two ~1.2 GB files with timestamps 1 second apart.

This is confirmed by the observed pattern: `anvil-backup-20260612-190951.db` and `anvil-backup-20260612-190952.db` — exactly 1 second apart, consistent with two sequential project scans completing their prune step back-to-back.

The backup timestamp uses `%Y%m%d-%H%M%S` (second-level granularity, `src/scanner.py:128`), so the two copies are distinguishable but effectively duplicate — both are snapshots of the same DB moments apart.

---

## (4) Is there ANY retention/pruning?

**No.** There is zero retention or pruning logic anywhere in the codebase. Confirmed by:

- No `delete`, `remove`, `unlink`, `glob`, or `os.listdir` calls targeting the `backups/` directory
- No keep-last-N, age-based, or size-based cleanup
- No scheduled maintenance or `VACUUM` of the database itself

Backups accumulate indefinitely. With ~2.4 GB per pipeline run (two projects x 1.2 GB), and runs happening regularly, the 15 GB accumulation (12+ snapshots / 6+ pipeline runs) is the expected outcome.

---

## (5) DB size context

The ~1.2 GB database size is **plausible but likely bloated** for the scan data volume:

- `code_chunks.content` (`src/db.py:41`) stores **full file contents** as TEXT for every discovered source file across both projects. This is the primary size driver.
- `chunk_fingerprints` stores per-cycle minhash signatures as BLOB (`src/db.py:68`), accumulating across cycles without pruning.
- `chunk_similarities` stores pairwise similarity scores per cycle (`src/db.py:115-121`), which grows quadratically with chunk count.
- **No `VACUUM` is ever called.** SQLite's WAL mode (`src/db.py:23`) means deleted rows from prune operations leave freelist pages. After many prune cycles, the DB file can be significantly larger than its live data.
- No historical data pruning — fingerprints, similarities, and health_scores from all past cycles persist indefinitely.

A periodic `VACUUM` and/or pruning old cycle data would likely reduce DB size substantially.

---

## (6) Recommended fix direction

### Primary fix: reduce backup frequency + add retention

**A. Gate backups to once per pipeline run, not per project scan.**
Move the backup call out of `prune_deleted_file_orphans` and into `run_cycle` (or a wrapper that calls `run_cycle` for all projects). Take one backup before any destructive operation in the entire run, not one per project. This alone halves the backup volume.

Better yet: **make backups opt-in via a flag** (e.g., `BACKUP_BEFORE_PRUNE = True` in config), defaulting to on but allowing suppression for routine runs where the data is recoverable from git.

**B. Add keep-last-N retention.**
After creating a new backup, glob `backups/anvil-backup-*.db`, sort by timestamp, and delete all but the most recent N (e.g., 3). This caps disk usage at ~3.6 GB regardless of run frequency. Simple to implement — ~5 lines in the backup code path.

**C. (Secondary) Address DB size.**
- Add a periodic `VACUUM` after prune operations (or as a post-cycle maintenance step).
- Consider pruning old-cycle data from `chunk_fingerprints`, `chunk_similarities`, and `health_scores` (keep last N cycles).
- Evaluate whether `code_chunks.content` (full file text) is needed long-term or could be loaded on-demand from disk.

### Recommended primary direction

**B (retention) is the highest-impact, lowest-risk fix** — it's a ~5-line addition that prevents unbounded disk growth regardless of pipeline frequency. Combine with **A** (deduplicate the per-project backup) to cut backup creation rate in half. **C** is a separate, lower-priority improvement for DB hygiene.

### Tradeoff

Retention (B) means losing older restore points. With keep-last-3, only the 3 most recent states are recoverable. Given that the pipeline runs frequently and the DB can be rebuilt from source code + git, this is an acceptable tradeoff — the backup is a convenience safety net, not a disaster-recovery archive.

---

#### Prompt Feedback

- Diagnostic prompt was clear, well-structured, and appropriately constrained (static-only).
- The six-question framework efficiently directed the investigation without unnecessary exploration.
- Explicit "do NOT run the pipeline" constraint was critical given the disk-fill context — good inclusion.
