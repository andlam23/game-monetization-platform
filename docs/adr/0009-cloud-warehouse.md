# ADR-0009: Cloud Warehouse

**Date**: 2026-05-06
**Status**: accepted

## Context

The project needs a cloud warehouse for two reasons: (1) recruiters scan resumes for specific warehouse names (Snowflake 30%, BigQuery 25%, Redshift 20%, Databricks 15% in JDs), and (2) the dbt + Dagster stack needs a real warehouse to run against. DuckDB (per `duckdb-skills`) is excellent for local SQL but isn't a cloud warehouse.

## Decision

Adopt **Google BigQuery** as the cloud warehouse. Use the always-free tier (10 GB storage, 1 TB queries/month) for portfolio scale.

## Alternatives

- **Snowflake** — leads JD frequency (~30%) and is the modern-data-stack default. Rejected for this project because: free trial is time-limited (30 days), the free credits run out, and ongoing portfolio work would need paid usage. BigQuery's free tier is permanent and quota-enforced rather than billing-enforced.
- **Amazon Redshift** — common in JDs (~20%) but has no equivalent permanent free tier; AWS free tier requires careful management to avoid charges. Rejected.
- **Databricks** — strong for ML-heavy workloads; less common in pure analytics JDs. Free Community Edition is limited. Rejected as overkill for this project's scope.
- **DuckDB-only** — works for local development but doesn't satisfy the resume-scan signal of "X cloud warehouse experience." Used as the local development tool, not the warehouse.

## Consequences

- "BigQuery" goes on the resume honestly. Resume signal partially captured (25% of JDs vs Snowflake's 30%).
- dbt-bigquery and dagster-gcp are mature, well-documented, and used by major data teams. Low integration risk.
- Looker Studio (ADR-0006) integrates natively with BigQuery — one-click connection. Stack consistency.
- BigQuery's pricing model (pay per query bytes scanned) requires care with `SELECT *` and unpartitioned scans. Acceptable trade-off; partition discipline is good practice anyway.
- If the project later needs Snowflake-specific experience for a job application, the dbt + Dagster code is largely portable — the warehouse swap is a profile and adapter change.
