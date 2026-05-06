# Project Context
This project works with video game monetization data — building software (ETL,
analytics, dashboards) around metrics like ARPDAU, ARPPU, LTV, retention cohorts,
conversion funnels, and IAP/ad revenue. Documentation is a first-class deliverable.

## Authority precedence
- `docs/glossary.md` and `docs/adr/` are CANONICAL sources of truth.
- Memory (claude-mem) and skills are SUPPLEMENTARY context.
- If memory or any skill disagrees with the docs, the docs win.
  Flag the discrepancy for review; do not silently follow the supplementary source.

## Documentation responsibilities

### Glossary entries (`docs/glossary.md`)

Every domain term, metric, or KPI referenced in code, docs, or analysis has a
glossary entry. The entry exists as soon as the term is first referenced — a
placeholder with TODO fields is acceptable until the definition is settled.
Use this fixed template:

````
## <Term>
**Definition**: <one or two sentences in plain English>
**Formula**: <exact computation, or "n/a" for non-numeric terms>
**Source of truth**: <table, dashboard, or doc that defines it canonically>
**First defined**: <YYYY-MM-DD the entry was written>
````

### ADR records (`docs/adr/`)

Every architectural decision that constrains future work gets a numbered ADR.
Filenames are `NNNN-kebab-case-title.md`. The index at `docs/adr/README.md`
lists every ADR; update it in the same commit as a new or superseded ADR.
Use this fixed template:

````
# ADR-NNNN: <Title>

**Date**: <YYYY-MM-DD>
**Status**: accepted | superseded by ADR-NNNN

## Context
<the situation, the problem, the forces in play>

## Decision
<what was chosen and any operative rules>

## Alternatives
- <option>: <why rejected>

## Consequences
- <outcome, trade-off, or follow-up>
````

## Confidentiality and PII
- Never include raw player IDs, device IDs, or email addresses in prompts,
  examples, or sample data. Use synthetic IDs (player_001, device_x) or hashed
  surrogates.
- Real revenue figures stay in the warehouse. When discussing or documenting
  amounts, use rounded/relative values ($X, "low five-figures") unless absolutely
  necessary.
- Tag sensitive content with <private>...</private> blocks. claude-mem honors
  these and excludes them from storage.

## Memory discipline
- claude-mem captures raw cross-session context automatically.
- Use /learn ONLY for explicit "remember this rule" moments (durable preferences,
  hard-won lessons). Don't use /learn for things claude-mem already covers.

## Documentation methodology
For docs OTHER than glossary and ADRs (READMEs, runbooks, tutorials, explanations),
the writing-documentation-with-diataxis skill provides the methodology.
For glossary entries and ADR records, the fixed templates in this CLAUDE.md
override Diataxis's "structure follows content" guidance — those templates are
mandatory.

## Decision-time documentation rule
When a choice is made that constrains future work (warehouse, library, schema,
attribution model, etc.), an ADR is written in the SAME COMMIT as the change it
documents. Retroactive ADRs are not acceptable; if a decision happens in
conversation with no ADR, ask before moving on.
