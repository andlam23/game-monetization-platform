"""Push a sample of events from BigQuery to Amplitude (Step 5.6).

Pulls ~500 events spanning the user funnel — gameplay sessions from real
Flood-It data, ad impressions from raw.synthetic_ad_events, and IAP
purchases from raw.synthetic_iap_events — and POSTs them to Amplitude's
HTTP API v2 batch endpoint. Once ingested, Amplitude's UI lets you
demonstrate funnel views (session_start → level_complete → iap_purchase),
cohort retention, and segment-level analyses against the same metrics
the dbt marts compute.

Sampling strategy: pick N users from Flood-It, then send ALL of their
session_start / level_complete events plus any synthetic ad/IAP events
keyed to them. Multiple events per user is what makes funnels work in
Amplitude (a single event per user can't form a sequence).

Usage:
    uv run python scripts/data/push_events_to_amplitude.py \\
        --user-sample 50 \\
        --max-events 500

Requires AMPLITUDE_API_KEY in .env (Step 4.2).

Reference: https://amplitude.com/docs/apis/analytics/http-v2
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import urllib.request
import urllib.error
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("amp-push")

PROJECT = "monetization-warehouse"
AMPLITUDE_BATCH_URL = "https://api2.amplitude.com/batch"


def fetch_sample_events(client: bigquery.Client, user_sample: int, max_events: int) -> list[dict]:
    """Pull a chronological multi-event-per-user sample for Amplitude.

    Picks `user_sample` Flood-It users, then unions their gameplay events
    (session_start, level_complete) with their synthetic ad-impression and
    IAP-purchase events. Sorted by timestamp; trimmed to `max_events`.
    """
    # Deliberately stratified: half random users (mostly non-payers), half
    # payers (sampled across whale/dolphin/minnow). With pure-random sampling
    # at 3% paying-conversion, 50 users would yield ~1-2 payers — not enough
    # to demonstrate IAP funnels in Amplitude. Stratifying ensures the
    # payload contains conversion behavior.
    n_payers = max(user_sample // 2, 5)
    n_random = user_sample - n_payers
    query = f"""
    WITH sampled_payers AS (
      SELECT user_pseudo_id
      FROM `monetization-warehouse.analytics.dim_players`
      WHERE is_payer
      ORDER BY FARM_FINGERPRINT(user_pseudo_id)
      LIMIT {n_payers}
    ),
    sampled_random AS (
      SELECT user_pseudo_id
      FROM `monetization-warehouse.analytics.dim_players`
      ORDER BY FARM_FINGERPRINT(user_pseudo_id)
      LIMIT {n_random}
    ),
    sampled_users AS (
      SELECT user_pseudo_id FROM sampled_payers
      UNION DISTINCT
      SELECT user_pseudo_id FROM sampled_random
    ),

    gameplay AS (
      SELECT
        user_pseudo_id,
        event_timestamp_us,
        event_name,
        country,
        CAST(NULL AS STRING) AS placement,
        CAST(NULL AS FLOAT64) AS revenue_usd,
        CAST(NULL AS STRING) AS product_id,
        CAST(NULL AS STRING) AS payer_segment
      FROM `monetization-warehouse.analytics.stg_floodit__events`
      WHERE user_pseudo_id IN (SELECT user_pseudo_id FROM sampled_users)
        AND event_name IN ('session_start', 'level_complete', 'level_start',
                           'level_fail', 'first_open')
    ),

    ads AS (
      SELECT
        user_pseudo_id,
        event_timestamp_us,
        event_name,
        country,
        placement,
        revenue_usd,
        CAST(NULL AS STRING) AS product_id,
        CAST(NULL AS STRING) AS payer_segment
      FROM `monetization-warehouse.analytics.stg_synthetic_ads__events`
      WHERE user_pseudo_id IN (SELECT user_pseudo_id FROM sampled_users)
        AND event_name = 'ad_impression'
    ),

    iap AS (
      SELECT
        user_pseudo_id,
        event_timestamp_us,
        'iap_purchase' AS event_name,
        country,
        CAST(NULL AS STRING) AS placement,
        price_usd AS revenue_usd,
        product_id,
        payer_segment
      FROM `monetization-warehouse.analytics.stg_synthetic_iap__events`
      WHERE user_pseudo_id IN (SELECT user_pseudo_id FROM sampled_users)
    )

    SELECT * FROM gameplay
    UNION ALL SELECT * FROM ads
    UNION ALL SELECT * FROM iap
    ORDER BY user_pseudo_id, event_timestamp_us
    LIMIT {max_events}
    """
    log.info("querying BigQuery for %d users, max %d events", user_sample, max_events)
    job = client.query(query)
    rows = list(job.result())
    log.info("pulled %d events (bytes_billed=%s)", len(rows), job.total_bytes_billed)
    return [dict(r) for r in rows]


def to_amplitude_events(rows: list[dict]) -> list[dict]:
    """Map BigQuery rows to Amplitude HTTP API v2 event objects."""
    out: list[dict] = []
    for r in rows:
        event_props: dict = {}
        if r.get("placement") is not None:
            event_props["placement"] = r["placement"]
        if r.get("revenue_usd") is not None:
            event_props["revenue_usd"] = float(r["revenue_usd"])
        if r.get("product_id") is not None:
            event_props["product_id"] = r["product_id"]

        user_props: dict = {}
        if r.get("country"):
            user_props["country"] = r["country"]
        if r.get("payer_segment"):
            user_props["payer_segment"] = r["payer_segment"]

        out.append({
            "user_id": r["user_pseudo_id"],
            "event_type": r["event_name"],
            # Amplitude wants Unix ms; our BQ column is microseconds.
            "time": int(r["event_timestamp_us"]) // 1000,
            "event_properties": event_props,
            "user_properties": user_props,
            # Mark synthetic-supplemented events so a future analyst can
            # filter them out in Amplitude's UI if desired.
            "platform": "iOS",
            "language": "en",
            "insert_id": f"{r['user_pseudo_id']}-{r['event_timestamp_us']}",
        })
    return out


def post_batch(api_key: str, events: list[dict]) -> dict:
    """POST a batch of events to Amplitude. Returns parsed response JSON."""
    payload = json.dumps({"api_key": api_key, "events": events}).encode("utf-8")
    req = urllib.request.Request(
        AMPLITUDE_BATCH_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "*/*"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        return {"status": resp.status, "body": json.loads(body) if body else {}}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--user-sample", type=int, default=50,
                   help="number of Flood-It users to sample (default 50)")
    p.add_argument("--max-events", type=int, default=500,
                   help="hard cap on events sent (default 500)")
    p.add_argument("--dry-run", action="store_true",
                   help="print the payload count, don't POST")
    args = p.parse_args()

    load_dotenv(find_dotenv(usecwd=True))
    api_key = os.environ.get("AMPLITUDE_API_KEY", "")
    if not api_key:
        raise SystemExit("AMPLITUDE_API_KEY not set in .env (see Step 4.2)")

    client = bigquery.Client(project=PROJECT)
    rows = fetch_sample_events(client, args.user_sample, args.max_events)
    if not rows:
        raise SystemExit("no rows returned; check sampled users")

    events = to_amplitude_events(rows)

    # Distribution by event type for log readability
    counts: dict[str, int] = {}
    for e in events:
        counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1
    log.info("payload event-type distribution: %s", counts)

    if args.dry_run:
        log.info("dry-run: would POST %d events to %s", len(events), AMPLITUDE_BATCH_URL)
        return

    try:
        result = post_batch(api_key, events)
    except urllib.error.HTTPError as e:
        log.error("Amplitude POST failed (HTTP %s): %s", e.code, e.read().decode("utf-8", "replace"))
        raise SystemExit(1)

    log.info("Amplitude responded HTTP %s: %s", result["status"], result["body"])
    log.info("done. Open https://app.amplitude.com to inspect.")


if __name__ == "__main__":
    main()
