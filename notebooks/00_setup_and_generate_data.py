# Databricks notebook source
# MAGIC %md
# MAGIC # 00 · Setup & Generate Sample Data
# MAGIC
# MAGIC Creates the `axos_grc_demo` catalog, schemas, Unity Catalog tags, and populates synthetic GRC data.
# MAGIC
# MAGIC **Runtime:** ~3–5 minutes on a small serverless cluster.
# MAGIC **Outputs:** `axos_grc_demo.bronze.*` tables ready for the Lakeflow Pipeline in notebook 01.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

dbutils.widgets.text("catalog", "axos_grc_demo", "Catalog")
dbutils.widgets.text("storage_location", "", "External storage location (optional)")

CATALOG = dbutils.widgets.get("catalog")
STORAGE = dbutils.widgets.get("storage_location")

print(f"Target catalog: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create catalog + schemas

# COMMAND ----------

managed_loc = f" MANAGED LOCATION '{STORAGE}'" if STORAGE else ""
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}{managed_loc}")
spark.sql(f"USE CATALOG {CATALOG}")

for schema in ["bronze", "silver", "gold", "audit"]:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema}")

print(f"Created catalog '{CATALOG}' with schemas: bronze, silver, gold, audit")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Unity Catalog tags for governance demo
# MAGIC
# MAGIC These tags drive the **PII** and **regulatory** classification used in Act 2.

# COMMAND ----------

# Tags will be applied to specific columns later. We define the catalog-level taxonomy here.
# Catalog tag is best-effort — workspace tag policies may restrict allowed values.
try:
    spark.sql(f"ALTER CATALOG {CATALOG} SET TAGS ('demo' = 'axos_grc')")
except Exception as e:
    print(f"WARN: catalog tag skipped due to tag policy: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate sample data
# MAGIC
# MAGIC All synthetic, no real PII. Generated from a fixed seed for reproducibility.

# COMMAND ----------

import random
from datetime import datetime, timedelta
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, TimestampType,
    DateType, BooleanType
)

random.seed(42)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Customers (5,000 rows)

# COMMAND ----------

FIRST_NAMES = ["James", "Maria", "Robert", "Jennifer", "Michael", "Linda", "David", "Patricia",
               "John", "Barbara", "William", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]
STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI", "NJ", "VA", "WA", "AZ", "MA"]
RACES = ["White", "Black or African American", "Asian", "American Indian or Alaska Native",
         "Native Hawaiian or Other Pacific Islander", "Information not provided"]
ETHNICITIES = ["Not Hispanic or Latino", "Hispanic or Latino", "Information not provided"]
GENDERS = ["Male", "Female", "Information not provided"]
RISK_TIERS = ["Low", "Medium", "High"]

customers = []
for i in range(5000):
    cid = f"C{i:06d}"
    fn = random.choice(FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    customers.append((
        cid,
        fn,
        ln,
        f"{fn.lower()}.{ln.lower()}{i}@example.com",
        f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
        f"{random.randint(100, 9999)} Main St",
        random.choice(["San Diego", "Los Angeles", "New York", "Chicago", "Houston", "Atlanta", "Boston"]),
        random.choice(STATES),
        f"{random.randint(10000, 99999)}",
        f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",  # synthetic SSN
        (datetime(1950, 1, 1) + timedelta(days=random.randint(0, 25000))).date(),
        random.choice(RACES),
        random.choice(ETHNICITIES),
        random.choice(GENDERS),
        random.choices(RISK_TIERS, weights=[70, 25, 5])[0],
        (datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2500))).date(),
        round(random.uniform(500, 250000), 2),
    ))

customer_schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("first_name", StringType()),
    StructField("last_name", StringType()),
    StructField("email", StringType()),
    StructField("phone", StringType()),
    StructField("street", StringType()),
    StructField("city", StringType()),
    StructField("state", StringType()),
    StructField("zip", StringType()),
    StructField("ssn", StringType()),
    StructField("date_of_birth", DateType()),
    StructField("race", StringType()),
    StructField("ethnicity", StringType()),
    StructField("gender", StringType()),
    StructField("kyc_risk_tier", StringType()),
    StructField("account_open_date", DateType()),
    StructField("balance_usd", DoubleType()),
])

(spark.createDataFrame(customers, customer_schema)
    .write.mode("overwrite").saveAsTable(f"{CATALOG}.bronze.raw_customers"))

print(f"✓ Wrote {CATALOG}.bronze.raw_customers (5,000 rows)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Apply PII tags
# MAGIC
# MAGIC In Act 2 we'll use these tags to drive dynamic masking via UC.

# COMMAND ----------

def safe_tag(sql):
    try:
        spark.sql(sql)
    except Exception as e:
        print(f"WARN: tag skipped: {e}")

pii_columns = ["ssn", "date_of_birth", "phone", "email", "street"]
for col in pii_columns:
    safe_tag(f"ALTER TABLE {CATALOG}.bronze.raw_customers "
             f"ALTER COLUMN {col} SET TAGS ('classification' = 'PII')")

# Tag race/ethnicity/gender as regulatory (HMDA / fair lending)
for col in ["race", "ethnicity", "gender"]:
    safe_tag(f"ALTER TABLE {CATALOG}.bronze.raw_customers "
             f"ALTER COLUMN {col} SET TAGS ('classification' = 'regulatory_HMDA')")

print("✓ PII and regulatory tags applied (best-effort)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Transactions (100,000 rows, with ~50 suspicious patterns)

# COMMAND ----------

CHANNELS = ["card_present", "card_not_present", "ach", "wire_domestic", "wire_intl", "zelle", "atm"]
HIGH_RISK_COUNTRIES = ["IR", "KP", "SY", "VE", "CU", "RU"]

txns = []
txn_id = 0
start_date = datetime(2025, 5, 1)

# Normal transactions
for _ in range(99950):
    cid = f"C{random.randint(0, 4999):06d}"
    txns.append((
        f"T{txn_id:08d}",
        cid,
        start_date + timedelta(seconds=random.randint(0, 365 * 86400)),
        round(random.uniform(5, 5000), 2),
        random.choice(CHANNELS),
        random.choice(["DEBIT", "CREDIT"]),
        random.choice(["US"] * 95 + ["MX", "CA", "GB", "DE"]),
        random.choice(["Walmart", "Amazon", "Starbucks", "Shell", "Target", "Whole Foods", "ATM", "Counterparty Bank", "Payroll", "Utility"]),
        False,  # not pre-flagged; AML model will score
    ))
    txn_id += 1

# Embed 50 suspicious patterns:
#   structuring (multiple sub-$10K cash within 24h)
#   high-risk country wires
#   rapid in-out movement
suspect_customers = random.sample(range(5000), 50)
for i, scid_idx in enumerate(suspect_customers):
    cid = f"C{scid_idx:06d}"
    base_time = start_date + timedelta(days=random.randint(30, 330))
    pattern = i % 3
    if pattern == 0:  # structuring: 3 cash deposits of ~$9,500 within 24h
        for k in range(3):
            txns.append((
                f"T{txn_id:08d}",
                cid,
                base_time + timedelta(hours=k * 6),
                round(random.uniform(9000, 9900), 2),
                "atm",
                "CREDIT",
                "US",
                "ATM Cash Deposit",
                False,
            ))
            txn_id += 1
    elif pattern == 1:  # high-risk wire
        txns.append((
            f"T{txn_id:08d}",
            cid,
            base_time,
            round(random.uniform(15000, 75000), 2),
            "wire_intl",
            "DEBIT",
            random.choice(HIGH_RISK_COUNTRIES),
            "International Wire",
            False,
        ))
        txn_id += 1
    else:  # rapid in-out: large credit followed by quick debit
        txns.append((
            f"T{txn_id:08d}", cid, base_time, round(random.uniform(20000, 50000), 2),
            "wire_domestic", "CREDIT", "US", "Inbound Wire", False,
        ))
        txn_id += 1
        txns.append((
            f"T{txn_id:08d}", cid, base_time + timedelta(hours=2),
            round(random.uniform(19000, 49000), 2),
            "wire_intl", "DEBIT", random.choice(HIGH_RISK_COUNTRIES),
            "Outbound Wire", False,
        ))
        txn_id += 1

txn_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("transaction_ts", TimestampType(), False),
    StructField("amount_usd", DoubleType(), False),
    StructField("channel", StringType(), False),
    StructField("direction", StringType(), False),
    StructField("counterparty_country", StringType()),
    StructField("counterparty_name", StringType()),
    StructField("flagged_by_source", BooleanType(), False),
])

(spark.createDataFrame(txns, txn_schema)
    .write.mode("overwrite").saveAsTable(f"{CATALOG}.bronze.raw_transactions"))

print(f"✓ Wrote {CATALOG}.bronze.raw_transactions ({len(txns):,} rows including ~{len(txns) - 99950} suspicious patterns)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Loans (2,000 rows, HMDA-compliant)

# COMMAND ----------

LOAN_PURPOSES = ["Home Purchase", "Refinance", "Home Improvement", "Cash Out Refi"]
LOAN_TYPES = ["Conventional", "FHA", "VA", "USDA"]
ACTIONS = ["Approved", "Denied", "Withdrawn", "Approved-Not-Accepted"]
DENIAL_REASONS = ["Debt-to-Income Ratio", "Credit History", "Collateral", "Insufficient Cash", "Employment History", "Credit Application Incomplete", None]

loans = []
for i in range(2000):
    cid = f"C{random.randint(0, 4999):06d}"
    action = random.choices(ACTIONS, weights=[60, 20, 10, 10])[0]
    loans.append((
        f"L{i:06d}",
        cid,
        random.choice(LOAN_PURPOSES),
        random.choice(LOAN_TYPES),
        round(random.uniform(50000, 1500000), -2),
        round(random.uniform(3.5, 8.5), 3),
        random.randint(15, 30),
        action,
        random.choice(DENIAL_REASONS) if action == "Denied" else None,
        round(random.uniform(20, 55), 1),  # DTI
        random.randint(580, 820),  # FICO
        round(random.uniform(50, 95), 1),  # LTV
        (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).date(),
        random.choice(["CA", "TX", "FL", "NY", "IL", "AZ", "WA", "CO"]),
    ))

loan_schema = StructType([
    StructField("loan_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("loan_purpose", StringType()),
    StructField("loan_type", StringType()),
    StructField("amount_usd", DoubleType()),
    StructField("interest_rate", DoubleType()),
    StructField("term_years", IntegerType()),
    StructField("action_taken", StringType()),
    StructField("denial_reason", StringType()),
    StructField("dti", DoubleType()),
    StructField("fico", IntegerType()),
    StructField("ltv", DoubleType()),
    StructField("application_date", DateType()),
    StructField("property_state", StringType()),
])

(spark.createDataFrame(loans, loan_schema)
    .write.mode("overwrite").saveAsTable(f"{CATALOG}.bronze.raw_loans"))

print(f"✓ Wrote {CATALOG}.bronze.raw_loans (2,000 rows)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Customer complaints (500 rows, free-text)
# MAGIC
# MAGIC Used in Act 4 with `ai_classify` to demonstrate AI Functions on unstructured data.

# COMMAND ----------

COMPLAINT_TEMPLATES = {
    "fraud": [
        "I noticed an unauthorized charge on my account from {merchant} for ${amount}. I never made this purchase.",
        "Someone used my debit card at {merchant}. I'm filing a fraud claim.",
        "There's a charge I don't recognize for ${amount}. Please investigate.",
    ],
    "fees": [
        "I was charged a ${amount} overdraft fee that should have been waived.",
        "Why am I seeing a maintenance fee of ${amount} on my account?",
        "I want a refund for the ${amount} fee charged last month.",
    ],
    "loan_servicing": [
        "My mortgage payment was applied incorrectly. I paid extra principal but it went to interest.",
        "I've been waiting 3 weeks for a payoff statement on loan {loan_id}.",
        "My escrow analysis is wrong. The new payment amount is too high.",
    ],
    "discrimination": [
        "I feel my loan application was denied because of my background.",
        "I was treated differently than another applicant for the same loan product.",
        "The loan officer made comments that felt discriminatory.",
    ],
    "account_access": [
        "I cannot log into online banking. The reset link doesn't work.",
        "My mobile app keeps crashing when I try to deposit a check.",
        "I've been locked out of my account for two days.",
    ],
    "credit_reporting": [
        "There's an error on my credit report from your bank. I never had a late payment.",
        "Please dispute the negative item you reported on my credit.",
        "My account shows as closed on my credit report but it's still open.",
    ],
    "deposits": [
        "My direct deposit hasn't posted yet and it's been 3 days.",
        "A check I deposited for ${amount} is still on hold after 5 business days.",
        "Wire transfer of ${amount} hasn't arrived. The sender confirmed it was sent.",
    ],
    "other": [
        "I'd like to close my account. Please send instructions.",
        "The branch hours have changed and no one notified me.",
        "I want to add a beneficiary to my account.",
    ],
}

complaints = []
for i in range(500):
    theme = random.choice(list(COMPLAINT_TEMPLATES.keys()))
    template = random.choice(COMPLAINT_TEMPLATES[theme])
    text = template.format(
        merchant=random.choice(["Amazon", "Walmart", "Best Buy", "Target", "Online Store"]),
        amount=round(random.uniform(10, 500), 2),
        loan_id=f"L{random.randint(0, 1999):06d}",
    )
    complaints.append((
        f"CMP{i:06d}",
        f"C{random.randint(0, 4999):06d}",
        (datetime(2025, 5, 1) + timedelta(days=random.randint(0, 365))).date(),
        random.choice(["phone", "email", "online_form", "branch", "social_media"]),
        text,
    ))

complaint_schema = StructType([
    StructField("complaint_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("received_date", DateType()),
    StructField("channel", StringType()),
    StructField("narrative", StringType()),
])

(spark.createDataFrame(complaints, complaint_schema)
    .write.mode("overwrite").saveAsTable(f"{CATALOG}.bronze.raw_complaints"))

print(f"✓ Wrote {CATALOG}.bronze.raw_complaints (500 rows)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### KYC documents (200 rows, free-text narratives)
# MAGIC
# MAGIC Used in Act 4 with `ai_extract` for entity extraction.

# COMMAND ----------

KYC_TEMPLATES = [
    "Customer {name} is a {occupation} residing in {city}, {state}. Source of funds is {source}. Annual income approximately ${income}. PEP screening: {pep}. Sanctions screening: clear. Beneficial owner: self.",
    "Application for business account by {name}, owner of {biz_name} (DBA), located in {city}, {state}. Industry: {industry}. Expected monthly transaction volume: ${volume}. PEP: {pep}. Sanctions: clear.",
    "{name} provided proof of address (utility bill dated {date}) and government ID. Occupation: {occupation}. Wealth source: {source}. Risk tier: {risk}.",
]
OCCUPATIONS = ["software engineer", "physician", "teacher", "nurse", "construction manager", "accountant", "retiree", "small business owner"]
INDUSTRIES = ["restaurant", "retail", "consulting", "real estate", "construction", "legal services", "healthcare"]
SOURCES = ["W-2 employment", "self-employment", "retirement income", "investments", "inheritance", "business proceeds"]

kyc_docs = []
for i in range(200):
    cid = f"C{random.randint(0, 4999):06d}"
    template = random.choice(KYC_TEMPLATES)
    text = template.format(
        name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        occupation=random.choice(OCCUPATIONS),
        city=random.choice(["San Diego", "Phoenix", "Dallas", "Atlanta", "Seattle"]),
        state=random.choice(STATES),
        source=random.choice(SOURCES),
        income=random.randint(50000, 350000),
        pep=random.choices(["clear", "match — escalated to compliance"], weights=[95, 5])[0],
        biz_name=f"{random.choice(LAST_NAMES)} {random.choice(['LLC', 'Inc', 'Group', 'Partners'])}",
        industry=random.choice(INDUSTRIES),
        volume=random.randint(10000, 500000),
        date=(datetime(2025, 1, 1) + timedelta(days=random.randint(0, 300))).date().isoformat(),
        risk=random.choice(RISK_TIERS),
    )
    kyc_docs.append((
        f"KYC{i:06d}",
        cid,
        (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).date(),
        text,
    ))

kyc_schema = StructType([
    StructField("kyc_doc_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("document_date", DateType()),
    StructField("narrative", StringType()),
])

(spark.createDataFrame(kyc_docs, kyc_schema)
    .write.mode("overwrite").saveAsTable(f"{CATALOG}.bronze.raw_kyc_docs"))

print(f"✓ Wrote {CATALOG}.bronze.raw_kyc_docs (200 rows)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Audit events (5,000 rows)

# COMMAND ----------

ACTIONS_LIST = ["query_table", "update_record", "delete_record", "export_report", "view_pii", "model_inference", "grant_permission"]

audit_events = []
for i in range(5000):
    audit_events.append((
        f"AE{i:08d}",
        (datetime(2025, 5, 1) + timedelta(seconds=random.randint(0, 365 * 86400))),
        random.choice([f"user{j}@axos.com" for j in range(50)]),
        random.choice(ACTIONS_LIST),
        random.choice([f"axos_grc_demo.silver.{t}" for t in ["customers_v", "transactions", "loans"]]),
        random.choice(["success", "denied"]),
    ))

audit_schema = StructType([
    StructField("event_id", StringType()),
    StructField("event_ts", TimestampType()),
    StructField("user_email", StringType()),
    StructField("action", StringType()),
    StructField("resource", StringType()),
    StructField("status", StringType()),
])

(spark.createDataFrame(audit_events, audit_schema)
    .write.mode("overwrite").saveAsTable(f"{CATALOG}.bronze.raw_audit_events"))

print(f"✓ Wrote {CATALOG}.bronze.raw_audit_events (5,000 rows)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Done
# MAGIC
# MAGIC Bronze tables ready. Next: run **`01_lakeflow_pipeline.py`** as a Lakeflow Pipeline (Delta Live Tables) to build silver and gold.

# COMMAND ----------

display(spark.sql(f"SHOW TABLES IN {CATALOG}.bronze"))
