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

**Real F2P data (preferred).** Uken Games' 2015 SFU case-study dataset — players, demographics, actions, revenue, retention. <http://people.stat.sfu.ca/~dac5/CaseStudy2015/CaseStudy2015/Dataset.html>

**Synthetic alternative.** Have Claude Code generate plausible event data with realistic monetization patterns:

- D1 retention 40%, D7 20%, D30 8%
- ~3% paying conversion
- 80/20 whale concentration

Save as Parquet, load to BigQuery `raw`.

> **📝 Decision-time doc:** Write **ADR-0013** — *"Data acquisition: real Uken dataset vs. synthetic generator"* — including data limitations, why you chose what you chose, what you'd swap to later.

### Step 5.2: Build the dbt model layer

Three layers:

- `stg_events` — cleans raw events
- `fct_revenue_daily` — per-day-per-player revenue
- `dim_players` — lifetime stats per player

```sh
dbt run
dbt test
```

> **📝 Glossary discipline:** For every metric encoded in `fct_*` and `dim_*`, **fill in the corresponding glossary entry** before the model's SQL is committed. ARPDAU, DAU, LTV, retention buckets — every one. Glossary entry and SQL ship in the same commit.

### Step 5.3: Wire up Soda checks

Define checks in `soda/checks.yml` for freshness, row counts, null rates on the marts. Schedule via Dagster sensor.

### Step 5.4: Build your first Looker Studio dashboard

Six tiles on `fct_revenue_daily`:

1. ARPDAU over time
2. Retention curve (D1/D7/D30)
3. Conversion rate
4. Revenue by cohort
5. Top-spending player segments
6. Total revenue scorecard

**Make it look polished.** Walkthrough: <https://blog.coupler.io/bigquery-to-data-studio/>

### Step 5.5: Push events to Amplitude

Send a sample of your events to Amplitude's HTTP API. A few hundred is enough to play with funnel and retention views and speak to it in interviews.

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
