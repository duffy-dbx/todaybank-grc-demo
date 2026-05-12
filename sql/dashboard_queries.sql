-- ===================================================================
-- TodayBank GRC Operations Hub – Dashboard Queries
-- These power the AI/BI Dashboard widgets. Each block is one widget.
-- ===================================================================

-- Widget 1 – KPI: Open AML alerts (last 30 days)
SELECT COUNT(*) AS open_aml_alerts
FROM todaybank_grc_demo.gold.aml_alerts
WHERE transaction_date > current_date() - INTERVAL 30 DAYS;

-- Widget 2 – KPI: Customers in High KYC tier
SELECT COUNT(*) AS high_kyc_customers
FROM todaybank_grc_demo.silver.customers
WHERE kyc_risk_tier = 'High';

-- Widget 3 – KPI: HMDA approval rate (overall)
SELECT
  ROUND(SUM(approved_count) / SUM(application_count) * 100, 1) AS overall_approval_rate_pct
FROM todaybank_grc_demo.gold.hmda_summary;

-- Widget 4 – KPI: Complaints this month
SELECT COUNT(*) AS complaints_this_month
FROM todaybank_grc_demo.silver.complaints_classified
WHERE DATE_TRUNC('month', received_date) = DATE_TRUNC('month', current_date());

-- Widget 5 – Bar: AML alerts by type, last 90 days
SELECT
  alert_type,
  COUNT(*) AS alert_count,
  SUM(structuring_total) AS total_amount_usd
FROM todaybank_grc_demo.gold.aml_alerts
WHERE transaction_date > current_date() - INTERVAL 90 DAYS
GROUP BY alert_type
ORDER BY alert_count DESC;

-- Widget 6 – Heatmap: Fair-lending approval rate by demographic
SELECT
  race,
  ethnicity,
  gender,
  loan_purpose,
  application_count,
  ROUND(approval_rate * 100, 1) AS approval_rate_pct
FROM todaybank_grc_demo.gold.hmda_summary
WHERE application_count >= 20
ORDER BY approval_rate_pct ASC;

-- Widget 7 – Time series: Complaint volume by theme
SELECT
  month,
  theme,
  SUM(complaint_count) AS complaints
FROM todaybank_grc_demo.gold.complaint_themes
GROUP BY month, theme
ORDER BY month, theme;

-- Widget 8 – Table: Top-risk customers (combined AML + complaint signal)
SELECT
  customer_id,
  full_name,
  state,
  kyc_risk_tier,
  aml_alert_count,
  aml_alert_total_usd,
  complaint_count,
  ROUND(balance_usd, 0) AS balance_usd
FROM todaybank_grc_demo.gold.customer_risk_360
WHERE aml_alert_count > 0
   OR (kyc_risk_tier = 'High' AND complaint_count >= 2)
ORDER BY aml_alert_total_usd DESC NULLS LAST, complaint_count DESC
LIMIT 25;

-- Widget 9 – Table: PEP matches surfaced by ai_extract on KYC narratives
SELECT
  kyc_doc_id,
  full_name,
  document_date,
  occupation,
  source_of_funds,
  pep_status
FROM todaybank_grc_demo.gold.kyc_pep_matches
ORDER BY document_date DESC;

-- Widget 10 – Bar: Model risk score distribution
SELECT
  CASE
    WHEN risk_score < 0.25 THEN '0.00–0.24'
    WHEN risk_score < 0.50 THEN '0.25–0.49'
    WHEN risk_score < 0.75 THEN '0.50–0.74'
    ELSE '0.75–1.00'
  END AS risk_bucket,
  COUNT(*) AS customer_count
FROM todaybank_grc_demo.gold.aml_risk_scores
GROUP BY risk_bucket
ORDER BY risk_bucket;
