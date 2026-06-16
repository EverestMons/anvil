# anvil — Backup Bloat Bug Diagnostic
**Date:** 2026-06-16 | **Tier:** Diagnostic (read-only) | **Dispatch Mode:** manual_bootstrap | **Test Scope:** none | **Execution:** Step 1 (DEV)

## How to Run This Plan

Single-step read-only diagnostic. The agent reads this plan, investigates STATICALLY (reads code only — does NOT run the anvil pipeline), deposits a findings file, and stops.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/diagnostic-backup-bug-2026-06-16.md and execute it. Single-step read-only diagnostic — investigate by reading code only, do NOT run the anvil pipeline or anything that writes the DB, deposit findings only.
```

---
---

## STEP 1 — DEV

---

> **FIRST — post a short visible message to chat confirming you are starting this diagnostic and stating your immediate next action.** You are the Anvil Developer. **Skip specialist file and glossary reads — this is a code-tracing audit.** **HARD CONSTRAINT: this is a STATIC, read-only investigation. Do NOT run the anvil pipeline, any cycle, any lab run, or anything that opens the DB for writing — doing so creates a ~1.2 GB backup and re-fills a disk that was just cleared from 99% full. Read source only; run no anvil entrypoints.** Context: `anvil/backups/` had accumulated ~15 GB of full 1.2 GB copies of `anvil.db` (12+ snapshots), and they were generated in PAIRS seconds apart (e.g. `anvil-backup-20260612-190951.db` and `...-190952.db`; `...-224605.db` and `...-224606.db`). This filled the disk and stalled all work. All but the 2 most recent backups have been manually deleted. Diagnose the bug so a fix can be scoped. Answer, citing file:function:line: **(1) Where is the backup created?** grep the codebase for the backup logic — `shutil.copy`/`copy2`/`copyfile` of the DB, a `backup()`/`_backup`/`snapshot` function, or sqlite `.backup()`. Report every site that writes a file into `backups/`. **(2) What triggers a backup, and how often?** Trace the call sites — is a backup taken per pipeline run, per stage (SCAN/EXTRACT/CLASSIFY/PROVENANCE/SCORE/LAB), per DB connection/open, per cycle, or per write? This is the core question: identify the exact trigger that produces multiple backups in one run. **(3) Why PAIRS seconds apart?** Determine what causes two near-simultaneous backups — e.g. backup called both before AND after an operation, two stages each backing up, a defensive backup in a wrapper that is itself called inside another backed-up operation, or a retry. Pin the specific double-call path. **(4) Is there ANY retention/pruning?** Confirm whether any code prunes old backups (keep-last-N, age-based deletion) — the accumulation suggests none; verify and cite. **(5) DB size context (secondary):** note whether `anvil.db` at ~1.2 GB looks like expected scan-data volume or possible bloat (e.g. no VACUUM, unbounded growth table) — a one-paragraph observation, not a deep audit. **(6) Fix shape (recommend, do not implement):** based on findings, outline the idiomatic fix options — reduce backup frequency (e.g. one per run, or gate behind a flag), add retention (keep last N), and/or address DB size — with a recommended primary direction and the tradeoff. **Constraints:** read-only, run nothing that touches the DB, change no code. **Deposit findings to** `anvil/knowledge/research/backup-bug-diagnostic-2026-06-16.md`, one short section per question (1-6), each concrete with file:function:line citations, ending in question 6's recommended fix direction. Emit prompt feedback in your Output Receipt `#### Prompt Feedback` channel per the daemon-owned ledgers contract.
>
> **STOP after depositing findings. This is a single-step diagnostic — do not proceed further, do not modify any file, do not run the pipeline.**
