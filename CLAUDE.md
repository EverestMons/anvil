# Anvil — CLAUDE.md

## Execution Protocol (Eluvian Standard)

This project follows the Eluvian execution protocol defined in `PLANNER_TEMPLATE.md § Execution Model`. The full specification for RUN EXE, RUN DIAG, execution claiming (`in-progress-` prefix), cross-plan dependencies, and priority ordering lives there. Key points repeated here for agent convenience:

### RUN EXE
Scan `knowledge/decisions/` for `executable-` files. Skip `in-progress-` and `Done/`. **BEFORE executing, RENAME the file:**
```python
import shutil
shutil.move("knowledge/decisions/executable-foo.md", "knowledge/decisions/in-progress-executable-foo.md")
```
Execute steps with CEO confirmation. After completion, move to Done (strip prefix). If no more executables: **"NO EXE"**.

### RUN DIAG
Scan `knowledge/decisions/` for `diagnostic-` files. Skip `in-progress-` and `Done/`. **BEFORE executing, RENAME the file:**
```python
import shutil
shutil.move("knowledge/decisions/diagnostic-foo.md", "knowledge/decisions/in-progress-diagnostic-foo.md")
```
Execute investigation, deposit findings to `knowledge/research/`. Move to Done (strip prefix). If no more diagnostics: **"NO DIAG"** and stop. Do NOT scan for executables. RUN DIAG only cares about diagnostics.

### Claiming + Dependencies
- `in-progress-` prefix = claimed by another session, SKIP IT
- `**Depends on:**` header field = check `Done/` for prerequisites before executing
- `**Priority:**` header field = lower number runs first
- Stale `in-progress-` files (>30 min unmodified) may be reclaimed

---

## Rules

1. **All file writes use Python `with open(..., "w") as f: f.write(content)`** — never bash heredocs. Heredocs corrupt JSON files.
2. **Run tests before every commit:** `cd anvil && python3 -m pytest tests/ -v`
3. **Commit messages follow conventional commits:** `feat:`, `fix:`, `docs:`, `chore:`, `test:`
4. **Never modify files outside the anvil directory without explicit CEO approval.**
5. **Read your specialist file at `anvil/agents/` before starting any task.**
6. **Read the domain glossary at `anvil/knowledge/research/domain-glossary.md`** for Anvil-specific terminology.
7. **Python 3.x, SQLite, no external API dependencies** — Claude Code is the intelligence layer.
8. **All knowledge deposits use `with open()` with absolute paths.**
