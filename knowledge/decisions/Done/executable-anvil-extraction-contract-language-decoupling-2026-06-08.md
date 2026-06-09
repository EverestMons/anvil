# Anvil — Extraction Contract + Language-Extractor Decoupling (Build Plan 1 of N)
**Date:** 2026-06-08 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_qa_step

## Context

First implementation step of the extraction-contract blueprint (`knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md`, commit `a933b21`). Scope is the **language-extraction axis ONLY**: formalize the `ChunkRecord` contract, introduce a language-extractor registry, wrap the existing Python parser behind the `LanguageExtractor` protocol, dispatch extraction by file extension instead of the hardcoded `.py`, and relax the `chunk_type` CHECK constraint.

**This plan deliberately does NOT touch the classifier, scoring weights, archetypes, or `SCAN_TARGETS`.** Re-cut from the blueprint's "Step 2" for two reasons: (1) the blueprint had `classify_chunk` take an archetype argument, but archetype definitions don't exist until the archetype-migration plan — a circular dependency; (2) the `SCAN_TARGETS` `(language, archetype)` metadata is only consumed by the classifier side. Both are deferred to Build Plan 2 (archetype-ization). Isolating the orthogonal axes makes each independently regression-testable.

**This plan is behavior-preserving.** Python is the only registered extractor, and `PythonExtractor` delegates to the unchanged `python_parser` functions, so invoice-pulse and bellows must extract identical chunks, classify identically (classifier untouched), and score identically afterward. The regression gate is: full test suite stays green AND a before/after extraction comparison on invoice-pulse + bellows is byte-identical.

Implements blueprint B.5 items 1–5 and 7 (contract, registry, `PythonExtractor` wrap, extractor dispatch, AST delegation, SQLAlchemy-hook relocation, module-resolution abstraction) plus the B.4 `chunk_type` relax. Omits B.5 item 6 (`SCAN_TARGETS` refactor) and all of section C (classifier).

## How to Run This Plan

Bellows dispatches automatically on deposit. DEV and QA run in one worktree; the plan pauses after QA for the Planner's terminal verdict (`pause_for_verdict: after_qa_step`, `auto_close: false`). Both steps stage their deposits.

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, the design blueprint `knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md` (sections A, B, B.4, B.5 — your spec), `src/parsers/python_parser.py`, `src/extractor.py`, `src/db.py`, `tests/test_python_parser.py`.
>
> **Working directory note:** the worktree IS the anvil root; use relative paths for source. For DB access use the absolute canonical path `/Users/marklehn/Developer/GitHub/anvil/anvil.db`.
>
> **Scope guardrails:** Implement ONLY the language-extraction axis below. Do NOT modify `classifier.py`, `scorer.py`'s role-weight logic, `config.py`'s `SCAN_TARGETS`, or any archetype/role data. If the blueprint suggests a classifier or `SCAN_TARGETS` change, that is deferred to a later plan — skip it. If any blueprint-specified edit doesn't match current source verbatim, STOP and report rather than improvising.
>
> **Step A — Capture the regression baseline BEFORE any change.** Record, for invoice-pulse and bellows, the current extraction state from `anvil.db`: chunk count, and a deterministic hash of all chunks ordered by `(file_path, start_line)` over the fields `(name, file_path, chunk_type, content_hash, structural_metadata)`. Write both baselines to `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/extract_baseline.txt` (`mkdir -p` first). This is the "before" the QA step compares against.
>
> **Step B — Implement (blueprint B.5 items 1–5, 7 + B.4):**
> 1. NEW `src/contracts.py` — `ChunkRecord`, `StructuralMetadata`, `SymbolData`, `ImportRecord`, `DefinitionRecord`, `CallRecord`, `TestMappingRecord` as TypedDicts per blueprint B.1; a `UNIVERSAL_CHUNK_TYPES` set constant per B.2; and the `LanguageExtractor` Protocol per B.3.
> 2. NEW `src/parsers/registry.py` — `register(extractor)` and `get_extractor(file_extension)` per B.3.
> 3. `src/parsers/python_parser.py` — wrap the existing module functions in a `PythonExtractor` class implementing `LanguageExtractor` (`language="python"`, `file_extensions={".py"}`). The class methods delegate to the existing functions — NO logic changes to parsing. Register it via `registry.register(PythonExtractor())` at import.
> 4. `src/extractor.py` — replace the `.py` hardcode (blueprint cites ~line 52) with extension dispatch via `registry.get_extractor(...)`; replace direct `ast.parse()` + `python_parser.*` calls with calls through the extractor instance; relocate `detect_sqlalchemy_models()` into `PythonExtractor` as a post-parse hook (other languages won't have it); abstract the Python module-path resolution (`file_path → module` at ~422-423) into a method on the extractor so `resolve_dependencies()` stays language-agnostic.
> 5. `src/db.py` — relax the `chunk_type` CHECK constraint to `chunk_type TEXT NOT NULL` (drop the closed enum) per B.4/B.5 item 8. Provide a migration path that does not destroy existing rows (the existing invoice-pulse/bellows chunks must survive).
>
> **Step C — Prove behavior preservation.** Re-run scan+extract for invoice-pulse and bellows against the refactored code, then recompute the same count+hash as Step A and confirm they are IDENTICAL to the baseline. Write the after-values + the comparison result to `.../extract_after.txt`. If anything differs, STOP and report the diff — do not paper over it.
>
> **Step D — Full suite.** `python3 -m pytest tests/ -q`. All must pass (baseline 240). Record the exact count. If `test_python_parser.py` needs updating because the parser is now class-wrapped, update the tests to call through `PythonExtractor` — but the assertions on parser OUTPUT must be unchanged (same expected chunks).
>
> **Stage the deposits (required so they survive teardown):**
> ```bash
> git add src/contracts.py src/parsers/registry.py src/parsers/python_parser.py src/extractor.py src/db.py tests/ knowledge/development/extraction-contract-language-decoupling-2026-06-08.md knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/
> git status --short
> ```
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/extraction-contract-language-decoupling-2026-06-08.md`
> - `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/extract_baseline.txt`, `extract_after.txt`

---
---

## STEP 2 — ANVIL QA ANALYST

---

> Read `knowledge/development/extraction-contract-language-decoupling-2026-06-08.md` and check the Output Receipt status. If status is not Complete, or DEV reported a STOP (extraction diff or verbatim mismatch), stop and report before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, the blueprint section B, the Step 1 dev log, `src/contracts.py`, `src/parsers/registry.py`, `src/extractor.py`.
>
> **Working directory note:** worktree IS anvil root. DB at `/Users/marklehn/Developer/GitHub/anvil/anvil.db`.
>
> **Do exactly this** (evidence dir `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/` already exists from Step 1):
>
> **(1) Contract + registry exist and conform.** Confirm `src/contracts.py` defines `ChunkRecord`, `LanguageExtractor` (Protocol), `StructuralMetadata`, `SymbolData`; `src/parsers/registry.py` defines `register`/`get_extractor`; `PythonExtractor` implements the protocol and is registered. `python3 -c "from src.parsers import registry; from src.parsers.python_parser import PythonExtractor; print(registry.get_extractor('.py'))"` → `.../contract_check.txt`. Expected: a `PythonExtractor` instance.
>
> **(2) Extraction is byte-identical before/after (the core regression).** Diff `extract_baseline.txt` vs `extract_after.txt` → `.../extract_diff.txt`. Expected: counts and hashes identical for BOTH invoice-pulse and bellows. ❌ if any differ.
>
> **(3) `chunk_type` constraint relaxed without data loss.** Confirm the CHECK no longer restricts to the closed enum, and existing chunk counts for invoice-pulse + bellows are unchanged in the DB. `.../chunk_type_constraint.txt`.
>
> **(4) Extraction no longer hardcodes `.py`.** `grep -n "endswith(\".py\")\|\.py\")" src/extractor.py > .../py_hardcode_check.txt 2>&1`. Expected: the extension dispatch goes through the registry; no remaining `.py` literal gating extraction. (A `.py`-specific path may legitimately remain INSIDE `PythonExtractor`.)
>
> **(5) Full suite (Rule 21).** `python3 -m pytest tests/ -q > .../pytest_full.txt 2>&1`. Expected: all pass; record exact count vs baseline 240; note any tests changed to call through `PythonExtractor` and confirm their output assertions are unchanged.
>
> **(6) Scope guard — classifier/SCAN_TARGETS untouched.** `git diff --cached --name-only > .../changed_files.txt`. Confirm `src/classifier.py` and the `SCAN_TARGETS` block of `src/config.py` are NOT modified. ❌ if either changed (out of scope for this plan).
>
> **(7) Write QA report** `knowledge/qa/2026-06-08-extraction-contract-language-decoupling-qa.md` with a verification table (rows for checks 1–6, each citing evidence) + an Observations section. No hedging keywords in a ✅ row.
>
> **(8) Rule 20 self-check** from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with:
> - `plan_slug`: `executable-anvil-extraction-contract-language-decoupling-2026-06-08`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-06-08-extraction-contract-language-decoupling-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/`
> - `required_evidence_files`: `["extract_baseline.txt", "extract_after.txt", "extract_diff.txt", "pytest_full.txt", "changed_files.txt"]`
>
> Include literal stdout. If `FAILED`, halt. Do NOT move the plan to Done — the Planner performs the terminal verdict.
>
> **Stage the deposits:**
> ```bash
> git add knowledge/qa/2026-06-08-extraction-contract-language-decoupling-qa.md knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/
> git status --short
> ```
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-08-extraction-contract-language-decoupling-qa.md`
> - `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/`
