# Anvil — Phase 2: Strategic Audit
**Date:** 2026-04-13 | **Type:** roadmap | **Status:** Pending

## Overview

Anvil currently scans codebase structure, extracts patterns, and scores volatility. Phase 2 adds a **domain interpretation layer** that cross-references structural findings against each project's stated mission, goals, and knowledge base. This enables Anvil to surface not just code-quality issues, but strategic gaps: architectural misalignments, knowledge gaps, unclear goals, and diagnostic opportunities.

## Why This Matters

Today structural audits catch "this code is untested" or "this function is called 17 times." Phase 2 adds context: "this untested code is critical to the invoice validation mission — here's a diagnostic to improve coverage" or "this function diverges in two places — are they intentional or a bug we haven't surfaced?" Findings become actionable because they're tied to project intent.

## Execution Model

- Triggered manually via RUN EXE in the anvil project (integrates into existing Anvil pipeline)
- No new infrastructure; uses existing project execution system
- Run at user discretion, roughly after every 5 commits per project
- Each project audited independently — no cross-project analysis in Phase 1

## What Anvil Phase 2 Does

- Reads PROJECT_BRIEF.md (project purpose, goals, constraints)
- Reads domain glossary (business rules, classifications, mappings)
- Audits full codebase structure (existing Phase 1 output)
- Cross-references findings: "Does this match project intent? Is this a gap?"
- Surfaces findings grouped by severity with structured metadata

## Output Format

Each finding follows this structure:

```
## [CRITICAL|HIGH|MEDIUM|LOW] — [Finding Title]

**What:** [Brief description of observation]

**Why it matters:** [Reason this is worth investigating]

**What needs to be discovered:** [What the diagnostic should answer]

**Success looks like:** [What we'd know when diagnostic is done]

**Diagnostic type:** [Fix / Clarification / Knowledge gap / Architecture check / other]
```

**Deposit location:** `[project]/knowledge/anvil/audit-findings-[date].md`

## Integration with Planner + Bellows

1. Anvil surfaces finding (e.g., "Fuel lookup logic exists in 2 places, diverges on rounding")
2. You + Planner review finding, refine the diagnostic question together
3. Planner writes the diagnostic prompt
4. Bellows executes the diagnostic on Mac
5. Findings inform next executable plan if action is needed

Anvil does NOT write diagnostic prompts in Phase 1 — that collaboration happens between you and Planner.

## Phases

### Phase 2.1 — Framework
- Define how Anvil reads and parses PROJECT_BRIEF.md + domain glossary
- Build the cross-reference layer that maps structural findings to project intent
- Implement finding categorization and severity tagging
- Test on invoice-pulse (most mature project with detailed glossary)

### Phase 2.2 — Rollout
- Apply to remaining active projects
- Refine finding descriptions based on real audit output
- Validate signal-to-noise ratio (findings should be actionable, not noise)

### Phase 2.3 — Learning (future)
- Track which findings lead to diagnostics vs. are dismissed
- Use feedback to improve audit quality over time
- Eventually: Anvil writes diagnostic prompts autonomously (Phase 3)

## Success Criteria

- Anvil audits one project and surfaces 5-10 findings
- Findings include a mix of fix opportunities, clarifications, and knowledge gaps
- At least 3 findings are actionable enough to write a diagnostic for
- Finding descriptions are clear enough that Planner can refine them without re-reading code
