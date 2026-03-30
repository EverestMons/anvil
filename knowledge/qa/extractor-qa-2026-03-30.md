# Anvil Extractor QA Report
**Date:** 2026-03-30
**Agent:** Anvil QA Analyst
**Blueprint:** `anvil/knowledge/architecture/extractor-blueprint-2026-03-30.md`
**Dev Logs:** `python-parser-implementation-2026-03-30.md`, `extractor-implementation-2026-03-30.md`

---

## Verification Areas

### 1. Unit Test Suites — PASS
Ran `python3 -m pytest tests/test_python_parser.py tests/test_extractor.py -v`.

**40/40 tests passed** (28 parser + 12 extractor) in 0.45s.

### 2. Live Extraction Against invoice-pulse — PASS

```json
{
  "files_processed": 188,
  "chunks_created": 3247,
  "chunks_updated": 17,
  "symbols_extracted": 34789,
  "dependencies_resolved": 12142,
  "fingerprints_created": 3247,
  "similarities_found": 381
}
```

All counts > 0. 188 Python files processed (matches scanner's 188 .py count). 3247 sub-chunks created across all types.

### 3. Chunk Type Distribution — PASS

| chunk_type | count |
|---|---|
| module | 939 |
| function | 1101 |
| class | 359 |
| method | 67 |
| test_case | 1720 |

All expected types present. Module count (939) matches scanner total. Function + class + method + test_case = 3247 sub-chunks.

### 4. Validator Gate Verification — PASS

54 functions/methods found in validator.py. All 10 gate functions present:
`gate_1_legitimacy`, `gate_2_timeliness`, `gate_3_billto`, `gate_4_pro_instance`, `gate_5_lane`, `gate_6_charge_type`, `gate_7_linehaul`, `gate_8_fuel`, `gate_9_accessorials`, `gate_10_reconsignment`.

Plus helper functions: `_aggregate_accessorial_confidence`, `_extract_gate_values`, `_find_element_for_gate`, `_validate_accessorial_rate`, `failed_gates`.

### 5. SQLAlchemy Model Detection — PASS (correct negative)

0 SQLAlchemy symbols found. This is correct — invoice-pulse uses raw SQLite (`sqlite3` module with `CREATE TABLE` statements), not SQLAlchemy ORM. The detection is working correctly by not producing false positives. SQLAlchemy detection will be exercised when Anvil scans projects that use ORM patterns.

### 6. Parent Chunk Linkage — PASS

Methods correctly linked to class parents:
- `__init__` (method) → `User` (class)
- `__init__` (method) → `PromptDef` (class)
- `contract` (method) → `ContractCache` (class)
- `get_invoice_filter` (method) → `ContractCache` (class)
- `get_tariff_rate` (method) → `ContractCache` (class)

Top-level functions linked to module parents (verified in unit tests).

### 7. Symbol Bindings — PASS

| binding_type | count |
|---|---|
| calls | 27,236 |
| defines | 3,274 |
| imports | 2,565 |
| tests | 1,714 |

All four binding types present with substantial counts. 1,714 test mappings reflects the large test suite (1,720 test_case chunks).

### 8. Dependencies — PASS

| dependency_type | scope | count |
|---|---|---|
| call | cross_file | 9,011 |
| call | within_file | 1,614 |
| import | cross_file | 1,514 |
| import | within_file | 3 |

Total: 12,142 dependencies. Both import and call types present. Both within_file and cross_file scopes represented.

### 9. MinHash Fingerprints — PASS

- Fingerprints created (cycle 1): 3,247
- With MinHash signature: 3,031 (chunks with 5+ lines)
- Without MinHash: 216 (small chunks)
- Similarity pairs: 381

MinHash coverage: 93.4% of chunks have signatures. 381 similarity pairs detected via LSH.

### 10. Blueprint Compliance — PASS

Checked against SA blueprint "How to verify" section:
1. Parser accuracy (validator.py gates) — PASS
2. Chunk type distribution — PASS (all types present)
3. Parent linkage (method→class, function→module) — PASS
4. Symbol bindings (imports, defines, calls, tests all present) — PASS
5. SQLAlchemy detection (correct negative for invoice-pulse) — PASS
6. Dependencies (import + call, within_file + cross_file) — PASS
7. MinHash fingerprints (3,031 with signatures) — PASS
8. Structural metadata (3,247 chunks with valid JSON) — PASS
9. Idempotency (verified in unit test) — PASS

---

## Summary

**Overall Result: PASS**

All 10 verification areas pass. Live extraction against invoice-pulse produced 3,247 sub-chunks across all 5 types, 34,789 symbol bindings, 12,142 dependencies, 3,247 fingerprints (3,031 with MinHash), and 381 similarity pairs. No fixes required.

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** Step 4
**Status:** Complete

### What Was Done
Verified the extractor implementation against 10 verification areas. Live extraction against invoice-pulse completed successfully with comprehensive coverage. All areas pass.

### Files Deposited
- `anvil/knowledge/qa/extractor-qa-2026-03-30.md` — extractor QA report

### Files Created or Modified (Code)
- None

### Decisions Made
- SQLAlchemy Area 5 scored as PASS (correct negative) — invoice-pulse uses raw SQLite, not ORM

### Flags for CEO
- None

### Flags for Next Step
- None — extractor is verified, ready for Phase 4 (Scorer)
