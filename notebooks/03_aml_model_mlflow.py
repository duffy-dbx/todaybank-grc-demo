# Databricks notebook source
# MAGIC %pip install -q mlflow scikit-learn
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %md
# MAGIC # 03 · AML Risk Model — MLflow + Model Registry
# MAGIC
# MAGIC Trains a simple AML risk-scoring model on transaction features and registers it to **Unity Catalog Model Registry** with full lineage to source tables.
# MAGIC
# MAGIC **Demo points (Model Risk Management / SR 11-7):**
# MAGIC 1. Model artifact lives in UC, governed alongside the data
# MAGIC 2. Lineage is automatic — UC shows which tables fed the model
# MAGIC 3. Champion/Challenger via aliases (`@champion`, `@challenger`)
# MAGIC 4. Lakehouse Monitoring tracks drift on the inference table
# MAGIC 5. AI Gateway provides rate limits, audit, and PII redaction at the endpoint

# COMMAND ----------

dbutils.widgets.text("catalog", "axos_grc_demo", "Catalog")
CATALOG = dbutils.widgets.get("catalog")
spark.sql(f"USE CATALOG {CATALOG}")

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
import pandas as pd
from pyspark.sql import functions as F
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

mlflow.set_registry_uri("databricks-uc")
MODEL_NAME = f"{CATALOG}.gold.aml_risk_model"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build training set
# MAGIC
# MAGIC We engineer features from `silver.transactions` and label rows that match suspicious patterns (`is_high_risk_geo OR is_structuring_candidate`).

# COMMAND ----------

features_df = spark.sql(f"""
    SELECT
      customer_id,
      COUNT(*) AS txn_count_30d,
      SUM(amount_usd) AS total_amount_30d,
      AVG(amount_usd) AS avg_amount_30d,
      MAX(amount_usd) AS max_amount_30d,
      SUM(CASE WHEN is_high_risk_geo THEN 1 ELSE 0 END) AS high_risk_geo_count,
      SUM(CASE WHEN is_structuring_candidate THEN 1 ELSE 0 END) AS structuring_count,
      SUM(CASE WHEN channel = 'wire_intl' THEN 1 ELSE 0 END) AS intl_wire_count,
      SUM(CASE WHEN channel = 'atm' THEN amount_usd ELSE 0 END) AS atm_total_30d,
      MAX(CASE WHEN is_high_risk_geo OR is_structuring_candidate THEN 1 ELSE 0 END) AS label
    FROM silver.transactions
    GROUP BY customer_id
""").toPandas()

X = features_df.drop(columns=["customer_id", "label"])
y = features_df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train + log to MLflow

# COMMAND ----------

with mlflow.start_run(run_name="aml_gbm_v1") as run:
    mlflow.autolog(disable=True)  # we'll log explicitly for clarity in the demo

    model = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)

    mlflow.log_param("algorithm", "GradientBoostingClassifier")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 4)
    mlflow.log_metric("roc_auc", auc)
    mlflow.log_metric("training_rows", len(X_train))
    mlflow.log_metric("positive_rate", float(y.mean()))

    # SR 11-7 documentation goes in the model description
    description = (
        "AML transaction-pattern risk model.\n"
        "Intended use: scoring customers for elevated AML review priority.\n"
        "Training data: silver.transactions, 12-month window.\n"
        "Features: txn_count, amount aggregates, channel mix, high-risk-geo count, structuring candidates.\n"
        "Limitations: does NOT replace human SAR review. Outputs are advisory only.\n"
        "Owner: Risk Analytics. Review cadence: quarterly. Performance threshold: AUC >= 0.75."
    )

    signature = infer_signature(X_train, model.predict_proba(X_train))

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        signature=signature,
        registered_model_name=MODEL_NAME,
    )
    mlflow.set_tag("description", description)

    print(f"AUC: {auc:.4f}")
    print(classification_report(y_test, y_pred))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Set the @champion alias

# COMMAND ----------

from mlflow.tracking import MlflowClient
client = MlflowClient()

versions = client.search_model_versions(f"name='{MODEL_NAME}'")
latest_version = max(int(v.version) for v in versions)
client.set_registered_model_alias(MODEL_NAME, "champion", latest_version)

print(f"Set {MODEL_NAME} version {latest_version} as @champion")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Score all customers — write to gold inference table
# MAGIC
# MAGIC In production this would be a streaming or scheduled job. For the demo we batch-score once.

# COMMAND ----------

import mlflow.sklearn
champion = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}@champion")

scoring_pdf = features_df.drop(columns=["label"]).copy()
scoring_pdf["risk_score"] = champion.predict_proba(scoring_pdf[X.columns])[:, 1]
scoring_pdf["scored_at"] = pd.Timestamp.utcnow()
scoring_pdf["model_version"] = latest_version

(spark.createDataFrame(scoring_pdf[["customer_id", "risk_score", "scored_at", "model_version"]])
    .write.mode("overwrite").saveAsTable(f"{CATALOG}.gold.aml_risk_scores"))

print(f"✓ Scored {len(scoring_pdf):,} customers → gold.aml_risk_scores")

# COMMAND ----------

# MAGIC %md
# MAGIC ## (Optional) Set up Lakehouse Monitoring on the inference table
# MAGIC
# MAGIC In the live demo, click into Catalog Explorer → `gold.aml_risk_scores` → "Quality" tab to set this up via UI.
# MAGIC The CLI version:
# MAGIC ```
# MAGIC databricks lakehouse-monitors create \
# MAGIC   --table-name axos_grc_demo.gold.aml_risk_scores \
# MAGIC   --inference-log-config '{...}'
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Done
# MAGIC
# MAGIC Next: **`04_governance_walkthrough.py`** — show lineage, dynamic masking, and audit log queries.
