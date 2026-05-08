# Interview-prep study tool

A Streamlit app that drills the contents of *this* repository — glossary, ADRs, marts, Soda checks, calibration decisions, setup gotchas, the project-walkthrough story — in five active-recall modes.

Built because passive re-reading doesn't internalize content under interview pressure. The 2026 monetization-analyst interview format (researched: 5 stages, live SQL on CoderPad/HackerRank, case-study walkthroughs, behavioral STAR, mostly-no-AI in live rounds at game studios) demands writing SQL yourself, articulating diagnoses out loud, and answering behavioral questions cold. This tool drills exactly those formats against the project's actual artifacts.

## What's inside

| Mode | What it drills | Format |
|------|---------------|--------|
| **Flashcards** | Metric formulas, ADR decisions/alternatives, calibration numbers, stack facts, setup gotchas | SM-2-lite spaced repetition, persisted in SQLite |
| **SQL drills** | ARPDAU, retention, whale share, cohort revenue, fill rate, etc. | Local DuckDB sandbox; runs your query, compares to expected output |
| **Case studies** | Diagnostic ("ARPDAU dropped, diagnose") and design ("price test, sample size") | Free-form draft → reveal model narrative |
| **STAR / behavioral** | Real ADR-mapped behavioral prompts (decisions under uncertainty, course corrections, etc.) | Fill S/T/A/R skeleton → reveal reference structure |
| **Project walkthrough** | 90-second elevator / 5-min dashboard demo / 15-min architecture deep-dive | Live timer + beat checklist for self-grading coverage |

All content lives in editable YAML files under `content/`; expand or refine as gaps surface.

## Setup

```sh
# 1. Build the local DuckDB snapshot from the BigQuery marts (one-time, ~30s).
uv run python scripts/study/setup_duckdb.py

# 2. Launch the app.
uv run streamlit run scripts/study/app.py
```

App opens at `http://localhost:8501`. SRS state, snapshot, and Parquet exports live in `scripts/study/data/` (gitignored).

## Refreshing the snapshot

Re-run `setup_duckdb.py` whenever:
- you regenerate the synthetic ad/IAP layers (changes raw data)
- you change a dbt model (changes the marts)
- you want to confirm SQL drills still pass against the current warehouse

Existing tables in DuckDB are dropped and replaced; SRS state is preserved.

## Recommended workflow

Repetition matters more than session length. The cadence below is calibrated to the 2026 monetization-analyst interview format (live SQL on CoderPad, case-study presentations, behavioral STAR; AI mostly banned in live rounds at game studios — so active recall is the right shape).

### Daily — 10–15 minutes

1. **Flashcards** (5–10 min). Open the app → Flashcards. Whatever's due, drill it. Self-grade honestly: *got it cold and complete* = ✅, *anything missed* = ❌. The SRS algorithm spaces correct answers further out and resurfaces wrong answers tomorrow. Don't peek before grading — the value is in the recall attempt, not the lookup.
2. **One SQL drill** (5 min). Pick one from the dropdown — preferably one you haven't seen. Write the query *cold*, no hints, no peeking at the reference. Run it. If it fails, read the failure message before opening hints. Only reveal the reference query after a serious attempt. Wrong answers teach you more than hint-assisted right ones.

### Weekly — 30–45 minutes

3. **Case studies, talked through out loud** (15–20 min). One or two prompts. Stand up, pace, narrate your hypothesis tree like an interviewer is on the call. Type a draft into the notes box if it helps you structure. Reveal the model narrative *only after* you've spoken your full answer. Compare structure (did you decompose ARPDAU into ad+IAP? did you mention validation before remediation?) — not exact wording.
4. **STAR / behavioral, written before talked** (10–15 min). Pick two prompts. Fill all four S/T/A/R boxes for each. Then say it out loud as if to an interviewer; the written form is a draft, not a script. Reveal the reference structure to compare specifics — *was your "Result" concrete with numbers, or was it vague?*
5. **One project walkthrough timer run** (5–15 min depending on which length you pick). Hit Start. Talk for the full duration without pausing. Tick beats in real time. End-of-run coverage tells you what you forgot.

### Pre-interview cycle (e.g., week of an actual interview)

- **2 days before**: full pass through STAR + project walkthrough. The 5-minute dashboard demo is what you'll likely give in the recruiter screen and the hiring-manager round.
- **1 day before**: SQL drills only. Random selection, all difficulties, cold. Build live-pressure muscle memory.
- **Morning of**: flashcards quick pass on the `numbers` and `metrics` decks (specific values you'll need to cite — $8,716 total revenue, 86% top-1% concentration, 13.4% D1, 68% whale share). Memorizing specific numbers from your own data signals depth fast.

### Maintenance

- **When a flashcard keeps coming up wrong**: that's a real gap. Edit `content/flashcards.yaml` to add a *follow-up* card that probes the gap from a different angle. (E.g., if you keep blanking on whale concentration's *formula*, add a card asking specifically for the SQL.)
- **When a new artifact lands in the repo** (new ADR, new mart, updated SETUP step): update the relevant content YAML in the same commit. Stale content is worse than no content.
- **Rebuild the DuckDB snapshot** after regenerating synthetic data or adding/changing a mart — `uv run python scripts/study/setup_duckdb.py`. SRS state is preserved across rebuilds.

### What to skip

- Don't drill the `setup-discoveries` deck before SQL/metrics decks. The setup gotchas are interview-relevant only if pressed; the metrics and architecture are foundation. Filter the deck multiselect at the top of Flashcards mode.
- Don't try to memorize the model narratives for case studies word-for-word. Memorize the *structure* (validate → decompose → segment → recommend). The interview answer should sound like you, not the YAML.

## Adding content

The decks are plain YAML — add cards / drills / cases / prompts / beats by editing the files in `content/`. Re-running the app picks up changes (Streamlit's `@st.cache_data` decorators clear when files change). For SQL drills, follow the existing schema: `id`, `difficulty`, `prompt`, `hints`, `reference_query`, optional `expected_value` block.

## What this tool does NOT do

- It does **not** drill broader monetization-analyst skills (industry knowledge, generic SQL textbook problems, statistics fundamentals). Scope is purely the repo's content.
- It does **not** simulate the live-interview environment beyond timers and prompts. For SQL drills under live pressure, practice elsewhere (LeetCode SQL, DataLemur, StrataScratch).
- It does **not** auto-grade case-study or STAR answers — those are talked through, not graded by string match. The reveal-model-answer pattern is the right shape for self-assessment.
