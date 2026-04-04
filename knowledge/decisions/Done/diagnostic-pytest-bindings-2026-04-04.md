# Anvil — Diagnostic: Pytest Symbol Binding Gap
**Date:** 2026-04-04 | **Type:** Diagnostic | **Priority:** 1
**Source:** Codebase Health Roadmap item 5.1

## How to Run This Plan

```
Read the plan at anvil/knowledge/decisions/diagnostic-pytest-bindings-2026-04-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV (Investigation)

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/diagnostic-pytest-bindings-2026-04-04.md", "anvil/knowledge/decisions/in-progress-diagnostic-pytest-bindings-2026-04-04.md")`. Read your specialist file first. Investigate the full pipeline path from test file extraction through to coverage scoring. Answer these 6 questions: **(1) Test mapping current behavior.** In `src/parsers/python_parser.py` `extract_symbols()`, the `test_mappings` list is built from filename convention only (`test_foo.py` → tested module `foo`). Confirm this is the only mechanism that creates `"tests"` type bindings. Are there any other paths in `extractor.py` that create `"tests"` bindings? **(2) Call bindings in test files.** When a test file has `from web.gap_dashboard import _reshape_for_apply` and then calls `_reshape_for_apply(args)`, what bindings get created? Trace through `extract_symbols()` — it should produce an `imports` entry and a `calls` entry. Then trace through `_store_symbols()` in `extractor.py` — what binding types are created for those? Are they `"calls"` and `"imports"` but NOT `"tests"`? **(3) Coverage scorer input.** In `src/scorer.py`, how is the coverage dimension computed? What query does it use to determine if a chunk has test coverage? Does it look at `"tests"` binding type specifically, or does it consider `"calls"` from test chunks too? Show the exact query or function. **(4) Fixture injection pattern.** In invoice-pulse's `tests/conftest.py`, `db` and `app_client` are pytest fixtures. When a test function uses `def test_foo(db, app_client):`, the parameter names `db` and `app_client` are not visible as function calls in the AST — they're injected by pytest at runtime. Confirm this: does the current parser extract any information about fixture parameters? **(5) Quantify the gap.** Run a quick query against `anvil.db`: count how many chunks with `chunk_type = 'test_case'` have at least one `"tests"` binding in `chunk_symbol_bindings`. Then count how many test_case chunks have zero `"tests"` bindings but DO have `"calls"` bindings. This shows the size of the gap. **(6) Proposed fix validation.** The fix would enhance `extract_symbols()` or `_store_symbols()` so that when a test_case chunk calls a function that's defined in a non-test file, a `"tests"` binding is created (in addition to the existing `"calls"` binding). The binding target would be the production chunk's name (not just the module). Would this conflict with any existing logic in the scorer or lab? Are there any edge cases (e.g., test helpers that call production code but aren't test functions themselves)? Deposit findings to `anvil/knowledge/research/pytest-bindings-diagnostic-2026-04-04.md`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Consolidation (Housekeeping)

---

> Before starting, read `anvil/knowledge/research/pytest-bindings-diagnostic-2026-04-04.md` and check the Output Receipt. If status is not Complete, stop and report. Update PROJECT_STATUS.md with a note that the pytest bindings diagnostic is complete. Move this plan to Done: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-diagnostic-pytest-bindings-2026-04-04.md", "anvil/knowledge/decisions/Done/diagnostic-pytest-bindings-2026-04-04.md")`. Commit: `chore: move pytest-bindings diagnostic to Done`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
