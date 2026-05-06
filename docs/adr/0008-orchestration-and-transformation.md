# ADR-0008: Orchestration and Transformation Stack

**Date**: 2026-05-06
**Status**: accepted

## Context

The data pipeline needs (a) a transformation layer to materialize raw events into analytics tables, and (b) an orchestration layer to schedule, monitor, and lineage-track those transformations. The candidates are well-established: dbt for transformations (de facto standard); Dagster, Airflow, Prefect, or Mage for orchestration.

## Decision

Adopt **Dagster + dbt** as the orchestration + transformation stack.

- **dbt** for in-warehouse transformations. Models defined as SQL `SELECT` statements; dbt handles materialization, dependency resolution, testing, and documentation. Industry standard.
- **Dagster** for orchestration. Asset-first model fits monetization data work especially well — each metric or table is a declared asset with explicit dependencies, automatic lineage, and observability built in. Dagster has first-class dbt integration via `dagster-dbt` (`DbtProjectComponent` pattern).

Anomaly detection is implemented as Dagster sensors (custom Python comparing metrics to rolling baselines), since enterprise anomaly tools (Monte Carlo, Anomalo) are expensive and the rules are domain-specific anyway.

## Alternatives

- **Airflow** — incumbent but heavy, dated DAG-centric model, Kubernetes-leaning. Rejected as overkill for solo/small-team scale.
- **Prefect** — reasonable Dagster alternative, simpler dynamic flows. Rejected because Dagster's asset model fits monetization analytics more naturally (each metric *is* an asset).
- **Mage** — newer, notebook-friendly, smaller community. Rejected due to ecosystem maturity.
- **GitHub Actions cron + dbt only** — minimum viable; works fine for small data and zero infra. Acceptable bootstrap path; not adopted as the primary because Dagster's lineage and observability pay off as soon as the pipeline is non-trivial.

## Consequences

- The asset graph in Dagster's UI becomes a self-documenting view of the warehouse — "where did this number come from?" is answered visually.
- dbt + Dagster handles the late-arriving-data failure mode (refunds, chargebacks, attribution backfill) naturally with partitioned assets and incremental dbt models. This is critical for monetization data and informs ADR for partition strategy when written.
- Idempotency and backfill-awareness are designed in from the start, not retrofitted.
- Slight onboarding curve for Dagster's asset-first mental model. Mitigated by the strong official docs.
