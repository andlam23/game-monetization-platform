"""One-time DuckDB sandbox builder for the study tool's SQL drill mode.

Pulls the three BigQuery marts and the two synthetic raw tables down as
Parquet, loads them into a local DuckDB file. Subsequent SQL practice runs
offline against this snapshot — no auth, no quota burn, no network.

Re-run if the warehouse changes (rare; the synthetic data is regenerable
but stable for the same seed).

Usage:
    uv run python scripts/study/setup_duckdb.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("study-setup")

PROJECT = "monetization-warehouse"
TABLES = [
    ("analytics", "fct_revenue_daily"),
    ("analytics", "dim_players"),
    ("analytics", "fct_retention_cohorts"),
    ("raw", "synthetic_ad_events"),
    ("raw", "synthetic_iap_events"),
]

THIS_DIR = Path(__file__).resolve().parent
DATA_DIR = THIS_DIR / "data"
DB_PATH = DATA_DIR / "snapshot.duckdb"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    bq = bigquery.Client(project=PROJECT)

    log.info("connecting to DuckDB at %s", DB_PATH)
    con = duckdb.connect(str(DB_PATH))

    # Mirror the BigQuery dataset structure as DuckDB schemas.
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for dataset, table in TABLES:
        full = f"{PROJECT}.{dataset}.{table}"
        parquet_path = DATA_DIR / f"{dataset}__{table}.parquet"

        log.info("[%s.%s] querying BigQuery …", dataset, table)
        df = bq.query(f"SELECT * FROM `{full}`").to_dataframe()
        df.to_parquet(parquet_path, index=False)
        log.info("[%s.%s] wrote %d rows to %s", dataset, table, len(df), parquet_path.name)

        # Replace any prior snapshot of the same table.
        con.execute(f'DROP TABLE IF EXISTS {dataset}."{table}"')
        con.execute(
            f'CREATE TABLE {dataset}."{table}" AS '
            f"SELECT * FROM read_parquet('{parquet_path.as_posix()}')"
        )

    con.close()
    log.info("done. DuckDB snapshot ready at %s", DB_PATH)


if __name__ == "__main__":
    main()
