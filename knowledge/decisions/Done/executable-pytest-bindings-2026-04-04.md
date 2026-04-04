# Anvil — Pytest Symbol Binding Resolver
**Date:** 2026-04-04 | **Tier:** Small | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Source:** Codebase Health Roadmap item 5.1
**Diagnostic:** `anvil/knowledge/research/pytest-bindings-diagnostic-2026-04-04.md`

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

```
Read the plan at anvil/knowledge/decisions/executable-pytest-bindings-2026-04-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-pytest-bindings-2026-04-04.md", "anvil/knowledge/decisions/in-progress-executable-pytest-bindings-2026-04-04.md")`. Read your specialist file first. Then read the diagnostic at `anvil/knowledge/research/pytest-bindings-diagnostic-2026-04-04.md` — it contains the full gap analysis and recommended fix. **The diagnostic found:** (1) "tests" bindings are only created at module-level via filename convention (`test_foo.py` → `"foo"`), never at function-level, (2) `target_chunk_id` is always NULL on "tests" bindings, (3) the scorer's Query 1 (target_chunk_id match) always returns 0, and Query 2 (name match) fails because it compares function names against module names, (4) 99.5% of production chunks show zero coverage as a result. **Implement the fix in `src/extractor.py:_store_file_symbols()`** after the calls binding storage loop (after ~line 273). For each call binding where: (a) the caller chunk has `chunk_type = 'test_case'`, (b) the callee name resolves to a production chunk via name lookup in the same project (use `_find_existing_chunk` or a query against `code_chunks` where `name = callee` AND `chunk_type IN ('function', 'method', 'class')` AND `file_path NOT LIKE 'tests/%'`), then create an additional binding: `db.create_symbol_binding(conn, caller_chunk_id, target_chunk_name, "tests", target_chunk_id=target_chunk_id)`. **Check if `create_symbol_binding` accepts a `target_chunk_id` parameter** — the diagnostic says it's never populated, so you may need to add it. Check `src/db.py:create_symbol_binding()` and add the parameter if missing. **Dedup:** Don't create duplicate "tests" bindings — if the same test_case already has a "tests" binding to the same target (from the existing module-level path), skip it. A simple `SELECT COUNT(*)` before insert, or use INSERT OR IGNORE with a unique constraint. **Preserve existing module-level "tests" bindings** — the new function-level bindings are additive, not replacements. **Tests:** Add tests in `tests/test_extractor.py` verifying: (1) a test_case chunk calling a production function gets a "tests" binding with target_chunk_id populated, (2) a test helper (chunk_type = "function") calling production code does NOT get a "tests" binding, (3) framework method calls (e.g., `execute`, `commit`) that don't resolve to production chunks don't create spurious bindings, (4) existing module-level "tests" bindings still work. Run `python3 -m pytest tests/ -v` to confirm all tests pass. Commit: `feat: function-level pytest bindings for coverage scoring`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read the Step 1 Output Receipt (check git log for the commit). If the fix wasn't committed, stop and report to the CEO. **FIRST — Deliverable Verification.** Read `src/extractor.py` and verify: (a) the new "tests" binding creation logic exists after the calls loop — grep for `"tests"` in the function-level binding context, (b) the logic checks `chunk_type = 'test_case'` before creating bindings, (c) the logic filters out test-file targets (`file_path NOT LIKE 'tests/%'` or equivalent), (d) `target_chunk_id` is populated on the new bindings. Read `src/db.py:create_symbol_binding()` and verify it accepts and stores `target_chunk_id`. Check new tests exist in `tests/test_extractor.py` — grep for the 4 test cases specified in Step 1. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. If ANY item is ❌, attempt to fix before proceeding. **Then** run the full test suite: `python3 -m pytest tests/ -v`. Confirm no regressions. **Then** run a validation cycle against invoice-pulse to verify the fix works end-to-end: execute `from src.extractor import extract_project` against the invoice-pulse project in `anvil.db`, then query: `SELECT COUNT(*) FROM chunk_symbol_bindings WHERE binding_type = 'tests' AND target_chunk_id IS NOT NULL` — this should be >0 (was 0 before the fix). Also query: `SELECT COUNT(DISTINCT target_chunk_id) FROM chunk_symbol_bindings WHERE binding_type = 'tests' AND target_chunk_id IS NOT NULL` to see how many production chunks gained coverage. Report both numbers. Deposit QA report to `anvil/knowledge/qa/pytest-bindings-qa-2026-04-04.md`. **Final:** Update PROJECT_STATUS.md — add a completed milestone for the pytest binding resolver with the coverage improvement numbers. Then move this plan to Done: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-executable-pytest-bindings-2026-04-04.md", "anvil/knowledge/decisions/Done/executable-pytest-bindings-2026-04-04.md")`. Commit: `chore: status update + move pytest-bindings plan to Done`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Do NOT move the plan to Done again. Wait for CEO confirmation before continuing.**
