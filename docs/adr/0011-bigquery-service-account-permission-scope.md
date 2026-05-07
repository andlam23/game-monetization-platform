# ADR-0011: BigQuery Service Account Permission Scope

**Date**: 2026-05-06
**Status**: accepted

## Context

Step 2.2 of `docs/SETUP.md` requires creating a service account that dbt-bigquery (and later Dagster) use to materialize models in the `monetization-warehouse` GCP project. Service accounts grant non-revocable, key-based access; over-privileged accounts are a real risk if a key leaks. dbt's official BigQuery setup guide lists three project-level roles. The narrowest config dbt actually requires for materialization is `bigquery.dataEditor` + `bigquery.jobUser`, with `bigquery.user` adding broader read and metadata-query coverage that some dbt features and ad-hoc analyst sessions rely on.

This ADR documents the role choice and the boundary it draws — written in the same commit as the service-account creation per CLAUDE.md's decision-time documentation rule.

## Decision

Grant the `dbt-service-account@monetization-warehouse.iam.gserviceaccount.com` service account **three project-level roles** at `monetization-warehouse` scope:

- `roles/bigquery.dataEditor` — create/update/delete tables and views, write data to datasets
- `roles/bigquery.jobUser` — submit query, load, and export jobs
- `roles/bigquery.user` — list datasets, query INFORMATION_SCHEMA, basic metadata reads

Keys are generated as JSON and stored at `~/.gcp/dbt-creds.json` — **outside the repo**. `.gitignore` carries defensive patterns (`**/*-creds.json`, `**/credentials*.json`, `**/service-account*.json`, `.gcp/`) so an accidental copy into the repo is caught locally before it reaches a remote.

The service account has **no other GCP roles** — no Storage, IAM, billing, Compute, or org-level permissions.

## Alternatives

- **Minimum-viable scope (`dataEditor` + `jobUser` only)**: tighter, sufficient for dbt's `run` / `test` / `build` paths. Rejected because dbt's `docs generate`, `compile` against existing schemas, and ad-hoc analyst queries via the same key all benefit from the broader read surface `bigquery.user` provides. The marginal blast radius from adding `user` is small (no write privileges; project-scoped). Acceptable trade-off for a single-developer portfolio project.
- **Dataset-level grants instead of project-level**: GCP allows binding `dataEditor` and `dataViewer` to specific datasets only. This is the strictest option and would limit the service account to `raw` and `analytics` exclusively. Rejected for now because dbt creates intermediate datasets (custom schemas, snapshots, seeds) under naming conventions that would require ongoing role-binding maintenance. Revisit if/when the schema layout stabilizes.
- **`roles/bigquery.admin`**: rejected outright. Includes IAM management, billing, and dataset deletion at the project level. Massively over-scoped for dbt's needs.
- **OAuth user credentials instead of a service account key**: rejected because dbt and Dagster need to run unattended in CI/cron contexts, where browser-based OAuth doesn't work.

## Consequences

- The key at `~/.gcp/dbt-creds.json` is the highest-value secret on the developer machine. If leaked, the attacker can read and write all data in `monetization-warehouse` and run jobs that consume the project's free-tier quota — but cannot escalate to other GCP projects, change billing, or modify IAM.
- Key rotation policy: rotate every 90 days, or immediately if the host machine is compromised. `gcloud iam service-accounts keys create` and `... keys delete` handle this; no code change needed.
- The defensive `.gitignore` patterns are scoped to credential-shaped filenames, so adding legitimate JSON files later (Claude Code project settings, tsconfig if a frontend is added, dbt-generated artifacts) does not require revising this rule.
- If a future component (Dagster sensor, alerting Lambda, etc.) needs broader GCP access, that is a **new** decision and warrants its own ADR rather than expanding this service account.
