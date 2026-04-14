# Anvil — Agent Prompt Feedback Log

## Patterns Identified

### 2026-04-14 — Specialist Sync: find-and-replace string mismatch
**Plan step:** Step 1B change (3) — replace `'SCAN → EXTRACT → SCORE → LAB'` in ANVIL_SYSTEMS_ANALYST.md Role Summary.
**What happened:** The plan's find string used arrow notation (`→`) but the file used comma notation `(SCAN, EXTRACT, SCORE, LAB)`. Python find-and-replace silently produced no match; the change was not applied. Caught in Step 2 QA.
**Recommendation:** Plan prompts should verify the exact text present in the file before specifying a find-and-replace string, or use a broader context anchor (e.g., surrounding sentence) rather than only the pipeline string itself.

