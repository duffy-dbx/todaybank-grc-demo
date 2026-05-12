# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · AI Functions – Classify Complaints & Extract from KYC
# MAGIC
# MAGIC Demonstrates Databricks **AI Functions** (`ai_classify`, `ai_extract`) running in SQL against unstructured text – no model training required, governed via Unity Catalog, audited like any other query.
# MAGIC
# MAGIC **Demo points:**
# MAGIC 1. AI as a SQL primitive – analysts use it without leaving DBSQL
# MAGIC 2. Governed via UC: every invocation logs to `system.access.audit`
# MAGIC 3. Replaces the lost RAG/LLM UCO with a simpler, auditable pattern

# COMMAND ----------

dbutils.widgets.text("catalog", "todaybank_grc_demo", "Catalog")
CATALOG = dbutils.widgets.get("catalog")
spark.sql(f"USE CATALOG {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Classify customer complaints into themes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE silver.complaints_classified AS
# MAGIC SELECT
# MAGIC   complaint_id,
# MAGIC   customer_id,
# MAGIC   received_date,
# MAGIC   channel,
# MAGIC   narrative,
# MAGIC   ai_classify(
# MAGIC     narrative,
# MAGIC     ARRAY('fraud', 'fees', 'loan_servicing', 'discrimination', 'account_access', 'credit_reporting', 'deposits', 'other')
# MAGIC   ) AS theme,
# MAGIC   ai_classify(
# MAGIC     narrative,
# MAGIC     ARRAY('low', 'medium', 'high', 'urgent')
# MAGIC   ) AS severity
# MAGIC FROM bronze.raw_complaints

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Validate: theme distribution
# MAGIC SELECT theme, COUNT(*) AS n
# MAGIC FROM silver.complaints_classified
# MAGIC GROUP BY theme
# MAGIC ORDER BY n DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract structured entities from KYC narratives

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE silver.kyc_extracted AS
# MAGIC SELECT
# MAGIC   kyc_doc_id,
# MAGIC   customer_id,
# MAGIC   document_date,
# MAGIC   narrative,
# MAGIC   ai_extract(
# MAGIC     narrative,
# MAGIC     ARRAY('occupation', 'source_of_funds', 'pep_status', 'sanctions_status', 'annual_income_usd', 'risk_tier')
# MAGIC   ) AS extracted
# MAGIC FROM bronze.raw_kyc_docs

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   kyc_doc_id,
# MAGIC   extracted.occupation,
# MAGIC   extracted.source_of_funds,
# MAGIC   extracted.pep_status,
# MAGIC   extracted.sanctions_status
# MAGIC FROM silver.kyc_extracted
# MAGIC WHERE extracted.pep_status RLIKE '(?i)match'
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build the gold complaint-themes mart

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.complaint_themes AS
# MAGIC SELECT
# MAGIC   theme,
# MAGIC   severity,
# MAGIC   DATE_TRUNC('month', received_date) AS month,
# MAGIC   COUNT(*) AS complaint_count,
# MAGIC   COUNT(DISTINCT customer_id) AS unique_customers
# MAGIC FROM silver.complaints_classified
# MAGIC GROUP BY theme, severity, DATE_TRUNC('month', received_date)
# MAGIC ORDER BY month DESC, complaint_count DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- For Act 4 – show that PEP matches are surfaced and reviewable
# MAGIC CREATE OR REPLACE TABLE gold.kyc_pep_matches AS
# MAGIC SELECT
# MAGIC   k.kyc_doc_id,
# MAGIC   k.customer_id,
# MAGIC   c.full_name,
# MAGIC   k.document_date,
# MAGIC   k.extracted.occupation,
# MAGIC   k.extracted.source_of_funds,
# MAGIC   k.extracted.pep_status
# MAGIC FROM silver.kyc_extracted k
# MAGIC JOIN silver.customers c ON c.customer_id = k.customer_id
# MAGIC WHERE k.extracted.pep_status RLIKE '(?i)match'

# COMMAND ----------

# MAGIC %md
# MAGIC ## Done
# MAGIC
# MAGIC Next: **`03_aml_model_mlflow.py`** trains and registers an AML risk-scoring model with full MLflow lineage.
