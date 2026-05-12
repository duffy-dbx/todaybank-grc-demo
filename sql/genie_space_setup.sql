-- ===================================================================
-- Axos GRC Operations Hub — Genie Space Setup
-- Curated views + instructions for the analyst-facing Genie space.
-- ===================================================================

-- The Genie space points at four curated views below. Each is documented
-- so Genie can answer natural-language questions without exposing
-- raw bronze tables.

-- View 1 — Customer 360 for Genie (PII-masked)
CREATE OR REPLACE VIEW axos_grc_demo.gold.genie_customer_360 AS
SELECT
  customer_id,
  full_name,
  state,
  kyc_risk_tier,
  aml_alert_count,
  aml_alert_total_usd,
  complaint_count,
  ROUND(balance_usd, 0) AS balance_usd
FROM axos_grc_demo.gold.customer_risk_360;

COMMENT ON VIEW axos_grc_demo.gold.genie_customer_360 IS
  'Customer-level GRC summary. One row per customer with KYC tier, AML alert count, '
  'AML alert total dollar amount, complaint count, and current balance. '
  'Use this view to answer questions about specific customers or top-N customers by risk.';

-- View 2 — AML alerts (analyst-friendly)
CREATE OR REPLACE VIEW axos_grc_demo.gold.genie_aml_alerts AS
SELECT
  customer_id,
  transaction_date,
  alert_type,
  structuring_count AS pattern_event_count,
  structuring_total AS pattern_total_usd
FROM axos_grc_demo.gold.aml_alerts;

COMMENT ON VIEW axos_grc_demo.gold.genie_aml_alerts IS
  'AML candidate alerts grouped by customer and date. alert_type is one of '
  '"STRUCTURING" or "HIGH_RISK_GEO_WIRE". Use this to answer questions about '
  'AML patterns, alert volume by date, or specific customer alert history.';

-- View 3 — HMDA summary
CREATE OR REPLACE VIEW axos_grc_demo.gold.genie_hmda AS
SELECT
  race,
  ethnicity,
  gender,
  loan_purpose,
  application_count,
  approved_count,
  denied_count,
  ROUND(approval_rate * 100, 1) AS approval_rate_pct,
  ROUND(avg_loan_amount, 0) AS avg_loan_amount_usd,
  ROUND(avg_fico, 0) AS avg_fico
FROM axos_grc_demo.gold.hmda_summary;

COMMENT ON VIEW axos_grc_demo.gold.genie_hmda IS
  'HMDA loan-application summary by demographic group and loan purpose. '
  'Use this for fair-lending analysis questions (approval rate by race/ethnicity/gender). '
  'application_count >= 20 is recommended for statistically meaningful comparisons.';

-- View 4 — Complaint themes
CREATE OR REPLACE VIEW axos_grc_demo.gold.genie_complaints AS
SELECT
  theme,
  severity,
  month,
  complaint_count,
  unique_customers
FROM axos_grc_demo.gold.complaint_themes;

COMMENT ON VIEW axos_grc_demo.gold.genie_complaints IS
  'Customer complaint volume by theme, severity, and month. '
  'Themes: fraud, fees, loan_servicing, discrimination, account_access, credit_reporting, deposits, other. '
  'Severity: low, medium, high, urgent. Use this to answer questions about complaint trends.';

-- ===================================================================
-- Genie Space Instructions (paste these into the Genie space settings)
-- ===================================================================
--
-- Title: Axos GRC Operations Hub
--
-- Description:
--   Ask questions about AML alerts, fair-lending, customer complaints,
--   and customer-level risk. All queries run against governed Gold views;
--   PII is masked unless you are in the risk_analysts group.
--
-- Sample questions:
--   - Show me the top 10 customers by AML alert dollar amount this quarter
--   - What is the loan approval rate by race for home purchase loans?
--   - Which complaint theme grew the most month over month?
--   - List PEP matches surfaced from KYC documents in the last 30 days
--   - How many customers in the High KYC tier have any AML alerts?
--
-- General Instructions:
--   - When users ask about "high risk customers", join genie_customer_360 to
--     genie_aml_alerts. High risk = aml_alert_count > 0 OR kyc_risk_tier = 'High'.
--   - For fair-lending questions, use genie_hmda only when application_count >= 20.
--   - Always show counts and totals, not raw transaction listings.
--   - PII (SSN, phone, email, DOB) is never available — do not attempt to query it.
