# Game Monetization Stack — Setup Plan

Step-by-step setup for the AI-assisted monetization data platform.
Roughly **5–7 hours total** if nothing goes sideways; budget a full day.

> **Companion files:**
>
> - **`ADRS.md`** — the 10 Architecture Decision Records that capture every choice already made during planning. These get committed to `docs/adr/` in **Phase 0** before any tools are installed.
> - **`CAREER.md`** — parallel track covering industry fluency, critical play, networking, job applications, and fallback positioning. SETUP.md handles the *project*; CAREER.md handles the *job*.

## Stack at a glance

| Layer | Tools |
|---|---|
| AI tooling | Claude Code, gstack, claude-mem, nimrodfisher data-analytics-skills, duckdb-skills, Diataxis skill, custom monetization skill |
| Data engineering | Python (uv), dbt-core, Dagster, Soda Core |
| Cloud + warehouse | Google Cloud Platform, BigQuery (free tier) |
| BI + analytics + observability | Looker Studio, Amplitude, Sentry |
| Documentation | `docs/glossary.md` (canonical metrics), `docs/adr/` (decisions), Diataxis methodology for everything else |

## Order of operations

**Phase 0 is non-negotiable and comes first.** Documentation must exist before the code that depends on it — that's the rule in your CLAUDE.md, and the rest of the system loses authority the moment Phase 0 is skipped. Phases 1–6 follow.

If you get stuck on any individual step, paste the error to Claude Code with `claude doctor` output included and ask. Most setup errors are credentials or PATH issues, not real problems.

---

## Phase 0 — Documentation foundation (~1 hour)

This phase produces nothing executable. It produces the **canonical record** that everything else references.

### Step 0.1: Create the public GitHub repo

Name it something like `game-monetization-platform`. **Public from day one** — this is your portfolio. Add an MIT or Apache 2.0 license. Initial commit: empty `README.md`, `.gitignore` for Python.

### Step 0.2: Set up Python with uv

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
# in your repo:
uv init && uv venv && source .venv/bin/activate
```

uv replaces pip + virtualenv + poetry. Reference: <https://docs.astral.sh/uv/>

### Step 0.3: Create the `docs/` skeleton

```sh
mkdir -p docs/adr
touch docs/glossary.md docs/adr/README.md
```

### Step 0.4: Write the 10 ADRs

Open `ADRS.md` (companion file). Each of the 10 ADRs corresponds to a decision already made during planning. Copy each into a separate file in `docs/adr/`:

- `0001-ai-workflow-framework.md`
- `0002-memory-architecture.md`
- `0003-documentation-authority-precedence.md`
- `0004-confidentiality-and-pii-handling.md`
- `0005-data-quality-tool.md`
- `0006-bi-tool.md`
- `0007-product-analytics-platform.md`
- `0008-orchestration-and-transformation.md`
- `0009-cloud-warehouse.md`
- `0010-documentation-methodology.md`

Build the index at `docs/adr/README.md` as a table:

```markdown
# Architecture Decision Records

| #    | Title                                | Status   | Date       |
|------|--------------------------------------|----------|------------|
| 0001 | AI Workflow Framework                | accepted | 2026-05-06 |
| 0002 | Memory Architecture                  | accepted | 2026-05-06 |
| ...  | ...                                  | ...      | ...        |
```

### Step 0.5: Stub `docs/glossary.md`

Add placeholder entries for the metrics this project will care about — definitions can be `TODO` for now, but the entries exist as soon as you reference the terms:

```markdown
# Metric & Domain Glossary

## ARPDAU
**Definition**: TODO
**Formula**: TODO
**Source of truth**: TODO
**First defined**: TODO

## ARPPU
[same shape]

## LTV
[same shape — note time horizon when defined]

## D1 / D7 / D30 retention
[same shape — note exact cohort definition when defined]

## Conversion rate
[same shape — note "paying / total" or "paying / new"]

## Whale concentration
[same shape]
```

You'll fill these in as Phase 3 and beyond create the SQL that encodes them. **Rule: a metric gets its glossary entry filled in *before* the SQL that materializes it.**

### Step 0.6: Commit `CLAUDE.md`

This is the version reflecting all your decisions through the planning conversation:

````markdown
# Project Context
This project works with video game monetization data — building software (ETL,
analytics, dashboards) around metrics like ARPDAU, ARPPU, LTV, retention cohorts,
conversion funnels, and IAP/ad revenue. Documentation is a first-class deliverable.

## Authority precedence
- `docs/glossary.md` and `docs/adr/` are CANONICAL sources of truth.
- Memory (claude-mem) and skills are SUPPLEMENTARY context.
- If memory or any skill disagrees with the docs, the docs win.
  Flag the discrepancy for review; do not silently follow the supplementary source.

## Documentation responsibilities
[your existing glossary + ADR rules — unchanged]

## Confidentiality and PII
- Never include raw player IDs, device IDs, or email addresses in prompts,
  examples, or sample data. Use synthetic IDs (player_001, device_x) or hashed
  surrogates.
- Real revenue figures stay in the warehouse. When discussing or documenting
  amounts, use rounded/relative values ($X, "low five-figures") unless absolutely
  necessary.
- Tag sensitive content with <private>...</private> blocks. claude-mem honors
  these and excludes them from storage.

## Memory discipline
- claude-mem captures raw cross-session context automatically.
- Use /learn ONLY for explicit "remember this rule" moments (durable preferences,
  hard-won lessons). Don't use /learn for things claude-mem already covers.

## Documentation methodology
For docs OTHER than glossary and ADRs (READMEs, runbooks, tutorials, explanations),
the writing-documentation-with-diataxis skill provides the methodology.
For glossary entries and ADR records, the fixed templates in this CLAUDE.md
override Diataxis's "structure follows content" guidance — those templates are
mandatory.

## Decision-time documentation rule
When a choice is made that constrains future work (warehouse, library, schema,
attribution model, etc.), an ADR is written in the SAME COMMIT as the change it
documents. Retroactive ADRs are not acceptable; if a decision happens in
conversation with no ADR, ask before moving on.
````

Commit. **At this point your repo has no executable code, but it has a complete record of every architectural decision and a placeholder for every metric you'll measure. That's the correct foundation.**

---

## Phase 1 — AI tooling (~1 hour)

### Step 1.1: Install Claude Code

Use the **native installer**, not npm — npm install is now deprecated.

- macOS / Linux: `curl -fsSL https://claude.ai/install.sh | bash`
- Windows PowerShell: `irm https://claude.ai/install.ps1 | iex`

After install, run `claude doctor` to verify, then `claude` to authenticate. You need a Claude Pro/Max/Team/Enterprise account.

- Official: <https://docs.claude.com/en/docs/claude-code/setup>
- May 2026 walkthrough: <https://findskill.ai/blog/install-claude-code-setup-guide/> — flags a known token-inflation regression in v2.1.100+; pin with `curl -fsSL https://claude.ai/install.sh | bash -s 2.1.34` if you hit limit issues.

### Step 1.2: Install gstack (full)

**Prerequisite: bun.** gstack's `./setup` script compiles its browser binary with [bun](https://bun.sh) and exits if `bun` isn't on PATH. Install it with the gstack-recommended verified flow:

```sh
BUN_VERSION="1.3.10"
tmpfile=$(mktemp)
curl -fsSL "https://bun.sh/install" -o "$tmpfile"
# verify checksum before running:
shasum -a 256 "$tmpfile"
BUN_VERSION="$BUN_VERSION" bash "$tmpfile" && rm "$tmpfile"
```

bun installs to `~/.bun/bin`. On Windows, also add `C:\Users\<you>\.bun\bin` to your User `PATH` so it survives shell restarts (PowerShell):

```powershell
[Environment]::SetEnvironmentVariable('Path', "$([Environment]::GetEnvironmentVariable('Path','User'));C:\Users\<you>\.bun\bin", 'User')
```

Verify with `bun --version`. Note the installer ignores `BUN_VERSION` in current builds and pulls the latest stable — fine for setup; pin via the GitHub releases page if you need a specific version.

**Then install gstack:**

```sh
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack \
  && cd ~/.claude/skills/gstack \
  && ./setup
```

The setup script auto-detects your agent hosts (Claude Code, Codex, Factory, OpenCode), compiles the `browse` binary, and registers ~45 skills. Repo: <https://github.com/garrytan/gstack>

### Step 1.3: Install claude-mem

```sh
npx claude-mem install
```

After installing, **start the worker** (autostart is skipped when the install runs from a non-TTY context like a Claude Code subshell):

```sh
npx claude-mem start
```

Verify it's running by checking <http://localhost:37777>. Repo: <https://github.com/thedotmack/claude-mem>

**If `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` is set in `~/.claude/settings.json` env block, remove it** — otherwise the plugin's hooks stay dormant and no observations get captured.

**Windows-only workaround for the in-session search MCP**: claude-mem's plugin manifest spawns its mcp-search server via `sh -c '... node "$CLAUDE_PLUGIN_ROOT/scripts/mcp-server.cjs"'`. On Windows, Claude Code doesn't set `CLAUDE_PLUGIN_ROOT` (or `PLUGIN_ROOT`) when spawning plugin MCPs, so Git Bash mangles the unset path to `C:\Program Files\Git\scripts\mcp-server.cjs` and the server fails with `MODULE_NOT_FOUND`. Fix by patching the cached `.mcp.json` to use a direct absolute path:

```
C:\Users\<you>\.claude\plugins\cache\thedotmack\claude-mem\<VERSION>\.mcp.json
```

Replace its `mcpServers.mcp-search` entry with:

```json
{
  "type": "stdio",
  "command": "node",
  "args": ["C:\\Users\\<you>\\.claude\\plugins\\cache\\thedotmack\\claude-mem\\<VERSION>\\scripts\\mcp-server.cjs"]
}
```

The auto-memory pipeline (hooks → worker → DB → Chroma) does **not** depend on this MCP and works without it; only the in-session `mem-search` skill breaks. **Reapply this patch after every claude-mem upgrade** (the path includes the version number). Upstream bug worth filing against `thedotmack/claude-mem`.

### Step 1.4: Install nimrodfisher data-analytics-skills

```sh
git clone https://github.com/nimrodfisher/data-analytics-skills.git \
  ~/.claude/skills/data-analytics-skills
```

Repo: <https://github.com/nimrodfisher/data-analytics-skills>

### Step 1.5: Install duckdb-skills

From inside Claude Code:

```
/plugin marketplace add duckdb/duckdb-skills
/plugin install duckdb-skills
```

Or clone manually: <https://github.com/duckdb/duckdb-skills>

### Step 1.6: Install the Diataxis skill

Easiest path — paste this to Claude Code:

> Please install the writing-documentation-with-diataxis skill from <https://github.com/sammcj/agentic-coding/archive/main.zip> — extract the diataxis-documentation folder and place it in `~/.claude/skills/`.

Reference: <https://skills.rest/skill/writing-documentation-with-diataxis>

### Step 1.7: Stub the monetization skill

Write a stub at `~/.claude/skills/monetization/SKILL.md` with just frontmatter. Fill it in when you actually need a metric defined. **Premature definition is the same trap as premature optimization.**

---

## Phase 2 — Cloud warehouse (~45 minutes)

### Step 2.1: Set up Google Cloud + BigQuery

Sign up at <https://cloud.google.com> — $300 in credits and a generous always-free tier (10 GB storage, 1 TB queries/month).

- Create project: `monetization-warehouse`
- Enable the BigQuery API
- Free tier is enforced by quota, not billing

### Step 2.2: Create a BigQuery service account

You can use the GCP console (**IAM & Admin → Service Accounts → Create**) or the gcloud CLI. With `gcloud auth login` already done from Step 2.1, the CLI is one-shot:

```sh
PROJECT_ID=monetization-warehouse
SA_EMAIL="dbt-service-account@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create dbt-service-account \
  --display-name="dbt service account" \
  --description="Used by dbt-bigquery to materialize models" \
  --project="$PROJECT_ID"

for role in roles/bigquery.dataEditor roles/bigquery.jobUser roles/bigquery.user; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" --role="$role" --condition=None --quiet
done

mkdir -p ~/.gcp
gcloud iam service-accounts keys create ~/.gcp/dbt-creds.json \
  --iam-account="$SA_EMAIL" --project="$PROJECT_ID"
```

The three roles match dbt's official BigQuery setup guide: <https://docs.getdbt.com/guides/bigquery>.

**`.gitignore` patterns** (defensive — the real key lives outside the repo):

```gitignore
# GCP / service account credentials
**/*-creds.json
**/credentials*.json
**/service-account*.json
.gcp/
```

> **Why not blanket `*.json`?** A blanket rule would also block legitimate JSON config the project will eventually want to track (Claude Code project settings, dbt-generated artifacts, tsconfig if a frontend is added). Targeted credential-shaped patterns satisfy the leak-prevention intent without that collateral. ADR-0011 has the full reasoning.

> **📝 Decision-time doc:** Step 2.2 establishes your service-account permission model. Write **ADR-0011** — *"BigQuery service account permission scope"* — in the same commit, with what you granted and your least-privilege rationale.

### Step 2.3: Create initial datasets in BigQuery

Two datasets:

- `raw` — landing data
- `analytics` — dbt outputs

Both are created by `scripts/gcp/setup-bigquery.sh` from Step 2.1; this step is already done if you ran that script. Verify with:

```sh
bq --project_id=monetization-warehouse ls
```

To create manually instead:

```sh
bq --project_id=monetization-warehouse --location=US mk -d raw
bq --project_id=monetization-warehouse --location=US mk -d analytics
```

---

## Phase 3 — Data engineering stack (~90 minutes)

> **Fresh-clone shortcut.** Every Python dependency in this phase is declared in the root `pyproject.toml` (`dbt-bigquery`, `soda-core-bigquery`, `google-cloud-bigquery-storage`) plus the editable path dependency on `monetization_orchestration/`, which transitively pulls in `dagster`, `dagster-dbt`, `dagster-gcp`, `dagster-gcp-pandas`, `dagster-webserver`, and `dagster-dg-cli`. From a fresh clone:
>
> ```sh
> uv sync
> ```
>
> The per-step `uv pip install ...` commands below still work — they're left in place to make each tool's purpose explicit. After running them ad-hoc, run `uv sync` once at the end to reconcile the lockfile.

### Step 3.1: Install dbt-core with BigQuery adapter

```sh
uv pip install dbt-bigquery
dbt --version
dbt init monetization_warehouse
```

When prompted: adapter `bigquery`, auth `service_account_file`, key path your JSON, project ID your GCP project, dataset `analytics`, location `US`.

Walkthrough: <https://oneuptime.com/blog/post/2026-02-17-how-to-set-up-a-dbt-project-with-bigquery-as-the-data-warehouse-backend/view>

### Step 3.2: Verify dbt connects

```sh
dbt debug
```

### Step 3.3: Install Dagster

```sh
uv pip install dagster dagster-webserver dagster-dbt dagster-gcp dagster-gcp-pandas
uvx create-dagster project monetization_orchestration
```

`dagster project scaffold` still works in 1.13.x but prints a `SupersessionWarning` — the new official scaffold is `create-dagster project`, distributed as a separate package. `uvx` runs it as a one-shot without polluting the venv.

### Step 3.4: Wire Dagster to dbt

Use the `DbtProjectComponent` pattern with the new dg-managed scaffold from Step 3.3. From inside `monetization_orchestration/`:

```sh
dg scaffold defs dagster_dbt.DbtProjectComponent monetization_warehouse \
  --project-path ../monetization_warehouse
```

That writes `src/monetization_orchestration/defs/monetization_warehouse/defs.yaml`. The default scaffold needs two adjustments before it loads:

1. The default `project` value points at the dbt project but doesn't override `profiles_dir`, so Dagster looks for `profiles.yml` inside the dbt project rather than `~/.dbt`.
2. On Windows, the scaffolder writes a backslash in the path (`/..\monetization_warehouse`) — replace with forward slashes for portability.

Working YAML:

```yaml
type: dagster_dbt.DbtProjectComponent

attributes:
  project:
    project_dir: '{{ project_root }}/../monetization_warehouse'
    profiles_dir: '{{ env("USERPROFILE") }}/.dbt'   # use $HOME on macOS/Linux
```

Add `dagster-dbt` (and any other `dagster-*` integrations) to `monetization_orchestration/pyproject.toml` `[project] dependencies` — `create-dagster project` only declares `dagster` itself.

Install the project in editable mode so its package is importable from the venv (the new src-layout scaffold won't load without this — `dagster dev` fails with `ModuleNotFoundError: No module named 'monetization_orchestration'`). If you used the Phase 3 `uv sync` shortcut, this is already done via the path-source declaration in the root `pyproject.toml`. Otherwise:

```sh
uv pip install -e ./monetization_orchestration
```

Note also: `create-dagster project` puts `dagster-webserver` and `dagster-dg-cli` in `[dependency-groups] dev` by default. Both are runtime requirements for `dagster dev` and `dg check defs`, so promote them to main `[project] dependencies` in `monetization_orchestration/pyproject.toml`.

Validate the wiring without launching the UI:

```sh
# venv must be active so dg can find the dbt CLI
dg check defs
```

Expected output: `All component YAML validated successfully. All definitions loaded successfully.`

Then `dagster dev` to launch the UI at <http://localhost:3000>. The dbt models appear as Dagster assets in the asset graph.

> **PATH gotcha**: `DbtProjectComponent` shells out to `dbt`, which only resolves if the venv is activated (so `.venv/Scripts/` or `.venv/bin/` is on PATH). `dg check defs` and `dagster dev` both fail otherwise. There's no `dbt_executable` field on the component schema as of `dagster-dbt` 1.13.x.

Reference: <https://docs.dagster.io/api/libraries/dagster-dbt>
End-to-end tutorial (older `@dbt_assets` pattern, but the BigQuery wiring is still useful): <https://airbyte.com/tutorials/weather-data-stack-with-dbt-dagster-and-bigquery> (ignore the Airbyte parts).

### Step 3.5: Install Soda Core

```sh
uv pip install soda-core-bigquery google-cloud-bigquery-storage
```

`google-cloud-bigquery-storage` isn't strictly required, but installing it (a) silences a "Cannot create BigQuery Storage client" warning Soda prints, and (b) gives a faster read path to any consumer that pulls result sets back to Python (Soda distributional checks, Dagster sensors materializing into pandas, ad-hoc analyst notebooks). Free under the BigQuery tier — billing is per bytes processed by the query, which is unchanged.

Create `soda/configuration.yml` (data source pointing at BigQuery, reusing the dbt service account key) and `soda/checks.yml` (intentionally empty for now — don't define checks for tables that don't exist yet). Per ADR-0005, Soda is the "cross-source freshness, SLA contracts, distributional assertions" layer; structural checks belong in dbt tests, anomaly detection in Dagster sensors.

Verify the connection:

```sh
soda test-connection -d monetization_warehouse -c soda/configuration.yml
```

Reference: <https://docs.soda.io/soda-core/overview-main.html>

> **📝 Decision-time doc:** After Phase 3 completes, write **ADR-0012** — *"dbt project structure: staging / intermediate / marts"* — capturing your folder layout and naming conventions. This constrains every future model.

---

## Phase 4 — BI, analytics, observability (~45 minutes)

### Step 4.1: Connect Looker Studio to BigQuery

- Go to <https://lookerstudio.google.com>
- **Create → Data source → BigQuery connector**
- Authorize with your GCP-owning Google account
- Pick your `analytics` dataset

Don't build a dashboard yet. Just confirm the connection.

Setup guide: <https://oneuptime.com/blog/post/2026-02-17-connect-looker-studio-bigquery-self-service-dashboards/view>

### Step 4.2: Set up Amplitude

- Sign up free at <https://amplitude.com> — Spark plan
- Create a new project
- Save the API key

Quickstart: <https://amplitude.com/docs/get-started>

### Step 4.3: Set up Sentry

- Free tier at <https://sentry.io>
- Create a Python project, copy the DSN
- Wire into Dagster via `sentry_sdk.init(dsn=...)`

Reference: <https://docs.sentry.io/platforms/python/>

---

## Phase 5 — Get data flowing (1–2 hours)

### Step 5.1: Acquire data

**Decision** (per ADR-0013): hybrid — Flood-It as the real-data backbone, synthetic ad-revenue layer for the dimension public data doesn't cover.

**Real backbone — GA4 Flood-It! sample.** Real F2P puzzle game events. 114 daily-sharded tables, of which the populated portion is **2018-08-01 → 2018-10-03** (~64 days, ~3.2M events; the later tables exist but are empty). Public in BigQuery at `firebase-public-project.analytics_153293282.events_*`. CC-BY 4.0. Read in place via a dbt source declaration — *not* copied into our `raw` dataset:

```yaml
# monetization_warehouse/models/staging/floodit/_floodit__sources.yml
sources:
  - name: floodit
    database: firebase-public-project
    schema: analytics_153293282
    tables:
      - { name: events, identifier: 'events_*' }
```

Verify access:

```sh
bq --project_id=monetization-warehouse query --nouse_legacy_sql \
  'SELECT event_name, COUNT(*) AS n
   FROM `firebase-public-project.analytics_153293282.events_20180801`
   GROUP BY event_name ORDER BY n DESC LIMIT 5'
```

**Synthetic ad-revenue layer.** Public ad-revenue datasets at row-level don't exist (verified by exhaustive search). A Python generator produces `ad_impression` / `ad_request` / `ad_revenue` events keyed against Flood-It's `user_pseudo_id` space, calibrated to published industry benchmarks (eCPM, fill rate, request frequency). Write Parquet → load to `raw.synthetic_ad_events`. Every synthetic row carries `is_synthetic = TRUE`; tables are prefixed `synthetic_` so the boundary is visible everywhere.

Why this hybrid and not pure-real or pure-synthetic: see ADR-0013. Recruiter scan wants "real F2P data" as a binary signal (Flood-It satisfies it); interviewer evaluates analytical depth (synthetic ad layer enables ad-mediation analytics that Flood-It can't); diminishing returns kicks in fast past one strong real source.

> **📝 Decision-time doc:** ADR-0013 lands in the same commit as the dbt source declaration above. Lists the search results, alternatives considered, and why Flood-It + synthetic ad layer beat the alternatives (Universalis FFXIV, Uken 2015, multi-real, pure synthetic).

### Step 5.2: Build the synthetic data generators (ad + IAP)

Per ADR-0013, two synthetic layers are needed because Flood-It alone provides neither ad-revenue events at row level (don't exist publicly) nor enough IAP events to be analytically useful (only 17 across the populated 64-day window — discovered when starting Step 5.3). Both layers follow the same pattern: Python generator → Parquet → `bq load` to `raw.synthetic_*_events`.

**Ad-revenue generator** at `scripts/data/generate_synthetic_ad_events.py`:

**Where it lives**: `scripts/data/generate_synthetic_ad_events.py`. CLI-driven (`uv run python scripts/data/generate_synthetic_ad_events.py --start 2018-08-01 --end 2018-10-03 --out data/synthetic_ad_events.parquet`). The end date matches Flood-It's actual last populated day; passing a later date works but scans empty tables.

**What it generates** — three event types, one row per event:

- `ad_request` — emitted on a per-session cadence. Fields: `event_timestamp`, `user_pseudo_id`, `ga_session_id`, `ad_unit`, `placement` (interstitial / rewarded / banner), `country`.
- `ad_impression` — emitted only when the ad request fills, governed by region- and placement-aware fill rates. Same key fields plus `ad_network`, `eCPM_usd`.
- `ad_revenue` — derived from impression × eCPM / 1000. Same key fields plus `revenue_usd`.

> **Flood-It schema quirk**: Flood-It is pre-GA4 (Firebase Analytics, 2018) — `event_params` does not contain `ga_session_id`. The generator approximates a session as one `user_pseudo_id` × one `event_date`, then synthesizes a deterministic 64-bit session ID from `(user_pseudo_id, event_date)` so downstream joins are stable. For ARPDAU and per-day metrics the user-day grain is the right one anyway.

Every row carries `is_synthetic = TRUE`. Tables are prefixed `synthetic_` so the boundary is visible in any downstream `ref()`.

**Calibration parameters** — cite the source in the script's docstring:

- eCPM by region & placement (rewarded > interstitial > banner; US > EU > APAC > LATAM)
- Fill rate by region (~95-99% in tier-1, lower in tier-3)
- Ad-request frequency per session minute (capped to feel realistic)
- Casual-puzzle-genre ad load expectations (1 interstitial per ~2 levels; 1 rewarded per session if offered)

Use **AppLovin / ironSource / Unity LevelPlay public industry reports** as the calibration anchor. Pin the report year and link in the docstring so an interviewer asking "where did your fill-rate come from?" gets a real answer.

**Loading to BigQuery**:

```sh
bq --project_id=monetization-warehouse load \
  --source_format=PARQUET \
  raw.synthetic_ad_events \
  data/synthetic_ad_events.parquet
```

The output Parquet file should be gitignored (it's generated, not source). The generator script is the source of truth.

**Dagster integration** (Phase 5.4 / 5.5 work, mentioned here for context): wrap the generator as a Dagster asset so it shows up in the asset graph alongside the dbt-Flood-It assets. Asset dependency: synthetic ad events declare `user_pseudo_id` keys that come from Flood-It events, so in Dagster the synthetic asset depends on at least one Flood-It-derived staging asset.

**IAP generator** at `scripts/data/generate_synthetic_iap_events.py` (added after Step 5.3 surfaced that Flood-It has only 17 real `in_app_purchase` events — see ADR-0013 amendment):

Sub-samples ~3% of Flood-It users as payers (calibrated against the GameAnalytics State of Mobile casual-puzzle benchmark). Draws per-payer total LTV from a log-normal distribution (μ = ln 5, σ = 2.0) tuned to produce 60-85% whale-revenue concentration on the actual cohort size. Greedy-decomposes each payer's LTV into individual purchases at realistic price tiers ($0.99 / $2.99 / $4.99 / $9.99 / $19.99 / $49.99 / $99.99); whales lean upper tiers, casual payers lean lower. First-purchase timestamps are concentrated near user start via a Beta(1.5, 5) bias.

**Payer segmentation is percentile-based** on the actual cohort, not a fixed dollar threshold:

- `whale` — top 10% by lifetime spend
- `dolphin` — next 30%
- `minnow` — bottom 60%

This is defensible because industry definitions vary ("$100+ lifetime spend" vs. "top 10% of payers"); percentile guarantees the segment label matches what an analyst would compute against the actual data.

Schema fields: `event_timestamp_us`, `event_date`, `user_pseudo_id`, `ga_session_id`, `event_name='iap_purchase'`, `product_id`, `product_category`, `price_usd`, `country`, `payer_segment`, `is_synthetic=TRUE`.

Generate + load:

```sh
uv run python scripts/data/generate_synthetic_iap_events.py \
  --start 2018-08-01 --end 2018-10-03 --seed 42 \
  --out data/synthetic_iap_events.parquet

bq --project_id=monetization-warehouse load \
  --source_format=PARQUET --replace \
  raw.synthetic_iap_events \
  data/synthetic_iap_events.parquet
```

Sanity-check the loaded data should show whale-revenue concentration in the 60-80% range; the verification query in Step 5.3 will catch this.

### Step 5.3: Build the dbt model layer

**Project-level config first.** Configure per-layer materialization in `monetization_warehouse/dbt_project.yml` per ADR-0012, and delete the default `models/example/` folder that `dbt init` scaffolded:

```yaml
models:
  monetization_warehouse:
    staging:      { +materialized: view }
    intermediate: { +materialized: view }
    marts:        { +materialized: table }
```

```sh
rm -rf monetization_warehouse/models/example
```

**Source declarations.** One YAML per source under `models/staging/<source>/`:

- `staging/floodit/_floodit__sources.yml` (already added in Step 5.1)
- `staging/synthetic_ads/_synthetic_ads__sources.yml`
- `staging/synthetic_iap/_synthetic_iap__sources.yml`

**Staging models — one per source per ADR-0012.** 1:1 source mirrors with light cleaning (column renames, type casts, `event_params` extraction); no business logic.

- `stg_floodit__events.sql` — staging from `firebase-public-project.analytics_153293282.events_*`. Filters on `_TABLE_SUFFIX` to avoid scanning the full 114-day history.
- `stg_synthetic_ads__events.sql` — staging from `raw.synthetic_ad_events`.
- `stg_synthetic_iap__events.sql` — staging from `raw.synthetic_iap_events`.

**Marts.** Three tables consumed by the dashboard and downstream analyses.

- `marts/finance/fct_revenue_daily.sql` — grain `(event_date, user_pseudo_id)`. Combines Flood-It activity (gameplay → DAU) with synthetic ad revenue and synthetic IAP revenue. UNIONs user-keys across the three sources so a row exists for any user-day with *any* signal. Day-partitioned, clustered on `user_pseudo_id`. Source of truth for **ARPDAU**.
- `marts/product/dim_players.sql` — grain `user_pseudo_id` (unique). Lifetime stats: LTV, total IAP revenue, total ad revenue, first/last seen, days active, payer segment (whale/dolphin/minnow/non_payer). Source of truth for **ARPPU**, **LTV**, **conversion rate**, **whale concentration**.
- `marts/product/fct_retention_cohorts.sql` — grain `(cohort_date, day_offset)`. Pre-aggregated cohort retention curve at offsets 0..30. Right-censored: rows where `cohort_date + day_offset` exceeds the latest available date are omitted. Source of truth for **D1 / D7 / D30 retention**.

**Build and test:**

```sh
cd monetization_warehouse
dbt build
```

Expected: 3 staging views + 3 mart tables, all PASS. Then per-mart tests in `_<domain>__models.yml` files (uniqueness on `dim_players.user_pseudo_id`, `accepted_values` on `payer_segment`, `not_null` across key columns).

> **📝 Glossary discipline:** For every metric encoded in `fct_*` and `dim_*`, **fill in the corresponding glossary entry** before the model's SQL is committed. ARPDAU, ARPPU, LTV, D1/D7/D30 retention, conversion rate, whale concentration — six entries, all live in `docs/glossary.md`. Glossary entry and SQL ship in the same commit.

> **⚠️ IAP gap warning.** When you query Flood-It's `event_name` distribution while building staging models, you'll find only 17 `in_app_purchase` events across 5 months — too sparse for honest IAP analytics. If you discover this *before* Step 5.2, build the synthetic IAP generator alongside the synthetic ad generator. If you discover it *during* Step 5.3 (this is what happened during the original build), pause to amend ADR-0013, build the IAP generator (`scripts/data/generate_synthetic_iap_events.py`), load to `raw.synthetic_iap_events`, then add `staging/synthetic_iap/` and resume.

### Step 5.4: Wire up Soda checks

Per ADR-0005, Soda is the second of three data-quality layers (above dbt tests, below Dagster anomaly sensors). Define checks in `soda/checks.yml` covering freshness, row-count SLAs, null rates, and distributional assertions tied to ADR-0013's calibration targets (paying-conversion ~3%, whale revenue share 60-85%).

**Check categories implemented**:

- **Structural** — `row_count > 0`, `missing_count(...) = 0`, `duplicate_count(...) = 0` for composite keys, fail conditions that catch leakage (e.g., `is_synthetic = false` rows in synthetic tables)
- **Freshness / coverage** — date range assertions on `fct_revenue_daily` (`min(event_date)` and `max(event_date)` against the populated Flood-It window)
- **Distributional / calibration** — `fail query` blocks asserting paying-conversion stays in 2-5% and whale revenue share stays in 60-85%; if these drift, either the synthetic generator parameters need re-tuning or downstream models compute things differently

**SodaCL syntax gotchas** (Windows + BigQuery):

- Date literals don't work as bare check expressions (`max(event_date) >= 2018-12-25`). Use a `failed rows` block with a `fail query` instead and quote the dates in the SQL.
- BigQuery's aggregation function is `countif`, not `count_if`. Soda passes the SQL through verbatim.
- Multiple `checks for <table>:` blocks for the same table fail YAML duplicate-key parsing — consolidate per-table.

**Verify**:

```sh
soda scan -d monetization_warehouse -c soda/configuration.yml soda/checks.yml
```

Expected: `All is good. No failures. No warnings. No errors.`

**Schedule via Dagster.** A `soda_quality_scan` asset + `soda_quality_job` + `soda_quality_daily` schedule live at `monetization_orchestration/src/monetization_orchestration/defs/soda_quality.py`. The asset uses Soda's Python `Scan` API directly (not a CLI subprocess) and walks up the directory tree to find `soda/configuration.yml` regardless of the running cwd. Cron is `0 6 * * *` (daily at 06:00 UTC).

### Step 5.5: Build your first Looker Studio dashboard

Six tiles on the marts. Looker Studio has no API, so this step is hands-on; the spec below is the configuration that produced the actual dashboard.

**Add three data sources** (Create → Data source → BigQuery → My Projects → monetization-warehouse → analytics → [table] → Connect):

- `analytics.fct_revenue_daily`
- `analytics.dim_players`
- `analytics.fct_retention_cohorts`

**Tile spec**:

| # | Tile | Source | Chart | Metric / formula | Filter |
|---|------|--------|-------|------------------|--------|
| 1 | ARPDAU over time | `fct_revenue_daily` | Time series | Calculated field `arpdau = SUM(total_revenue_usd) / COUNT_DISTINCT(user_pseudo_id)` | `is_active_today = true` |
| 2 | Retention curve | `fct_retention_cohorts` | Line | Calculated field `weighted_retention = SUM(retained_users) / SUM(cohort_size)` | `day_offset` IN {0, 1, 7, 14, 30} |
| 3 | Paying conversion | `dim_players` | Scorecard | `COUNT_DISTINCT(CASE WHEN is_payer THEN user_pseudo_id END) / COUNT_DISTINCT(user_pseudo_id)`, format Percent | none |
| 4 | Revenue by cohort | `dim_players` | Column chart | `SUM(ltv_usd)` by `first_seen_date` | none |
| 5 | Top-spending segments | `dim_players` | Bar chart | `SUM(ltv_usd)` and `COUNT_DISTINCT(user_pseudo_id)` (renamed `user_count`) by `payer_segment` | none |
| 6 | Total revenue | `fct_revenue_daily` | Scorecard with sparkline | `SUM(total_revenue_usd)`, sparkline dimension `event_date` | none |

**Polish that meaningfully changes how the dashboard reads**:

- Tile 2: rename X-axis ticks `0/1/7/14/30 → D0/D1/D7/D14/D30`. Add three horizontal **reference lines** (Style → Reference line → Constant) at `0.30 / 0.10 / 0.04` for industry casual-puzzle benchmarks; set their labels to `D1 (0.3)`, `D7 (0.1)`, `D30 (0.04)`. The chart now compares your retention to industry benchmarks at a glance.
- Tile 1 + Tile 4 + Tile 6: format metrics as **Currency (USD)** at the calculated-field / data-source level, not just at the chart level (some chart types ignore chart-level format).
- One accent color across all tiles (Theme & Layout → Theme → Custom).
- A small text annotation noting *"Real F2P data from GA4 Flood-It! sample (Aug-Oct 2018) + calibrated synthetic ad/IAP layers per ADR-0013"* — recruiter-readable transparency.

**Looker Studio gotchas you'll hit** (encountered building the actual dashboard):

- **Filter clauses default to AND, not OR.** A filter like `day_offset = 0 AND day_offset = 1 AND day_offset = 7` returns zero rows. Click the literal `AND` label between clauses to toggle to `OR`. The `In list` operator that would solve this in one clause is **only available for string fields**, not numeric — so for `day_offset` (INT64), OR-toggling between `Equal to` clauses is the path.
- **Scorecard with dimension ≠ scorecard with comparison.** Current LS exposes three scorecard types: plain `Scorecard`, `Scorecard with compact numbers`, `Scorecard with dimension`. Use plain Scorecard for tiles 3 and 6.
- **Default date range "Auto" silently truncates static data.** "Auto" = "Last 28 days relative to today." Against the 2018 Flood-It window that filters to ~nothing. Set every tile's Default date range to **Custom** with `2018-08-01` → `2018-10-04` explicitly.
- **A report-level date control overrides every tile's date range.** If you add one and leave its default at the standard "Last 28 days," your scorecards quietly show a sliver of revenue (the symptom: total revenue scorecard reads `$237.74` instead of `$8,716.02`). Set the control's default to the same custom range, or remove the control entirely.
- **Bar chart row limits live in the Style tab**, not Setup. Without bumping it, `Revenue by cohort` only shows the first ~10 cohort dates.
- **Y-axis currency formatting on time-series.** The metric's field-level Currency type formats tooltips and data labels but is sometimes ignored by axis tick labels. Style tab → Y-axis → Number format → Currency (USD) is the override that works on the axis.
- **Reference lines are horizontal only** (Y-axis thresholds). There's no native "vertical line at X = day_offset 7" — for that, filter the chart to the canonical offsets instead.
- **Default sort is by metric descending.** For ordered X-axes (cohort dates, day offsets), explicitly set Sort to the dimension ascending so the curve reads left-to-right correctly.

**Dashboard publishing**: Share → Public access if you want it visible on the portfolio. Add the URL to the repo README.

**Live dashboard for this project**: <https://datastudio.google.com/reporting/dca0554f-5906-4c2d-8576-e5c4f922c3cb>

Walkthrough (introductory, not the level of detail above): <https://blog.coupler.io/bigquery-to-data-studio/>

### Step 5.6: Push events to Amplitude

Push a sample of warehouse events to Amplitude's HTTP API v2 batch endpoint so the funnel, retention, and segment views in Amplitude's UI run against the same events the dbt marts compute. A few hundred events across diverse types is enough — the goal is being able to *demonstrate* Amplitude fluency, not load the whole pipeline.

Loader at `scripts/data/push_events_to_amplitude.py`:

```sh
uv run python scripts/data/push_events_to_amplitude.py --user-sample 50 --max-events 500
```

**Sampling strategy that matters**: stratify the user sample, don't pure-random. With ~3% paying conversion, 50 random users produces 1-2 payers — not enough to demo IAP funnels in Amplitude. The loader splits the sample 50/50 between payers and random users, ensuring conversion behavior in the payload. Confirmed at run time:

```
payload event-type distribution:
  ad_impression  : 208
  session_start  : 117
  level_start    : 65
  iap_purchase   : 60   ← matters for funnel demo
  level_complete : 40
  first_open     : 5
  level_fail     : 5

Amplitude responded HTTP 200: events_ingested: 500
```

**Schema mapping** to Amplitude HTTP API v2:

- `user_id` ← Flood-It `user_pseudo_id`
- `event_type` ← BigQuery `event_name`
- `time` ← `event_timestamp_us / 1000` (Amplitude wants Unix milliseconds, our column is microseconds — easy to forget)
- `event_properties` ← `placement`, `revenue_usd`, `product_id`
- `user_properties` ← `country`, `payer_segment`
- `insert_id` ← `user_pseudo_id-event_timestamp_us` (idempotency key; lets you re-run the script without duplicating events in Amplitude)

**Verify in Amplitude**: open <https://app.amplitude.com> → your project → Events tab. New events typically appear within ~30 seconds. Build one quick funnel: `session_start` → `level_complete` → `iap_purchase` to demonstrate end-to-end conversion analysis.

Reference: <https://amplitude.com/docs/apis/analytics/http-v2>

---

## Phase 6 — Portfolio polish (ongoing)

### Step 6.1: Write your three core analyses

Pick three concrete questions, write each as a repo README or blog post:

1. What does a healthy retention curve look like in this dataset, and what would I test to improve D7?
2. How concentrated is revenue in the top 1% of players, and what's the implication for live-ops priorities?
3. If I were running a price test on the starter pack, how would I design it, and what's the minimum sample size?

Each one references your glossary, links your dashboard, cites your ADRs.

**This is what hiring managers care about** — not the infrastructure, the thinking on top of it.

### Step 6.2: Make the repo presentable

Root README with:

- One-paragraph project description
- Architecture diagram (Mermaid, generated by Claude Code)
- Live Looker Studio dashboard link
- Links to the three analyses
- Tech stack section
- Link to `docs/adr/README.md` (your decision log)

Pin it on your GitHub profile.

### Step 6.3: Publish the dbt docs site

dbt's `docs generate` produces lineage graphs, column-level documentation, source freshness, and test coverage as a hostable HTML site. Single most-impressive recruiter artifact past the dashboard, since it makes the model graph visually inspectable.

**Generate as a single self-contained file**:

```sh
cd monetization_warehouse
dbt docs generate --static
cp target/static_index.html ../docs/dbt-docs/index.html
```

`--static` inlines the manifest and catalog into the HTML so no sibling JSON files are needed at runtime — one ~2.5MB file, deploys anywhere static.

**Enable GitHub Pages** (programmatic via `gh`, no web UI clicking):

```sh
gh api -X POST repos/<owner>/<repo>/pages --input - <<'EOF'
{"source":{"branch":"main","path":"/docs"}}
EOF
```

The first build kicks off on the commit that pushes `docs/dbt-docs/index.html`. Poll for completion:

```sh
gh api repos/<owner>/<repo>/pages/builds/latest --jq .status
```

Status goes `building` → `built` in ~30-60s.

**Live URL**: `https://<owner>.github.io/<repo>/dbt-docs/`. Add it to the README's Documentation section.

**Regeneration cadence**: manual on each model change (no GitHub Action wired — overkill for a static portfolio with infrequent updates). Just rerun the `generate --static` + `cp` pair and push.

---

## Final checklist

- [ ] Phase 0: 10 ADRs written, glossary stubbed, CLAUDE.md committed
- [ ] Phase 1: All AI tooling installed and verified
- [ ] Phase 2: GCP project, service account, datasets, ADR-0011 written
- [ ] Phase 3: dbt + Dagster + Soda installed and connected, ADR-0012 written
- [ ] Phase 4: Looker Studio, Amplitude, Sentry accounts set up
- [ ] Phase 5: Data loaded (with ADR-0013), dbt models running, glossary filled in, dashboard live, Amplitude events flowing
- [ ] Phase 6: Three analyses written, repo presentable, pinned on profile
- [ ] CAREER.md tracks running in parallel (industry fluency, critical play, networking, fallback prep)

## Maintenance rules (forever)

These keep the system honest after setup:

1. **Decision-time documentation is not optional.** A new ADR ships in the same commit as the change it constrains. No retroactive ADRs.
2. **A metric's glossary entry ships in the same commit as the SQL that materializes it.** No exceptions.
3. **Diff-before-write on `docs/`.** Show the diff, get confirmation, then write.
4. **Never include raw player IDs, device IDs, emails, real revenue figures.** Synthetic IDs and rounded amounts only.
5. **Tag sensitive context with `<private>...</private>` blocks** so claude-mem excludes them.
