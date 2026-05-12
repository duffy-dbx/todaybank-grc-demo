# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Governance Walkthrough — Lineage, Masking, Audit
# MAGIC
# MAGIC The "Act 2" notebook. Doesn't build new tables — it surfaces what UC already gives you for free, plus creates dynamic views that mask PII based on group membership.
# MAGIC
# MAGIC **Demo points:**
# MAGIC 1. Catalog tree + tags (already created in notebook 00)
# MAGIC 2. Lineage from a Gold widget back to a source row — Catalog Explorer click-through
# MAGIC 3. Dynamic views: SSN visible to `risk_analysts` group, masked for everyone else
# MAGIC 4. Audit queries against `system.access.audit`

# COMMAND ----------

dbutils.widgets.text("catalog", "axos_grc_demo", "Catalog")
dbutils.widgets.text("privileged_group", "risk_analysts", "Group allowed to see PII")
CATALOG = dbutils.widgets.get("catalog")
PRIV_GROUP = dbutils.widgets.get("privileged_group")
spark.sql(f"USE CATALOG {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dynamic view with conditional PII masking
# MAGIC
# MAGIC `is_account_group_member()` returns true if the running user is in the group. Members of `risk_analysts` see real values; everyone else sees masks.

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.silver.customers_v AS
SELECT
  customer_id,
  first_name,
  last_name,
  full_name,
  CASE WHEN is_account_group_member('{PRIV_GROUP}') THEN email ELSE 'REDACTED' END AS email,
  CASE WHEN is_account_group_member('{PRIV_GROUP}') THEN phone ELSE 'REDACTED' END AS phone,
  CASE WHEN is_account_group_member('{PRIV_GROUP}') THEN ssn ELSE CONCAT('XXX-XX-', RIGHT(ssn, 4)) END AS ssn,
  CASE WHEN is_account_group_member('{PRIV_GROUP}') THEN date_of_birth ELSE NULL END AS date_of_birth,
  city,
  state,
  zip,
  race,
  ethnicity,
  gender,
  kyc_risk_tier,
  account_open_date,
  balance_usd,
  age
FROM {CATALOG}.silver.customers
""")

print(f"✓ Created {CATALOG}.silver.customers_v with dynamic masking on PII")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Row-level security: customers can only see customers from their assigned region
# MAGIC
# MAGIC In production, `current_user()` would be matched to a region mapping table. For demo simplicity, we show the pattern.

# COMMAND ----------

# Row filter: best-effort. SET ROW FILTER requires a Delta table, but Lakeflow Pipelines
# sometimes create silver.customers as a streaming-table view depending on the mode.
# In that case we apply the filter to bronze.raw_customers (a regular Delta table) instead.
try:
    spark.sql(f"""
    CREATE OR REPLACE FUNCTION {CATALOG}.silver.region_filter(state STRING)
    RETURN
      is_account_group_member('risk_admins')
      OR (is_account_group_member('risk_analysts_west') AND state IN ('CA', 'WA', 'OR', 'AZ'))
      OR (is_account_group_member('risk_analysts_east') AND state IN ('NY', 'NJ', 'MA', 'PA'))
    """)
    try:
        spark.sql(f"ALTER TABLE {CATALOG}.silver.customers SET ROW FILTER {CATALOG}.silver.region_filter ON (state)")
        print("✓ Row filter attached to silver.customers")
    except Exception:
        spark.sql(f"ALTER TABLE {CATALOG}.bronze.raw_customers SET ROW FILTER {CATALOG}.silver.region_filter ON (state)")
        print("✓ Row filter attached to bronze.raw_customers (silver.customers is a streaming-table view)")
except Exception as e:
    print(f"WARN: row filter skipped: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Audit log queries
# MAGIC
# MAGIC These run against the **real** `system.access.audit` table — not the synthetic `bronze.raw_audit_events` we generated.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Who has read the customers table in the last 7 days?
# MAGIC SELECT
# MAGIC   event_time,
# MAGIC   user_identity.email AS user_email,
# MAGIC   action_name,
# MAGIC   request_params.full_name_arg AS table_name
# MAGIC FROM system.access.audit
# MAGIC WHERE service_name = 'unityCatalog'
# MAGIC   AND action_name IN ('getTable', 'queryTable')
# MAGIC   AND request_params.full_name_arg LIKE 'axos_grc_demo.silver.customers%'
# MAGIC   AND event_time > current_date() - INTERVAL 7 DAYS
# MAGIC ORDER BY event_time DESC
# MAGIC LIMIT 50

# COMMAND ----------

# MAGIC %sql
# MAGIC -- AI Function invocations — every call to ai_classify, ai_extract, ai_query is audited
# MAGIC SELECT
# MAGIC   event_time,
# MAGIC   user_identity.email AS user_email,
# MAGIC   action_name,
# MAGIC   request_params
# MAGIC FROM system.access.audit
# MAGIC WHERE service_name = 'modelServing'
# MAGIC   AND event_time > current_date() - INTERVAL 7 DAYS
# MAGIC ORDER BY event_time DESC
# MAGIC LIMIT 25

# COMMAND ----------

# MAGIC %md
# MAGIC ## Lineage demonstration — programmatic
# MAGIC
# MAGIC In the live demo, click through Catalog Explorer for the visual. For automation, query the lineage system tables.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   source_table_full_name,
# MAGIC   target_table_full_name,
# MAGIC   event_time
# MAGIC FROM system.access.table_lineage
# MAGIC WHERE source_table_catalog = 'axos_grc_demo'
# MAGIC    OR target_table_catalog = 'axos_grc_demo'
# MAGIC ORDER BY event_time DESC
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %md
# MAGIC ## Done
# MAGIC
# MAGIC Notebooks complete. Now import the dashboard from `dashboards/axos_grc_dashboard.lvdash.json` and create a Genie space using the views set up in `sql/genie_space_setup.sql`.
