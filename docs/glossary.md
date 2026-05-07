# Metric & Domain Glossary

## ARPDAU
**Definition**: Average Revenue Per Daily Active User. The average per-active-user revenue (ad + IAP combined) on a given calendar day. Day-level metric; aggregated across days by averaging daily values, never by recomputing on a multi-day window (which would understate it).
**Formula**: `SUM(total_revenue_usd) / COUNT(DISTINCT IF(is_active_today, user_pseudo_id, NULL))` over a single `event_date`. Both numerator and denominator come from `analytics.fct_revenue_daily`.
**Source of truth**: `monetization-warehouse:analytics.fct_revenue_daily`
**First defined**: 2026-05-07

## ARPPU
**Definition**: Average Revenue Per Paying User. Total IAP revenue divided by the count of distinct payers (users with at least one purchase across the data window). Excludes ad revenue per industry convention — ARPPU isolates spend from the converted cohort.
**Formula**: `SUM(total_iap_revenue_usd) / COUNT(*)` from `analytics.dim_players` filtered to `is_payer = TRUE`. Equivalent to `AVG(ltv_usd)` over the payer cohort.
**Source of truth**: `monetization-warehouse:analytics.dim_players` (filter on `is_payer = TRUE`)
**First defined**: 2026-05-07

## LTV
**Definition**: Lifetime Value. Total cumulative revenue (ad + IAP) attributed to a single user across the data window. Time horizon for this project is the actual Flood-It data range (2018-08-01 → 2018-10-03, ~64 days; daily-sharded tables exist through 2018-12-31 but the late ones are empty) — *not* a forecast and *not* truncated to D7/D30/D90/D365 the way LTV is sometimes reported in production. Switch to a windowed/forecasted variant when joining to acquisition cost data for ROAS analysis.
**Formula**: `SUM(total_revenue_usd)` per `user_pseudo_id` across the entire data window. Materialized as `dim_players.ltv_usd`.
**Source of truth**: `monetization-warehouse:analytics.dim_players` (`ltv_usd` column)
**First defined**: 2026-05-07

## D1 / D7 / D30 retention
**Definition**: Exact-day cohort retention. Of users whose first session was on `cohort_date`, the share who have at least one active Flood-It event on `cohort_date + N` (where N = 1, 7, or 30). UTC calendar-day boundaries — Flood-It's geo data is country-grain only, no IANA timezone available, so user-local-time retention isn't computable. **Exact-day**, not rolling: D7 means returned *on* day 7, not "active any day ≥ 7." Right-censored: cohorts whose `cohort_date + N` falls past the latest available date are omitted entirely so retention is never deflated by missing follow-up data.
**Formula**: For a single cohort: `COUNT(DISTINCT users active on cohort_date + N) / COUNT(DISTINCT users in cohort)`. Across cohorts (weighted): `SUM(retained_users) / SUM(cohort_size)` filtered to `day_offset = N`. Materialized at all offsets 0..30 in `fct_retention_cohorts`.
**Source of truth**: `monetization-warehouse:analytics.fct_retention_cohorts` (`cohort_date`, `day_offset`, `cohort_size`, `retained_users`, `retention_rate`)
**First defined**: 2026-05-07

## Conversion rate
**Definition**: Paying conversion rate. Share of users who made at least one IAP purchase across the data window, out of the total user base. The "paying / total" formulation, *not* "paying / new" (which is paying-conversion-of-new-cohort and is computed separately when needed).
**Formula**: `COUNTIF(is_payer) / COUNT(*)` from `analytics.dim_players`.
**Source of truth**: `monetization-warehouse:analytics.dim_players`
**First defined**: 2026-05-07

## Whale concentration
**Definition**: Share of total IAP revenue attributable to the top 10% of payers ("whales") by lifetime spend. Tracks how skewed the payer revenue distribution is. The 80/20 rule says whales drive 70-80% of IAP revenue in healthy F2P; this project's synthetic IAP layer is calibrated to land in that range.
**Formula**: `SUM(IF(payer_segment = 'whale', total_iap_revenue_usd, 0)) / NULLIF(SUM(total_iap_revenue_usd), 0)` from `analytics.dim_players`. Payer segment is percentile-assigned at IAP generation time per ADR-0013 (top 10% of payers by LTV).
**Source of truth**: `monetization-warehouse:analytics.dim_players` (`payer_segment` + `total_iap_revenue_usd`)
**First defined**: 2026-05-07
