# TodayBank GRC Operations Hub – Demo Overview
## Slide Content Spec · 11 Slides · Customer-Facing

**Copied presentation (from Databricks template):** `1r-lQs9pGI5aLkJPnJaCHXYtTu6z0amuzHiBnRgNePyo`

---

## Slide 1 – Title

**Title:** TodayBank GRC Operations Hub

**Subtitle:** Databricks Data Intelligence Platform

**Presenter line:** Duffy Walsh · Field Engineering, Financial Services · duffy.walsh@databricks.com

---

## Slide 2 – Agenda

**Title:** What We'll Cover Today

| Act | Topic | Time |
|---|---|---|
| The Problem | Three systems, no unified view | 3 min |
| Governed Foundation | Unity Catalog – tags, lineage, masking, audit | 5 min |
| Pipelines That Just Work | Lakeflow – declarative ETL, DQ expectations, streaming | 7 min |
| AI You Can Trust | AI Functions, MLflow, SR 11-7, drift monitoring | 8 min |
| Self-Service for Business | AI/BI Dashboard + Genie | 5 min |
| Persona Add-Ons (optional) | Data Engineer · Marketing Analyst | +8 min |

---

## Slide 3 – The Challenge

**Title:** Monday Morning for a Risk Officer

**Body:**

She comes in. Her AML system flagged 200 alerts overnight.

- Log into the **AML system** to see the alerts
- Log into the **KYC system** to identify the customers
- Log into the **complaints system** to check for overlap

**Three systems. Three logins. Half her morning – gone.**

And when her boss asks: *"How do you know the model isn't biased?"*
She has no answer. The model lives outside her data platform entirely.

> **Speaker note:** No screen yet. Let the audience visualize the pain before showing the solution.

---

## Slide 4 – The Platform

**Title:** One Platform. One Governance Model. One Audit Trail.

**Five capability tiles:**

| Capability | What it does |
|---|---|
| **Unity Catalog** | Governance umbrella over tables, files, models, dashboards, and AI. PII tags, lineage, and audit are automatic. |
| **Lakeflow Pipelines** | Declarative ETL with built-in data quality expectations and schema enforcement. Replaces SSIS / Informatica / Glue. |
| **AI Functions** | `ai_classify`, `ai_extract`, `ai_query` as SQL primitives – governed and audited like any query. No model training required. |
| **MLflow + Lakehouse Monitoring** | Model registry, SR 11-7 documentation, drift detection. MRM-ready out of the box. |
| **AI/BI Dashboards + Genie** | Curated dashboards for Risk Officers. Natural-language self-service for analysts, with the SQL always shown. |

---

## Slide 5 – Act 2: Governed Foundation

**Title:** Governance That Enforces Itself

**Subtitle:** Unity Catalog

**Four proof points:**

- **PII Tags, Enforced** – Classify sensitive columns once. Tags drive masking, discovery, and audit reporting. Not labels in a wiki – enforced policy.
- **Dynamic Masking by Role** – Same underlying table, different view depending on your group. No data copy. No separate masked database.
- **Automatic Lineage** – Every table, model, and dashboard widget traces to source automatically. No Collibra. No Alation. No stewardship tickets.
- **Complete Audit Log** – Every read, every `ai_classify` call, every model inference lands in a queryable system table.

**Bottom line:** When the regulator asks "where did this number come from?" – two clicks.

---

## Slide 6 – Act 3: Pipelines That Just Work

**Title:** Declarative ETL. Zero Boilerplate.

**Subtitle:** Lakeflow Pipelines (Delta Live Tables)

**Code snippet:**

```python
@dlt.table(table_properties={"regulatory": "BSA_AML"})
@dlt.expect_or_drop("valid_amount", "amount_usd > 0")
def gold_aml_alerts():
    ...  # ~15 lines generates full AML alert detection
```

**Four proof points:**

- Bronze → Silver → Gold, declared in Python – no DDL, no mapping sheets, no SSIS packages
- Data quality expectations **quarantine** bad rows; they don't crash jobs or corrupt data silently
- Schema enforcement at write time; new columns from source flow through automatically
- Same pipeline: **batch or streaming** – one keyword change

**Replaces:** SSIS · Informatica · Glue · hand-rolled Spark jobs

---

## Slide 7 – Act 4: AI You Can Trust

**Title:** AI That's Governed, Auditable, and SR 11-7 Ready

**Left column – AI Functions as SQL Primitives:**

- `ai_classify(narrative, ARRAY('fraud','fees','loan_servicing',...))` – no model training, no API keys
- `ai_extract(text, schema)` – structured fields from free-text KYC documents
- PEP matches surfaced automatically from plain-prose narratives
- Every call audited in Unity Catalog system tables

**Right column – MLflow + Model Risk Management:**

- Model registered in Unity Catalog – same permissions, lineage, and audit as data
- SR 11-7 documentation in the model description: intended use, limitations, performance thresholds, review cadence
- Training data lineage: two clicks from the model to the source rows it trained on
- `@champion` alias for production promotion; challenger pattern built in
- Lakehouse Monitoring: feature drift detection on the inference table, wire alerts to PagerDuty or email

---

## Slide 8 – Act 5: Self-Service for the Business

**Title:** The Risk Officer's Morning Is Now One Browser Tab

**Left column – AI/BI Dashboard (for the Risk Officer):**

- Four KPIs at a glance: open AML alerts · high-KYC customers · HMDA approval rate · complaints this month
- Every widget traces back to source via native lineage – no *"where does that number come from?"* tickets
- Fair Lending heatmap: approval rates by race, gender, ethnicity – statistically filtered, drill-through to loan level

**Right column – Genie (for everyone else):**

- Natural language: *"Show me top 10 customers by AML alert dollar amount this quarter"*
- SQL always shown – auditable, copyable, schedulable as a job
- Follow-up: *"How does the loan approval rate for home purchase compare across races?"*
- Same governed views. Same access controls. The platform enforces the rules.

---

## Slide 9 – Persona Add-On: Data Engineer (4 min, optional)

**Title:** For Your Data Team: Code-First, Governed by Default

**What the demo shows:**

- Open `01_lakeflow_pipeline.py` in code view – `@dlt.table`, `@dlt.expect_or_drop`, `table_properties` in ~20 lines per table. No DDL. No mapping sheets.
- Switch to the Pipeline DAG – dependency graph inferred automatically from `dlt.read()` calls. You didn't draw it.
- Catalog Explorer lineage on `gold.aml_alerts` – you called `dlt.read('silver.transactions')`, the catalog recorded it for free. Same lineage appears on the ML model.
- `databricks.yml` – one config, two commands to production: `databricks bundle deploy --target prod`
- System Tables – `system.lakeflow.pipeline_events` and `system.lakeflow.expectations` for full pipeline observability

**The message:** Declare in Python. Deploy with one command. Lineage and observability are free.

---

## Slide 10 – Persona Add-On: Marketing Analyst (4 min, optional)

**Title:** For Marketing: Customer Intelligence, No Ticket Required

**What the demo shows:**

- Genie: *"Show me customers aged 25–45 with a mortgage and no complaints in the last 12 months, ranked by balance"* → cross-sell targets, SQL shown, schedulable as a weekly CRM export
- Follow-up: *"How many of those are in California and Arizona?"* – session context remembered, no re-filtering needed
- `silver.complaints_classified` – 500 complaints classified by `ai_classify` into themes (fees, loan_servicing, account_access, credit_reporting) and severity. Real-time voice-of-the-customer signal.
- If `fees` complaints trend up before a campaign launches, marketing sees it in the same platform where they build segments

**The message:** Same governed data layer. PII masking enforced. Marketing self-serves safely – no IT ticket, no separate masked copy.

---

## Slide 11 – Next Steps

**Title:** Your Path from Demo to Production

**Step 1 – 30-Minute Mapping Call**
Your data + risk leadership, our Solution Architect. Identify three real source feeds to light up first.

**Step 2 – 2-Week Solution Accelerator**
Stand up this demo on your real AML transaction data + a sample of complaints. We bring the patterns, you bring the data.

**Step 3 – Production Build (6–10 Weeks)**
Full GRC lakehouse build, parallel to your existing systems. Same patterns you saw today – applied to your real data.

---

**Account Team**

| Role | Name | Contact |
|---|---|---|
| Account Executive | Katie Trevino | katie.trevino@databricks.com |
| Solution Architect | Nikhil Suthar | nikhil.suthar@databricks.com |
| Industry SME, FinServ | Duffy Walsh | duffy.walsh@databricks.com |
