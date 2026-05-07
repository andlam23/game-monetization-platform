import os
from pathlib import Path

import sentry_sdk
from dagster import definitions, load_from_defs_folder
from dotenv import find_dotenv, load_dotenv

# Load .env from anywhere up the tree so env vars are available regardless of
# whether dagster dev / dg / pytest is invoked from the repo root or from
# monetization_orchestration/.
load_dotenv(find_dotenv(usecwd=True))

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    traces_sample_rate=0.0,
    send_default_pii=False,
)


@definitions
def defs():
    return load_from_defs_folder(path_within_project=Path(__file__).parent)
