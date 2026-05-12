# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Lakeflow Pipeline – Bronze → Silver → Gold
# MAGIC
# MAGIC Wire this notebook up as a **Delta Live Tables / Lakeflow Pipeline**. It declaratively builds the GRC data marts from the bronze tables created in notebook 00.
# MAGIC
# MAGIC **Demo points to hit while showing the pipeline DAG:**
# MAGIC 1. Schema is enforced declaratively (no SSIS-style mapping)
# MAGIC 2. **Expectations** catch data quality issues at pipeline runtime, not after
# MAGIC 3. Streaming + batch coexist in the same pipeline
# MAGIC 4. Lineage is captured automatically (no separate Collibra/Alation needed)

# COMMAND ----------

import dlt
from pyspark.sql import functions as F

CATALOG = spark.conf.get("CATALOG", "todaybank_grc_demo")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver layer – cleansed, conformed, PII-aware

# COMMAND ----------

@dlt.table(
    name="silver.customers",
    comment="Cleansed customer master. PII columns retained but tagged for masking via dynamic views.",
    table_properties={"quality": "silver", "pii": "true"},
)
@dlt.expect_or_drop("valid_customer_id", "customer_id IS NOT NULL")
@dlt.expect("valid_email", "email RLIKE '^[^@]+@[^@]+\\.[^@]+$'")
@dlt.expect("recent_account", "account_open_date >= '2018-01-01'")
def silver_customers():
    return (
        dlt.read(f"{CATALOG}.bronze.raw_customers")
        .withColumn("full_name", F.concat_ws(" ", "first_name", "last_name"))
        .withColumn("age", F.floor(F.datediff(F.current_date(), "date_of_birth") / 365.25))
    )

# COMMAND ----------

@dlt.table(
    name="silver.transactions",
    comment="Transactions with derived risk features (high-risk geo flag, structuring window).",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("valid_amount", "amount_usd > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_transactions():
    HIGH_RISK = ["IR", "KP", "SY", "VE", "CU", "RU"]
    return (
        dlt.read(f"{CATALOG}.bronze.raw_transactions")
        .withColumn("is_high_risk_geo", F.col("counterparty_country").isin(HIGH_RISK))
        .withColumn("is_structuring_candidate",
                    (F.col("amount_usd") >= 9000) & (F.col("amount_usd") < 10000) & (F.col("channel") == "atm"))
        .withColumn("transaction_date", F.to_date("transaction_ts"))
    )

# COMMAND ----------

@dlt.table(
    name="silver.loans",
    comment="Loan applications with HMDA fields joined from customer demographics.",
    table_properties={"quality": "silver", "pii": "regulatory_HMDA"},
)
@dlt.expect("valid_fico", "fico BETWEEN 300 AND 850")
@dlt.expect("valid_dti", "dti BETWEEN 0 AND 100")
def silver_loans():
    customers = dlt.read(f"{CATALOG}.bronze.raw_customers").select(
        "customer_id", "race", "ethnicity", "gender"
    )
    return (
        dlt.read(f"{CATALOG}.bronze.raw_loans")
        .join(customers, on="customer_id", how="left")
    )

# COMMAND ----------

@dlt.table(
    name="silver.complaints",
    comment="Customer complaints. Theme classification added in notebook 02 via ai_classify.",
    table_properties={"quality": "silver"},
)
def silver_complaints():
    return dlt.read(f"{CATALOG}.bronze.raw_complaints")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold layer – business-ready marts

# COMMAND ----------

@dlt.table(
    name="gold.aml_alerts",
    comment="AML candidate alerts. Aggregated suspicious patterns by customer in a 24h window.",
    table_properties={"quality": "gold", "regulatory": "BSA_AML"},
)
def gold_aml_alerts():
    txns = dlt.read("silver.transactions")
    structuring = (
        txns.filter("is_structuring_candidate")
        .groupBy("customer_id", "transaction_date")
        .agg(
            F.count("*").alias("structuring_count"),
            F.sum("amount_usd").alias("structuring_total"),
        )
        .filter("structuring_count >= 2")
        .withColumn("alert_type", F.lit("STRUCTURING"))
    )
    high_risk_wires = (
        txns.filter("is_high_risk_geo AND amount_usd >= 10000")
        .groupBy("customer_id", "transaction_date")
        .agg(
            F.count("*").alias("structuring_count"),
            F.sum("amount_usd").alias("structuring_total"),
        )
        .withColumn("alert_type", F.lit("HIGH_RISK_GEO_WIRE"))
    )
    return structuring.unionByName(high_risk_wires)

# COMMAND ----------

@dlt.table(
    name="gold.hmda_summary",
    comment="HMDA approval-rate summary by demographic group. Used by Compliance Officer for fair-lending review.",
    table_properties={"quality": "gold", "regulatory": "HMDA_ECOA"},
)
def gold_hmda_summary():
    return (
        dlt.read("silver.loans")
        .groupBy("race", "ethnicity", "gender", "loan_purpose")
        .agg(
            F.count("*").alias("application_count"),
            F.sum(F.when(F.col("action_taken") == "Approved", 1).otherwise(0)).alias("approved_count"),
            F.sum(F.when(F.col("action_taken") == "Denied", 1).otherwise(0)).alias("denied_count"),
            F.avg("amount_usd").alias("avg_loan_amount"),
            F.avg("fico").alias("avg_fico"),
        )
        .withColumn("approval_rate", F.col("approved_count") / F.col("application_count"))
    )

# COMMAND ----------

@dlt.table(
    name="gold.customer_risk_360",
    comment="One-row-per-customer risk profile combining KYC tier, AML alerts, complaint count.",
    table_properties={"quality": "gold"},
)
def gold_customer_risk_360():
    customers = dlt.read("silver.customers").select(
        "customer_id", "full_name", "state", "kyc_risk_tier", "balance_usd"
    )
    alerts = (
        dlt.read("gold.aml_alerts")
        .groupBy("customer_id")
        .agg(F.count("*").alias("aml_alert_count"),
             F.sum("structuring_total").alias("aml_alert_total_usd"))
    )
    complaints = (
        dlt.read("silver.complaints")
        .groupBy("customer_id")
        .agg(F.count("*").alias("complaint_count"))
    )
    return (
        customers
        .join(alerts, on="customer_id", how="left")
        .join(complaints, on="customer_id", how="left")
        .fillna(0, subset=["aml_alert_count", "aml_alert_total_usd", "complaint_count"])
    )
