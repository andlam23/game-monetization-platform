"""Interview-prep study tool for the game-monetization-platform repo.

Streamlit app with five modes:
  1. Flashcards     — SRS over the repo's facts
  2. SQL drills     — write SQL, run against local DuckDB, compare
  3. Case studies   — diagnostic / design prompts; talk through, reveal model
  4. STAR drills    — behavioral prompts mapped to ADRs; structured reflection
  5. Walkthrough    — timed elevator/dashboard/architecture walkthroughs

Run:
    uv run streamlit run scripts/study/app.py

State (SRS history, last-seen timestamps) persists in
scripts/study/data/srs_state.db so progress survives restarts.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure modes/ is importable when invoked via `streamlit run`.
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import streamlit as st

from modes import case_studies, flashcards, sql_drills, star_behavioral, walkthrough


st.set_page_config(
    page_title="game-monetization-platform — interview prep",
    page_icon="🎮",
    layout="wide",
)

st.sidebar.title("🎮 Interview prep")
st.sidebar.caption("Repo content, drilled.")

mode = st.sidebar.radio(
    "Mode",
    [
        "Flashcards",
        "SQL drills",
        "Case studies",
        "STAR / behavioral",
        "Project walkthrough",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Repo surfaces this drills:** glossary, 13 ADRs, dbt marts, "
    "Soda checks, three written analyses, Dagster wiring, calibration "
    "decisions, setup gotchas, and the project-walkthrough story.\n\n"
    "Built fresh against the warehouse — SQL drills run on a local "
    "DuckDB snapshot of the BigQuery marts (rebuild via "
    "`uv run python scripts/study/setup_duckdb.py`)."
)

if mode == "Flashcards":
    flashcards.render()
elif mode == "SQL drills":
    sql_drills.render()
elif mode == "Case studies":
    case_studies.render()
elif mode == "STAR / behavioral":
    star_behavioral.render()
elif mode == "Project walkthrough":
    walkthrough.render()
