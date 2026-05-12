# TodayBank GRC Operations Hub – Databricks Demo

A 100-level Databricks demo for **TodayBank Bank** showcasing the Data Intelligence Platform across **Governance, Risk, and Compliance (GRC)** use cases. End-to-end runtime: ~15 minutes for the data setup + pipeline; demo presentation ~30 minutes.

---

## Audience

- **Primary:** Risk Officers, Compliance Officers, BSA Officers, Model Risk Managers
- **Secondary:** Data Platform Owners, Heads of Data, CDOs
- **Persona demos:** Data Engineers (4 min), Marketing Analysts (4 min)
- **Level:** 100 (broad capability overview, light on code deep-dives)

## Storyline (one-liner)

*"TodayBank's Risk Officer needs a single, governed view across structured transactions, semi-structured KYC documents, and unstructured customer complaints – without standing up three different tools, three different governance models, and three different AI black boxes. The same platform serves the data engineer who builds those pipelines and the marketing analyst who mines customer insights from them – one governance model, every persona."*

## What this demo proves

1. **One platform** spans batch + streaming + ML + GenAI + BI
2. **One governance layer** (Unity Catalog) covers tables, files, models, dashboards, and AI agents
3. **AI is auditable** – model registry, lineage from dashboard widget to source row, drift monitoring, audit logs in system tables
4. **Business users self-serve** safely via Genie – with the SQL shown for transparency
5. **Every persona is served** – the data engineer who builds the pipelines, the risk officer who monitors them, and the marketing analyst who mines customer insights from them all work from the same governed data layer

---

## Architecture

```
                          ┌──────────────────────────────────────┐
                          │      UNITY CATALOG (governance)      │
                          │  PII tags · lineage · ABAC · audit   │
                          └──────────────────────────────────────┘
                                            │
        ┌──────────────────┬────────────────┼──────────────────────┐
        │                  │                │                      │
   raw_transactions   raw_customers    raw_loans (HMDA)     raw_complaints
   raw_kyc_docs                                                      │
        │                                                            │
        ▼                                                            ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │              LAKEFLOW PIPELINE  (Bronze → Silver → Gold)              │
  │   schema enforcement · expectations · streaming · CDC                 │
  └──────────────────────────────────────────────────────────────────────┘
        │                  │                │                      │
        ▼                  ▼                ▼                      ▼
   aml_alerts         hmda_summary    risk_dashboard         complaint_themes
                                            │
                          ┌─────────────────┴────────────────┐
                          │                                  │
                          ▼                                  ▼
                  AI/BI DASHBOARD                      GENIE SPACE
                  (Risk Officer view)            (analyst self-service)

                          ┌──────────────────────────────────────┐
                          │      MLflow + Lakehouse Monitoring   │
                          │   AML model · drift · SR 11-7 docs   │
                          └──────────────────────────────────────┘

             ┌────────────────────────────────────────────────────────┐
             │                  PERSONA DEMO OVERLAYS                 │
             │  Data Engineer (4 min) ── pipeline code · DABs ·      │
             │    lineage · System Tables                             │
             │  Marketing Analyst (4 min) ── Genie segments ·        │
             │    complaint themes · safe self-service               │
             └────────────────────────────────────────────────────────┘
```

---

## Repo layout

```
todaybank-grc-demo/
├── README.md                          ← this file
├── databricks.yml                     ← DAB deployment config
├── notebooks/
│   ├── 00_setup_and_generate_data.py  ← creates catalog, schemas, tags, sample data
│   ├── 01_lakeflow_pipeline.py        ← Lakeflow Pipeline (DLT) bronze→silver→gold
│   ├── 02_ai_classify_and_extract.py  ← AI Functions on complaints + KYC docs
│   ├── 03_aml_model_mlflow.py         ← Train + register AML risk model
│   └── 04_governance_walkthrough.py   ← Lineage, masking, audit demo
├── sql/
│   ├── dashboard_queries.sql          ← Queries powering the dashboard
│   ├── genie_space_setup.sql          ← Curated views + instructions for Genie
│   └── governance_audit.sql           ← Audit log queries (system.access.audit)
├── dashboards/
│   └── todaybank_grc_dashboard.lvdash.json ← Lakeview dashboard definition
└── docs/
    ├── talk_track.md                  ← Speaker notes by act
    ├── demo_flow.md                   ← Click-through flow with timing
    └── customer_takeaways.md          ← Leave-behind one-pager
```

---

## Prerequisites

- Databricks workspace with **Unity Catalog** enabled
- Permissions to create a catalog (or use an existing one – set `CATALOG` in `notebooks/00_setup_and_generate_data.py`)
- Access to **Foundation Model APIs** for AI Functions (`databricks-meta-llama-3-3-70b-instruct` or workspace default)
- A **serverless SQL warehouse** for the dashboard
- Cluster: 15.4 LTS or later (Serverless preferred)

## Quick start

```bash
# 1. Clone or copy this repo into your workspace
databricks workspace import-dir ./todaybank-grc-demo /Workspace/Demos/todaybank-grc-demo

# 2. Run the setup notebook (creates catalog + populates sample data, ~5 min)
#    Open: 00_setup_and_generate_data.py and run it

# 3. Deploy and run the Lakeflow Pipeline
#    Open: 01_lakeflow_pipeline.py – wire it up as a DLT pipeline

# 4. Run the AI + ML notebooks (in any order)
#    02_ai_classify_and_extract.py
#    03_aml_model_mlflow.py

# 5. Import the dashboard
databricks dashboards import dashboards/todaybank_grc_dashboard.lvdash.json

# 6. (Optional) Create a Genie space pointing at the gold schema
#    See sql/genie_space_setup.sql for curated views
```

Or with **Databricks Asset Bundles** (recommended):

```bash
cd todaybank-grc-demo
databricks bundle deploy --target dev
databricks bundle run setup_job --target dev
```

---

## Demo flow at a glance (30 min)

| Act | Duration | What you show | What it proves |
|---|---|---|---|
| **1. The Problem** | 3 min | Status quo: 3 systems, no lineage, AI black box | Why the lakehouse |
| **2. Governed Foundation** | 5 min | UC tree, PII tags, dynamic views, lineage, audit | One governance model |
| **3. Pipelines That Just Work** | 7 min | Lakeflow Pipeline DAG, expectations, schema | Replace SSIS/Informatica |
| **4. AI You Can Trust** | 8 min | AI Functions, MLflow registry, drift monitoring | SR 11-7 ready |
| **5. Self-service for Business** | 5 min | AI/BI dashboard, Genie Q&A with SQL shown | Killer for BI mod UCO |
| **Q&A** | 5–10 min | – | – |

Full speaker notes: [`docs/talk_track.md`](docs/talk_track.md). Click-through: [`docs/demo_flow.md`](docs/demo_flow.md).

**Persona demos (4 min each):**
- Data Engineers: [`docs/talk_track_data_engineer.md`](docs/talk_track_data_engineer.md)
- Marketing Analysts: [`docs/talk_track_marketing.md`](docs/talk_track_marketing.md)

---

## What's in the sample data

| Table | Rows | Purpose |
|---|---|---|
| `bronze.raw_customers` | 5,000 | Customer master with PII (SSN, DOB, address) |
| `bronze.raw_transactions` | 100,000 | 12 months of card + ACH + wire transactions; ~50 suspicious patterns embedded (structuring, rapid movement, high-risk geos) |
| `bronze.raw_loans` | 2,000 | Mortgage applications with HMDA fields (race, ethnicity, gender, action_taken) |
| `bronze.raw_complaints` | 500 | Free-text customer complaints across 8 themes |
| `bronze.raw_kyc_docs` | 200 | Free-text KYC narratives for entity extraction demo |
| `bronze.raw_audit_events` | 5,000 | System audit events |

All synthetic. No real PII. Generated deterministically from a fixed seed for reproducibility.

---

## Talk track + demo flow

- Speaker notes: [`docs/talk_track.md`](docs/talk_track.md)
- Click-through demo flow with timing: [`docs/demo_flow.md`](docs/demo_flow.md)
- One-page customer leave-behind: [`docs/customer_takeaways.md`](docs/customer_takeaways.md)
