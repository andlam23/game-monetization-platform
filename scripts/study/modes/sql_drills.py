"""SQL drill mode — write SQL, run against the local DuckDB snapshot,
compare against the reference answer, get pass/fail with a diff hint."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st
import yaml

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DRILLS_PATH = Path(__file__).resolve().parents[1] / "content" / "sql_drills.yaml"
DB_PATH = DATA_DIR / "snapshot.duckdb"


@st.cache_data
def _load_drills() -> list[dict]:
    with DRILLS_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def _run_query(sql: str) -> tuple[pd.DataFrame | None, str | None]:
    if not DB_PATH.exists():
        return None, (
            f"DuckDB snapshot not found at {DB_PATH}. "
            f"Build it first: uv run python scripts/study/setup_duckdb.py"
        )
    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)
        df = con.execute(sql).fetchdf()
        con.close()
        return df, None
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def _compare(user_df: pd.DataFrame, ref_df: pd.DataFrame, expected: dict | None) -> tuple[bool, list[str]]:
    """Compare user output to reference. Returns (passed, list-of-issues)."""
    issues: list[str] = []

    if expected:
        if "row_count_exact" in expected and len(user_df) != expected["row_count_exact"]:
            issues.append(
                f"Expected exactly {expected['row_count_exact']} rows; got {len(user_df)}."
            )
        if "row_count_min" in expected and len(user_df) < expected["row_count_min"]:
            issues.append(
                f"Expected at least {expected['row_count_min']} rows; got {len(user_df)}."
            )
        if "row_count_max" in expected and len(user_df) > expected["row_count_max"]:
            issues.append(
                f"Expected at most {expected['row_count_max']} rows; got {len(user_df)}."
            )

        if "column" in expected and "approx" in expected:
            col = expected["column"]
            if col not in user_df.columns:
                issues.append(f"Expected column `{col}` not present in result.")
            elif len(user_df) != 1:
                issues.append(
                    f"Expected single-row result containing `{col}`; got {len(user_df)} rows."
                )
            else:
                actual = float(user_df[col].iloc[0])
                expected_val = float(expected["approx"])
                tol = float(expected.get("tolerance", 0.001))
                if abs(actual - expected_val) > tol:
                    issues.append(
                        f"`{col}` = {actual:.4f}; expected ≈ {expected_val:.4f} "
                        f"(tolerance ±{tol})."
                    )

        if "contains_segments" in expected:
            seg_col = next(
                (c for c in user_df.columns if c.lower() in {"payer_segment", "segment"}),
                None,
            )
            if seg_col is None:
                issues.append(
                    f"Expected a payer_segment column with values "
                    f"{expected['contains_segments']}."
                )
            else:
                got = set(user_df[seg_col].astype(str).tolist())
                missing = set(expected["contains_segments"]) - got
                if missing:
                    issues.append(f"Missing segments in result: {sorted(missing)}.")

    # Schema-level cross-check vs reference: column count match (lenient — names
    # often differ across approaches).
    if not issues and len(user_df.columns) != len(ref_df.columns):
        issues.append(
            f"Column count differs: yours {len(user_df.columns)}, "
            f"reference {len(ref_df.columns)}. Both are valid for many prompts; "
            f"verify your interpretation matches the prompt."
        )

    return (not issues), issues


def render() -> None:
    st.title("SQL drills")
    st.caption(
        "Live SQL practice. Queries run against a local DuckDB snapshot of "
        "the BigQuery marts (mirrors the warehouse's `analytics.*` and `raw.*` tables)."
    )

    drills = _load_drills()
    if not drills:
        st.error("No drills found.")
        return

    if not DB_PATH.exists():
        st.error(
            f"Local DuckDB snapshot missing at `{DB_PATH}`. "
            f"Build it once: `uv run python scripts/study/setup_duckdb.py`"
        )
        return

    options = {f"{d['id']}  ({d['difficulty']})": d for d in drills}
    selection = st.selectbox(
        "Drill",
        list(options.keys()),
        index=0,
        key="sql_drill_select",
    )
    drill = options[selection]

    st.markdown(f"### {drill['id']}")
    st.markdown(drill["prompt"])

    with st.expander("Hints"):
        for h in drill.get("hints", []):
            st.markdown(f"- {h}")

    sql = st.text_area(
        "Your SQL",
        value=st.session_state.get(f"sql_user_{drill['id']}", ""),
        height=240,
        key=f"sql_user_{drill['id']}",
        placeholder="-- write your query here. Tables: analytics.fct_revenue_daily, "
        "analytics.dim_players, analytics.fct_retention_cohorts, "
        "raw.synthetic_ad_events, raw.synthetic_iap_events",
    )

    col_run, col_ref, col_reset = st.columns(3)
    run = col_run.button("Run", type="primary", disabled=not sql.strip())
    show_ref = col_ref.button("Show reference query")
    if col_reset.button("Reset"):
        st.session_state.pop(f"sql_user_{drill['id']}", None)
        st.rerun()

    if run and sql.strip():
        user_df, user_err = _run_query(sql)
        ref_df, ref_err = _run_query(drill["reference_query"])

        if user_err:
            st.error(f"Your query errored: {user_err}")
            return
        if ref_err:
            st.warning(f"Reference query errored on this snapshot: {ref_err}")
            st.dataframe(user_df, use_container_width=True)
            return

        passed, issues = _compare(user_df, ref_df, drill.get("expected_value"))

        if passed:
            st.success("✅ Result matches expected.")
        else:
            st.warning("⚠️ Result differs from expected:")
            for issue in issues:
                st.markdown(f"- {issue}")

        st.markdown("**Your result:**")
        st.dataframe(user_df, use_container_width=True)
        with st.expander("Reference result"):
            st.dataframe(ref_df, use_container_width=True)

    if show_ref:
        st.markdown("**Reference query:**")
        st.code(drill["reference_query"], language="sql")
