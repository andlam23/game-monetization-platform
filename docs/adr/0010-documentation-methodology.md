# ADR-0010: Documentation Methodology

**Date**: 2026-05-06
**Status**: accepted

## Context

Documentation is a first-class deliverable for this project. Two structured documentation forms have already been mandated by CLAUDE.md (`docs/glossary.md` and `docs/adr/`), but the project will produce many other docs: READMEs, runbooks, tutorials, explanations of attribution models, onboarding guides for analysts, technical references for the warehouse schema. These need a methodology so they don't devolve into amorphous prose.

## Decision

Adopt the **Diataxis framework** for all documentation that is not a glossary entry or an ADR. Diataxis splits docs into four types — tutorials (learning-oriented), how-to guides (task-oriented), reference (information-oriented), explanation (understanding-oriented) — and the methodology guides each toward its appropriate voice and structure.

Install the Diataxis Claude Code skill (`writing-documentation-with-diataxis` from sammcj/agentic-coding) to apply the methodology automatically when generating non-canonical docs.

For the canonical artifacts (glossary, ADRs), the **fixed templates in CLAUDE.md override** Diataxis's "structure follows content" guidance. Diataxis still informs the *voice* inside those templates — Decision sections read as reference (declarative), Context sections read as explanation (discursive) — but the templates themselves are mandatory.

## Alternatives

- **No methodology** — docs become amorphous; the failure mode is "one giant blob that does none of the four jobs well." Rejected.
- **Custom in-house methodology** — engineering cost without the benefit of Diataxis's existing tooling and community.
- **Different methodologies (e.g., Microsoft Style Guide, Google Developer Documentation Style Guide)** — these address style, not structural typology. Diataxis addresses both *what kind of doc this is* and *how it should sound*.

## Consequences

- Every non-canonical doc starts with the question "which Diataxis quadrant is this?" That question is itself a useful filter — if you can't answer, the doc probably has multiple jobs and should be split.
- Glossary and ADR templates remain fixed; they win over Diataxis's "structure follows content" guidance for those specific artifacts. CLAUDE.md states this explicitly so future Claude sessions don't try to "improve" the templates.
- Onboarding new contributors to the project's docs is easier — Diataxis is a public, well-documented framework.
