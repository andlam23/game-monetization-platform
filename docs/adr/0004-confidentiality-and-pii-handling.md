# ADR-0004: Confidentiality and PII Handling

**Date**: 2026-05-06
**Status**: accepted

## Context

Game monetization data includes player IDs, device IDs, email addresses, exact revenue figures, and partner names — much of which is sensitive even in synthetic form because production patterns leak through. The CLAUDE.md already requires placeholders in *documentation*. The same discipline must apply at the *operational* layer: when data is pasted into prompts, when claude-mem captures tool results, when example queries are written.

## Decision

Three operational rules, encoded in CLAUDE.md:

1. Never include raw player IDs, device IDs, or email addresses in prompts, examples, or sample data. Use synthetic IDs (`player_001`, `device_x`) or hashed surrogates.
2. Real revenue figures stay in the warehouse. When discussing or documenting amounts, use rounded or relative values (`$X`, "low five-figures") unless absolutely necessary.
3. Tag sensitive content with `<private>...</private>` blocks. claude-mem honors these blocks and excludes them from storage.

## Alternatives

- **Documentation-only confidentiality (status quo)** — leaves operational data flowing into prompts and memory unchecked. Rejected.
- **Strict no-real-data ever** — over-restrictive; sometimes a single concrete value is needed for debugging and the `<private>` tag handles that case.
- **Tooling-level redaction (e.g., a regex pre-processor)** — heavier engineering investment than the project warrants at this stage. Revisit if the manual rules fail.

## Consequences

- Slight friction in interactive use: synthetic IDs and rounded amounts require thinking before pasting.
- claude-mem's vector DB stays clear of sensitive content.
- This discipline carries directly into the public portfolio: a recruiter or client browsing the repo never encounters real customer data.
