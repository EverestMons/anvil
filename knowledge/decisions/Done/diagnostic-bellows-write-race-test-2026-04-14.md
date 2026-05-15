# Bellows Write-Race Test — Throwaway Diagnostic
**Date:** 2026-04-14 | **Purpose:** Validate Planner staging-move write pattern against live Bellows watcher | **Disposable:** Yes — safe to delete after run

## Context

This is a throwaway test plan. Its only job is to prove that the Planner's new staging-move write pattern produces a single, complete file event that Bellows parses and executes correctly. The plan does no real work — it writes a timestamped marker, deposits a short findings file, and moves itself to Done.

If this plan runs cleanly, the staging-move pattern is validated and the Planner can resume depositing real plans for Bellows to execute.

If this plan strands, fails, or produces garbled output, the pattern is not yet correct and the Planner must diagnose further before depositing any Forge or invoice-pulse work.

---

## STEP 1 — Investigation Agent (throwaway)

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/diagnostic-bellows-write-race-test-2026-04-14.md", "anvil/knowledge/decisions/in-progress-diagnostic-bellows-write-race-test-2026-04-14.md")`. Skip all specialist file and glossary reads — this is a disposable smoke test for Bellows infrastructure, not real investigative work. Working directory: `/Users/marklehn/Desktop/GitHub/anvil/`. **Write a timestamped marker file** via Python: `import datetime; ts = datetime.datetime.now().isoformat(); content = f"Bellows write-race test executed at {ts}\n"; import os; os.makedirs("knowledge/research/bellows-tests", exist_ok=True); open("knowledge/research/bellows-tests/write-race-test-marker.txt", "w").write(content); print(content)`. **Deposit a findings file** to `knowledge/research/bellows-write-race-test-findings-2026-04-14.md` with the following content via `with open(...) as f: f.write(...)`: a short markdown file titled "Bellows Write-Race Test — Findings" with sections Status (report whether each phase succeeded: claim rename, marker write, findings deposit, move-to-Done), Context (one sentence: this was a throwaway smoke test of the Planner staging-move write pattern), and a standard Output Receipt block at the bottom with Agent=throwaway, Step=1, Status=Complete, Files Deposited listing the marker and findings files, Flags for CEO=None, Flags for Next Step=None. **Move this plan to Done:** `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-diagnostic-bellows-write-race-test-2026-04-14.md", "anvil/knowledge/decisions/Done/diagnostic-bellows-write-race-test-2026-04-14.md")`. **Do NOT commit anything** — this plan produces no code changes and the artifacts are throwaway. A single final print statement confirming "Bellows write-race test complete" is sufficient.
