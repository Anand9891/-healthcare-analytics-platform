-- ============================================================
-- Azure Synapse Analytics — Serverless SQL Pool
-- Hospital Patient & Operations Analytics Platform
-- Queries the Gold Delta Lake tables directly via OPENROWSET
-- ============================================================

-- 1. Create database
CREATE DATABASE healthcare_gold;
GO

USE healthcare_gold;
GO

-- 2. Master key + database-scoped credential (Managed Identity)
CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<your-strong-password>';

CREATE DATABASE SCOPED CREDENTIAL healthcare_cred
WITH IDENTITY = 'Managed Identity';
GO

-- 3. External data source pointing at the Gold container
CREATE EXTERNAL DATA SOURCE gold_adls
WITH (
    LOCATION = 'https://adlshealthcaredevs.dfs.core.windows.net/healthcare/gold',
    CREDENTIAL = healthcare_cred
);
GO

-- ============================================================
-- KPI Queries
-- ============================================================

-- Admissions by Department
SELECT *
FROM OPENROWSET(
    BULK 'https://adlshealthcaredevs.dfs.core.windows.net/healthcare/gold/admissions_by_department/',
    FORMAT = 'DELTA'
) AS dept_summary
ORDER BY total_admissions DESC;

-- Monthly Admissions Trend
SELECT *
FROM OPENROWSET(
    BULK 'https://adlshealthcaredevs.dfs.core.windows.net/healthcare/gold/monthly_admissions_trend/',
    FORMAT = 'DELTA'
) AS monthly_trend
ORDER BY month;

-- Top Diagnoses
SELECT *
FROM OPENROWSET(
    BULK 'https://adlshealthcaredevs.dfs.core.windows.net/healthcare/gold/top_diagnoses/',
    FORMAT = 'DELTA'
) AS diagnoses
ORDER BY total_cases DESC;

-- Severity Summary
SELECT *
FROM OPENROWSET(
    BULK 'https://adlshealthcaredevs.dfs.core.windows.net/healthcare/gold/severity_summary/',
    FORMAT = 'DELTA'
) AS severity
ORDER BY severity;
