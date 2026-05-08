"""Case-study mode — diagnostic / design prompts. User talks through cold
(into a notes box if they want), then reveals the model answer to compare."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import yaml

CASES_PATH = Path(__file__).resolve().parents[1] / "content" / "case_studies.yaml"


@st.cache_data
def _load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def render() -> None:
    st.title("Case studies")
    st.caption(
        "Diagnostic and design prompts you should be able to talk through "
        "cold. Use the notes box to draft your answer, then reveal the "
        "model answer to compare structure and depth."
    )

    cases = _load_cases()
    if not cases:
        st.error("No case studies found.")
        return

    options = {f"{c['id']}  ({c['category']})": c for c in cases}
    selection = st.selectbox("Case", list(options.keys()), index=0)
    case = options[selection]

    st.markdown(f"### {case['id']}")
    st.markdown(case["prompt"])

    with st.expander("What an interviewer wants to hear (talking points)"):
        for tp in case.get("talking_points", []):
            st.markdown(f"- {tp}")

    st.markdown("**Your draft answer** (talk through out loud as you type):")
    st.text_area(
        "draft",
        height=240,
        key=f"case_draft_{case['id']}",
        label_visibility="collapsed",
        placeholder="Walk through it like you're answering live. Hypothesis → "
        "validate → segment → recommend.",
    )

    cols = st.columns(2)
    show = cols[0].button("Show model answer", type="primary", key=f"case_show_{case['id']}")
    if cols[1].button("Reset draft", key=f"case_reset_{case['id']}"):
        st.session_state.pop(f"case_draft_{case['id']}", None)
        st.rerun()

    if show:
        st.markdown("---")
        st.markdown("**Model narrative:**")
        st.markdown(case["narrative"])
        if "gotcha" in case:
            st.warning(f"**Gotcha to avoid:** {case['gotcha']}")
