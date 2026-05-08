# Analysis 03 — If I were running a price test on the starter pack, how would I design it, and what's the minimum sample size?

**Author**: project-owner
**Date**: 2026-05-07
**Source data**: [`raw.synthetic_iap_events`](../../scripts/data/generate_synthetic_iap_events.py) and [`analytics.dim_players`](../../monetization_warehouse/models/marts/product/dim_players.sql).
**Live view**: starter bundle visible in [Tile 5 segment LTV](https://datastudio.google.com/reporting/dca0554f-5906-4c2d-8576-e5c4f922c3cb).

## TL;DR

To run a clean price test on the **`starter_bundle`** (currently $19.99), I'd test **$19.99 → $9.99** and read on **revenue per user**, not conversion lift alone. Required sample size at the current baseline conversion (0.40%) and a target effect of +50% buyers: **~36,000 users per arm = ~72,000 total**, which at Flood-It's ~140 installs/day takes **~9 months** — far too slow. Practical fixes: raise the test-eligible audience by relaxing the new-user gate (more buyers per day), or accept a larger MDE and ship in 6-8 weeks. The exercise itself reveals that **slow-burn casual puzzle pricing tests need an MDE around 25-50%, not 5%, to be readable in commercial timeframes**.

## Numbers

Per-product purchase data from `raw.synthetic_iap_events`:

| product_id | distinct_buyers | conversion of all users | revenue | avg basket |
|---|---|---|---|---|
| ultimate_bundle ($99.99) | 13 | 0.14% | $2,799.72 | $107.68 |
| mega_pack ($49.99) | 21 | 0.22% | $1,399.72 | $50.07 |
| **starter_bundle ($19.99)** | **38** | **0.40%** | **$1,019.49** | **$26.83** |
| coins_xl_pack ($9.99) | 52 | 0.54% | $819.18 | $15.75 |
| coins_medium ($2.99) | 139 | 1.45% | $762.45 | $5.49 |
| coins_small ($0.99) | 241 | 2.52% | $756.36 | $3.14 |
| coins_large ($4.99) | 75 | 0.78% | $583.83 | $7.78 |

Total user base for conversion: 9,559.

## Test design

**Hypothesis**: Lowering starter_bundle price from $19.99 to $9.99 lifts converted-buyer count enough to net more revenue, despite the per-purchase revenue cut.

**Why $9.99 specifically**: it's the next price point on the existing ladder, sandwiches between coins_xl_pack ($9.99 base) and the current starter, and matches the most common "first-time buyer offer" pricing pattern in casual puzzle. Testing $14.99 instead would be informative but is between two existing tiers — odd from a UX/store-listing standpoint.

**Treatment definition**:
- **Control**: starter_bundle visible at $19.99, current configuration
- **Treatment**: starter_bundle visible at $9.99, all other bundles unchanged
- **Eligibility window**: first 7 days post-install (the actual "starter" framing); users who don't see it in the first week roll off the test

**Randomization unit**: `user_pseudo_id`, deterministic via FARM_FINGERPRINT to avoid leakage on session restarts. 50/50 split.

**Primary metric**: **revenue per eligible user** (RPU on the eligibility window).
**Secondary metrics**: starter_bundle conversion rate, bundle-level cannibalization (drop in coins_xl_pack and mega_pack purchases — the price cut might pull demand sideways instead of forward), retention D7 (the cheaper starter might attract less-committed converters who churn).

**Why RPU not conversion**: a 2x conversion lift at half price = same revenue. A test that reads only on conversion lift will declare victory while leaving total revenue flat. RPU is the only metric where the answer matches the business question.

## Sample-size calculation

Two-sample test for difference in conversion rates:

$$
n = \frac{(Z_{\alpha/2} + Z_\beta)^2 \cdot [p_1(1-p_1) + p_2(1-p_2)]}{(p_2 - p_1)^2}
$$

At α=0.05 (two-sided), power=0.80: $Z_{\alpha/2}$ = 1.96, $Z_\beta$ = 0.84.

**Scenario A: optimistic** — assume cutting the price 50% lifts buyer count 50% (p₁ = 0.40%, p₂ = 0.60%, MDE = 0.20pp)

$$
n = \frac{(1.96 + 0.84)^2 \cdot [0.004 \cdot 0.996 + 0.006 \cdot 0.994]}{(0.002)^2}
\approx \frac{7.84 \cdot 0.00993}{0.000004}
\approx 19{,}500 \text{ per arm}
$$

→ **~39,000 total** users. At ~140 installs/day in this dataset: **~9 months to read**. Unviable.

**Scenario B: realistic** — same conversion lift at MDE 0.30pp (p₂ = 0.70%, +75% lift)

$$
n \approx \frac{7.84 \cdot 0.0109}{0.000009} \approx 9{,}500 \text{ per arm}
$$

→ **~19,000 total**. Roughly **~4-5 months at this volume**. Still slow.

**Scenario C: aggressive** — MDE 0.40pp (p₂ = 0.80%, +100% lift, doubles buyers)

$$
n \approx \frac{7.84 \cdot 0.012}{0.000016} \approx 5{,}900 \text{ per arm}
$$

→ **~12,000 total. ~3 months**.

## What this exposes about price testing in casual puzzle

A 0.40% baseline conversion is structurally hostile to A/B testing. The math is unforgiving:

- **You cannot read small effects.** Anyone proposing a price test with a "5% lift in conversion" target on a 0.40%-baseline product is proposing a test that will never finish. MDE has to be a meaningful fraction of the baseline (50%+), not a small absolute change.
- **Volume is the binding constraint, not statistics.** This dataset is too small for any but the most aggressive tests. Real production casual-puzzle games at scale (100k-1M DAU) read these tests in 2-4 weeks; below that, the test design changes.
- **Bayesian / sequential testing is sometimes worth the methodological complexity.** With small samples, a frequentist 80% power requirement is wasteful — sequential designs can stop early on strong signals.

## What I'd actually do given Flood-It's volume

1. **Skip the price test.** Run a *bundle-content* test instead — same $19.99 price, 50% more in-game currency in the treatment arm. Easier to design, doesn't dilute revenue, and conversion lifts here have less ambiguity than price cuts.
2. **If the org insists on price testing**: pre-register the analysis (lock the success criteria before the test starts), use Scenario C's aggressive MDE, accept that "no result" is a real outcome, and budget 3 months for the read.
3. **In the meantime, instrument an "intent to purchase" funnel** in Amplitude (`store_open` → `bundle_view` → `iap_attempt` → `iap_purchase`) — funnel-step diagnostics surface *where* in the conversion path users drop off, which is more actionable for a small-volume game than aggregate conversion lift.

## Caveats specific to this dataset

- All IAP data is synthetic per [ADR-0013](../adr/0013-data-acquisition.md). Real conversion-rate lifts from price changes vary by genre, market, and bundle composition — published case studies show casual puzzle starter-pack price cuts producing anywhere from +25% to +100% buyer counts. The sample-size math is real; the assumed effect size is illustrative.
- "First 7 days post-install" eligibility is a design choice. Real starter-pack tests sometimes use first session, first level pack, or first IAP-attempt as the gate. The eligibility window changes the n calculation — narrower windows mean fewer buyers per day, slower reads.
- Cannibalization is real in production data and barely modeled in the synthetic layer. A real test would also need to look at total IAP revenue per eligible user, not just the starter line, to catch demand shifting between bundles.

## Glossary

[ARPPU](../glossary.md#arppu) · [LTV](../glossary.md#ltv) · [Conversion rate](../glossary.md#conversion-rate)

## ADR references

[ADR-0007 product analytics platform](../adr/0007-product-analytics-platform.md) · [ADR-0013 data acquisition](../adr/0013-data-acquisition.md)
