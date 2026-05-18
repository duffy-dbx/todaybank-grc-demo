# TodayBank GRC Operations Hub – Setup Guide

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

## Setup checklist

### First-time deploy (run once, not before every demo)

- [ ] `databricks catalogs create todaybank_grc_demo --profile e2-demo-west`
- [ ] `databricks bundle deploy --target dev`
- [ ] `databricks bundle run setup_job --target dev`
- [ ] `databricks bundle run pipeline_kickoff --target dev`
- [ ] Import the dashboard: AI/BI → Dashboards → Import → select `dashboards/todaybank_grc_dashboard.lvdash.json` → connect the `TodayBank GRC Demo Warehouse` in Dashboard Settings → click Run all to verify all tiles populate
- [ ] Configure the 6 chart/table widgets manually (the 4 KPI counters configure automatically; the rest need field bindings set in the viz editor):

  **Bar charts** — click widget → open viz editor → assign fields:

  | Widget | X axis | Y axis |
  |---|---|---|
  | AML Alerts by Type | `alert_type` | `alert_count` |
  | Risk Score Distribution | `risk_bucket` | `customer_count` |

  **Line chart (Complaint Volume by Theme)** — `month` → X axis · `complaints` → Y axis · `theme` → Color/Group by

  **Tables** — click each column name in the field list to add it:

  | Widget | Columns |
  |---|---|
  | Fair Lending | `race`, `ethnicity`, `gender`, `loan_purpose`, `application_count`, `approval_rate_pct` |
  | Top-Risk Customers | `full_name`, `state`, `kyc_risk_tier`, `aml_alert_count`, `aml_alert_total_usd`, `complaint_count`, `balance_usd` |
  | PEP Matches | `full_name`, `document_date`, `occupation`, `source_of_funds`, `pep_status` |
- [ ] Create the four curated Genie views: run lines 1–76 of `sql/genie_space_setup.sql` in the SQL editor (or `databricks sql execute --warehouse-id <id> --file sql/genie_space_setup.sql --profile e2-demo-west`)
- [ ] Create the Genie space: Genie → New Genie space → name it `TodayBank GRC Operations Hub` → add the four tables below → set warehouse to `TodayBank GRC Demo Warehouse` → Save
  - `todaybank_grc_demo.gold.genie_customer_360`
  - `todaybank_grc_demo.gold.genie_aml_alerts`
  - `todaybank_grc_demo.gold.genie_hmda`
  - `todaybank_grc_demo.gold.genie_complaints`
- [ ] In Genie space settings, paste General Instructions and 5 Sample Questions from `sql/genie_space_setup.sql` (lines 89–101) — public API doesn't expose these fields yet

### Before every demo (30 min prior)

- [ ] Open dashboard once to warm the cache: <https://e2-demo-field-eng.cloud.databricks.com/dashboardsv3/01f14e33aa4f1eac9fdbd4728db47513>
- [ ] Open Genie space once to warm the cache: <https://e2-demo-field-eng.cloud.databricks.com/genie/rooms/01f14e4097ff1ce48bf2520f456ef9f6>
- [ ] Start the `TodayBank GRC Demo Warehouse` (SQL → Warehouses) so Act 4's live `ai_classify` doesn't cold-start
- [ ] Open all 6 tabs in the order listed in `talk_track.md` Pre-flight section
- [ ] Test the audit-log query and the lineage popup – lineage can take ~5 min to populate after a fresh pipeline run
