# Glossary Analyzer — Phase 1: Domain Knowledge Audit
**Date:** 2026-04-13 | **Type:** roadmap | **Status:** Pending

## Overview

Each Eluvian project maintains a domain glossary (`knowledge/research/domain-glossary.md`) that defines business rules, charge codes, system relationships, and operational facts. Over time, glossaries accumulate stale entries (terms no longer used in code), contradictions (conflicting definitions), and gaps (code uses terms not yet defined). The Glossary Analyzer is a company-level system that audits all project glossaries, surfaces these issues, and maintains institutional domain knowledge across projects.

## Why This Matters

Agents read the domain glossary before executing work. Stale or contradictory entries cause agents to apply outdated rules. Gaps cause agents to make incorrect assumptions. As projects evolve and new projects are created, the glossary should be a living, accurate source of truth — not a graveyard of old definitions.

## Scope

### Company-Level System
The Glossary Analyzer lives at the Eluvian level, not within any single project. It audits all active project glossaries independently, then optionally surfaces cross-project patterns (Phase 2).

### What It Audits (Phase 1 — Per Project)
- **Staleness:** Entries not referenced in code for 90+ days
- **Contradictions:** Two definitions of the same concept within a glossary
- **Gaps:** Terms used in code that don't exist in the glossary
- **Age tracking:** When was each entry last updated, last referenced

### What It Surfaces (Phase 2 — Cross-Project)
- Terms defined in multiple project glossaries — are they consistent?
- Terms from one project that are relevant to another (e.g., DAA defined in invoice-pulse but referenced in freight-kb)
- Shared concepts that could live in a company-level glossary
- New projects can tap into prior project glossaries to avoid re-learning domain concepts

## Execution Model

- Triggered manually via RUN EXE (consistent with Anvil and existing pipeline)
- Audits each project independently first
- Phase 2 adds cross-project consistency analysis

## Output Format

Per-project audit report deposited to `[project]/knowledge/anvil/glossary-audit-[date].md`:

```
## Stale Entries
- [term] — last referenced [date], not found in codebase scan

## Contradictions
- [term] — defined as X in section A, defined as Y in section B

## Gaps
- [term] — found in code at [file:line], not defined in glossary

## Retirement Candidates
- [term] — [reason to retire or archive]
```

Cross-project report deposited to `governance/glossary-audit-[date].md`.

## Phases

### Phase 1 — Per-Project Audit
- Scan each project's domain glossary
- Check each entry against codebase (grep for term usage)
- Flag stale, contradictory, and missing entries
- Deposit findings per project

### Phase 2 — Cross-Project Consistency
- Compare definitions across project glossaries
- Flag inconsistencies and shared concepts
- Identify terms that belong in a shared company-level glossary
- New project onboarding can reference prior glossaries for domain context

## Success Criteria

- Glossary Analyzer runs on invoice-pulse and surfaces at least 3 actionable findings
- At least 1 stale entry identified and retired
- At least 1 gap identified and added to glossary
- Cross-project analysis surfaces at least 1 shared concept across 2 projects
