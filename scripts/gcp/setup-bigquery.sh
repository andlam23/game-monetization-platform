#!/usr/bin/env bash
# Step 2.1 of docs/SETUP.md: Set up Google Cloud + BigQuery.
# Idempotent — safe to re-run; existing resources are reported and skipped.
#
# Prerequisites (you, the human, must do these first):
#   1. Sign up at https://cloud.google.com if you don't have a Google account.
#   2. Attach a billing account in the GCP console
#      (https://console.cloud.google.com/billing). Free-tier usage stays free
#      but a billing account must exist on your identity to create projects.
#   3. Install gcloud CLI and run: gcloud auth login
#
# Usage:
#   ./scripts/gcp/setup-bigquery.sh                              # uses defaults
#   PROJECT_ID=my-project ./scripts/gcp/setup-bigquery.sh        # override
#   PROJECT_ID=my-project LOCATION=EU ./scripts/gcp/setup-bigquery.sh
#   BILLING_ACCOUNT_ID=01ABCD-... ./scripts/gcp/setup-bigquery.sh # skip prompt
#
# What this does:
#   - Creates the GCP project (skipped if it already exists).
#   - Links a billing account (you'll be prompted to pick one if multiple).
#   - Enables the BigQuery API.
#   - Sets the project as your gcloud default.
#   - Creates two BigQuery datasets: `raw` and `analytics`.
#
# What this does NOT do:
#   - Step 2.2: service account creation. That has its own ADR requirement
#     (ADR-0011) and is in scripts/gcp/setup-service-account.sh.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-monetization-warehouse}"
LOCATION="${LOCATION:-US}"
DATASETS=("raw" "analytics")

# --- preflight ----------------------------------------------------------------

if ! command -v gcloud >/dev/null 2>&1; then
  echo "ERROR: gcloud CLI not found on PATH." >&2
  echo "Install it from https://cloud.google.com/sdk/docs/install, then re-run." >&2
  exit 1
fi

# Windows: bq invokes python and silently falls back to python3.13 if it can't
# find one, which fails on machines without that exact version. Point bq at the
# python that ships with the SDK if CLOUDSDK_PYTHON isn't already set.
if [ -z "${CLOUDSDK_PYTHON:-}" ]; then
  GCLOUD_BIN=$(command -v gcloud)
  GCLOUD_ROOT=$(dirname "$(dirname "$GCLOUD_BIN")")
  BUNDLED_PY="$GCLOUD_ROOT/platform/bundledpython/python.exe"
  if [ -x "$BUNDLED_PY" ]; then
    export CLOUDSDK_PYTHON="$BUNDLED_PY"
  fi
fi

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q .; then
  echo "ERROR: no active gcloud account. Run: gcloud auth login" >&2
  exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo "Active gcloud account: $ACTIVE_ACCOUNT"
echo "Target project ID:     $PROJECT_ID"
echo "Dataset location:      $LOCATION"
echo

# --- project creation ---------------------------------------------------------

if gcloud projects describe "$PROJECT_ID" >/dev/null 2>&1; then
  echo "[skip] Project $PROJECT_ID already exists."
else
  echo "[create] gcloud projects create $PROJECT_ID --name='Monetization Warehouse'"
  gcloud projects create "$PROJECT_ID" --name="Monetization Warehouse"
fi

gcloud config set project "$PROJECT_ID" >/dev/null

# --- billing link -------------------------------------------------------------

CURRENT_BILLING=$(gcloud beta billing projects describe "$PROJECT_ID" --format="value(billingAccountName)" 2>/dev/null || echo "")
if [ -n "$CURRENT_BILLING" ]; then
  echo "[skip] Billing already linked: $CURRENT_BILLING"
else
  if [ -n "${BILLING_ACCOUNT_ID:-}" ]; then
    BILLING_ID="$BILLING_ACCOUNT_ID"
    echo "[billing] Linking pre-supplied account: $BILLING_ID"
  elif [ -t 0 ]; then
    echo "[billing] Available billing accounts:"
    gcloud beta billing accounts list --format="table(name,displayName,open)"
    echo
    echo "Enter the billing account ID to link (the part after 'billingAccounts/'),"
    read -r -p "  or press Enter to skip and link manually in the console: " BILLING_ID
  else
    echo "[warn] No BILLING_ACCOUNT_ID env var set and no TTY for prompting."
    echo "       List accounts with: gcloud beta billing accounts list"
    echo "       Re-run with: BILLING_ACCOUNT_ID=<id> ./scripts/gcp/setup-bigquery.sh"
    BILLING_ID=""
  fi
  if [ -n "$BILLING_ID" ]; then
    gcloud beta billing projects link "$PROJECT_ID" --billing-account="$BILLING_ID"
    echo "[ok] Billing linked."
  else
    echo "[warn] Skipped billing link. Link manually at:"
    echo "       https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
  fi
fi

# --- API enablement -----------------------------------------------------------

if gcloud services list --enabled --project="$PROJECT_ID" --filter="config.name:bigquery.googleapis.com" --format="value(config.name)" 2>/dev/null | grep -q bigquery; then
  echo "[skip] BigQuery API already enabled."
else
  echo "[enable] bigquery.googleapis.com"
  gcloud services enable bigquery.googleapis.com --project="$PROJECT_ID"
fi

# --- datasets -----------------------------------------------------------------

for ds in "${DATASETS[@]}"; do
  if bq --project_id="$PROJECT_ID" show --format=json "$PROJECT_ID:$ds" >/dev/null 2>&1; then
    echo "[skip] Dataset $ds already exists."
  else
    echo "[create] dataset $ds (location=$LOCATION)"
    bq --project_id="$PROJECT_ID" --location="$LOCATION" mk -d "$ds"
  fi
done

echo
echo "Done. Project $PROJECT_ID is configured with BigQuery datasets: ${DATASETS[*]}."
echo "Next: Step 2.2 in docs/SETUP.md (service account + ADR-0011)."
