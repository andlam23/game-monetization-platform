"""Project walkthrough mode — three durations (90s / 5m / 15m) with an
ordered checklist of beats. Start the timer, talk through cold, tick off
the beats you actually hit, see your coverage when time's up."""

from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
import yaml

WALKTHROUGH_PATH = Path(__file__).resolve().parents[1] / "content" / "walkthrough.yaml"


@st.cache_data
def _load() -> list[dict]:
    with WALKTHROUGH_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def render() -> None:
    st.title("Project walkthrough")
    st.caption(
        "Timed practice for 'walk me through your project' at three depths. "
        "Pick a duration, hit Start, talk through cold, tick beats as you "
        "hit them. Coverage shows at the end."
    )

    items = _load()
    if not items:
        st.error("No walkthrough entries found.")
        return

    options = {item["label"]: item for item in items}
    selection = st.selectbox("Duration / use case", list(options.keys()), index=0)
    item = options[selection]
    duration_s = int(item["duration_seconds"])

    st.markdown(f"**Use case:** {item['use_case']}")

    state_key = f"wt_started_{item['label']}"
    start_key = f"wt_start_time_{item['label']}"
    coverage_key = f"wt_cov_{item['label']}"

    if coverage_key not in st.session_state:
        st.session_state[coverage_key] = [False] * len(item["beats"])

    cols = st.columns(2)
    if cols[0].button("Start / restart", type="primary", key=f"wt_start_{item['label']}"):
        st.session_state[state_key] = True
        st.session_state[start_key] = time.time()
        st.session_state[coverage_key] = [False] * len(item["beats"])
        st.rerun()
    if cols[1].button("Reveal beats without timer", key=f"wt_reveal_{item['label']}"):
        st.session_state[state_key] = "reveal"
        st.rerun()

    state = st.session_state.get(state_key)

    if state is True:
        elapsed = time.time() - st.session_state[start_key]
        remaining = max(0, duration_s - int(elapsed))
        mins, secs = divmod(remaining, 60)
        st.metric("Time remaining", f"{mins:02d}:{secs:02d}")

        if remaining > 0:
            st.info(
                "Talk through your project out loud. Tick beats as you hit "
                "them. Beats are NOT a script — they're an interviewer's "
                "checklist of what they want to hear."
            )
        else:
            st.success("⏰ Time's up. Reveal beats below.")

        # Live-ticking via small auto-refresh; only while timer is running
        if remaining > 0:
            time.sleep(1)
            st.rerun()

    if state in (True, "reveal"):
        # Show beats with checkboxes for self-grading
        st.markdown("---")
        st.markdown("**Beats** (tick the ones you actually hit):")
        for i, beat in enumerate(item["beats"]):
            checked = st.checkbox(
                beat,
                value=st.session_state[coverage_key][i],
                key=f"wt_beat_{item['label']}_{i}",
            )
            st.session_state[coverage_key][i] = checked

        hit = sum(st.session_state[coverage_key])
        st.markdown("---")
        st.metric(
            "Coverage",
            f"{hit} / {len(item['beats'])} beats",
            delta=f"{int(100 * hit / len(item['beats']))}%",
        )
    else:
        st.markdown(
            f"**Duration:** {duration_s}s · **Beats:** {len(item['beats'])}"
        )
        st.caption("Hit *Start* to begin a timed run, or *Reveal beats* to study cold.")
