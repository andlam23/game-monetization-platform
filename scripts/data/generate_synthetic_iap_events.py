"""Synthetic IAP (in-app purchase) event generator (Step 5.2 / ADR-0013).

Reads unique users from Flood-It, sub-samples a realistic paying-user cohort,
simulates purchase histories with a log-normal LTV distribution that produces
the canonical 80/20 whale concentration, writes Parquet ready for `bq load`
into `raw.synthetic_iap_events`.

Why a synthetic IAP layer in addition to the ad layer:
  Flood-It contains only 17 `in_app_purchase` events across 5 months — far
  too sparse to compute ARPPU, LTV, conversion rate, or whale concentration
  honestly. ADR-0013 amendment captures the discovery and scope change.

Calibration anchors (rough, casual-puzzle genre; cite in any analyst writeup):
  - ~3% paying conversion rate (GameAnalytics State of Mobile benchmarks)
  - Top 10% of payers contribute ~70-80% of total IAP revenue (industry
    consensus across AppLovin, Swrve, GameRefinery whale concentration
    publications)
  - Per-payer LTV distribution: log-normal, mean ~$15, sigma 1.5 → median
    ~$5, P99 ~$300, with a heavy right tail
  - Price ladder skew: $0.99 / $2.99 / $4.99 / $9.99 / $19.99 / $49.99 /
    $99.99 — non-whales cluster on $0.99-$4.99, whales on $19.99+
  - Repeat-purchase decay: whales buy 5-50+ times, casual payers 1-3 times,
    intervals follow a stretched exponential

All numbers are plausible round figures, not authoritative. Real platforms
refresh these monthly. Reproducible: same --seed produces the same output.

Usage:
    uv run python scripts/data/generate_synthetic_iap_events.py \\
        --start 2018-08-01 --end 2018-12-31 \\
        --out data/synthetic_iap_events.parquet \\
        --seed 42
"""

from __future__ import annotations

import argparse
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("synth-iap")

PROJECT = "monetization-warehouse"
FLOODIT_PUBLIC = "firebase-public-project.analytics_153293282.events_*"


# --- calibration ---------------------------------------------------------------

PAYING_CONVERSION_RATE = 0.03   # ~3% of users ever pay (puzzle casual benchmark)

# Per-payer total LTV in USD: log-normal with a heavy enough tail to produce
# the canonical 80/20 whale concentration (top 10% of payers drive 70-80% of
# revenue). With mu = ln(5), sigma = 2.0:
#   median ≈ $5, mean ≈ $37, P90 ≈ $64, P99 ≈ $720.
# Tuned by validating on the actual cohort size — see whale share log line.
LTV_MU = np.log(5.0)
LTV_SIGMA = 2.0

# Whale segmentation is percentile-based on the cohort, NOT a fixed absolute
# threshold. Defensible because industry definitions vary ("top 10% of payers"
# vs. "$100+ lifetime spend"); percentile guarantees the segment label matches
# what an analyst would compute against the actual data.
WHALE_PERCENTILE = 90        # top 10% of payers by LTV
DOLPHIN_PERCENTILE = 60      # next 30%; below 60% = minnow

# Price ladder; non-whales sample lower tiers, whales upper.
PRICE_TIERS = (0.99, 2.99, 4.99, 9.99, 19.99, 49.99, 99.99)
PRICE_PRODUCTS = {
    0.99: ("coins_small", "consumable_currency"),
    2.99: ("coins_medium", "consumable_currency"),
    4.99: ("coins_large", "consumable_currency"),
    9.99: ("coins_xl_pack", "consumable_currency"),
    19.99: ("starter_bundle", "consumable_bundle"),
    49.99: ("mega_pack", "consumable_bundle"),
    99.99: ("ultimate_bundle", "consumable_bundle"),
}

# Per-payer purchase count: roughly correlates with LTV. Casual payers 1-3,
# whales 5-50+. Use ceil(LTV / mean_basket_size) bounded.
MAX_PURCHASES_PER_PAYER = 80
MIN_PURCHASES_PER_PAYER = 1


# --- session input -------------------------------------------------------------

@dataclass(frozen=True)
class UserSpan:
    user_pseudo_id: str
    country: str
    first_us: int
    last_us: int


def fetch_user_spans(client: bigquery.Client, start: str, end: str) -> list[UserSpan]:
    """One row per Flood-It user with their activity window in [start, end]."""
    suffix_start = start.replace("-", "")
    suffix_end = end.replace("-", "")
    query = f"""
    SELECT
      user_pseudo_id,
      ANY_VALUE(geo.country) AS country,
      MIN(event_timestamp) AS first_us,
      MAX(event_timestamp) AS last_us
    FROM `{FLOODIT_PUBLIC}`
    WHERE _TABLE_SUFFIX BETWEEN '{suffix_start}' AND '{suffix_end}'
      AND user_pseudo_id IS NOT NULL
    GROUP BY user_pseudo_id
    HAVING last_us > first_us
    """
    log.info("querying Flood-It for user spans in [%s, %s] …", start, end)
    job = client.query(query)
    rows = list(job.result())
    spans = [
        UserSpan(
            user_pseudo_id=r["user_pseudo_id"],
            country=r["country"] or "ZZ",
            first_us=int(r["first_us"]),
            last_us=int(r["last_us"]),
        )
        for r in rows
    ]
    log.info("got %d distinct users (bytes_billed=%s)", len(spans), job.total_bytes_billed)
    return spans


def synth_session_id(user_pseudo_id: str, event_date: str) -> int:
    """Stable, positive 64-bit session ID matching the ad generator's convention."""
    h = hashlib.sha1(f"{user_pseudo_id}|{event_date}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") & 0x7FFFFFFFFFFFFFFF


# --- simulation ----------------------------------------------------------------

@dataclass
class IapEvent:
    event_timestamp_us: int
    event_date: str
    user_pseudo_id: str
    ga_session_id: int
    event_name: str       # always 'iap_purchase' for v1
    product_id: str
    product_category: str
    price_usd: float
    country: str
    payer_segment: str    # minnow | dolphin | whale (derived from total LTV)


def decompose_ltv_to_purchases(
    rng: np.random.Generator, ltv: float, is_whale: bool
) -> list[float]:
    """Greedy decomposition of total LTV into individual purchase prices.

    Whales prefer larger tiers first; casual payers prefer smaller tiers.
    Stops when remaining < smallest tier or purchase count cap is hit.
    """
    if is_whale:
        order = sorted(PRICE_TIERS, reverse=True)
    else:
        order = sorted(PRICE_TIERS)

    purchases: list[float] = []
    remaining = ltv
    for _ in range(MAX_PURCHASES_PER_PAYER):
        affordable = [p for p in order if p <= remaining + 0.01]
        if not affordable:
            break
        # weight choice: whales lean large, casual lean small. Use first half
        # of `order` 70% of the time, second half 30%.
        first_half = affordable[: max(1, len(affordable) // 2)]
        second_half = affordable[max(1, len(affordable) // 2):]
        if rng.random() < 0.70 and first_half:
            picks = first_half
        else:
            picks = second_half if second_half else first_half
        price = float(rng.choice(picks))
        purchases.append(price)
        remaining -= price
    if not purchases:
        # Ensure at least one purchase for sampled payers
        purchases.append(float(rng.choice([0.99, 2.99])))
    return purchases


def simulate_payer(
    rng: np.random.Generator, span: UserSpan, ltv: float, segment: str
) -> list[IapEvent]:
    is_whale = segment == "whale"
    purchases = decompose_ltv_to_purchases(rng, ltv, is_whale)
    if len(purchases) < MIN_PURCHASES_PER_PAYER:
        return []

    duration_us = max(span.last_us - span.first_us, 1)
    # First purchase concentrated near user start; later purchases stretch out.
    # Use Beta(1.5, 5) to bias offsets toward early in the window.
    raw_offsets = sorted(rng.beta(a=1.5, b=5.0, size=len(purchases)))

    out: list[IapEvent] = []
    for offset_frac, price in zip(raw_offsets, purchases):
        ts_us = span.first_us + int(offset_frac * duration_us)
        date = datetime.fromtimestamp(ts_us / 1_000_000, tz=timezone.utc).strftime("%Y-%m-%d")
        product_id, category = PRICE_PRODUCTS[price]
        out.append(IapEvent(
            event_timestamp_us=ts_us,
            event_date=date,
            user_pseudo_id=span.user_pseudo_id,
            ga_session_id=synth_session_id(span.user_pseudo_id, date),
            event_name="iap_purchase",
            product_id=product_id,
            product_category=category,
            price_usd=price,
            country=span.country,
            payer_segment=segment,
        ))
    return out


# --- output --------------------------------------------------------------------

SCHEMA = pa.schema([
    pa.field("event_timestamp_us", pa.int64()),
    pa.field("event_date", pa.string()),
    pa.field("user_pseudo_id", pa.string()),
    pa.field("ga_session_id", pa.int64()),
    pa.field("event_name", pa.string()),
    pa.field("product_id", pa.string()),
    pa.field("product_category", pa.string()),
    pa.field("price_usd", pa.float64()),
    pa.field("country", pa.string()),
    pa.field("payer_segment", pa.string()),
    pa.field("is_synthetic", pa.bool_()),
])


def write_parquet(events: list[IapEvent], out_path: Path) -> None:
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
        cols["product_id"].append(e.product_id)
        cols["product_category"].append(e.product_category)
        cols["price_usd"].append(e.price_usd)
        cols["country"].append(e.country)
        cols["payer_segment"].append(e.payer_segment)
        cols["is_synthetic"].append(True)
    table = pa.Table.from_pydict(cols, schema=SCHEMA)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, out_path, compression="snappy")
    log.info("wrote %d events to %s (%.2f MiB)",
             len(events), out_path, out_path.stat().st_size / 1024 / 1024)


# --- main ----------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--end", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--out", type=Path, default=Path("data/synthetic_iap_events.parquet"))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--paying-conversion", type=float, default=PAYING_CONVERSION_RATE,
                   help=f"override paying conversion rate (default {PAYING_CONVERSION_RATE})")
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    client = bigquery.Client(project=PROJECT)
    spans = fetch_user_spans(client, args.start, args.end)

    n_payers = max(1, int(len(spans) * args.paying_conversion))
    payer_idx = rng.choice(len(spans), size=n_payers, replace=False)
    payers = [spans[i] for i in payer_idx]
    log.info("sampled %d payers from %d users (rate=%.2f%%)",
             len(payers), len(spans), 100 * len(payers) / max(len(spans), 1))

    # Sample all per-payer LTVs first so percentile-based segmentation matches
    # the actual cohort distribution.
    ltvs = rng.lognormal(mean=LTV_MU, sigma=LTV_SIGMA, size=len(payers))
    whale_cutoff = float(np.percentile(ltvs, WHALE_PERCENTILE))
    dolphin_cutoff = float(np.percentile(ltvs, DOLPHIN_PERCENTILE))
    log.info("LTV cutoffs: whale ≥ $%.2f (P%d), dolphin ≥ $%.2f (P%d)",
             whale_cutoff, WHALE_PERCENTILE, dolphin_cutoff, DOLPHIN_PERCENTILE)

    def classify(ltv: float) -> str:
        if ltv >= whale_cutoff:
            return "whale"
        if ltv >= dolphin_cutoff:
            return "dolphin"
        return "minnow"

    events: list[IapEvent] = []
    for span, ltv in zip(payers, ltvs):
        events.extend(simulate_payer(rng, span, float(ltv), classify(float(ltv))))

    if events:
        total = sum(e.price_usd for e in events)
        whales = sum(1 for e in events if e.payer_segment == "whale")
        whale_revenue = sum(e.price_usd for e in events if e.payer_segment == "whale")
        log.info("simulated %d purchases, total revenue $%.2f, whale share %.1f%%",
                 len(events), total,
                 100 * whale_revenue / total if total else 0.0)

    write_parquet(events, args.out)


if __name__ == "__main__":
    main()
