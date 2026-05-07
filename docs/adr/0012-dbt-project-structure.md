# ADR-0012: dbt Project Structure — staging / intermediate / marts

**Date**: 2026-05-07
**Status**: accepted

## Context

Phase 3 of `docs/SETUP.md` is complete: dbt-bigquery is wired into Dagster via `DbtProjectComponent`, and the example scaffold materializes end-to-end against BigQuery. The next thing the project will accumulate is **real models** — staging tables that mirror raw event sources, intermediate tables that bake in reusable business logic, and consumer-facing tables for analysts and the Looker Studio dashboards described in ADR-0006.

A flat `models/` directory with no subdivisions works for the first three or four models, then turns into chaos. Choosing a layered structure once — and choosing it before the first real model lands — costs almost nothing now and avoids retrofitting hundreds of models later. SETUP.md flags this as a decision-time doc immediately after Phase 3.

## Decision

Adopt the dbt-Labs-recommended **three-layer structure** under `monetization_warehouse/models/`:

```
models/
├── staging/
│   └── <source>/
│       ├── _<source>__sources.yml      # source definitions (one per raw source)
│       ├── _<source>__models.yml       # staging model docs and tests
│       └── stg_<source>__<entity>.sql  # 1:1 staging models
├── intermediate/
│   └── <domain>/
│       └── int_<entity>__<verb>.sql    # reusable joins / aggregations
└── marts/
    ├── finance/                        # IAP revenue, ad revenue, cost
    ├── product/                        # engagement, retention, funnel
    └── marketing/                      # attribution, paid acquisition
```

**Naming conventions** (mandatory):

- `stg_<source>__<entity>` — e.g. `stg_amplitude__events`, `stg_app_store__purchases`. Double underscore separates source from entity.
- `int_<entity>__<verb>` — e.g. `int_revenue__daily`, `int_users__pivoted`. Verb describes the transformation.
- Marts use plain entity names — e.g. `fct_revenue_daily`, `dim_players`, `arpdau`, `retention_cohorts`. No prefix required, but `fct_` / `dim_` is encouraged for warehouse modeling.

**Layer responsibilities**:

| Layer | Materialization | Allowed inputs | Allowed in SQL |
|-------|-----------------|----------------|----------------|
| `staging/` | view (default) | `source()` only | column renames, type casts, light filtering |
| `intermediate/` | view or ephemeral | `ref()` to staging or other intermediate | joins, aggregations, business logic that's reused by ≥2 marts |
| `marts/` | table or incremental | `ref()` to intermediate or staging | final shape consumed by BI / analysts |

A staging model never references another staging model. A marts model never references a source directly — go through staging.

**Sources** (`_<source>__sources.yml`) declare the raw BigQuery datasets/tables in the `raw` BigQuery dataset (per Step 2.3) and own freshness checks where appropriate.

## Alternatives

- **Flat `models/` directory**: simplest. Rejected because monetization analytics will produce 50+ models within the first year (one per metric, plus staging per source) and a flat layout becomes unsearchable. The cost of the structure now is one paragraph of CLAUDE.md docs; the cost of retrofitting is touching every model file.
- **Custom domain-first layout** (`models/iap/`, `models/ads/`, `models/retention/`): groups by business domain instead of pipeline stage. Rejected because models still need stage-aware materialization defaults (staging = view, marts = table) and dbt's `dbt_project.yml` configures these by directory path. Domain-first layouts force per-model overrides; stage-first inherits cleanly.
- **Two-layer (staging + marts, no intermediate)**: simpler. Rejected because monetization metrics share heavy joins (player attributes joined to revenue joined to acquisition) — without an intermediate layer, those joins get duplicated across marts and the project drifts toward inconsistency. Every junior analyst's first instinct is to copy-paste a join from a neighboring file; intermediate exists to give them a `ref()` instead.
- **Four-layer with `core/` between intermediate and marts**: dbt-Labs has discussed this for very large projects. Rejected as premature; revisit if marts grows past ~30 models.

## Consequences

- Every new model has a clear home: read raw → staging; reuse → intermediate; consume → marts. Code review can ask "is this in the right layer?" instead of "where should this go?"
- `dbt_project.yml` will need per-layer materialization configuration (added when the first real model lands, not now):
  ```yaml
  models:
    monetization_warehouse:
      staging:
        +materialized: view
      intermediate:
        +materialized: view
      marts:
        +materialized: table
  ```
- Marts subdirectories (`finance/`, `product/`, `marketing/`) match the way the business will consume metrics, which makes Looker Studio dashboard organization obvious.
- The default `models/example/` folder from `dbt init` is now an outlier and should be deleted as soon as the first real staging model lands. This ADR doesn't delete it preemptively — that change belongs with the first real PR — but flags the cleanup.
- Glossary entries (per ADR-0003 and `docs/glossary.md`) point at marts tables as the source of truth for each metric. ARPDAU's "Source of truth" field, when filled in, will be `marts/finance/arpdau` (or similar).
- Naming convention enforcement is currently manual / via review. If drift becomes a problem, dbt's `--check` flags or a project-level convention test can be added later.
