# ADR-0005: Data Quality Tool

**Date**: 2026-05-06
**Status**: accepted

## Context

The data engineering stack needs a tool for ongoing data quality checks beyond what dbt's built-in tests cover (uniqueness, not-null, accepted values). Two open-source candidates dominate: **Great Expectations (GX)** and **Soda Core**. Both check freshness, distribution, and custom assertions; their philosophies and ergonomics differ significantly.

## Decision

Adopt **Soda Core** for cross-source data quality, freshness, and SLA-style contracts. Layer it behind dbt tests (which handle in-warehouse structural checks) and Dagster sensors (which handle anomaly detection per ADR-0008).

## Alternatives

- **Great Expectations** — older, more mature, more built-in expectations (~50), better data-science notebook ergonomics. Rejected because: SodaCL (YAML-based check language) reads as documentation, fits the project's "docs as code" ethos, and diffs cleanly in pull requests. GX's Python expectation objects are more expressive but read as code, not contracts. GX also overlaps with dbt tests in a way that creates "where do I put this test" decision fatigue; Soda is intentionally designed to complement dbt rather than duplicate it. GX's v1 rewrite (2024) also fragmented its community and documentation.
- **dbt tests alone** — sufficient for in-warehouse checks but misses cross-source freshness, SLA contracts, and any check that needs to live outside the dbt run.
- **Custom Python checks** — rejected as not worth the engineering cost when a mature tool exists.

## Consequences

- Three-layer data quality: dbt tests (cheap, in-warehouse, structural) → Soda (cross-source, contracts, SLAs) → Dagster sensors (anomaly detection on metrics). Clean separation of concerns.
- Some advanced statistical profiling (distribution drift via KS-test, etc.) isn't natively expressible in SodaCL. If needed later, can drop into Soda's Python extensions or run a separate GX check just for that. Hasn't been needed in the project's first six months.
- SodaCL contracts double as natural ADR companions ("we established this freshness SLA on `fact_revenue_daily` in ADR-NNNN").
