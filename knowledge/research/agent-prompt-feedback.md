# Agent Prompt Feedback

> *Pre-activation history preserved in `agent-prompt-feedback-ARCHIVE.md`.*


## 2026-08-18 — Cycle 21 Plan (executable-447)

1. **Verification (6) references wrong file.** The plan says "grep the findings file for `Untested Complexity`" — but the Untested Complexity section is in the cycle report (`knowledge/research/cycle-{id}-findings-{date}.md`), not the audit findings file (`invoice-pulse/knowledge/anvil/audit-findings-{date}.md`). The audit findings file only contains intent-gap findings from `find_intent_gaps()`. Future cycle plans should specify "grep the cycle report" for this check.

2. **UTC date derivation is the recurring default.** `lab.py:103` uses `datetime.now(timezone.utc)` for filenames. The plan expected `2026-08-18` (local date) but `run_cycle` produces `2026-08-19` (UTC date). Prior cycles also used UTC. Plan templates should expect UTC-dated filenames or explicitly note the UTC behavior.
