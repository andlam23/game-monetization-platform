# ADR-0006: Business Intelligence Tool

**Date**: 2026-05-06
**Status**: accepted

## Context

The project needs a BI tool both for internal use (visualizing monetization metrics from the BigQuery warehouse) and for portfolio purposes (job market signal). Three free candidates: Looker Studio (formerly Google Data Studio), Tableau Public, and Power BI free tier. Tableau leads in JD frequency (~40% vs ~20% for Looker, ~30% for Power BI).

## Decision

Adopt **Looker Studio** as the primary BI tool. If portfolio breadth is later valuable, build one Tableau Public dashboard as a secondary entry.

## Alternatives

- **Tableau Public** — more common in JDs, but the hard constraint that *every workbook is forced public on your Tableau Public profile* breaks the moment any client work happens, and forces all portfolio work to use mock data only. Rejected as primary because of this constraint.
- **Power BI free tier** — only natively supports Microsoft data sources; BigQuery integration requires a Pro license. Rejected.
- **Build everything as custom HTML/Plotly dashboards** — works but doesn't pattern-match recruiter scans for "Tableau / Power BI / Looker" tool names. Rejected as primary.

## Consequences

- Job market: Looker Studio / Looker recognition is ~20% of JDs vs Tableau's ~40%. Some friction at resume scan time. Mitigated by adding Tableau Public as a secondary portfolio entry if time permits.
- Looker Studio integrates natively with BigQuery (per ADR-0009) — one-click connection, shared auth, no desktop install. Lowest-friction path to a live dashboard.
- Looker Studio supports both private reports (for client work) and public reports (for portfolio), eliminating Tableau Public's forced-public limitation.
- Looker Studio is the same product family as enterprise Looker, which is the BI tool growing fastest in modern-data-stack JDs.
