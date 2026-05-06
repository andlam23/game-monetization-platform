# Career Track — The Parallel Plan

This file covers everything `SETUP.md` doesn't: the work of becoming the person who *gets* a game monetization role, not just the person who *built* a relevant project. SETUP.md handles the **project** (the artifact). This handles the **candidate** (you).

> **80% goal:** land a monetization analyst / game data analyst / live ops analyst role at a video game company.
> **20% fallback:** if gaming doesn't pan out, redeploy the same skills into D2C subscription / SaaS product / fintech / marketplace analytics — where game-trained instincts (sharp retention math, LTV intuition, A/B rigor) carry a premium.

## How this file relates to SETUP.md

SETUP.md is sequential (Phase 0 → Phase 6). CAREER.md is **mostly parallel** — most tracks here run concurrently with the build, and a few (job applications, freelance launch) come after the portfolio is real enough to point at. The five tracks:

| Track | Run when | Goal |
|---|---|---|
| **A. Industry fluency** | Concurrent with SETUP.md | You sound like someone who's been in the industry for a year. |
| **B. Critical play** | Concurrent with Phase 5+ | You can talk about real games like a designer/analyst, not a player. |
| **C. Network presence** | Concurrent throughout | You're recognizable to the people who hire. |
| **D. Job applications** | After SETUP.md Phase 6.1 | You're applying with proof, not promises. |
| **E. Fallback prep** | Concurrent throughout, low intensity | If gaming roles don't materialize, you can pivot in 30 days, not 6 months. |

---

## Track A — Industry fluency (concurrent, ~3–4 hours/week)

The point: in a monetization interview, the difference between "candidate" and "hire" is often whether you can casually reference what's happening in the industry *right now*. JDs literally list "follows industry developments" and "plays top games critically" as differentiators.

### Step A.1: Read *Freemium Economics* (Eric Seufert)

The foundational text on F2P monetization math — LTV, payer conversion, whale dynamics, retention modeling. Written in 2014, still the reference. Author is the most-cited voice in the space.

- Free book PDF and code: <https://mobiledevmemo.com/freemium-economics/>
- Author profile: <https://mobiledevmemo.com/about/>
- About a week's evening reading. Take notes — the formulas reappear in interviews.

### Step A.2: Subscribe to the four newsletters that matter

These are the ones currently working analysts and operators actually read in 2026:

1. **Mobile Dev Memo** (Eric Seufert) — free weekly newsletter at <https://mobiledevmemo.com>. Independent analysis of mobile, ad tech, and monetization. Sharpest single voice in the space. Also has a paid tier (MDM Pro) and a private Slack. Free version is enough to start.

2. **Naavik Digest** (Naavik consulting firm) — described as "the #1 games industry newsletter" with weekly issues. Deep deconstructions of game design, business models, and company strategy. Sign up at <https://naavik.co>. Their podcast (Naavik Gaming Podcast) reads the digest on air, useful for commute listening.

3. **Deconstructor of Fun** (Michail Katkoff and team) — newsletter + podcast for games professionals. Multiple hosts, weekly cadence, very tactical (what worked, what didn't, what the data shows). <https://www.deconstructoroffun.com> and find "Deconstructor of Fun" on Apple Podcasts / Spotify.

4. **GameDiscoverCo** (Simon Carless) — Steam and PC market intelligence specifically. If your interest extends beyond mobile F2P into PC/console live service, this is the source. Free newsletter at <https://newsletter.gamediscoverable.com>.

Set aside 30 minutes Monday morning for the week's issues. **Take notes on terminology you don't recognize** — that's your homework list.

### Step A.3: Listen to the two podcasts that sharpen monetization thinking

- **Mobile Dev Memo Podcast** (Eric Seufert hosts) — weekly, ~45-60 minutes. Recent episodes from May 2026 cover the modern mobile gaming economy with Phil Black, agentic commerce, Reddit ad earnings, search behavior shifts. Find on Spotify or via <https://mobiledevmemo.com/category/original-content/podcast/>.
- **Deconstructor of Fun** — weekly. Recent episodes break down Newzoo's 2026 PC & Console report, GDC 2026 takes, the shift toward $30-50 mid-priced premium games, AI's role in UA. <https://podbay.fm/p/deconstructor-of-fun>.

You don't have to listen to every episode. Pick 1–2 per week. Listen at 1.25–1.5x. The goal is exposure to vocabulary and current debates, not encyclopedic recall.

### Step A.4: Follow the right people on LinkedIn

A short, focused list (DON'T just follow 200 random people — follow these and engage thoughtfully):

- Eric Seufert (Mobile Dev Memo)
- Michail Katkoff, Phillip Black, Eric Kress, Jen Donahoe (Deconstructor of Fun hosts)
- Joost van Dreunen (CEO of Aldora, NYU Stern professor, prolific on games industry economics)
- Aaron Bush (Co-founder Naavik)
- Joseph Kim (Lila Games, writes on F2P design)
- Matej Lančarič (UA specialist, writes very practical pieces)

When you read a piece you find sharp, leave a substantive comment on LinkedIn. Not "great post" — actual engagement with the argument. Over six months this is how recruiters and hiring managers learn your name.

### Step A.5: Read one industry report per month

Sensor Tower, Newzoo, AppsFlyer, Adjust, and data.ai all publish free quarterly/annual reports. Pick one each month. Skim, then write a 200-word "what I learned" post on LinkedIn or in your repo's `docs/explanations/` folder (Diataxis-style explanation doc).

This serves three purposes: it forces you to internalize the data, it generates LinkedIn content, and it builds a public catalog of your monetization thinking that hiring managers can find.

---

## Track B — Critical play (concurrent with SETUP.md Phase 5+, ~3 hours/week)

You cannot interview for a monetization role without playing F2P games critically. This isn't entertainment time; it's research.

### Step B.1: Pick your five games

Aim for diversity across genre and monetization model:

1. **A top-grossing match-3** (Royal Match, Candy Crush, Match Masters) — for energy systems and IAP pacing.
2. **A 4X / strategy** (Last War: Survival, Whiteout Survival, Top Heroes) — for whale concentration and battle pass mechanics.
3. **A merge or puzzle** (Travel Town, Merge Mansion) — for narrative-driven retention and event design.
4. **An RPG / gacha** (Genshin Impact, Honkai: Star Rail, Reverse: 1999) — for gacha psychology and pity systems.
5. **A live-service shooter or hypercasual breakout** — for offers, season passes, and ad monetization.

The current top-grossing list is on Mobile Dev Memo's homepage at <https://mobiledevmemo.com> and updates 3x daily.

### Step B.2: Set up a critical play notebook

Make a `docs/teardowns/` folder in your repo. For each game, take screenshots and notes on:

- **Onboarding flow** — what's the first 10 minutes? What's the first ask? When does the first soft offer appear?
- **Store layout** — what's the first thing you see? How are price points anchored? What's a "bundle" and what's not?
- **Energy / time gates** — what limits play? What's the cost to skip?
- **Battle pass / season** — price, length, hard currency yield, premium-vs-free track gap.
- **Whale touchpoints** — VIP systems, $99.99 packs, "limited time" offers, daily deals.
- **Engagement loops** — daily login, streaks, events, social pressure.
- **Ad placement** — rewarded video offers, interstitials, opt-out economics.

Play each game for at least a week. Spend a small amount in one of them ($5-10 in a single IAP) so you understand what the post-purchase flow looks like — that's where most analysts who haven't paid get blindsided in interviews.

### Step B.3: Write five teardowns

One per game. Format as a Diataxis "explanation" doc — discursive, captures the *why* behind the design choices. Each ~1500-2500 words. Structure:

1. **The pitch** — what does this game think it's selling? Who to?
2. **The economy** — soft currency, hard currency, premium currency, sinks, faucets. Diagram if you can.
3. **The progression treadmill** — what gates exist? How fast do they tighten? Where's the natural friction point that triggers spend?
4. **The monetization stack** — IAP, ads, battle pass, subscriptions. What's the relative weight?
5. **What I'd test** — three specific hypotheses for moving ARPDAU or retention by 3-5%.

Publish these on your repo and on a personal blog (Substack, Hashnode, or Medium — pick one). Cross-post to LinkedIn with a hook.

These are the strongest interview prep documents that exist for monetization roles. Hiring managers read them and ask "tell me about that test you'd run on Royal Match" — and now you have a 30-minute answer prepared.

---

## Track C — Network presence (concurrent throughout, ~1 hour/week)

You cannot get hired by people who don't know you exist. The good news: the games industry is small. A few targeted moves matter more than a thousand cold applications.

### Step C.1: LinkedIn optimization

Spend 90 minutes once on these:

- **Headline**: not "Aspiring Data Analyst" — instead "Building open-source monetization analytics tooling | dbt + Dagster + BigQuery | F2P retention & LTV". Specific signals.
- **About**: 3-5 sentences explaining what you're building and why. Link to the public repo. Mention the analyses (when written).
- **Featured section**: pin the repo, the live Looker Studio dashboard, your three analyses, your five teardowns.
- **Skills**: SQL, Python, dbt, Dagster, BigQuery, Amplitude, A/B Testing, Cohort Analysis, Data Visualization, Soda, Sentry. Not LinkedIn's auto-suggestions.

A current and well-cited guide on LinkedIn optimization for data roles: search "LinkedIn data analyst profile 2026" — the patterns change yearly. The framework above is durable.

### Step C.2: Join the Mobile Dev Memo Slack

Free with newsletter signup. Active community of mobile and F2P operators. **Lurk for two weeks, then participate**. When someone asks a question you can credibly answer, answer it. Don't spam, don't pitch yourself. Over months this is where job opportunities surface that never hit LinkedIn.

### Step C.3: Conferences and events

The two that matter for monetization:

- **Pocket Gamer Connects** — multiple cities per year (London, Helsinki, Toronto, San Francisco, Bangalore, Jordan in the 2026 calendar). Tickets aren't cheap but indie/student rates exist. Schedule: <https://www.pocketgamer.biz/connects/>. The *single best* event for mobile/F2P networking. If you can swing one in your geography, do it.
- **GDC** (San Francisco, late March) — broader but with strong F2P track. 2026 saw lower attendance but a "more efficient executive" crowd. Day passes available; full pass is expensive.

If conferences aren't financially feasible right now, skip them — but follow the post-event newsletters, since most people summarize what they heard.

### Step C.4: Ship one piece of public writing per month

Beyond your teardowns and the analyses in SETUP.md, write one short piece per month — a reaction to a recent industry event, a novel data analysis, a methodology breakdown. ~800-1500 words. Post on LinkedIn (it has the best discovery for this audience) and your personal blog.

This compounds. By month 6, you have a body of public work that speaks for you in interviews.

---

## Track D — Job applications (after SETUP.md Phase 6.1)

Don't apply with a half-finished portfolio. Wait until at least:

- 3 ADRs written
- Glossary populated for the metrics in your dashboard
- Live Looker Studio dashboard pointing at real(ish) data
- Three analyses published
- Pinned repo on GitHub profile

That's roughly the end of SETUP.md Phase 6.1. From there:

### Step D.1: Resume rewrite

A monetization analyst resume is structurally different from a generic data analyst resume. The hierarchy:

1. **Headline** — same shape as your LinkedIn headline.
2. **Summary** — 3 lines. What you build, what you can do, what you're looking for.
3. **Featured Project** — your repo. Bullet points on stack (BigQuery, dbt, Dagster, Soda, Looker Studio, Amplitude), KPIs analyzed (ARPDAU, LTV, retention cohorts), and **measurable outcomes** ("identified $X opportunity in Y cohort," even on synthetic data). Link the repo and the dashboard.
4. **Analyses** — your three SETUP.md analyses + your five teardowns, with one-line descriptions and links.
5. **Other work** — whatever your prior background is, framed in terms of analytical/engineering rigor.
6. **Skills** — same list as LinkedIn skills.
7. **Education / certifications** — bottom.

### Step D.2: Where to find roles

Monetization JDs cluster on a few sources:

- **Hitmarker** — game industry job board specifically. <https://hitmarker.net>. Usually has the freshest mobile/F2P listings.
- **Work With Indies** — indie + small studio focus. <https://workwithindies.com>.
- **LinkedIn Jobs** — set alerts for "monetization analyst," "game data analyst," "live ops analyst," "user acquisition analyst," "growth analyst gaming."
- **Naavik FractionalTalent** — Naavik places fractional analytics talent. <https://naavik.co>.
- **Eric Seufert's job board** if MDM Pro — paid tier but comprehensive.
- **Direct studio careers pages** for the studios you'd want to work at — King, Supercell, Zynga, Scopely, Wooga, Playrix, Playtika, Activision Blizzard, Riot, EA, Take-Two, Roblox.

### Step D.3: Target list — apply seriously to 10-15 companies

Don't spray. Pick 10-15 studios that match your interest and skill profile. Research each (recent games, monetization model, news from the newsletters above). Tailor the cover letter to *that company* — reference their specific games, their public moves, their recent struggles or successes.

A cover letter that says "I read the recent Naavik piece on your Q3 retention drop and ran a similar analysis on my synthetic data — here's what I'd test first" lands differently than "I'm passionate about games." Massively differently.

### Step D.4: Interview prep

Three categories of question dominate monetization interviews:

1. **Technical**: SQL (window functions, cohort queries, retention math), dbt (models, tests, incremental), basic statistics (sample size for an A/B test, confidence intervals, when to use which test).
2. **Domain**: explain LTV, explain ARPDAU vs ARPPU, what's a healthy D1/D7/D30 for genre X, how would you detect a whale cohort drift, how would you set up a price test.
3. **Case**: "Our DAU dropped 12% week-over-week — what do you investigate?" or "We want to launch a battle pass — what's the test plan?"

Your teardowns prepare you for category 3. Your analyses prepare you for category 2. SQL and dbt practice prepares you for category 1. Allocate a week of focused prep before serious interviews.

---

## Track E — Fallback prep (concurrent throughout, low intensity)

The 20% scenario: gaming roles don't materialize within 6 months, or you decide you'd rather work in an adjacent vertical. The same skill stack redeploys with **almost no rework** — the difference is positioning, not capability.

### Step E.1: The cross-vertical positioning

The strongest fallback angle is **"F2P-trained growth analyst applied to subscription / e-commerce."** Game industry analysts have measurably sharper retention and LTV intuitions than non-game analysts because the data signal is so much faster and stronger. D2C subscription companies (Headspace, Calm, MasterClass, every meal kit, every direct media subscription) pay a premium for someone who can apply F2P patterns to slower-feedback markets.

The move: same portfolio, recast the analyses to mention the cross-vertical applicability. *"This whale-concentration analysis on game data — the same Pareto math applies to top-1% cohort spend in any subscription product."* Same code, different framing.

### Step E.2: Set up freelance profiles (light touch)

Don't spend serious time on these until/unless you decide to actually pursue freelance. But **set them up early** so you're not starting from zero when you need them:

- **Toptal** — applies a screening gate; senior data consultants on Toptal hit $150-200+/hour. Apply once your portfolio is at SETUP.md Phase 6 done. Apply at <https://www.toptal.com/freelance-jobs>.
- **Upwork** — lower bar to entry, more competition. Useful for building review history. Profile setup at <https://www.upwork.com>.
- **Contra** — newer, higher-end, no fees on client side. <https://contra.com>.
- **A.Team** — for embedded fractional engineering / analytics roles. <https://www.a.team>.

A 60-minute investment per platform: profile, skills tags, portfolio links (your public repo), 2-3 paragraphs on what you do. **No pricing yet — that's Step E.4.**

### Step E.3: Define your service offering

If you go freelance, you're not selling "I'm a data analyst." You're selling specific outcomes. Three sharp offerings, each tied to your actual portfolio capability:

1. **"Modern data stack setup"** — fixed-scope: dbt + Dagster + warehouse, with proper docs and tests. 2-4 weeks. $5-15K.
2. **"Cohort & LTV analysis"** — fixed-scope: take their raw transactional data, deliver cohort retention curves, LTV by acquisition channel, payback analysis. 1-2 weeks. $3-8K.
3. **"Monetization audit"** — for D2C subscription / e-commerce companies — apply F2P frameworks to their funnel and propose 3-5 testable hypotheses. 1-2 weeks. $4-10K.

Each one references your repo as proof.

### Step E.4: Pricing

Hourly is a trap. Fixed-scope wins if you can scope tightly. As a starting point with no review history:

- $75-100/hour for hourly work on Upwork (you'll bid against $20/hour competitors but your portfolio justifies the gap).
- $100-150/hour on Toptal (after gate).
- Fixed scopes per Step E.3.

Raise prices every 3-5 successful engagements. The market signal is "did clients accept easily?" — if yes, you're underpriced.

### Step E.5: One cross-vertical analysis per quarter

Even while pursuing the gaming track, write one piece per quarter that explicitly applies F2P frameworks to a non-gaming domain. *"What Headspace's churn curve tells me about their retention strategy."* *"Applying whale-concentration math to Substack creator earnings."* *"Why Duolingo's streak system works — and where it would fail in a fitness app."*

This builds the cross-vertical positioning organically. By month 6, you have public work in both gaming and adjacent verticals. If gaming dries up, you don't pivot — you just emphasize the other half of your existing portfolio.

---

## Cadence summary

| Week | SETUP.md | CAREER.md |
|---|---|---|
| 1 | Phase 0 + Phase 1 | Newsletters subscribed, *Freemium Economics* started |
| 2-3 | Phase 2-3 | LinkedIn optimized, MDM Slack joined, picked 5 games |
| 4-5 | Phase 4-5 | Started teardowns 1-2, first podcast episodes listened |
| 6-8 | Phase 5-6 | Teardowns 3-5, analyses written, first LinkedIn post |
| 9-12 | Phase 6 polish | Resume rewritten, target list built, applications start |
| Ongoing | Maintenance rules | Track E set up minimally, one piece of public writing per month |

By month 3 you have a public portfolio and a public voice. By month 6 you have application traction or you pivot to fallback positioning. This is durable either way.

---

## Final reality check

The 80% goal is real but not guaranteed. Hiring cycles are uneven, and the games industry has been contracting since 2023. The 20% fallback isn't a consolation prize — D2C subscription analytics has been hiring through the contraction, often pays better, and finds F2P-trained analysts unusually valuable. Build for both. Measure success by **public work shipped**, not by **applications sent** — the public work is what compounds.
