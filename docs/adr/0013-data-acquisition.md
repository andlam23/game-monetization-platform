# ADR-0013: Data Acquisition — Flood-It (real) + synthetic ad-revenue layer

**Date**: 2026-05-07
**Status**: accepted

## Context

Step 5.1 of `docs/SETUP.md` chooses the data that flows through the pipeline this project just built (BigQuery + dbt + Dagster + Soda + Sentry). The choice constrains every metric, model, and dashboard downstream — and SETUP.md flags it as the decision that warrants ADR-0013.

Two extensive searches established the public-data landscape:

- **No fully modern (2023+) row-level F2P mobile dataset with IAP + ad revenue + attribution + demographics exists publicly.** Studios treat that bundle as a competitive moat. The closest academic release (Unity's 2.87B-row corpus behind ACM `10.1145/3582927`) is paper-only, not downloadable.
- The only real, BigQuery-native, event-level F2P-shaped dataset publicly available is the **GA4 "Flood-It!" sample** at `firebase-public-project.analytics_153293282.events_*` — 114 daily tables (2018-08 → 2018-12), CC-BY 4.0, hundreds of millions of event rows from a real F2P puzzle game. Verified accessible from our `monetization-warehouse` project.
- Other candidates (Universalis FFXIV market board, EVE Online MER, Uken 2015 SFU) are real but either off-domain (MMO subscription / virtual economy, not F2P mobile) or schema-incomplete (Uken is user-aggregate, not event-level).
- Kaggle "2025"-labeled mobile-game datasets are LLM-generated; passing them off as real torches portfolio credibility.

Recruitment value diminishes fast past one strong real dataset. The recruiter screen wants "worked with real F2P data" as a binary signal; the hiring-manager interview evaluates *what* you did with the data — model quality, ADRs, dashboard storytelling — not how many sources you stitched together. Time spent on additional real datasets is time not spent on model quality.

## Decision

Use the **GA4 Flood-It! sample** as the single real-data source, supplemented by a **synthetic ad-revenue / ad-impression layer** generated locally and loaded into BigQuery's `raw` dataset.

**Real data — Flood-It (zero-copy)**:
- Declared as a dbt source pointing at `firebase-public-project.analytics_153293282.events_*`. Not copied into our `raw` dataset; queried in place via dbt staging models.
- Provides: session events, engagement, level start/complete/fail, screen views, IAP events (`ecommerce` field), install attribution (`traffic_source`), pseudo IDs, geo, device.
- Provides the canonical metrics' numerator/denominator inputs: ARPDAU, ARPPU (paying-user IAP), retention cohorts (D1/D7/D30), conversion funnel.

**Synthetic data — ad layer only**:
- Python generator that produces `ad_impression`, `ad_request`, `ad_revenue` events keyed against Flood-It's `user_pseudo_id` space, written to Parquet, loaded to `raw.synthetic_ad_events`.
- Calibrated parameters sourced from published industry benchmarks (eCPM by region, fill rate, ad request frequency by session length). Citations live in the generator's docstring and are mirrored in the ADR's References section as they're chosen.
- Generated content is **always** marked synthetic — column `is_synthetic = TRUE`, table prefixed `synthetic_`, dbt source description flags it.

**Battle pass, gacha, and detailed waterfall data are not generated.** No public dataset has them and synthesizing them adds surface area without recruitment value. Out of scope for this project.

## Alternatives

- **Pure synthetic generator across all event types**: full schema control, modern F2P mechanics. Rejected because passing the recruiter "real data" sniff test matters and is essentially free with Flood-It already in BigQuery.
- **Pure Flood-It (no synthetic ad layer)**: simplest. Rejected because half of F2P revenue is ad mediation; demonstrating that pipeline matters for a monetization-analyst portfolio. Skipping it leaves a visible gap on the resume.
- **Multi-real (Flood-It + Universalis FFXIV + Uken 2015)**: best diversity of real data. Rejected as diminishing-returns work — recruiters never see the additional sources, interviewers value depth on *one* dataset over breadth across several. The hours go further into model and dashboard quality.
- **Wait for a better public dataset**: no signal one is coming.
- **Real Uken 2015 alone**: pre-rewarded-ads era, no event grain, schema gaps. Rejected; if older real F2P depth ever matters, it can be added as a secondary source later.

## Consequences

- The `raw` BigQuery dataset will hold **only** synthetic ad-revenue tables. Flood-It is read in place from the `firebase-public-project` dataset via cross-project queries — billed against our quota's 1 TB/month free tier (bytes scanned, not stored).
- Every model, dashboard, and analysis must clearly distinguish **real** (Flood-It-derived) metrics from **synthetic** (ad-revenue-derived) ones. The convention: column `is_synthetic` propagates through staging → intermediate → marts; mart names default to real-only metrics with a `_with_ads` variant where the synthetic layer is mixed in.
- Flood-It's IAP coverage is real but vintage 2018-19. Modern F2P norms (battle passes, gacha pity, subscription tiers, store sales, ROAS-targeted UA) won't show up in the data. The portfolio narrative explicitly acknowledges this.
- Flood-It's ad-revenue events don't exist in the dataset, so the synthetic layer is the only way to demonstrate ad mediation analytics. Calibration cites public benchmarks transparently; an interviewer asking "where did your fill-rate come from?" gets a real answer.
- Cross-project query cost discipline: all dbt staging models against Flood-It must use partition filters (`_TABLE_SUFFIX BETWEEN ...`) to avoid scanning all 114 tables on every refresh. Staging models materialize as views with the partition filter pushed down, or as incremental tables keyed on `event_date`.
- Should public modern F2P data ever surface, swapping Flood-It for it is one staging-source change plus column re-mapping. The architecture is source-pluggable by design (per ADR-0012's staging layer).
- Glossary entries (`docs/glossary.md`) point at the marts tables built on this data. Each metric's "Source of truth" field will name the specific mart, with a note in the metric description if the metric depends on the synthetic layer.

## References

- GA4 Flood-It! BigQuery sample: <https://developers.google.com/analytics/bigquery/app-gaming-demo-dataset>
- License: <https://creativecommons.org/licenses/by/4.0/>
- Industry benchmark calibration sources for the synthetic ad layer: TBD as parameters are chosen — to be cited in the generator's docstring.
