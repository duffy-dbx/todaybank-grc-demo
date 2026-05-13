# TodayBank GRC Operations Hub – Click-through Demo Flow

Step-by-step click sequence with timing. Use alongside `talk_track.md`.

---

## Live assets on `e2-demo-field-eng`

| Asset | Where to find it in the UI |
|---|---|
| Catalog | Catalog Explorer → [`todaybank_grc_demo`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo) |
| Lakeflow Pipeline | Workflows → Delta Live Tables → `todaybank-grc-demo-pipeline` |
| Setup Job | Workflows → Jobs → `TodayBank GRC Demo – Setup & Generate Data` |
| Pipeline + AI + ML Job | Workflows → Jobs → `TodayBank GRC Demo – Run Pipeline + AI + ML` |
| SQL Warehouse | SQL → Warehouses → `TodayBank GRC Demo Warehouse` |
| Notebooks (bundle files) | Workspace → `/Workspace/Users/duffy.walsh@databricks.com/.bundle/todaybank-grc-demo/dev/files/notebooks/` |
| Dashboard | AI/BI → Dashboards → [TodayBank GRC Operations Hub](https://e2-demo-field-eng.cloud.databricks.com/dashboardsv3/01f14e33aa4f1eac9fdbd4728db47513) |
| Genie space | Genie → [TodayBank GRC Operations Hub](https://e2-demo-field-eng.cloud.databricks.com/genie/rooms/01f14e4097ff1ce48bf2520f456ef9f6) |

Curated Gold views the Genie space points at:
- [`gold.genie_customer_360`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/genie_customer_360)
- [`gold.genie_aml_alerts`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/genie_aml_alerts)
- [`gold.genie_hmda`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/genie_hmda)
- [`gold.genie_complaints`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/genie_complaints)

Files used during the talk:
- `sql/dashboard_queries.sql` – source queries behind the dashboard tiles
- `sql/demo_live_unstructured.sql` – three cells to paste for the AI segment (Act 4)
- `sql/genie_space_setup.sql` – view DDL + Genie instructions/sample-questions text

---

## Setup checklist (do this 30 min before the demo)

**First-time deploy only (run once, not before every demo):**

- [ ] Create the catalog first (bundle deploy requires it to exist): `databricks catalogs create --name todaybank_grc_demo --profile e2-demo-west`
- [ ] `databricks bundle deploy --target dev` – creates jobs, pipeline definition, SQL warehouse
- [ ] `databricks bundle run setup_job --target dev` – creates catalog/schemas, generates bronze data
- [ ] `databricks bundle run pipeline_kickoff --target dev` – runs Bronze→Silver→Gold pipeline, then AI/ML notebooks (wait ~20 min)
- [ ] Import the dashboard: AI/BI → Dashboards → Import → select `dashboards/todaybank_grc_dashboard.lvdash.json`
- [ ] Create the Genie space manually and point it at the four `gold.genie_*` views
- [x] In the Genie space settings, paste General Instructions and 5 Sample Questions from `sql/genie_space_setup.sql` (lines 89–101). _Public API doesn't expose these fields yet._

**Before every demo (30 min prior):**

- [ ] Open dashboard once to warm the cache: <https://e2-demo-field-eng.cloud.databricks.com/dashboardsv3/01f14e33aa4f1eac9fdbd4728db47513>
- [ ] Open Genie space once to warm the cache: <https://e2-demo-field-eng.cloud.databricks.com/genie/rooms/01f14e4097ff1ce48bf2520f456ef9f6>
- [ ] Start the `TodayBank GRC Demo Warehouse` (SQL → Warehouses) so Act 4's live `ai_classify` doesn't cold-start
- [ ] Open all 6 tabs in the order listed in `talk_track.md` Pre-flight
- [ ] Test the audit-log query and the lineage popup – sometimes lineage takes ~5 min to populate after a fresh pipeline run

---

## Demo flow (30 min)

### 0:00 – Greeting + warm-up question
- Hands-up question about three-system GRC
- Brief intro of yourself and Databricks

### 0:02 – Act 1: The Problem (no screen)
- Day-in-the-life narrative
- Don't show anything yet – let them visualize the pain

### 0:05 – Act 2: Governed Foundation (Catalog Explorer)
- **0:05** – [Catalog Explorer at `todaybank_grc_demo`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo) (catalog tree visible)
- **0:06** – Click [`bronze.raw_customers`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/bronze/raw_customers) → Tags tab → highlight `PII` and `regulatory_HMDA` tags
- **0:07** – Sample Data tab → run `SELECT * FROM todaybank_grc_demo.silver.customers_v LIMIT 5;`
- **0:08** – Click [`gold.aml_alerts`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/aml_alerts) → Lineage tab → click through to source
- **0:09** – Switch to `notebooks/04_governance_walkthrough.py` → run the audit-log cell

### 0:10 – Act 3: Pipelines That Just Work (Lakeflow Pipeline)
- **0:10** – Open the Lakeflow Pipeline DAG view
- **0:11** – Click an Expectation → show dropped/quarantined rows
- **0:13** – Click `silver_transactions` → Schema tab
- **0:15** – Show the `@dlt.table` decorator code for `gold.aml_alerts`
- **0:16** – Mention streaming (don't switch – just point at the keyword)

### 0:17 – Act 4: AI You Can Trust (SQL editor → MLflow → Catalog Explorer)
- **0:17** – SQL editor: paste **Cell 1** from `sql/demo_live_unstructured.sql` – live `ai_classify` on raw complaints (10 rows)
- **0:18** – Paste **Cell 2** – the full 500-row population already classified
- **0:19** – Open [`silver.complaints_classified`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/silver/complaints_classified) → show theme + severity columns
- **0:20** – Paste **Cell 3** OR open [`gold.kyc_pep_matches`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/kyc_pep_matches) → 2 PEP rows visible
- **0:21** – MLflow registry → [`todaybank_grc_demo.gold.aml_risk_model`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/models/todaybank_grc_demo/gold/aml_risk_model)
- **0:22** – Model description tab → SR 11-7 documentation visible
- **0:23** – Lineage tab on the model
- **0:24** – `@champion` alias → mention challenger pattern
- **0:24:30** – Catalog Explorer → [`gold.aml_risk_scores`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/aml_risk_scores) → Quality tab → Lakehouse Monitoring

### 0:25 – Act 5: Self-service for the Business (AI/BI Dashboard → Genie)
- **0:25** – [TodayBank GRC Operations Hub dashboard](https://e2-demo-field-eng.cloud.databricks.com/dashboardsv3/01f14e33aa4f1eac9fdbd4728db47513) → 4 KPI tiles
- **0:26** – Hover KPI → "View lineage"
- **0:27** – Click the Fair Lending heatmap
- **0:28** – Switch to the [Genie space](https://e2-demo-field-eng.cloud.databricks.com/genie/rooms/01f14e4097ff1ce48bf2520f456ef9f6)
- **0:28:30** – Type: *"Show me top 10 customers by AML alert dollar amount this quarter"* (resolves against `gold.genie_customer_360` + `gold.genie_aml_alerts`)
- **0:29:30** – Click "Show SQL" – emphasize transparency; point out it's querying the curated `genie_*` views, not raw bronze
- **0:30** – Type follow-up: *"How does the loan approval rate for home purchase compare across races?"* (resolves against `gold.genie_hmda`)

### 0:30 – Close + Q&A
- Three pillars · one platform · one audit trail
- Map back to TodayBank: lakehouse live, AI/BI evaluating, Genie evaluating – bridge what's missing
- 30-min follow-up call to map demo to their real source feeds

---

## Backup demos (if asked)

| Audience hot-button | Where to detour |
|---|---|
| "What about regulatory reporting?" | Open [`silver.transactions`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/silver/transactions) → show how a Call Report aggregation would look (1-min mock SQL) |
| "How do you handle data quality issues?" | Lakeflow expectations – re-run the pipeline with a forced bad row |
| "We use Snowflake today – can we coexist?" | Lakehouse Federation tab in Catalog Explorer – show querying a foreign Snowflake table |
| "We're worried about cost" | Open System Tables → `system.billing.usage` → filter to demo workspace → show DBU spend |
| "Show me the model card / SR 11-7 paperwork" | MLflow → model description → mention auto-generated model cards |
| "Can Genie see PII?" | Open [`gold.genie_customer_360`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/gold/genie_customer_360) DDL – no SSN/phone/email/DOB columns, by design |

---

## Recovery moves (if something breaks live)

| Symptom | Recovery |
|---|---|
| Lakeflow pipeline shows red | Don't dwell – say "this is the kind of failure that won't get past expectations into production" and move on |
| `ai_classify` is slow / errors | Switch to the pre-populated [`silver.complaints_classified`](https://e2-demo-field-eng.cloud.databricks.com/explore/data/todaybank_grc_demo/silver/complaints_classified) table |
| Genie returns nonsense | Refresh; rephrase question; or switch to dashboard. Genie quality has improved a lot but it's still LLM-paced |
| Lineage popup is empty | Wait 30 sec and refresh – if still empty, click into Catalog Explorer Lineage tab manually |
| Dashboard is slow | Mention serverless cold-start; use the moment to monologue about cost economics |
