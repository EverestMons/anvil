# Bellows — Roadmap
**Date:** 2026-04-13 | **Type:** roadmap | **Status:** Active
**Version:** 2.0 — updated after characterization session 2026-04-13

---

## Overview

Bellows is the autonomous execution engine for Eluvian. It picks up plans deposited by the Planner, runs them through Claude Code step by step, feeds each step's output to the Planner API for judgment, and only interrupts the CEO when the Planner escalates. The CEO plans and decides. Bellows keeps the fire burning between those moments.

---

## Architecture (Resolved)

### Two-Claude Design
Bellows drives two Claude instances with distinct roles:

**Claude Code (execution):**
- Invoked via `claude -p "..." --output-format json --resume [session_id]`
- Runs plan steps against actual project codebases
- Session ID captured from Step 1 JSON output, reused via `--resume` for all subsequent steps
- Default model: Sonnet (Opus ~5x more expensive, not justified for mechanical execution)

**Claude API (judgment):**
- Called with Planner system prompt (PLANNER_TEMPLATE.md + COMPANY.md + project context)
- Receives context envelope after each step
- Decides: continue as planned / rewrite next step prompt / escalate to CEO
- Stateless per call — Bellows injects context explicitly

### JSON Output Structure (Confirmed via characterization test 2026-04-13)
```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "result": "...prose response including Output Receipt...",
  "stop_reason": "end_turn",
  "session_id": "4f632b0e-fb32-43e7-958d-bbca60a27c78",
  "total_cost_usd": 0.372,
  "permission_denials": [],
  "usage": { ... }
}
```

**Bellows parses four fields:**
- `is_error` — primary error flag
- `stop_reason` — `end_turn` = clean completion
- `result` — text scan for Output Receipt status and Flags for CEO
- `session_id` — passed to `--resume` for next step
- `permission_denials` — advisory log if non-empty, not a blocker

### Context Envelope
Bellows injects context to the Planner API rather than relying on MCP tool calls. Per step, the envelope contains:
- Full plan file (current + next step highlighted)
- Output Receipt from the step that just completed
- Full `result` text from Claude Code stdout
- Any knowledge files listed in Output Receipt "Files Deposited"
- Project PROJECT_BRIEF.md and PROJECT_STATUS.md
- Governance files: PLANNER_TEMPLATE.md, COMPANY.md

### Escalation Model
Planner API response parsed for one of three signals:
- **Continue** — next step executes automatically
- **Rewrite** — Planner returns revised prompt for next step, Bellows substitutes and executes
- **Escalate** — CEO notified via Pushover, Bellows waits

CEO responds via Tailscale-accessible Flask endpoint (phone browser). Options: "Continue", "Stop", free-text instruction. Free-text injected into next Planner API call as CEO directive.

### Notification Stack
- **Pushover** — one-way push to phone on escalation, plan completion, critical failure
- **Tailscale** — makes Mac Flask callback server reachable from phone without public exposure
- **Flask** — lightweight local server receives phone response, signals Bellows to proceed

Routine step transitions are silent. Phone is a judgment channel, not a progress ticker.

---

## Resolved Infrastructure Questions

| Question | Answer |
|---|---|
| How does Bellows communicate with Mac? | It runs ON the Mac as a persistent daemon |
| How does CEO send approvals from mobile? | Pushover notification → Tailscale URL → phone browser |
| How does Bellows relay step output? | Pushover push with escalation summary |
| Does Bellows need its own repo? | Yes — `/Users/marklehn/Desktop/GitHub/bellows/` |
| What model for Claude Code execution? | Sonnet (default), Opus only if plan header specifies |
| What model for Planner API calls? | Sonnet — judgment calls are pattern matching, not novel reasoning |
| Context injection vs MCP tools? | Injection — Bellows assembles deterministic context envelope |
| Pushover callbacks? | Pushover is one-way — callback via Tailscale Flask endpoint |

---

## Phase 1 — Core Execution Loop
**Goal:** Plans run end-to-end without CEO at Mac. Planner API makes step judgments. CEO only interrupted on escalation.

### Deliverables
- `orchestrator.py` — watcher + runner + session manager
- `parser.py` — JSON output parser, Output Receipt text scanner, escalation signal detector
- `planner.py` — Planner API client, context envelope assembler
- `notifier.py` — Pushover push integration
- `server.py` — Flask callback endpoint (Tailscale-accessible)
- `config.json` — watched project paths, model defaults
- `bellows/logs/` — per-run JSON output archive

### Watch Scope
All Eluvian project `knowledge/decisions/` directories. Config-driven — add/remove projects without code changes.

### Success Criteria
- A plan deposited in any watched project runs start to finish without CEO at Mac
- CEO receives Pushover notification only on escalation or completion
- Planner API correctly rewrites at least one step mid-execution based on Output Receipt findings
- Run artifacts committed to project repo and available for Forge consumption
- Cost per step logged to SQLite run history

---

## Phase 2 — Parallel Plan Groups
**Goal:** Handle `parallel-N-` prefixed plan groups — run matching group members back-to-back within single confirmation window.

### Deliverables
- Parallel group detection in watcher
- Back-to-back execution within one Planner judgment window
- Group-level escalation (any member escalates → whole group pauses)

---

## Phase 3 — Forge/Anvil Integration
**Goal:** Bellows triggers Forge/Anvil cycles automatically after plan batches complete.

### Deliverables
- Post-batch trigger: after all plans in a session move to Done, signal Forge cycle
- Anvil findings surfaced to CEO via Pushover summary
- CEO-approved diagnostics auto-queued for next Bellows cycle

---

## Phase 4 — Trusted Execution (Future)
**Goal:** Certain plan classes execute without per-step Planner judgment. CEO only notified on Critical findings or failures.

### Trigger condition
After Phase 1-3 prove reliability across N plan executions, define trusted plan signatures (e.g. documentation-only, test-only, glossary updates) that Bellows can complete fully autonomously.

---

## Relationship to Other Systems

| System | Relationship |
|---|---|
| **Planner** | Writes plans Bellows executes. Bellows calls Planner API for step judgment. |
| **Forge** | Consumes Output Receipts, QA reports, feedback logs produced by Bellows-run plans |
| **Anvil** | Consumes code changes committed by Claude Code sessions Bellows drives |
| **Claude Code** | Bellows drives it via `claude -p`; doesn't replace it |
| **RUN EXE / RUN DIAG** | Manual fallback — Bellows is the automated version of the same loop |

---

## Notes

- Bellows roadmap currently lives in `anvil/knowledge/decisions/` — migrate to `bellows/knowledge/decisions/` once Bellows repo is fully set up
- Purple square characterization test (2026-04-13) confirmed JSON structure, session ID stability, and `--resume` behavior. Test deliverable (purple square) should be removed from BrewBuddy after characterization is complete.
- `permission_denials` on git lock file removal is a recurring BrewBuddy pattern — not a Bellows concern, but worth noting in the parser as advisory-only
