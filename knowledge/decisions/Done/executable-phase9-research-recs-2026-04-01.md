# anvil — Phase 9: Research Recommendations in Lab
**Date:** 2026-04-01 | **Tier:** Medium | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)
**Depends on:** `executable-phase8-best-practices-2026-04-01.md`

## How to Run This Plan

**Bootstrap:**
```
Read the plan at anvil/knowledge/decisions/executable-phase9-research-recs-2026-04-01.md. Execute Step 1. After completing Step 1, stop and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — ANVIL SYSTEMS ANALYST

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/executable-phase9-research-recs-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-phase9-research-recs-2026-04-01.md")`. You are the Anvil Systems Analyst. Read your specialist file. Read the Phase 8 blueprint at `anvil/knowledge/architecture/phase8-best-practices-blueprint-2026-04-01.md`. Read the current `src/lab.py` for the existing finding generation and report format. **Produce a blueprint for research recommendations in the Lab.**
>
> **Blueprint must cover:** (1) **New finding type: `best_practice_deviation`.** For each chunk with a functional_role, query best_practices for that role. For each practice, check whether the chunk violates it (via detection_hint pattern matching on content/structural_metadata). Produce a finding: chunk name, file_path, functional_role, practice violated, current observation, recommendation. (2) **Recommendation format.** Each recommendation is: "[chunk] is a [role]. Best practice: [pattern_name] — [description]. Current: [what the code actually does]. Recommendation: [specific action to improve]." The "Current" observation comes from structural_metadata + content analysis. The "Recommendation" comes from the best practice description. (3) **New Planner constraint type: `pattern_recommendation`.** Format: "file::name (role) deviates from [pattern]. Action: [specific improvement]." Severity from best_practice.severity. (4) **Cycle report "Research Recommendations" section.** Grouped by functional_role. Per role: list of deviations with recommendations. Summary: N chunks deviate from M patterns across K roles. (5) **Cross-project comparison (future-ready).** When multiple projects are scanned, the Lab can compare average scores per role across projects and recommend the better-performing project's patterns. Spec the data model but don't implement — just the schema hook. (6) **Detection hint engine.** How detection_hints work: regex patterns on chunk content (e.g., "bare except" → "Consistent error handling" violation), structural_metadata checks (CC > threshold for role → "complexity" violation), AST checks (missing return type → "Structured return type" violation). Spec the detection engine API. (7) **How to verify.**
>
> Deposit blueprint to `anvil/knowledge/architecture/phase9-research-recs-blueprint-2026-04-01.md` using `with open()`. Standard prompt feedback protocol.

---
---

## STEP 2 — ANVIL DEVELOPER

---

> Before starting, read `anvil/knowledge/architecture/phase9-research-recs-blueprint-2026-04-01.md` and check the Output Receipt status. If not Complete, stop and report. You are the Anvil Developer. Read your specialist file.
>
> **Task 1 — Detection hint engine.** Create `src/detector.py` (or add to existing module per SA direction). `check_best_practice(chunk, practice) → {compliant: bool, observation: str}`. Supports 3 detection modes: regex on content, structural_metadata threshold check, AST pattern check. Commit: `"feat: best practice detection hint engine"`.
>
> **Task 2 — Best practice deviation finder.** Add `find_best_practice_deviations(conn, project_name)` to `src/lab.py`. For each classified chunk: query best_practices for its role, run detection engine, produce deviation findings. Commit: `"feat: best_practice_deviation finding type in Lab"`.
>
> **Task 3 — Pattern recommendation constraints.** Add `pattern_recommendation` to Planner constraint generation. Deviation findings → structured constraints with role, pattern, and specific action. Commit: `"feat: pattern_recommendation Planner constraint type"`.
>
> **Task 4 — Cycle report Research Recommendations section.** Add section to cycle report: grouped by role, deviations with recommendations, summary counts. Commit: `"feat: Research Recommendations section in cycle report"`.
>
> **Task 5 — Tests.** Test detection engine: known compliant chunk → compliant, known violating chunk → deviation with observation. Test deviation finder: seeded chunks + practices → expected deviations. Test report section: deviations render correctly. Commit: `"test: detection engine + deviation finder + report tests"`.
>
> Run full test suite. Deposit dev log to `anvil/knowledge/development/phase9-research-recs-2026-04-01.md` using `with open()`. Standard prompt feedback protocol.

---
---

## STEP 3 — ANVIL QA ANALYST

---

> Before starting, read `anvil/knowledge/development/phase9-research-recs-2026-04-01.md` and check Output Receipt status. If not Complete, stop and report. **Verify across 7 areas:**
>
> **Area 1 — Detection engine.** Test 3 detection modes: regex pattern on content, structural_metadata threshold, AST pattern. Verify each produces correct compliant/non-compliant results. PASS/FAIL.
> **Area 2 — Deviation findings.** Run deviation finder against invoice-pulse. Verify findings produced for chunks with known violations (e.g., route handlers with high CC, validation gates without structured returns). PASS/FAIL.
> **Area 3 — Recommendation quality.** Read 5 deviation findings. Verify each has: chunk name, role, practice violated, current observation, specific recommendation. Verify recommendations are actionable (not generic). PASS/FAIL.
> **Area 4 — Planner constraints.** Verify `pattern_recommendation` constraints generated. Verify format includes role, pattern name, and action. PASS/FAIL.
> **Area 5 — Cycle report.** Run a full cycle. Verify "Research Recommendations" section in report. Verify grouped by role. Verify summary counts. PASS/FAIL.
> **Area 6 — Existing findings intact.** Verify all 6 original finding types still produce correct output. PASS/FAIL.
> **Area 7 — Test suite.** Run full test suite. PASS/FAIL.
>
> Deposit QA report to `anvil/knowledge/qa/phase9-research-recs-qa-2026-04-01.md` using `with open()`. **Final:** Update `anvil/PROJECT_STATUS.md`. Move to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-phase9-research-recs-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/Done/executable-phase9-research-recs-2026-04-01.md")`. Commit: `"chore: status update + move Phase 9 to Done"`.
