# Architecture Notes

## Medallion Architecture Rationale

This project follows the **Medallion (Bronze/Silver/Gold) Architecture**, a widely-adopted
pattern in modern data lakehouse design (popularized by Databricks) that progressively
refines data quality and usability at each layer.

### Bronze — Raw / Landing Zone
- Exact copy of source data, no transformations.
- Format: CSV (as received from source systems).
- Purpose: auditability, replay capability, schema-on-read flexibility.

### Silver — Cleansed & Conformed
- Type casting, null handling, deduplication.
- Entities joined into a single denormalized fact table (`admissions_master`).
- Format: Delta Lake (ACID transactions, time travel, schema enforcement).

### Gold — Business / Aggregated
- Pre-aggregated KPI tables tailored to specific business questions.
- Optimized for fast querying (small, summarized, indexed by `OPENROWSET` in Synapse).
- Consumed directly by BI tools (Power BI) or ad-hoc SQL analysts.

---

## Why Delta Lake over plain Parquet?

- ACID transactions prevent partial/corrupt writes during pipeline reruns.
- Schema enforcement catches upstream data quality issues early.
- Time travel allows historical KPI comparisons and rollback if a bad run pollutes Gold.
- Native support in both Databricks and Synapse Serverless SQL (`FORMAT = 'DELTA'`).

---

## Why Synapse Serverless (not Dedicated SQL Pool)?

- No infrastructure to provision/manage — pay only per query (per TB scanned).
- Ideal for ad-hoc analytics directly on Delta Lake files without a separate ETL/load step.
- Cost-effective for a portfolio/dev project compared to a dedicated SQL pool's fixed cost.

---

## Authentication Design

| Component | Auth Method | Role Granted |
|---|---|---|
| Databricks → ADLS Gen2 | OAuth 2.0 Client Credentials (Service Principal) | Storage Blob Data Contributor |
| Synapse → ADLS Gen2 | Managed Identity | Storage Blob Data Reader |
| ADF → ADLS Gen2 | Account Key (linked service) | N/A (storage account key) |

> Production recommendation: migrate Service Principal secrets into **Azure Key Vault**,
> and reference them in Databricks via **Secret Scopes** instead of inline notebook config.

---

## Known Issues & Resolutions (real troubleshooting log)

| Issue | Root Cause | Fix |
|---|---|---|
| `SqlServerRegionDoesNotAllowProvisioning` | East US region capacity restriction on subscription | Deployed Synapse workspace in East US 2 |
| `401 Server failed to authenticate` (Databricks → ADLS) | Storage account name mismatch in Spark config | Corrected `adlshealthcaredev` → `adlshealthcaredevs` |
| `Password validation failed` (Synapse master key) | Password too short / didn't meet complexity policy | Used a longer password with upper/lower/digit/special char |
| `There is already a master key` | Re-ran `CREATE MASTER KEY` after a prior partial run | `DROP DATABASE SCOPED CREDENTIAL` → `DROP MASTER KEY` → recreate both |
