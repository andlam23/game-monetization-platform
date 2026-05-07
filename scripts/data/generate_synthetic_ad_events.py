"""Synthetic ad-revenue event generator (Step 5.2 / ADR-0013).

Reads Flood-It session boundaries from BigQuery, simulates plausible ad-mediation
events keyed against those sessions, writes Parquet ready for `bq load` into
`raw.synthetic_ad_events`. Every row carries `is_synthetic=True`.

Three event types per ADR-0013:
  - ad_request    — emitted on a per-session cadence
  - ad_impression — only when the request fills (region-aware fill rate)
  - ad_revenue    — derived from impression × eCPM / 1000

Calibration anchors (rough, casual-puzzle genre, late 2024 / early 2025):
  - AppLovin / ironSource / Unity LevelPlay public industry benchmarks for
    rewarded / interstitial / banner eCPM by region tier.
  - GameAnalytics State of Mobile reports for ad-load expectations.
  - Treat all numbers as plausible round figures, not authoritative — the
    point is documented, reproducible synthetic data, not a faithful market
    snapshot. Real platforms refresh these monthly.

Reproducible: same --seed produces the same output.

Usage:
    uv run python scripts/data/generate_synthetic_ad_events.py \\
        --start 2018-08-01 --end 2018-08-07 \\
        --out data/synthetic_ad_events.parquet \\
        --seed 42

Then load to BigQuery (separate step, not run by this script):
    bq --project_id=monetization-warehouse load \\
        --source_format=PARQUET \\
        raw.synthetic_ad_events \\
        data/synthetic_ad_events.parquet
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("synth-ads")

PROJECT = "monetization-warehouse"
FLOODIT_PUBLIC = "firebase-public-project.analytics_153293282.events_*"


# --- calibration ---------------------------------------------------------------

# Region tiers. Flood-It's geo.country is FULL country names (Firebase
# Analytics legacy schema), not ISO codes — match accordingly.
# Tier-1: high-eCPM markets. Tier-2: mid. Tier-3: everything else.
TIER_1 = {
    "United States", "Canada", "United Kingdom", "Australia",
    "Germany", "France", "Japan", "South Korea", "Netherlands",
    "Sweden", "Norway", "Denmark", "Finland", "Switzerland", "Ireland",
}
TIER_2 = {
    "Brazil", "Mexico", "Spain", "Italy", "Poland", "Turkey", "Russia",
    "Argentina", "Chile", "Colombia", "Portugal", "Greece", "Czechia",
    "Czech Republic", "Israel", "Saudi Arabia", "United Arab Emirates",
}

# Mean eCPM USD per 1000 impressions, by (placement, tier). Lognormal-distributed
# at runtime around these means with sigma=0.3 for plausible variance.
ECPM_MEAN = {
    ("rewarded", 1): 18.0,   ("rewarded", 2): 6.0,    ("rewarded", 3): 2.0,
    ("interstitial", 1): 7.5, ("interstitial", 2): 2.2, ("interstitial", 3): 0.9,
    ("banner", 1): 0.5,       ("banner", 2): 0.2,       ("banner", 3): 0.08,
}

# Fill rate by tier — probability an ad_request becomes an ad_impression.
FILL_RATE = {1: 0.97, 2: 0.88, 3: 0.72}

# Placement mix per session — probability of at least one of each.
P_INTERSTITIAL = 0.85   # most sessions get an interstitial after some level
P_REWARDED = 0.22       # ~1 in 5 sessions opt into a rewarded ad
P_BANNER = 0.30         # banners during gameplay; most casual puzzle UI hides them

# Per-session ad-request counts (Poisson lambda). Capped to avoid absurd values.
LAMBDA_INTERSTITIAL = 1.5   # roughly one per 2 levels
LAMBDA_REWARDED = 0.4
LAMBDA_BANNER = 2.0         # banners refresh, so more requests
MAX_REQUESTS_PER_SESSION = 12

AD_NETWORKS = ("applovin", "ironsource", "unity", "google_admob", "meta_audience")


def country_tier(country: str | None) -> int:
    if country is None:
        return 3
    if country in TIER_1:
        return 1
    if country in TIER_2:
        return 2
    return 3


# --- session input -------------------------------------------------------------

@dataclass(frozen=True)
class Session:
    user_pseudo_id: str
    ga_session_id: int
    country: str
    start_us: int
    end_us: int


def fetch_sessions(client: bigquery.Client, start: str, end: str) -> list[Session]:
    """Pull session boundaries from Flood-It for [start, end] inclusive (YYYY-MM-DD).

    Flood-It is pre-GA4 (Firebase Analytics schema circa 2018); event_params does
    not contain `ga_session_id`. We approximate a "session" as one user_pseudo_id
    × one event_date, then synthesize a deterministic 64-bit session ID from
    (user_pseudo_id, event_date) so downstream joins are stable and reproducible.
    For ARPDAU / per-day metrics this is the right grain anyway.
    """
    suffix_start = start.replace("-", "")
    suffix_end = end.replace("-", "")
    query = f"""
    SELECT
      user_pseudo_id,
      PARSE_DATE('%Y%m%d', _TABLE_SUFFIX) AS event_date,
      geo.country AS country,
      MIN(event_timestamp) AS start_us,
      MAX(event_timestamp) AS end_us
    FROM `{FLOODIT_PUBLIC}`
    WHERE _TABLE_SUFFIX BETWEEN '{suffix_start}' AND '{suffix_end}'
      AND user_pseudo_id IS NOT NULL
    GROUP BY user_pseudo_id, event_date, country
    HAVING end_us > start_us
    """
    log.info("querying Flood-It for sessions in [%s, %s] …", start, end)
    job = client.query(query)
    rows = list(job.result())
    sessions = [
        Session(
            user_pseudo_id=r["user_pseudo_id"],
            ga_session_id=_synth_session_id(r["user_pseudo_id"], str(r["event_date"])),
            country=r["country"] or "ZZ",
            start_us=int(r["start_us"]),
            end_us=int(r["end_us"]),
        )
        for r in rows
    ]
    log.info("got %d sessions (bytes_billed=%s)", len(sessions), job.total_bytes_billed)
    return sessions


def _synth_session_id(user_pseudo_id: str, event_date: str) -> int:
    """Stable, positive 64-bit session ID derived from (user, date)."""
    import hashlib
    h = hashlib.sha1(f"{user_pseudo_id}|{event_date}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") & 0x7FFFFFFFFFFFFFFF


# --- simulation ----------------------------------------------------------------

@dataclass
class AdEvent:
    event_timestamp_us: int
    event_date: str
    user_pseudo_id: str
    ga_session_id: int
    event_name: str   # ad_request | ad_impression | ad_revenue
    placement: str    # rewarded | interstitial | banner
    ad_unit: str
    country: str
    ad_network: str | None
    ecpm_usd: float | None
    revenue_usd: float | None


def simulate_session(rng: np.random.Generator, s: Session) -> list[AdEvent]:
    out: list[AdEvent] = []
    tier = country_tier(s.country)
    duration_us = max(s.end_us - s.start_us, 1)

    placements: list[str] = []
    if rng.random() < P_INTERSTITIAL:
        n = min(int(rng.poisson(LAMBDA_INTERSTITIAL)) + 1, MAX_REQUESTS_PER_SESSION)
        placements.extend(["interstitial"] * n)
    if rng.random() < P_REWARDED:
        n = min(int(rng.poisson(LAMBDA_REWARDED)) + 1, 4)
        placements.extend(["rewarded"] * n)
    if rng.random() < P_BANNER:
        n = min(int(rng.poisson(LAMBDA_BANNER)) + 1, MAX_REQUESTS_PER_SESSION)
        placements.extend(["banner"] * n)

    if not placements:
        return out

    # randomly distribute requests within the session window
    offsets = sorted(rng.uniform(0, duration_us, size=len(placements)).astype(np.int64))

    for offset, placement in zip(offsets, placements):
        ts = s.start_us + int(offset)
        date = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc).strftime("%Y-%m-%d")
        ad_unit = f"{placement}_{tier}"

        # ad_request — always emitted
        out.append(AdEvent(
            event_timestamp_us=ts,
            event_date=date,
            user_pseudo_id=s.user_pseudo_id,
            ga_session_id=s.ga_session_id,
            event_name="ad_request",
            placement=placement,
            ad_unit=ad_unit,
            country=s.country,
            ad_network=None,
            ecpm_usd=None,
            revenue_usd=None,
        ))

        # fill?
        if rng.random() >= FILL_RATE[tier]:
            continue

        network = AD_NETWORKS[int(rng.integers(0, len(AD_NETWORKS)))]
        mean = ECPM_MEAN[(placement, tier)]
        ecpm = float(rng.lognormal(mean=np.log(mean), sigma=0.3))
        revenue = ecpm / 1000.0
        impression_ts = ts + int(rng.integers(50_000, 500_000))   # 50-500ms after request
        revenue_ts = impression_ts + int(rng.integers(100_000, 1_000_000))

        out.append(AdEvent(
            event_timestamp_us=impression_ts,
            event_date=date,
            user_pseudo_id=s.user_pseudo_id,
            ga_session_id=s.ga_session_id,
            event_name="ad_impression",
            placement=placement,
            ad_unit=ad_unit,
            country=s.country,
            ad_network=network,
            ecpm_usd=ecpm,
            revenue_usd=None,
        ))
        out.append(AdEvent(
            event_timestamp_us=revenue_ts,
            event_date=date,
            user_pseudo_id=s.user_pseudo_id,
            ga_session_id=s.ga_session_id,
            event_name="ad_revenue",
            placement=placement,
            ad_unit=ad_unit,
            country=s.country,
            ad_network=network,
            ecpm_usd=ecpm,
            revenue_usd=revenue,
        ))

    return out


# --- output --------------------------------------------------------------------

SCHEMA = pa.schema([
    pa.field("event_timestamp_us", pa.int64()),
    pa.field("event_date", pa.string()),
    pa.field("user_pseudo_id", pa.string()),
    pa.field("ga_session_id", pa.int64()),
    pa.field("event_name", pa.string()),
    pa.field("placement", pa.string()),
    pa.field("ad_unit", pa.string()),
    pa.field("country", pa.string()),
    pa.field("ad_network", pa.string()),
    pa.field("ecpm_usd", pa.float64()),
    pa.field("revenue_usd", pa.float64()),
    pa.field("is_synthetic", pa.bool_()),
])


def write_parquet(events: list[AdEvent], out_path: Path) -> None:
    if not events:
        log.warning("no events to write; skipping output")
        return
    cols: dict[str, list] = {f.name: [] for f in SCHEMA}
    for e in events:
        cols["event_timestamp_us"].append(e.event_timestamp_us)
        cols["event_date"].append(e.event_date)
        cols["user_pseudo_id"].append(e.user_pseudo_id)
        cols["ga_session_id"].append(e.ga_session_id)
        cols["event_name"].append(e.event_name)
        cols["placement"].append(e.placement)
        cols["ad_unit"].append(e.ad_unit)
        cols["country"].append(e.country)
        cols["ad_network"].append(e.ad_network)
        cols["ecpm_usd"].append(e.ecpm_usd)
        cols["revenue_usd"].append(e.revenue_usd)
        cols["is_synthetic"].append(True)
    table = pa.Table.from_pydict(cols, schema=SCHEMA)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, out_path, compression="snappy")
    log.info("wrote %d events to %s (%.1f MiB)",
             len(events), out_path, out_path.stat().st_size / 1024 / 1024)


# --- main ----------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--end", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--out", type=Path, default=Path("data/synthetic_ad_events.parquet"))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-sessions", type=int, default=None,
                   help="cap session count for testing (random sample)")
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    client = bigquery.Client(project=PROJECT)
    sessions = fetch_sessions(client, args.start, args.end)

    if args.max_sessions and len(sessions) > args.max_sessions:
        idx = rng.choice(len(sessions), size=args.max_sessions, replace=False)
        sessions = [sessions[i] for i in idx]
        log.info("downsampled to %d sessions", len(sessions))

    events: list[AdEvent] = []
    for s in sessions:
        events.extend(simulate_session(rng, s))
    log.info("simulated %d ad events from %d sessions (%.2f events/session)",
             len(events), len(sessions),
             len(events) / max(len(sessions), 1))

    write_parquet(events, args.out)


if __name__ == "__main__":
    main()
