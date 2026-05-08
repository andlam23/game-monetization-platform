# Analyses

Three core analyses written against the warehouse data — the *thinking on top of the infrastructure* that the rest of the project enables.

| # | Question | Punchline |
|---|----------|-----------|
| [01](01-retention-curve-and-d7-improvements.md) | Is the retention curve healthy, and what would I test to improve D7? | Leaky front door, sticky back door — fix D1 and D7 follows for free |
| [02](02-revenue-concentration-and-live-ops-priorities.md) | How concentrated is revenue in the top 1% of players, and what does that mean for live-ops? | Top 1% of users = 86% of revenue; whale retention beats casual conversion 10:1 in EV per engineering hour |
| [03](03-starter-pack-price-test-design.md) | If I were running a price test on the starter pack, how would I design it, and what's the minimum sample size? | Sample math at 0.40% baseline conversion is structurally hostile — skip the price test, run a bundle-content test |

Each piece grounds its claims in a SQL query against the warehouse, ends with a concrete recommendation, and links back to the [glossary](../glossary.md), [ADRs](../adr/), and the [live dashboard](https://datastudio.google.com/reporting/dca0554f-5906-4c2d-8576-e5c4f922c3cb).
