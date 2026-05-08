"""STAR / behavioral drill mode — a behavioral prompt, the ADR or repo
event it maps to, and a structured S/T/A/R skeleton the user fills in
before revealing the reference structure."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import yaml

PROMPTS_PATH = Path(__file__).resolve().parents[1] / "content" / "star_prompts.yaml"


@st.cache_data
def _load_prompts() -> list[dict]:
    with PROMPTS_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def render() -> None:
    st.title("STAR / behavioral")
    st.caption(
        "Behavioral prompts you'll get asked. Each one maps to a real "
        "decision or event in this project — use it as the content of "
        "your STAR (Situation/Task/Action/Result) answer."
    )

    prompts = _load_prompts()
    if not prompts:
        st.error("No STAR prompts found.")
        return

    options = {p["prompt"]: p for p in prompts}
    selection = st.selectbox("Prompt", list(options.keys()), index=0)
    p = options[selection]

    st.markdown(f"### {p['prompt']}")
    st.info(f"**Maps to:** {p['maps_to']}")

    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Your draft (talk through out loud):**")
        for label in ["Situation", "Task", "Action", "Result"]:
            st.text_area(
                label,
                height=110,
                key=f"star_{label}_{p['prompt'][:20]}",
                placeholder=f"{label.lower()}…",
            )

    with cols[1]:
        if st.button("Show reference structure", type="primary", key=f"star_show_{p['prompt'][:20]}"):
            st.markdown("**Reference S/T/A/R:**")
            for label, key in [("Situation", "situation"), ("Task", "task"),
                                ("Action", "action"), ("Result", "result")]:
                if key in p["structure"]:
                    st.markdown(f"**{label}**")
                    st.markdown(p["structure"][key])
        else:
            st.caption(
                "Type your own S/T/A/R first, THEN reveal the reference "
                "to compare structure and specifics. The point is "
                "active recall, not passive review."
            )
