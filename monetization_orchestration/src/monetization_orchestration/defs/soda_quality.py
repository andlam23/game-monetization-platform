"""Soda Core quality checks scheduled from Dagster.

Soda lives in `soda/` at the repo root. This module wires it into the Dagster
daemon as a scheduled job, so the dbt + Soda + Dagster three-layer data-quality
stack from ADR-0005 actually runs without a human hand on a button.

The schedule is daily at 06:00 UTC. In production with live data it'd run
right after the upstream dbt build; for this static-data project the cadence
is symbolic — the checks pass deterministically against the fixed Flood-It
window.
"""

from __future__ import annotations

import logging
from pathlib import Path

from dagster import (
    Definitions,
    ScheduleDefinition,
    asset,
    define_asset_job,
    get_dagster_logger,
)


def _find_repo_root() -> Path:
    """Walk up from this file to find the repo root (where soda/ lives)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "soda" / "configuration.yml").exists():
            return parent
    raise RuntimeError("repo root with soda/configuration.yml not found")


@asset(
    name="soda_quality_scan",
    description=(
        "Runs `soda scan` against the configured BigQuery data source using "
        "soda/configuration.yml + soda/checks.yml at the repo root. Materializes "
        "successfully when all Soda checks pass; fails the asset (and the run) "
        "otherwise. Per ADR-0005, Soda is the cross-source freshness / SLA / "
        "distributional layer above dbt tests."
    ),
    group_name="data_quality",
)
def soda_quality_scan() -> None:
    # Imported lazily so module import doesn't pull soda's full dependency
    # graph before Dagster's loader has finished its own bootstrap.
    from soda.scan import Scan

    log = get_dagster_logger()
    log.setLevel(logging.INFO)

    root = _find_repo_root()
    config_path = root / "soda" / "configuration.yml"
    checks_path = root / "soda" / "checks.yml"

    log.info("running soda scan with config=%s checks=%s", config_path, checks_path)

    scan = Scan()
    scan.set_data_source_name("monetization_warehouse")
    scan.add_configuration_yaml_file(str(config_path))
    scan.add_sodacl_yaml_files(str(checks_path))

    exit_code = scan.execute()
    log_text = scan.get_logs_text()

    if exit_code != 0:
        log.error("soda scan failed (exit_code=%s)\n%s", exit_code, log_text)
        raise RuntimeError(f"soda scan failed (exit_code={exit_code})")

    log.info("soda scan PASSED\n%s", log_text)


soda_quality_job = define_asset_job(
    name="soda_quality_job",
    selection=["soda_quality_scan"],
    description="Run all Soda Core checks from soda/checks.yml against the warehouse.",
)


soda_quality_schedule = ScheduleDefinition(
    name="soda_quality_daily",
    job=soda_quality_job,
    cron_schedule="0 6 * * *",   # daily at 06:00 UTC
    description="Daily run of Soda data-quality checks.",
)


# The new dg-managed scaffold's load_from_defs_folder picks up Definitions()
# objects from any module under defs/. Exporting one keeps the wiring local
# to this file rather than depending on top-level imports.
defs = Definitions(
    assets=[soda_quality_scan],
    jobs=[soda_quality_job],
    schedules=[soda_quality_schedule],
)
