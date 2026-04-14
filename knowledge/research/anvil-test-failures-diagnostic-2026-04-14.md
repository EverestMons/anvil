# Anvil Diagnostic — Pre-existing Test Failures (cochange, staleness)
**Date:** 2026-04-14 | **Status:** Complete

---

## (1) Failing Test Definitions

**`test_find_cochange_patterns`** — `tests/test_lab.py` lines 162–174:

```python
def test_find_cochange_patterns(conn, lab_project):
    pid, _, _, _, _ = lab_project
    patterns = find_cochange_patterns(conn, pid)
    assert len(patterns) >= 1
    # main.py and utils.py share 4 commits
    pair = next(
        (p for p in patterns
         if {p["file_a"], p["file_b"]} == {"main.py", "utils.py"}),
        None,
    )
    assert pair is not None
    assert pair["cochange_count"] >= 3
    assert pair["jaccard_score"] > 0
```

**`test_find_staleness_alerts`** — `tests/test_lab.py` lines 179–183:

```python
def test_find_staleness_alerts(conn, lab_project):
    pid, _, _, _, _ = lab_project
    alerts = find_staleness_alerts(conn, pid, 1)
    stale_names = [a["name"] for a in alerts]
    assert "risky_func" in stale_names  # staleness=0.7 >= 0.6 threshold
```

---

## (2) `lab_project` Fixture

Defined in `tests/test_lab.py` lines 43–120.

**Tables/data seeded:**

- `code_chunks`: 5 chunks — `main.py` (module), `risky_func` (function in main.py), `safe_func` (function in utils.py), `test_safe` (test_case in test_utils.py), `clone_func` (function in other.py)
- `health_scores`: 4 rows, cycle_id=1
  - `risky_func`: volatility=0.9, coverage=1.0, complexity=0.95, coupling=0.85, **staleness=0.7**, composite=0.75
  - `safe_func`: staleness=0.0, composite=0.1
  - `test_safe`: staleness=0.0, composite=0.02
  - `clone_func`: staleness=0.0, composite=0.4
- `dependencies`: c1 → c2 ("call", "cross_file")
- `symbol_bindings`: c3 binds "safe_func"
- `similarities`: (c1, c4) score=0.85
- `git_changes`: **4 commits shared between main.py and utils.py** (hash0–hash3, dates 2026-03-20 through 2026-03-23), plus 1 separate commit for other.py (hash_other)

---

## (3) Finding Function Source

### `find_cochange_patterns` — `src/lab.py` lines 276–313

```python
def find_cochange_patterns(conn, project_id: int) -> list[dict]:
    """Find files that frequently change together in git commits."""
    cur = conn.execute(
        "SELECT commit_hash, file_path FROM git_changes "
        "WHERE project_id = ? AND file_path != ''",
        (project_id,),
    )
    commit_files = defaultdict(set)
    file_commits = defaultdict(set)
    for commit_hash, file_path in cur.fetchall():
        commit_files[commit_hash].add(file_path)
        file_commits[file_path].add(commit_hash)

    pair_counts = defaultdict(int)
    for commit_hash, files in commit_files.items():
        files_list = sorted(files)
        for i in range(len(files_list)):
            for j in range(i + 1, len(files_list)):
                pair = (files_list[i], files_list[j])
                pair_counts[pair] += 1

    results = []
    for (file_a, file_b), count in pair_counts.items():
        if count >= COCHANGE_MIN_COUNT:   # <-- THRESHOLD FILTER
            union = len(file_commits[file_a] | file_commits[file_b])
            jaccard = count / union if union > 0 else 0.0
            results.append({...})

    results.sort(key=lambda x: x["cochange_count"], reverse=True)
    return results
```

**Threshold:** `COCHANGE_MIN_COUNT = 5` (from `src/config.py` line 67)

### `find_staleness_alerts` — `src/lab.py` lines 210–228

```python
def find_staleness_alerts(conn, project_id: int, cycle_id: int) -> list[dict]:
    """Find chunks whose dependencies are newer than the chunk itself."""
    cur = conn.execute(
        "SELECT cc.id, cc.file_path, cc.name, hs.staleness_score, "
        "hs.composite_score "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE hs.cycle_id = ? AND hs.staleness_score >= ? "  # <-- THRESHOLD FILTER
        "AND cc.project_id = ? "
        "ORDER BY hs.staleness_score DESC",
        (cycle_id, STALENESS_THRESHOLD, project_id),
    )
    return [
        {"chunk_id": r[0], "file_path": r[1], "name": r[2],
         "staleness_score": r[3], "composite_score": r[4]}
        for r in cur.fetchall()
    ]
```

**Threshold:** `STALENESS_THRESHOLD = 0.8` (from `src/config.py` line 65)

---

## (4) Pytest Output

Full output captured to `knowledge/research/anvil-test-failures-pytest.txt`.

Summary:
- `test_find_cochange_patterns`: `assert 0 >= 1` — `patterns` is `[]`
- `test_find_staleness_alerts`: `assert 'risky_func' in []` — `alerts` is `[]`

---

## (5) Intermediate DB State

Investigation script confirmed:

**Staleness:**
```
risky_func: staleness_score=0.7
safe_func: staleness_score=0.0
STALENESS_THRESHOLD = 0.8
0.7 >= 0.8? False  → risky_func filtered OUT → empty results
```

**Co-change:**
```
Commit groups: 5 commits
  hash0: {main.py, utils.py}
  hash1: {main.py, utils.py}
  hash2: {main.py, utils.py}
  hash3: {main.py, utils.py}
  hash_other: {other.py}

Pair co-change counts:
  ('main.py', 'utils.py'): count=4

COCHANGE_MIN_COUNT = 5
4 >= 5? False  → pair filtered OUT → empty results
```

The function logic and SQL are correct. The data is present. The filters work. The problem is the thresholds exceed what the fixture seeds.

---

## (6) Root Cause Category

Both failures are **(d) Threshold misconfiguration**.

- **`test_find_staleness_alerts`**: Fixture seeds `staleness_score=0.7`. The test comment says `# staleness=0.7 >= 0.6 threshold`. But `STALENESS_THRESHOLD` in `src/config.py` is `0.8`. The threshold was raised after the test was written (or the fixture seeding was lowered). `0.7 >= 0.8` is `False`, so `risky_func` is excluded.

- **`test_find_cochange_patterns`**: Fixture seeds 4 shared commits between `main.py` and `utils.py`. `COCHANGE_MIN_COUNT` in `src/config.py` is `5`. `4 >= 5` is `False`, so the pair is excluded. The test asserts `cochange_count >= 3`, which would pass with 4 — but the function never returns the pair at all because it's filtered before that assertion is reached.

---

## (7) What Would Need to Change to Make Each Test Pass

Both can be fixed in one of two ways (fix the config OR fix the fixture). The right approach is to align the fixture with the current production threshold values so tests remain meaningful.

**`test_find_staleness_alerts`:**

- `STALENESS_THRESHOLD` is currently `0.8`.
- `risky_func` is seeded with `staleness_score=0.7`.
- **Fix option A (recommended — fix the fixture):** Change `staleness_score=0.7` to `staleness_score=0.85` in the `create_health_score` call for `c1` in `lab_project` (line 65–68 of `tests/test_lab.py`). Update the test comment from `# staleness=0.7 >= 0.6 threshold` to `# staleness=0.85 >= 0.8 threshold`.
- **Fix option B (not recommended):** Lower `STALENESS_THRESHOLD` back to `0.6` in `src/config.py`, but this would change production behavior.

**`test_find_cochange_patterns`:**

- `COCHANGE_MIN_COUNT` is currently `5`.
- Fixture seeds 4 shared commits.
- **Fix option A (recommended — fix the fixture):** Add a 5th shared commit for `main.py` and `utils.py` in the `lab_project` fixture (e.g. add `create_git_change(conn, pid, "main.py", "hash4", "2026-03-24", "commit 4", "dev")` and `create_git_change(conn, pid, "utils.py", "hash4", "2026-03-24", "commit 4", "dev")`). The test already asserts `cochange_count >= 3`, so 5 would satisfy it trivially.
- **Fix option B (not recommended):** Lower `COCHANGE_MIN_COUNT` to `3` or `4` in `src/config.py`.

---

## (8) Shared Root Cause

Yes — both failures share the same root cause **category** (threshold misconfiguration) and likely the same **event** (a config update that raised thresholds without updating test fixtures).

- Both thresholds in `src/config.py` were raised: `STALENESS_THRESHOLD` to `0.8` and `COCHANGE_MIN_COUNT` to `5`.
- Both test fixtures seed values that satisfied the old thresholds but not the new ones.
- The two failures are **independent** in mechanism — fixing the staleness fixture would NOT fix the co-change test, and vice versa. Each needs its own fixture adjustment.
- However, both can be fixed in a single commit touching only `tests/test_lab.py` (the `lab_project` fixture).

**Recommended single fix:** In `tests/test_lab.py`, `lab_project` fixture:
1. Change `staleness_score=0.7` → `staleness_score=0.85` for `risky_func` (line ~67).
2. Add a 5th shared commit for `main.py` and `utils.py` (after line 115).
