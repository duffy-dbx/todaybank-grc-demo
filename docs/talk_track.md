# TodayBank GRC Operations Hub – Talk Track

Speaker notes per act. Times are presenter-pace, not screen-time.

---

## Pre-flight

**Open in tabs, in this order:**
1. Catalog Explorer at `todaybank_grc_demo`
2. Notebook `01_lakeflow_pipeline.py` (pipeline DAG view)
3. MLflow registry view of `todaybank_grc_demo.gold.aml_risk_model`
4. AI/BI Dashboard "TodayBank GRC Operations Hub"
5. Genie space "TodayBank GRC Operations Hub"
6. Notebook `04_governance_walkthrough.py` (for the audit query)

**Open by greeting the room and asking one warm-up question:**
> "Before I run the demo – quick show of hands. How many of you currently use three or more separate systems to handle AML monitoring, fair-lending review, and complaint analytics?"

(Most hands go up. That sets up Act 1.)

---

## Act 1 – The Problem (3 min)

**Goal:** anchor the pain. Don't show the screen yet.

**Talk track:**

> "Here's the day in the life of an TodayBank Risk Officer that you've probably seen.
>
> She comes in Monday morning. Her AML system flagged 200 alerts overnight – but she has to log into a separate KYC system to see who the customer actually is, then a third complaints system to see if any of those flagged customers also complained recently. By the time she has a full picture, half her morning is gone.
>
> Three systems. Three logins. Three different governance models. And when her boss asks 'how do you know the AML model isn't biased?' – she has no good answer because the model lives outside her data platform entirely.
>
> What I'm going to show you in the next 25 minutes is how the same data, the same governance model, and the same AI layer can do all three things – and tell her exactly where every number on her dashboard came from."

**Transition:** "Let me start with what makes this possible – Unity Catalog."

---

## Act 2 – Governed Foundation (5 min)

**Goal:** show that one governance layer covers tables, files, models, dashboards, and AI.

**Steps:**

1. **Open Catalog Explorer** at `todaybank_grc_demo`.
   > "This is everything in our TodayBank GRC demo – bronze raw landing, silver cleansed, gold business-ready, plus an audit schema. Notice that it's one tree."

2. **Click `bronze.raw_customers` → "Tags" tab.**
   > "We've already classified PII columns and HMDA-regulatory columns. These tags drive masking, data discovery, and audit reporting – they're not labels in a wiki, they're enforced."

3. **Click "Sample Data" – show real values.** Then run:
   ```sql
   SELECT * FROM todaybank_grc_demo.silver.customers_v LIMIT 5;
   ```
   > "Same underlying table, different view. Because I'm not in the `risk_analysts` group, the SSN, email, phone, and DOB are masked. A risk analyst running the same query sees real values. No copy of the data, no separate masked database."

4. **Click `gold.aml_alerts` → "Lineage" tab.**
   > "Here's the upstream lineage. This Gold table came from `silver.transactions`, which came from `bronze.raw_transactions`. When the regulator asks 'where did this number come from?' – that's the answer, and it's automatic. No Collibra, no Alation, no manual stewardship."

5. **Open `04_governance_walkthrough.py` and run the audit-log cell.**
   > "And here's every read against the customers table in the last 7 days. We log who saw it, when, from where. Same audit table tracks AI Function calls – every `ai_classify` invocation lands here."

**Transition:** "OK, governance is the foundation. Now let me show how data actually gets into Gold."

---

## Act 3 – Pipelines That Just Work (7 min)

**Goal:** show that Lakeflow Pipelines replace SSIS / Informatica / Glue with a declarative, observable pipeline.

**Steps:**

1. **Open the Lakeflow Pipeline DAG view** of `01_lakeflow_pipeline.py`.
   > "This is one Lakeflow Pipeline. Bronze → Silver → Gold. Five tables in Silver, three in Gold. Look at the green checkmarks – those are data quality expectations passing. The yellow ones – let me click into one."

2. **Click an Expectation – show the dropped/quarantined rows.**
   > "We declared that emails must match a regex. Two rows didn't. They're quarantined, not silently corrupted. This is what `expect_or_drop` does. Compare that to a typical SSIS package: a failed row either crashes the package or silently passes corrupt data downstream. Lakeflow handles it as a first-class concept."

3. **Click into `silver_transactions` → "Schema" tab.**
   > "Schema is enforced at write time. If our source system adds a new column tomorrow, the pipeline doesn't break – schema evolution is built in. If they change a column type incompatibly, we fail loudly, not silently."

4. **Show the code for `gold.aml_alerts`:**
   ```python
   @dlt.table(table_properties={"regulatory": "BSA_AML"})
   def gold_aml_alerts():
       structuring = ...
       high_risk_wires = ...
       return structuring.unionByName(high_risk_wires)
   ```
   > "This is the entire AML alert generation logic. About 15 lines of code. The `regulatory` table property tags the table for downstream reporting – your BSA officer can find every BSA-relevant table with one query."

5. **(Optional) Click `silver_transactions` → click into the streaming variant.**
   > "Same pipeline can run on a schedule for batch, or continuously for streaming. The transition is one keyword."

**Transition:** "We've got governed data flowing into Gold. Now what about the unstructured stuff – customer complaints, KYC narratives – and the AI layer?"

---

## Act 4 – AI You Can Trust (8 min)

**Goal:** show that AI is governed, auditable, and replaces the customer's lost RAG/Document Audit UCOs.

### Part A – AI Functions (3 min)

1. **Open a SQL editor and run:**
   ```sql
   SELECT
     complaint_id,
     LEFT(narrative, 80) AS snippet,
     ai_classify(narrative, ARRAY('fraud','fees','loan_servicing','discrimination','account_access','credit_reporting','deposits','other')) AS theme
   FROM todaybank_grc_demo.bronze.raw_complaints
   LIMIT 10;
   ```
   > "That's it. No model training, no prompt engineering, no API key management. `ai_classify` is a SQL primitive. The model behind it is governed by Unity Catalog – every call lands in the audit log."

2. **Show `silver.complaints_classified` already populated.**
   > "We classified all 500 complaints in seconds. Notice we added a second classification: severity. Same pattern. An analyst could write this query without ever leaving DBSQL."

3. **Quick `ai_extract` example – show `gold.kyc_pep_matches`:**
   > "Same pattern, different verb. `ai_extract` pulls structured fields out of free-text KYC narratives. Look – these PEP matches were extracted from documents that came in as plain prose. Your Commercial Lending Document Audit team can finally automate the document review they've been doing manually."

### Part B – MLflow + MRM (3 min)

1. **Open MLflow registry view** of `todaybank_grc_demo.gold.aml_risk_model`.
   > "Here's our AML risk-scoring model. Notice it's in the same catalog as the data – it's a UC object, not a sidecar. That means lineage, permissions, and audit are all unified."

2. **Click into the model description.**
   > "This is the SR 11-7 model documentation. Intended use, limitations, performance threshold, owner, review cadence. Anyone in the bank – including your model risk validator – can read this without asking the data scientist."

3. **Click "Lineage" on the model.**
   > "And here's what the model trained on. If the training data changes upstream, you'll see it here. If a regulator wants to know what features are in production: this view, two clicks."

4. **Show the `@champion` alias.**
   > "We promote a model to production by setting an alias, not by overwriting a file. We can run a challenger in parallel and swap with one command. This is how Model Risk Management is supposed to work."

### Part C – Drift monitoring (2 min)

1. **Catalog Explorer → `gold.aml_risk_scores` → "Quality" tab.**
   > "Lakehouse Monitoring tracks drift on the inference table. If our customer base shifts – say, more international wires in Q3 – we see the feature distribution change here. We can wire alerts to PagerDuty or email."

2. **(Skip if running long)** – but mention: "AI Gateway sits between models and consumers. Rate limits, PII redaction at the request layer, full audit. Same governance umbrella."

**Transition:** "Last piece – making this useful for the people who don't write SQL all day."

---

## Act 5 – Self-service for the Business (5 min)

**Goal:** show AI/BI Dashboard + Genie. This is the closer for the BI modernization UCOs.

**Steps:**

1. **Open the TodayBank GRC Operations Hub dashboard.**
   > "This is what the Risk Officer sees Monday morning. Four KPIs at the top – open AML alerts, high-KYC customers, HMDA approval rate, complaints this month. Each tile is one click away from the underlying data."

2. **Hover a KPI – show the lineage popup.**
   > "Click the menu – 'View lineage'. Same lineage we saw in Act 2. Every dashboard widget traces back to source. No more 'where does that number come from?' tickets."

3. **Click the Fair Lending heatmap.**
   > "Approval rates by race, ethnicity, gender, loan purpose. We filter to 20+ applications per cell for statistical relevance. If a cell turns red, the Compliance Officer has the conversation she needs to have – backed by the underlying loan-level data, two clicks away."

4. **Switch to the Genie space.**
   > "And here's where it gets interesting. The dashboard is for the Risk Officer. Genie is for everyone else – analysts who don't want to wait for IT to build them a dashboard."

5. **Type a question into Genie:**
   > "Show me top 10 customers by AML alert dollar amount this quarter."

   Wait for response. Click "Show SQL".
   > "Notice that Genie doesn't just give the answer – it shows the SQL it ran. The analyst can verify it, copy it, schedule it as a job. This is auditable AI."

6. **Type a follow-up:**
   > "How does the loan approval rate for home purchase compare across races?"

   Wait. Show response.
   > "Same governed views. Same access controls. The analyst doesn't need to know SQL or schemas – but the platform does, and the platform enforces the rules."

**Close:**
> "So – three pillars. Governance, Risk, Compliance. One platform, one governance model, one audit trail. The Risk Officer's morning that started this presentation? It's a single browser tab now.
>
> The good news for TodayBank is you already have most of this. You're live on the lakehouse. You have AI/BI. You're evaluating Genie. What we'd love to do next is help you stand up exactly this kind of unified GRC view on your real data – and the patterns you saw today are the same patterns we'd use."

---

## Common questions + crisp answers

| Q | A |
|---|---|
| "Is the AI model auditable for SR 11-7?" | Yes – every model is registered with documentation, lineage, performance metrics, and review cadence. Every inference logs to system tables. |
| "Can our compliance team access this without help from data engineers?" | Yes – Genie + AI/BI Dashboards are explicitly designed for that. Permissions are inherited from Unity Catalog. |
| "What about real-time alerts?" | Lakeflow Pipelines run streaming. AML alerts can be generated continuously. Wire into PagerDuty / SNS / email via Databricks Workflows. |
| "Cost?" | Serverless SQL + serverless compute keeps cost variable. We can size for your transaction volume – typical mid-size bank GRC pattern is 4–10 DBU/hour active. |
| "Replace our existing AML vendor?" | Not necessarily – the demo shows the *data + AI + governance layer.* Many banks keep a tier-1 AML vendor for SAR filing and use Databricks for the analytics + investigator UX layer. |
| "How long would this take to stand up at TodayBank?" | The demo footprint took about 15 minutes to deploy. A production version with your real source feeds is typically a 6–10 week engagement, parallel to your existing systems. |

---

## What to leave behind

- This README + the demo flow document
- The `customer_takeaways.md` one-pager
- A 30-min follow-up with the Risk + Data leadership to map the demo back to their real data sources
