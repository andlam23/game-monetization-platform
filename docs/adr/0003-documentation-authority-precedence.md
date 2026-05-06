# ADR-0003: Documentation Authority Precedence

**Date**: 2026-05-06
**Status**: accepted

## Context

This project uses multiple sources of context: claude-mem (cached past sessions), several skills (gstack, nimrodfisher, duckdb-skills, Diataxis), the custom monetization skill, and the project's own canonical docs (`docs/glossary.md`, `docs/adr/`). Any of these could "know" what a metric means or how a decision was made. When they conflict — e.g., claude-mem caches an old definition of ARPDAU that the glossary later refines — there must be an unambiguous winner.

## Decision

Establish explicit precedence: **`docs/glossary.md` and `docs/adr/` are canonical. Memory and skills are supplementary.** When supplementary sources disagree with the canonical docs, the docs win, and the conflicting supplementary content should be flagged for review (corrected, updated, or invalidated).

This rule is encoded in CLAUDE.md so every Claude session reads it.

## Alternatives

- **Most-recent-wins** — rejected because it makes correctness depend on update order, which is fragile.
- **Memory-wins** — rejected because canonical docs would lose authority and become decorative.
- **Per-conflict resolution** — rejected as too slow and inconsistent.

## Consequences

- The cost of writing into the canonical docs is correspondingly higher: errors compound. This is why the project uses diff-before-write discipline on `docs/`.
- claude-mem may need periodic correction sweeps when canonical docs change in ways that invalidate cached context.
- The system's authority structure is unambiguous to every Claude session and to human reviewers.
