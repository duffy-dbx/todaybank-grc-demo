-- ===================================================================
-- TodayBank GRC Demo — Live "Unstructured + AI" segment
-- Three SQL cells to paste into the DBSQL editor during the talk.
-- Warehouse: Shared Unity Catalog Serverless (start it before the demo).
-- Catalog: todaybank_grc_demo
-- ===================================================================


-- CELL 1 -------------------------------------------------------------
-- Live ai_classify on 10 raw complaints (~15s on a small warehouse).
-- Talk: "Here's unstructured complaint text. Watch SQL classify it inline."

SELECT
  complaint_id,
  LEFT(complaint_text, 80) AS complaint_excerpt,
  ai_classify(
    complaint_text,
    ARRAY('fraud','fees','loan_servicing','discrimination',
          'account_access','credit_reporting','deposits','other')
  ) AS theme,
  ai_classify(
    complaint_text,
    ARRAY('low','medium','high','urgent')
  ) AS severity
FROM todaybank_grc_demo.bronze.raw_complaints
LIMIT 10;


-- CELL 2 -------------------------------------------------------------
-- The full population of 500 complaints, already classified.
-- Talk: "We ran this across all 500 in seconds — themes and severity."

SELECT theme, severity, COUNT(*) AS complaints
FROM todaybank_grc_demo.silver.complaints_classified
GROUP BY theme, severity
ORDER BY complaints DESC;


-- CELL 3 -------------------------------------------------------------
-- ai_extract pulled structured fields out of unstructured KYC narratives.
-- Talk: "Same idea on KYC docs — we extracted PEP status, occupation,
--        source of funds, and surfaced two PEP matches the analyst
--        would have missed scrolling through PDFs."

SELECT
  kyc_doc_id,
  full_name,
  document_date,
  occupation,
  source_of_funds,
  pep_status
FROM todaybank_grc_demo.gold.kyc_pep_matches
ORDER BY document_date DESC;
