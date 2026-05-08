# Analysis 02 — How concentrated is revenue in the top 1% of players, and what does that mean for live-ops priorities?

**Author**: project-owner
**Date**: 2026-05-07
**Source data**: [`analytics.dim_players`](../../monetization_warehouse/models/marts/product/dim_players.sql) — lifetime stats per user. Derived from real Flood-It activity, real ad-event keys, and synthetic ad/IAP revenue per [ADR-0013](../adr/0013-data-acquisition.md).
**Live view**: [Tile 5 of the dashboard](https://datastudio.google.com/reporting/dca0554f-5906-4c2d-8576-e5c4f922c3cb).

## TL;DR

Revenue concentration in this game is **more extreme than the standard 80/20**: **the top 1% of all 9,559 users (96 people) generate 86% of revenue**; the bottom 50% generate 0.39%. This isn't a bug or a calibration drift — it's the characteristic shape of free-to-play monetization, and it forces a specific live-ops priority stack: **whale retention beats casual conversion 10:1 in expected value per hour of engineering effort.**

## Numbers

Revenue concentration computed via `PERCENT_RANK()` over `dim_players.ltv_usd`:

| Segment of all users | Users | Revenue | % of total | Avg LTV |
|---|---|---|---|---|
| **Top 1%** | 96 | $7,495.82 | **86.0%** | $78.08 |
| Top 5% (next 4%) | 382 | $820.12 | 9.4% | $2.15 |
| Top 10% (next 5%) | 478 | $138.28 | 1.6% | $0.29 |
| Top 50% (next 40%) | 3,823 | $228.00 | 2.6% | $0.06 |
| Bottom 50% | 4,780 | $33.80 | 0.4% | $0.01 |

Cross-check from the [whale-concentration glossary entry](../glossary.md#whale-concentration): 68.4% of *IAP-only* revenue comes from the `whale` segment (top 10% of *payers*). The 86% figure here is broader because it includes ad revenue and is computed against *all users*, not just payers — the top 1% by LTV captures the heavy IAP whales plus the most ad-engaged users.

## What this means

**The top 1% is the only cohort where unit economics work.** Average LTV in that group is $78.08, against a casual-puzzle CPI (cost-per-install) range typically $0.50-$2.00. ROAS for whales is 40-150x. Every other segment is at best break-even on ad revenue.

**Implications, ranked**:

1. **Whale retention is the highest-leverage live-ops priority.** Losing one whale ($78 average, with the top-of-top-1% well into 3-figures) costs more than acquiring 50 random users. A live-ops calendar that doesn't have explicit "whale-tier engagement" beats are leaving money on the floor.
2. **VIP/loyalty programs are net-positive even at unflattering economics.** A program that costs the studio $5/mo per whale (concierge support, exclusive cosmetics, priority queue) needs only ~6.5% retention lift on those 96 users to break even ($5/mo × 96 users × marginal months / $78 LTV).
3. **Live-ops events should A/B-test whale uplift, not casual conversion.** Standard event-design instinct ("get more casuals to spend their first $0.99") chases the segment that contributes 0.5% of revenue. The same engineering hours spent designing a *whale-targeted* event (high-tier bundle, time-limited prestige cosmetic) compound at 10-100x.
4. **Acquisition budget should over-target whale-likely cohorts.** Even small DSP biases toward markets, devices, and creatives that historically over-index on whale conversion are worth more than absolute install volume. *Cost per whale*, not CPI, is the optimization function.
5. **Retention metrics should be segment-weighted.** The flat D7 retention number (7.3% per [Analysis 01](01-retention-curve-and-d7-improvements.md)) hides everything that matters: whale D7 is what determines revenue forecasts. A dashboard that doesn't break retention by `payer_segment` is misreading the game's health.

## What this DOESN'T mean

- It does NOT mean ignore the bottom 99%. Their ad impressions are revenue (small per-user, but accretive at volume), and they fund the social fabric (chat, leaderboards, live-event populations) that whales actually pay to be in. Pure-whale games tend to die fast.
- It does NOT mean every dollar above the top 1% line came from a "real" whale. The top 1% includes both spendy converted players and unusually ad-engaged free players. The hint: average top-1% LTV is $78, but the top whale's LTV is several hundred dollars. Distribution within the top 1% itself is heavy-tailed.
- It does NOT mean "find more whales" is a sustainable acquisition strategy on its own. Whales convert from the broader paying funnel; you can't acquire them directly. Step 1 is widening the paying-conversion funnel from 2.87% (current) to ~5%; step 2 is moving converted users up the segment ladder (minnow → dolphin → whale) via well-designed bundle progressions.

## What I'd build first

**Whale-segment retention dashboard tile.** A single Looker Studio chart: D1, D7, D30 retention split by `payer_segment` from `dim_players` joined to `fct_retention_cohorts`. If whale D30 retention is materially below segment average, that's the single most important number in the company.

After that, the live-ops calendar redesign per implication #3 above — but the dashboard tile is the prerequisite to having the right conversation.

## Caveats specific to this dataset

- The 86% figure is from synthetic IAP revenue calibrated to industry-realistic distributions per [ADR-0013](../adr/0013-data-acquisition.md). The *shape* (heavy-tailed power law) is reliable; the exact %  varies game-to-game in real data — typical casual puzzle numbers are 60-85%.
- 96 users in the top 1% is a small sample. Whale-segment statistical claims (e.g., "whale D7 retention is X%") at this dataset size have wide confidence intervals. In a production setting with 100k+ daily payers, the same analysis would have far more statistical power.
- The synthetic IAP layer was tuned to produce exactly this shape (whale concentration target 60-85% per [ADR-0013](../adr/0013-data-acquisition.md)). The validity of the *technique* — segment-by-LTV, compute revenue share, draw live-ops conclusions — is what generalizes.

## Glossary

[ARPPU](../glossary.md#arppu) · [LTV](../glossary.md#ltv) · [Conversion rate](../glossary.md#conversion-rate) · [Whale concentration](../glossary.md#whale-concentration)

## ADR references

[ADR-0007 product analytics platform](../adr/0007-product-analytics-platform.md) · [ADR-0012 dbt project structure](../adr/0012-dbt-project-structure.md) · [ADR-0013 data acquisition](../adr/0013-data-acquisition.md)
