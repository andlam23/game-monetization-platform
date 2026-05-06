# ADR-0002: Memory Architecture

**Date**: 2026-05-06
**Status**: accepted

## Context

Cross-session memory is critical for a long-running project — losing context between sessions wastes hours of re-explaining decisions, schema, and reasoning. Two mechanisms in the chosen tooling both provide memory: `claude-mem` (raw cross-session context, semantically compressed, automatic) and gstack's `/learn` (manual capture of explicit rules and lessons). Used naively, both run unchecked, producing duplicate context injection and risk of contradiction.

## Decision

Use `claude-mem` as the primary memory layer for raw cross-session context. **Restrict gstack's `/learn` to explicit "remember this rule" moments only** — durable preferences and hard-won lessons that are worth promoting to a named, reusable artifact.

## Alternatives

- **claude-mem only, no `/learn`** — clean but loses the value of explicitly named rules.
- **`/learn` only, no claude-mem** — would lose the automatic raw context capture that makes claude-mem valuable.
- **Both unrestricted** — produces duplicate bookkeeping and potential contradictions; rejected.

## Consequences

- Memory has two layers with clear boundaries: automatic (claude-mem) and intentional (`/learn`).
- Discipline required: when tempted to invoke `/learn`, ask "is this a durable rule, or context claude-mem already captured?" If the latter, skip `/learn`.
- Authority precedence (ADR-0003) handles the residual risk that memory disagrees with the canonical docs.
