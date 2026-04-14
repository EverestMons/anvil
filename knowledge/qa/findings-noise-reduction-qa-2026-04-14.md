# QA Report — Findings Noise Reduction
**Date:** 2026-04-14 | **Plan:** executable-findings-noise-reduction-2026-04-14 | **Cycle:** 13

## Verification Table

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `_is_noise_chunk` helper defined | 1 definition in `src/lab.py` | ✅ | `src/lab.py:34` |
| 4 call sites wired | `find_coverage_gaps`, `find_coupling_hotspots`, `find_complexity_hotspots`, `find_intent_gaps` ×3 sub-queries = 6 total | ✅ | Lines 128, 177, 258, 482, 536, 591 |
| `_SESSION_LIFECYCLE_NAMES` defined + used | ≥2 occurrences | ✅ | Lines 29, 42 |
| `_CONNECTION_FACTORY_NAMES` defined + used | ≥2 occurrences | ✅ | Lines 31, 40 |
| `_SESSION_LIFECYCLE_PATH_HINTS` defined + used | ≥2 occurrences | ✅ | Lines 30, 42 |
| SQL `NOT LIKE 'tests/%'` filters added | ≥6 occurrences (3 existing in find_intent_gaps + 3 new) | ✅ | Lines 122, 151, 246, 475, 529, 584 |
| 3 new tests present | `test_is_noise_chunk_test_file`, `test_is_noise_chunk_session_lifecycle`, `test_is_noise_chunk_connection_factory` | ✅ | `tests/test_lab.py:406-417` |
| 3 new tests pass | All 3 pass, pre-existing failures (`test_find_cochange_patterns`, `test_find_staleness_alerts`) remain | ✅ | `evidence/findings-noise-reduction/pytest_targeted.txt` — 18 passed, 2 pre-existing failures |
| Live cycle runs clean | `run_cycle(conn, 'invoice-pulse')` completes without error | ✅ | `evidence/findings-noise-reduction/cycle_run.txt` — "cycle complete" |
| Filter check assert passes | `find_coupling_hotspots` top-20: NOISE_COUNT=0 | ✅ | `evidence/findings-noise-reduction/top20_filter_check.txt` — NOISE_COUNT=0, ASSERT_PASSED |
| Cycle report markdown shows zero noise in Coupling Hotspots | No `tests/` or `profile_ingestion.py` rows in Coupling Hotspots table | ✅ | `knowledge/research/cycle-13-findings-2026-04-14.md` — Coupling Hotspots (44 findings): all production code |

## Notes

- `tests/` entries remain in Clone Candidates and Staleness Alerts sections — these finding types are out of scope for this plan (no SQL or helper filter was specified for those functions).
- Coverage Gaps section is also clean (zero `tests/` rows in cycle 13 report).
- `execute` in `app.py` correctly passes through the noise filter (session lifecycle names only suppressed when file path contains a session-context hint).
