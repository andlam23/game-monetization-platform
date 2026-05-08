"""Flashcards mode with SM-2-lite spaced repetition.

State persists in scripts/study/data/srs_state.db — one row per card
keyed by stable (deck, prompt) hash. Algorithm:
  - new card: due immediately, ease=2.5, interval_days=1
  - correct: interval *= ease, ease floor 1.3
  - wrong:   interval=1, ease *= 0.85 (floor 1.3)
"""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import streamlit as st
import yaml

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DECK_PATH = Path(__file__).resolve().parents[1] / "content" / "flashcards.yaml"
STATE_DB = DATA_DIR / "srs_state.db"


# ----- persistence ------------------------------------------------------------

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(STATE_DB))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS card_state (
            card_id     TEXT PRIMARY KEY,
            ease        REAL    NOT NULL DEFAULT 2.5,
            interval_d  INTEGER NOT NULL DEFAULT 1,
            due_date    TEXT    NOT NULL,
            seen        INTEGER NOT NULL DEFAULT 0,
            correct     INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    return conn


def _card_id(deck: str, prompt: str) -> str:
    return hashlib.sha1(f"{deck}|{prompt}".encode("utf-8")).hexdigest()[:12]


def _load_state(card_ids: list[str]) -> dict[str, dict]:
    conn = _conn()
    placeholders = ",".join("?" * len(card_ids))
    rows = conn.execute(
        f"SELECT card_id, ease, interval_d, due_date, seen, correct "
        f"FROM card_state WHERE card_id IN ({placeholders})",
        card_ids,
    ).fetchall() if card_ids else []
    by_id = {
        r[0]: {"ease": r[1], "interval_d": r[2], "due_date": r[3], "seen": r[4], "correct": r[5]}
        for r in rows
    }
    conn.close()
    return by_id


def _upsert(card_id: str, *, ease: float, interval_d: int, due_date: str, correct: bool) -> None:
    conn = _conn()
    existing = conn.execute(
        "SELECT seen, correct FROM card_state WHERE card_id = ?", (card_id,)
    ).fetchone()
    seen = (existing[0] if existing else 0) + 1
    correct_count = (existing[1] if existing else 0) + (1 if correct else 0)
    conn.execute(
        """
        INSERT INTO card_state (card_id, ease, interval_d, due_date, seen, correct)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(card_id) DO UPDATE SET
            ease=excluded.ease,
            interval_d=excluded.interval_d,
            due_date=excluded.due_date,
            seen=excluded.seen,
            correct=excluded.correct
        """,
        (card_id, ease, interval_d, due_date, seen, correct_count),
    )
    conn.commit()
    conn.close()


# ----- card loading -----------------------------------------------------------

@st.cache_data
def _load_cards() -> list[dict]:
    with DECK_PATH.open("r", encoding="utf-8") as f:
        cards = yaml.safe_load(f) or []
    for c in cards:
        c["id"] = _card_id(c["deck"], c["prompt"])
    return cards


def _due_cards(cards: list[dict], today: date) -> list[dict]:
    state = _load_state([c["id"] for c in cards])
    due: list[dict] = []
    for c in cards:
        s = state.get(c["id"])
        if s is None:
            due.append({**c, "is_new": True})
        else:
            if date.fromisoformat(s["due_date"]) <= today:
                due.append({**c, "is_new": False, **s})
    # Order: new cards first, then by overdue-ness
    due.sort(
        key=lambda c: (
            0 if c.get("is_new") else 1,
            c.get("due_date", "0000-00-00"),
        )
    )
    return due


# ----- SRS update -------------------------------------------------------------

def _grade(card: dict, *, correct: bool) -> dict:
    ease = float(card.get("ease", 2.5))
    interval_d = int(card.get("interval_d", 1))

    if correct:
        new_interval = max(1, int(round(interval_d * ease)))
        new_ease = ease  # could bump on "easy" but we're 2-state
    else:
        new_interval = 1
        new_ease = max(1.3, ease * 0.85)

    next_due = date.today() + timedelta(days=new_interval)
    return {"ease": new_ease, "interval_d": new_interval, "due_date": next_due.isoformat()}


# ----- render -----------------------------------------------------------------

def render() -> None:
    st.title("Flashcards")
    st.caption(
        "Active-recall drills over the repo's facts. Click *Show answer*, "
        "self-grade, the algorithm schedules the next review."
    )

    cards = _load_cards()
    today = date.today()

    decks = sorted({c["deck"] for c in cards})
    deck_filter = st.multiselect(
        "Decks",
        decks,
        default=decks,
        help="Filter to specific topic decks.",
    )
    filtered = [c for c in cards if c["deck"] in deck_filter]
    due = _due_cards(filtered, today)

    state_all = _load_state([c["id"] for c in filtered])
    seen_count = sum(1 for s in state_all.values() if s["seen"] > 0)
    cols = st.columns(4)
    cols[0].metric("Cards in scope", len(filtered))
    cols[1].metric("Due now", len(due))
    cols[2].metric("Seen ever", seen_count)
    if seen_count:
        avg_acc = sum(s["correct"] for s in state_all.values()) / max(
            sum(s["seen"] for s in state_all.values()), 1
        )
        cols[3].metric("Avg accuracy", f"{avg_acc:.0%}")

    st.markdown("---")

    if not due:
        st.success(
            "Nothing due. ✨ Come back when cards mature, or change deck filter."
        )
        return

    # Pick first-due card; track current ID across reruns.
    current = due[0]
    if "fc_show_answer" not in st.session_state or st.session_state.get("fc_id") != current["id"]:
        st.session_state["fc_id"] = current["id"]
        st.session_state["fc_show_answer"] = False

    st.markdown(f"**Deck:** `{current['deck']}` · **Card** {current['id']}")
    st.markdown(f"### {current['prompt']}")

    if not st.session_state["fc_show_answer"]:
        if st.button("Show answer", type="primary"):
            st.session_state["fc_show_answer"] = True
            st.rerun()
    else:
        st.markdown("**Answer:**")
        st.markdown(current["answer"])
        if "source" in current:
            st.caption(f"Source: `{current['source']}`")

        st.markdown("---")
        col_wrong, col_right = st.columns(2)
        if col_wrong.button("❌ Got it wrong", use_container_width=True):
            grade = _grade(current, correct=False)
            _upsert(current["id"], **grade, correct=False)
            st.session_state["fc_show_answer"] = False
            st.rerun()
        if col_right.button("✅ Got it right", type="primary", use_container_width=True):
            grade = _grade(current, correct=True)
            _upsert(current["id"], **grade, correct=True)
            st.session_state["fc_show_answer"] = False
            st.rerun()
