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

## Adding content

The decks are plain YAML — add cards / drills / cases / prompts / beats by editing the files in `content/`. Re-running the app picks up changes (Streamlit's `@st.cache_data` decorators clear when files change). For SQL drills, follow the existing schema: `id`, `difficulty`, `prompt`, `hints`, `reference_query`, optional `expected_value` block.

## What this tool does NOT do

- It does **not** drill broader monetization-analyst skills (industry knowledge, generic SQL textbook problems, statistics fundamentals). Scope is purely the repo's content.
- It does **not** simulate the live-interview environment beyond timers and prompts. For SQL drills under live pressure, practice elsewhere (LeetCode SQL, DataLemur, StrataScratch).
- It does **not** auto-grade case-study or STAR answers — those are talked through, not graded by string match. The reveal-model-answer pattern is the right shape for self-assessment.
