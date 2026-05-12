# TodayBank GRC Demo – Data Engineer Talk Track (4 min)

A focused persona demo for data engineers. Run this standalone or splice it into Act 3 of the main 30-min demo.

**Audience:** Data engineers, platform engineers, anyone who builds or maintains pipelines
**Hook:** Show code first – the DAG is the reward, not the starting point

---

## Pre-flight

Open two tabs before you start:
1. Notebook `01_lakeflow_pipeline.py` (code view, not pipeline DAG)
2. Catalog Explorer at `todaybank_grc_demo.gold.aml_alerts` (Lineage tab ready to open)

---

## Talk track

### 0:00 – Open with the code, not the DAG (1 min)

Open `01_lakeflow_pipeline.py` in code view.

> "I want to show you what a production-grade GRC pipeline looks like at Databricks – starting with the code, not a screenshot.
>
> Here's `silver_transactions`. A `@dlt.table` decorator declares the output table, its schema, its properties. Then `@dlt.expect_or_drop` – one line – says: drop any row where `amount_usd` is zero or negative. Below that, the transformation logic. That's it. No DDL, no CREATE TABLE IF NOT EXISTS, no SSIS mapping sheet."

Scroll to `gold_aml_alerts`.

> "Here's the AML alert generation logic – about 20 lines. Two patterns: structuring candidates and high-risk-geography wires. A `unionByName` at the end. The table property `regulatory: BSA_AML` tags this table for downstream compliance reporting. When your BSA officer wants every BSA-relevant table in the catalog: one SQL query on `information_schema` against that property. You wrote the tag once, in code."

---

### 1:00 – Switch to the Pipeline DAG (45 sec)

Open the Lakeflow Pipeline DAG view.

> "Now look at what Databricks generated from that code. Bronze → Silver → Gold. Dependency graph, resolved automatically. You didn't draw this – you declared tables and reads; the runtime inferred the graph.
>
> Green checkmarks mean expectations passed. Click into one."

Click an expectation node.

> "Two rows dropped on `valid_email`. They're quarantined in a side table, not silently passed downstream and not crashing the job. The same `expect_or_drop` line that you saw in the code produced this. If you want to investigate: `SELECT * FROM todaybank_grc_demo.system.expectations WHERE status = 'DROPPED'` – it's a real table."

---

### 1:45 – Unity Catalog lineage is automatic, not a side project (1 min)

Switch to Catalog Explorer → `todaybank_grc_demo.gold.aml_alerts` → Lineage tab.

> "Here's what most banks spend months building in Collibra or Alation. The lineage from `bronze.raw_transactions` all the way into the Gold AML table – captured for free, because Lakeflow Pipelines talk natively to Unity Catalog.
>
> You didn't instrument anything. You didn't fill in a metadata form. You called `dlt.read('silver.transactions')` and the catalog recorded it.
>
> Same lineage shows up on the ML model – open the MLflow registry and you'll see training lineage back to the same silver tables. One governance model, one lineage graph, no extra tools."

---

### 2:45 – Deployment in one command (45 sec)

Open `databricks.yml` in the file browser.

> "Deployment is a DAB – Databricks Asset Bundle. This YAML file describes the pipeline, the notebooks, the catalog target. To go from dev to production:
>
> ```bash
> databricks bundle deploy --target prod
> databricks bundle run setup_job --target prod
> ```
>
> That's your CI/CD hook. Point your GitHub Actions or GitLab runner at those two commands. The bundle handles catalog name interpolation across environments – your dev pipeline writes to `todaybank_grc_demo_dev`, prod writes to `todaybank_grc_demo`. No find-and-replace in YAML files."

---

### 3:30 – Pipeline observability via System Tables (30 sec)

Stay in the SQL editor or mention verbally.

> "Last thing – observability. Every pipeline run lands in System Tables: `system.lakeflow.pipeline_events` for run history, `system.lakeflow.expectations` for per-expectation pass/fail rates over time. Wire these to a Grafana dashboard or a Databricks alert: if the structuring-row drop rate spikes, you get paged. You don't need a separate data quality tool.
>
> The whole pattern – declare in Python, run on Lakeflow, govern in Unity Catalog, observe in System Tables – is the same whether you're running one pipeline or fifty."

---

## Q&A hooks

| Common DE question | Crisp answer |
|---|---|
| "Can we use Terraform instead of DABs?" | DABs and Terraform are complementary – DABs own the analytics assets (pipelines, notebooks, jobs), Terraform owns workspace-level infra (clusters, permissions). |
| "What if our source is Kafka, not batch files?" | `dlt.read_stream` instead of `dlt.read` – same decorator, same expectations. Streaming and batch coexist in one pipeline graph. |
| "How do we version the pipeline code?" | It's Python in Git – same PR workflow as any code. DABs deploy from a branch or tag. |
| "What about schema drift from the source system?" | `schema_evolution = "addNewColumns"` as a pipeline setting – new columns from source propagate automatically. Incompatible type changes fail loudly. |
| "Can we run unit tests on the DLT logic?" | Yes – extract transformation logic into plain PySpark functions, test with pytest. The `@dlt.table` wrapper is a thin decorator; the function is testable in isolation. |
