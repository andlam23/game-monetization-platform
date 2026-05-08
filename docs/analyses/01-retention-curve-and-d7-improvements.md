# Analysis 01 — Is the retention curve healthy, and what would I test to improve D7?

**Author**: project-owner
**Date**: 2026-05-07
**Source data**: [`analytics.fct_retention_cohorts`](../../monetization_warehouse/models/marts/product/fct_retention_cohorts.sql) — exact-day cohort retention per [glossary.md § D1 / D7 / D30 retention](../glossary.md).
**Live view**: [Tile 2 of the dashboard](https://datastudio.google.com/reporting/dca0554f-5906-4c2d-8576-e5c4f922c3cb).

## TL;DR

The cohort has a **leaky front door and a sticky back door**. D1 retention (13.4%) sits ~17pp below the casual-puzzle industry benchmark, but D30 (5.7%) actually beats the benchmark by ~2pp. The D7 gap (7.3% vs ~10%) is downstream of the D1 problem — most users who churn between D1 and D7 had already disengaged on day 1. **Improving D7 efficiently means fixing D1 first**; a D1 lift from 13.4% to 20% would mathematically lift D7 to ~10% even without any D2-D7-specific intervention.

## Numbers

Retention curve from `fct_retention_cohorts`, weighted across all cohorts in the populated Flood-It window (2018-08-01 → 2018-10-03):

| day_offset | retention_rate | casual-puzzle benchmark | gap |
|---|---|---|---|
| D0  | 100.0% | 100% | — |
| D1  | 13.4% | ~30% | **−16.6pp** |
| D7  | 7.3%  | ~10% | −2.7pp |
| D14 | 7.3%  | ~6%  | +1.3pp |
| D30 | 5.7%  | ~4%  | **+1.7pp** |

Benchmarks pulled from GameAnalytics State-of-Mobile-style reports for casual puzzle (rough industry medians; treat as direction, not gospel). The D14 ≈ D7 plateau is consistent with [exact-day vs rolling-retention semantics](../glossary.md#d1--d7--d30-retention) — different users return on different days, and right-censoring shifts the cohort mix between offsets.

## Diagnosis

**The D1 cliff is doing all the work.** Going from 100% to 13.4% in 24 hours means 86.6% of acquired users churned before they returned even once. Every downstream retention number is a tax on that initial drop:

- D1 → D7 conditional retention: 7.3 / 13.4 = **54.5%**. Of users who came back on day 1, more than half were still active on day 7. That's actually a **strong** number — D1→D7 conditional benchmark for casual puzzle is roughly 30-40%. Users who survive the first day are stickier than industry average.
- D7 → D30 conditional retention: 5.7 / 7.3 = **78%**. Outstanding. Long-tail audience is committed.

**Translation**: this isn't a "bored mid-game" problem. It's a **first-session activation** problem.

## Hypotheses ranked by leverage

1. **First-session content density too low** — Flood-It's tutorial/early levels may not deliver enough stimulus variety in the first 5 minutes for the 86% who never return. Verify: pull `level_complete` event counts per user-day-1 and see whether the D1-returning cohort played meaningfully more levels on day 0 than the D1-churned cohort.
2. **No D1 re-engagement push** — Casual puzzle benchmark D1 retention often relies on a 24h push notification ("come back for daily reward"). If the game shipped without one, that alone explains the gap.
3. **Difficulty curve front-loaded** — early `level_fail` events spiking would suggest users hit a wall before completing the onboarding loop. Worth checking `level_fail / level_start` ratio in the first session vs subsequent sessions.
4. **Geography mismatch** — eCPM-rich tier-1 markets often have weaker organic D1 because installs include a lot of misclick/incidental traffic. Verify: D1 by `country` from `dim_players`. If tier-1 D1 << tier-3 D1, it's quality-of-acquisition, not quality-of-game.
5. **Platform / OS version regressions** — straightforward to rule out: D1 by `device_os`. If iOS D1 = Android D1 ≈ aggregate D1, ignore; if one platform is materially worse, prioritize a platform-specific debug.

## What I'd ship to test the leading hypothesis

**Test**: 24-hour push notification on day 1 with a daily-reward unlock framing. Random 50/50 split on install date.

**Predicted effect size**: D1 lift from 13.4% to 17-20%. (Industry case studies in casual puzzle put push-D1 lift at 3-7pp.)

**Sample-size sanity**: at p₁ = 0.134 and p₂ = 0.18 (an MDE of 4.6pp), two-sample proportion test with α=0.05, power=0.8 needs **n ≈ 1,250 per arm** = ~2,500 total installs. With Flood-It's ~140 installs/day, that's ~18 days to read the test. Reasonable.

**Read criteria**: significant uplift in D1 alone is enough — D7 and D30 will follow per the conditional-retention math above. Track them, but don't gate the decision on them (fewer days to read = faster shipping).

**Failure mode to watch**: a D1 push that *cannibalizes* otherwise-organic returns. If the test arm's D2 drops while D1 lifts, the push is just shifting return timing, not creating it. Check D2 retention in the test arm vs. control.

## Caveats specific to this dataset

- Flood-It's data is from 2018, before app-store privacy changes (ATT, Android privacy sandbox) materially changed acquisition quality. D1 numbers from 2024+ casual puzzle would likely be lower than the benchmarks above. The diagnosis still holds; the calibration target shifts.
- Retention computed against real Flood-It activity events only — the synthetic ad and IAP layers (per [ADR-0013](../adr/0013-data-acquisition.md)) don't add or remove "active" users, so retention numbers reflect real player behavior.
- Right-censoring removes late-window cohorts from D30 but not from D1 — see the model docstring for the cohort-mix difference between offsets.

## Glossary

[ARPDAU](../glossary.md#arpdau) · [D1 / D7 / D30 retention](../glossary.md#d1--d7--d30-retention) · [LTV](../glossary.md#ltv)

## ADR references

[ADR-0012 dbt project structure](../adr/0012-dbt-project-structure.md) · [ADR-0013 data acquisition](../adr/0013-data-acquisition.md)
