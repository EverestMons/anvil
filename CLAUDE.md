# Anvil — CLAUDE.md

## Rules

1. **All file writes use Python `with open(..., "w") as f: f.write(content)`** — never bash heredocs. Heredocs corrupt JSON files.
2. **Run tests before every commit:** `cd anvil && python3 -m pytest tests/ -v`
3. **Commit messages follow conventional commits:** `feat:`, `fix:`, `docs:`, `chore:`, `test:`
4. **Never modify files outside the anvil directory without explicit CEO approval.**
5. **Read your specialist file at `anvil/agents/` before starting any task.**
6. **Read the domain glossary at `anvil/knowledge/research/domain-glossary.md`** for Anvil-specific terminology.
7. **Python 3.x, SQLite, no external API dependencies** — Claude Code is the intelligence layer.
8. **All knowledge deposits use `with open()` with absolute paths.**
