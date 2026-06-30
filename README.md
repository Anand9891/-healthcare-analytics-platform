# 🏥 Hospital Patient & Operations Analytics Platform

An end-to-end Azure data engineering project that ingests, transforms, and analyzes hospital operations data using the **Medallion Architecture** (Bronze → Silver → Gold).

---

## 📌 Project Overview

This project simulates a real-world healthcare data platform for a hospital network, covering patient admissions, diagnoses, doctors, and billing. It demonstrates a complete batch data engineering pipeline on Azure — from raw ingestion to business-ready analytics.

**Goal:** Enable hospital administrators to answer questions like:
- Which department has the highest patient volume and cost?
- Are admissions trending up or down month over month?
- What are the most common diagnoses, and how severe are cases?

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Raw CSV Files   │────▶│  Azure Data  │────▶│   ADLS Gen2 Bronze   │
│ (Patients, Adm., │     │   Factory    │     │   (raw landing zone) │
│  Diagnoses, Docs)│     │   (Copy Act.)│     │                      │
└─────────────────┘     └──────────────┘     └──────────┬───────────┘
                                                          │
                                                          ▼
                                            ┌─────────────────────────┐
                                            │  Azure Databricks        │
                                            │  Bronze → Silver         │
                                            │  (clean, cast, join)     │
                                            └──────────┬───────────────┘
                                                        │
                                                        ▼
                                            ┌─────────────────────────┐
                                            │  Azure Databricks        │
                                            │  Silver → Gold           │
                                            │  (KPI aggregations)      │
                                            └──────────┬───────────────┘
                                                        │
                                                        ▼
                                            ┌─────────────────────────┐
                                            │  Azure Synapse Analytics │
                                            │  Serverless SQL Pool     │
                                            │  (OPENROWSET queries)    │
                                            └──────────┬───────────────┘
                                                        │
                                                        ▼
                                                  Power BI / Reporting
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | Azure Data Factory (ADF) |
| Storage | Azure Data Lake Storage Gen2 (ADLS Gen2) |
| Transformation | Azure Databricks (PySpark, Delta Lake) |
| Serving / Querying | Azure Synapse Analytics (Serverless SQL) |
| Security | Microsoft Entra ID App Registration (Service Principal), RBAC |
| Data Format | Delta Lake (Parquet + Transaction Log) |

---

## 🗂️ Medallion Architecture

### 🥉 Bronze Layer — Raw Ingestion
- Source: 4 CSV files (`patients`, `admissions`, `diagnoses`, `doctors`)
- Ingested via **ADF Copy Activities** (parallel execution)
- Stored as-is in `healthcare/bronze/<entity>/`

### 🥈 Silver Layer — Cleaned & Joined
- Type casting (dates, doubles, integers)
- Deduplication and null handling
- Derived column: `length_of_stay` (discharge_date − admission_date)
- Joined into a single **admissions_master** Delta table (patients + doctors + diagnoses + admissions)

### 🥇 Gold Layer — Business KPIs
Four aggregated Delta tables, each answering a specific business question:

| Gold Table | Business Question |
|---|---|
| `admissions_by_department` | Which department has highest volume / cost / avg stay? |
| `monthly_admissions_trend` | Is patient volume increasing or decreasing over time? |
| `top_diagnoses` | What are the most common ICD diagnoses and their cost impact? |
| `severity_summary` | How do costs and admission status vary by case severity? |

---

## 📁 Repository Structure

```
healthcare-project/
├── README.md
├── data/
│   └── generate_healthcare_data.py     # Synthetic data generator (Faker)
├── notebooks/
│   ├── 02_silver_transformation.py     # Bronze → Silver (Databricks)
│   └── 03_gold_transformation.py       # Silver → Gold (Databricks)
├── adf/
│   └── pl_ingest_healthcare_bronze.json # ADF pipeline definition
├── sql/
│   └── synapse_external_tables.sql     # Synapse serverless SQL scripts
├── docs/
│   └── architecture.md                 # Detailed architecture notes
└── images/
    └── architecture-diagram.png
```

---

## 🚀 How It Works — Step by Step

1. **Generate synthetic data** locally using `generate_healthcare_data.py` (Faker library) — produces 200 patients, 500 admissions, 500 diagnoses, 20 doctors.
2. **Upload to ADLS Gen2 Bronze** layer (manual or via ADF).
3. **ADF Pipeline** (`pl_ingest_healthcare_bronze`) automates ingestion with 4 parallel Copy Activities.
4. **Databricks Notebook 1** reads Bronze CSVs, cleans/casts types, joins into a unified Silver Delta table.
5. **Databricks Notebook 2** aggregates Silver data into 4 Gold KPI Delta tables.
6. **Synapse Serverless SQL** creates external data source + queries Gold Delta tables directly via `OPENROWSET`.
7. *(Optional)* Connect Power BI to Synapse for dashboards.

---

## 🔐 Security & Access

- **Service Principal** (`sp-healthcare-databricks`) created in Microsoft Entra ID for Databricks ↔ ADLS authentication (OAuth 2.0 client credentials flow).
- **RBAC roles** assigned: `Storage Blob Data Contributor` (Databricks), `Storage Blob Data Reader` (Synapse).
- Credentials managed via Spark config at runtime (production setup would use **Azure Key Vault + Databricks Secret Scopes**).

---

## 📊 Sample KPI Output

**Admissions by Department**

| department | total_admissions | avg_bill | avg_length_of_stay |
|---|---|---|---|
| Cardiology | 85 | 18,500 | 6.2 |
| Emergency | 72 | 12,300 | 3.1 |
| Oncology | 45 | 32,800 | 9.4 |

---

## 🧠 Key Learnings / Challenges Solved

- Resolved `401 authentication` errors between Databricks and ADLS Gen2 by correctly configuring OAuth Service Principal credentials and RBAC role propagation.
- Handled Synapse master key/credential dependency errors (`DROP CREDENTIAL` before `DROP MASTER KEY`).
- Worked around regional `SqlServerRegionDoesNotAllowProvisioning` error by deploying Synapse in an alternate region.
- Designed idempotent Delta writes (`mode("overwrite")`) for repeatable pipeline runs.

---

## 🔮 Future Enhancements

- [ ] Power BI dashboard connected to Synapse
- [ ] Scheduled ADF trigger (daily/weekly ingestion)
- [ ] Data quality framework (Great Expectations / custom validation rules)
- [ ] SCD Type 2 for slowly changing patient dimension
- [ ] CI/CD with GitHub Actions for notebook deployment
- [ ] Azure Monitor alerting on pipeline failures

---

## 👤 Author

**Anand Koujalagi**
Azure Data Engineer | [LinkedIn](#) | [GitHub](https://github.com/Anand9891)
