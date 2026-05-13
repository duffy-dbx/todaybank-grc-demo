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
- [ ] Import the dashboard: AI/BI → Dashboards → Import → select `dashboards/todaybank_grc_dashboard.lvdash.json`
- [ ] Create the Genie space and point it at the four `gold.genie_*` views
- [ ] In Genie space settings, paste General Instructions and 5 Sample Questions from `sql/genie_space_setup.sql` (lines 89–101) — public API doesn't expose these fields yet

### Before every demo (30 min prior)

- [ ] Open dashboard once to warm the cache: <https://e2-demo-field-eng.cloud.databricks.com/dashboardsv3/01f14e33aa4f1eac9fdbd4728db47513>
- [ ] Open Genie space once to warm the cache: <https://e2-demo-field-eng.cloud.databricks.com/genie/rooms/01f14e4097ff1ce48bf2520f456ef9f6>
- [ ] Start the `TodayBank GRC Demo Warehouse` (SQL → Warehouses) so Act 4's live `ai_classify` doesn't cold-start
- [ ] Open all 6 tabs in the order listed in `demo_flow.md` Pre-flight
- [ ] Test the audit-log query and the lineage popup – lineage can take ~5 min to populate after a fresh pipeline run
