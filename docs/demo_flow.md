# Axos GRC Operations Hub — Click-through Demo Flow

Step-by-step click sequence with timing. Use alongside `talk_track.md`.

---

## Setup checklist (do this 30 min before the demo)

- [ ] Run `notebooks/00_setup_and_generate_data.py` end-to-end
- [ ] Start the Lakeflow Pipeline from `notebooks/01_lakeflow_pipeline.py` and verify all tables built
- [ ] Run `notebooks/02_ai_classify_and_extract.py` end-to-end (silver.complaints_classified must exist)
- [ ] Run `notebooks/03_aml_model_mlflow.py` (model must be registered with `@champion` alias)
- [ ] Run the dynamic-view cell in `notebooks/04_governance_walkthrough.py`
- [ ] Import `dashboards/axos_grc_dashboard.lvdash.json`
- [ ] Create Genie space using `sql/genie_space_setup.sql`
- [ ] Open all 6 tabs in the order listed in `talk_track.md` Pre-flight
- [ ] Test the audit-log query and the lineage popup — sometimes lineage takes ~5 min to populate after a fresh run

---

## Demo flow (30 min)

### 0:00 — Greeting + warm-up question
- Hands-up question about three-system GRC
- Brief intro of yourself and Databricks

### 0:02 — Act 1: The Problem (no screen)
- Day-in-the-life narrative
- Don't show anything yet — let them visualize the pain

### 0:05 — Act 2: Governed Foundation (Catalog Explorer)
- **0:05** — Catalog Explorer at `axos_grc_demo` (catalog tree visible)
- **0:06** — Click `bronze.raw_customers` → Tags tab → highlight `PII` and `regulatory_HMDA` tags
- **0:07** — Sample Data tab → run `SELECT * FROM axos_grc_demo.silver.customers_v LIMIT 5;`
- **0:08** — Click `gold.aml_alerts` → Lineage tab → click through to source
- **0:09** — Switch to `04_governance_walkthrough.py` → run the audit-log cell

### 0:10 — Act 3: Pipelines That Just Work (Lakeflow Pipeline)
- **0:10** — Open the Lakeflow Pipeline DAG view
- **0:11** — Click an Expectation → show dropped/quarantined rows
- **0:13** — Click `silver_transactions` → Schema tab
- **0:15** — Show the `@dlt.table` decorator code for `gold.aml_alerts`
- **0:16** — Mention streaming (don't switch — just point at the keyword)

### 0:17 — Act 4: AI You Can Trust (SQL editor → MLflow → Catalog Explorer)
- **0:17** — SQL editor: live `ai_classify` on raw complaints (10 rows)
- **0:19** — Open `silver.complaints_classified` → show theme + severity columns
- **0:20** — `gold.kyc_pep_matches` → 2 PEP rows visible
- **0:21** — MLflow registry → `axos_grc_demo.gold.aml_risk_model`
- **0:22** — Model description tab → SR 11-7 documentation visible
- **0:23** — Lineage tab on the model
- **0:24** — `@champion` alias → mention challenger pattern
- **0:24:30** — Catalog Explorer → `gold.aml_risk_scores` → Quality tab → Lakehouse Monitoring

### 0:25 — Act 5: Self-service for the Business (AI/BI Dashboard → Genie)
- **0:25** — Axos GRC Operations Hub dashboard → 4 KPI tiles
- **0:26** — Hover KPI → "View lineage"
- **0:27** — Click Fair Lending heatmap
- **0:28** — Switch to Genie space
- **0:28:30** — Type: "Show me top 10 customers by AML alert dollar amount this quarter"
- **0:29:30** — Click "Show SQL" — emphasize transparency
- **0:30** — Type follow-up: "How does the loan approval rate for home purchase compare across races?"

### 0:30 — Close + Q&A
- Three pillars · one platform · one audit trail
- Map back to Axos: lakehouse live, AI/BI evaluating, Genie evaluating — bridge what's missing
- 30-min follow-up call to map demo to their real source feeds

---

## Backup demos (if asked)

| Audience hot-button | Where to detour |
|---|---|
| "What about regulatory reporting?" | Open the `silver.transactions` table → show how a Call Report aggregation would look (1-min mock SQL) |
| "How do you handle data quality issues?" | Lakeflow expectations — re-run the pipeline with a forced bad row |
| "We use Snowflake today — can we coexist?" | Lakehouse Federation tab in Catalog Explorer — show querying a foreign Snowflake table |
| "We're worried about cost" | Open System Tables → `system.billing.usage` → filter to demo workspace → show DBU spend |
| "Show me the model card / SR 11-7 paperwork" | MLflow → model description → mention auto-generated model cards |

---

## Recovery moves (if something breaks live)

| Symptom | Recovery |
|---|---|
| Lakeflow pipeline shows red | Don't dwell — say "this is the kind of failure that won't get past expectations into production" and move on |
| `ai_classify` is slow / errors | Switch to the pre-populated `silver.complaints_classified` table |
| Genie returns nonsense | Refresh; rephrase question; or switch to dashboard. Genie quality has improved a lot but it's still LLM-paced |
| Lineage popup is empty | Wait 30 sec and refresh — if still empty, click into Catalog Explorer Lineage tab manually |
| Dashboard is slow | Mention serverless cold-start; use the moment to monologue about cost economics |
