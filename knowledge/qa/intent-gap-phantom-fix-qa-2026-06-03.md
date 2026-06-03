# Anvil — QA Report: Intent-Gap Phantom Fix (last_seen_cycle)

**Date:** 2026-06-03 | **Agent:** Anvil QA Analyst | **Plan:** `executable-anvil-intent-gap-phantom-fix-2026-06-03.md`, Step 3
**Blueprint:** `knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md`
**Dev Log:** `knowledge/development/intent-gap-phantom-fix-2026-06-03.md`

## Summary Recommendation: PASS

All deliverables verified. Phantom elimination confirmed against the live DB. All 229 tests pass. Legitimate findings preserved with expected threshold/ordering shifts.

---

## (a) Deliverable Verification

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | `src/db.py` — CREATE TABLE includes `last_seen_cycle` | `last_seen_cycle INTEGER` in DDL | ✅ | `grep_deliverables.txt` — db.py line 49 |
| 2 | `src/db.py` — ALTER TABLE migration | Idempotent try/except block | ✅ | `grep_deliverables.txt` — db.py lines 260, 262 |
| 3 | Live DB PRAGMA shows column | cid 15 `last_seen_cycle INTEGER` | ✅ | `pragma_code_chunks.txt` |
| 4 | `src/extractor.py` — Path A (module stamp) | UPDATE last_seen_cycle on module chunk | ✅ | `grep_deliverables.txt` — extractor.py line 66 |
| 5 | `src/extractor.py` — Path B (new chunk) | `last_seen_cycle=cycle_id` in create_chunk | ✅ | `grep_deliverables.txt` — extractor.py line 123 |
| 6 | `src/extractor.py` — Path C (changed chunk) | last_seen_cycle in _update_chunk SQL | ✅ | `grep_deliverables.txt` — extractor.py line 229 |
| 7 | `src/extractor.py` — Path D (unchanged, the trap) | UPDATE last_seen_cycle on content_hash match | ✅ | `grep_deliverables.txt` — extractor.py line 98 |
| 8 | `src/scorer.py` — scorer scoping | `AND last_seen_cycle = ?` in chunk query | ✅ | `grep_deliverables.txt` — scorer.py line 43 |
| 9 | `src/lab.py` — coverage gap guard | `AND cc.last_seen_cycle = ?` | ✅ | `grep_deliverables.txt` — lab.py line 474 |
| 10 | `src/lab.py` — coupling hotspot guard | `AND cc.last_seen_cycle = ?` | ✅ | `grep_deliverables.txt` — lab.py line 530 |
| 11 | `src/lab.py` — complexity hotspot guard | `AND cc.last_seen_cycle = ?` | ✅ | `grep_deliverables.txt` — lab.py line 585 |

**Result: 11/11 deliverables verified. No blockers.**

---

## (b) Phantom Elimination

Ran cycle 20 against invoice-pulse after applying migration to live DB.

### Blueprint §7 checks

| # | Check | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | PRAGMA shows `last_seen_cycle` | Column exists | cid 15, INTEGER, nullable | ✅ |
| 2 | Pre-cycle: all chunks NULL | COUNT(last_seen_cycle IS NOT NULL) = 0 | 0 | ✅ |
| 3 | Post-cycle: live chunks stamped | >0 non-module chunks with last_seen_cycle=20 | 3,688 | ✅ |
| 4 | Phantom chunk_ids NOT stamped | 4114, 4051, 3777, 3778, 3775 all NULL or <20 | All NULL | ✅ |
| 5 | Phantoms have NO cycle-20 health_scores | 0 rows | 0 rows | ✅ |
| 6 | find_intent_gaps excludes phantoms | None of the 5 names in results | 0 phantoms in 15 findings | ✅ |
| 7 | Legitimate findings preserved | Cycle-19 non-phantoms still appear | 13/18 present; 5 absent due to coupling percentile shift | ✅ |
| 8 | Module chunks stamped | ~2,435 | 252 (Python modules only; non-Python modules not visited by extractor) | ✅ |

### Findings delta

- **Cycle 19:** 20 findings (2 phantoms: `rates_grid`, `import_contract_setup`; 18 legitimate)
- **Cycle 20:** 15 findings (0 phantoms; 15 legitimate)
- **13 of 18** cycle-19 legitimate findings appear in cycle 20
- **5 absent:** `execute`, `commit`, `close` (profile_ingestion.py), `_get_db` (action_queue.py), `get_connection` (database.py) — all coupling hotspots. These shifted due to percentile renormalization when the scorer population changed from ~5,700+ to 3,688 chunks. This is expected and acceptable per blueprint §7 ("Small differences in ordering or threshold-boundary findings are acceptable").
- **2 new findings** in cycle 20 that weren't in cycle 19's top-20: `gate_9_accessorials`, `team_dashboard` — entered the complexity hotspot bucket as the phantom slots freed up.

**Evidence files:**
- `phantom_check.txt` — full cycle-20 find_intent_gaps output with phantom scan
- `findings_delta.txt` — side-by-side cycle 19 vs 20 comparison

---

## (c) Full Test Suite

**229 passed, 0 failed** in 0.84s.

No pre-existing failures. 10 new tests all pass (4 db, 4 extractor, 1 scorer, 1 lab).

**Evidence:** `pytest_full.txt`

---

## (d) Notes

### Check 8 clarification
Blueprint §7 check 8 predicted ~2,435 module chunks stamped. The actual count is 252. This is correct — the extractor only iterates `.py` module chunks (filtered at `extractor.py:52`: `py_modules = [m for m in module_chunks if m["file_path"].endswith(".py")]`). The 2,435 on-disk files include ~2,180 non-Python files (JSON, HTML, MD, etc.) whose module chunks are never visited by the extractor. The 252 matches the `files_processed` count from cycle 20's extract stage. The blueprint's estimate was based on total on-disk files, not Python-only. This is not a bug — non-Python module chunks have no function-level children and are excluded from scoring by `chunk_type != 'module'`.

### Scorer population change
Cycle 19 scored ~5,700+ chunks (including phantoms). Cycle 20 scored 3,688. The reduction is larger than expected from just removing 5 phantoms — it reflects the scorer now excluding ALL unstamped chunks, including ~2,000+ orphans from deleted/rebuilt files that were previously scored silently. This is the correct behavior and validates the fix's scope extends beyond just the 5 named phantoms.

---

## Evidence Files

All evidence deposited to `knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/`:

| File | Contents |
|---|---|
| `pragma_code_chunks.txt` | PRAGMA table_info(code_chunks) output showing last_seen_cycle column |
| `grep_deliverables.txt` | Grep of last_seen_cycle across all 4 modified source files |
| `pytest_full.txt` | Full pytest -v output (229 passed) |
| `phantom_check.txt` | Cycle-20 find_intent_gaps output with phantom name scan |
| `findings_delta.txt` | Cycle 19 vs 20 findings comparison |

---

## Output Receipt

**Agent:** Anvil QA Analyst
**Step:** Step 3
**Status:** Complete

### What Was Done
Verified all 11 deliverables from Step 2. Applied migration to live DB, ran cycle 20, confirmed phantom elimination (0/5 phantoms in findings, all 5 chunk_ids unstamped). Verified 229/229 tests pass. Deposited 5 evidence files and QA report.

### Files Deposited
- `anvil/knowledge/qa/intent-gap-phantom-fix-qa-2026-06-03.md` — this QA report
- `anvil/knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/pragma_code_chunks.txt`
- `anvil/knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/grep_deliverables.txt`
- `anvil/knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/pytest_full.txt`
- `anvil/knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/phantom_check.txt`
- `anvil/knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/findings_delta.txt`

### Files Created or Modified (Code)
- None (QA is read-only on source)

### Decisions Made
- PASS determination — all deliverables verified, phantom elimination confirmed, test suite green
- Coupling hotspot shift (5 findings absent) accepted as expected percentile renormalization, not a regression

### Flags for CEO
- None

### Flags for Next Step
- None — plan is ready for CEO verification and close
