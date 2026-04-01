# anvil — Full Cycle with Research Pipeline (invoice-pulse)
**Date:** 2026-04-01 | **Tier:** Small | **Execution:** Step 1 (DEV)

## How to Run This Plan

**Bootstrap:**
```
Read the plan at anvil/knowledge/decisions/executable-cycle-research-2026-04-01.md. Execute Step 1.
```

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/executable-cycle-research-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-cycle-research-2026-04-01.md")`. You are the Anvil Developer. Read your specialist file at `anvil/agents/ANVIL_DEVELOPER.md`. **Run a full Anvil cycle against invoice-pulse with the new research pipeline (Phases 7-9).**
>
> **The pipeline is now: SCAN → EXTRACT → CLASSIFY → SCORE (purpose-aware) → LAB (with research recommendations).** Invoice-pulse has changed massively since the last cycle — full UX redesign across 46 pages, data examples pipeline, team hub consolidation, new card-loader infrastructure, copilot inline redesign, navigation overhaul (sidebar removed, breadcrumbs added).
>
> **Step-by-step execution:**
>
> **(1) Pre-scan sync.** Run `bash /Users/marklehn/Desktop/GitHub/forge/scripts/pre-scan-sync.sh` to pull latest from all repos. Verify invoice-pulse repo is up to date.
>
> **(2) SCAN.** `from src.scanner import scan_project` — scan invoice-pulse. Report: files discovered (expect significantly more than the 939 from last cycle due to new templates, partials, JS files), new/changed files since last cycle, git commits ingested.
>
> **(3) EXTRACT.** `from src.extractor import extract_project` — parse all new/changed Python files. Report: chunks created, symbols extracted, dependencies resolved, fingerprints computed, similarity pairs found.
>
> **(4) CLASSIFY.** `from src.classifier import classify_project` — assign functional roles to all chunks using heuristic classification. Then `from src.provenance import ingest_provenance` — parse dev logs from `invoice-pulse/knowledge/development/` and populate chunk_provenance. Report: chunks classified per role (table of role → count), provenance entries created, unclassified chunk count.
>
> **(5) SCORE.** `from src.scorer import score_project` — compute purpose-aware health scores using role-specific weights. Report: score distribution (high/medium/low risk counts), compare to last cycle (29 high-risk, 1413 medium, 1805 low — how did the redesign affect risk?), top 10 highest-risk chunks with their functional roles.
>
> **(6) LAB — Findings.** Run all finding types including the new `best_practice_deviation`. Report: total findings by type, top 5 coverage gaps, top 5 complexity hotspots, top 5 best practice deviations with specific recommendations. Compare finding counts to last cycle (1212 total, 292 constraints).
>
> **(7) LAB — Research recommendations.** For the top 3 best practice deviations, produce detailed research recommendations: what the code does (functional role + provenance), what the best practice says, what specifically should change, and why. These should be actionable enough for the Planner to write an executable.
>
> **(8) LAB — Web research.** For any functional role that has <2 best practice entries in the `best_practices` table, use web research to find established patterns. Add 2-3 new best practices per under-served role. Report what was added.
>
> **(9) Cycle report.** Write the full cycle report to `anvil/knowledge/research/cycle-research-2026-04-01.md`. Include: executive summary, scan/extract/classify stats, scoring comparison vs last cycle, all findings by type, research recommendations section, Planner constraints, specialist update data.
>
> **Deliverable Verification:** Verify (a) cycle report file exists, (b) chunk_provenance table has entries, (c) code_chunks.functional_role populated for >80% of chunks, (d) best_practices table has entries for top 5 roles, (e) health_scores updated for this cycle.
>
> Move to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-cycle-research-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/Done/executable-cycle-research-2026-04-01.md")`. Commit: `"docs: full research cycle against invoice-pulse"`.
