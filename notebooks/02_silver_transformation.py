# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze → Silver Transformation
# MAGIC Cleans, type-casts, deduplicates, and joins the 4 Bronze entities
# MAGIC (patients, admissions, diagnoses, doctors) into a single Silver
# MAGIC `admissions_master` Delta table.

# COMMAND ----------

# MAGIC %md ### Cell 1 — Configure ADLS Gen2 access (OAuth Service Principal)

# COMMAND ----------

storage_account = "adlshealthcaredevs"
container = "healthcare"

# NOTE: In production, pull these from Azure Key Vault via Databricks Secret Scopes
# instead of hardcoding them here.
client_id = dbutils.secrets.get(scope="healthcare-scope", key="client-id")
tenant_id = dbutils.secrets.get(scope="healthcare-scope", key="tenant-id")
client_secret = dbutils.secrets.get(scope="healthcare-scope", key="client-secret")

spark.conf.set(f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net", "OAuth")
spark.conf.set(f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net",
               "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
spark.conf.set(f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net", client_id)
spark.conf.set(f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net", client_secret)
spark.conf.set(f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net",
               f"https://login.microsoftonline.com/{tenant_id}/oauth2/token")

print("✅ ADLS Gen2 configuration set")

# COMMAND ----------

# MAGIC %md ### Cell 2 — Read Bronze Layer

# COMMAND ----------

bronze_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/bronze"

patients_df   = spark.read.option("header", True).csv(f"{bronze_path}/patients/")
admissions_df = spark.read.option("header", True).csv(f"{bronze_path}/admissions/")
diagnoses_df  = spark.read.option("header", True).csv(f"{bronze_path}/diagnoses/")
doctors_df    = spark.read.option("header", True).csv(f"{bronze_path}/doctors/")

print(f"✅ patients:   {patients_df.count()} rows")
print(f"✅ admissions: {admissions_df.count()} rows")
print(f"✅ diagnoses:  {diagnoses_df.count()} rows")
print(f"✅ doctors:    {doctors_df.count()} rows")

# COMMAND ----------

# MAGIC %md ### Cell 3 — Clean & Cast Types

# COMMAND ----------

from pyspark.sql.functions import col, to_date, datediff

patients_clean = patients_df \
    .withColumn("dob", to_date(col("dob"), "yyyy-MM-dd")) \
    .dropDuplicates(["patient_id"]) \
    .na.drop(subset=["patient_id", "patient_name"])

admissions_clean = admissions_df \
    .withColumn("admission_date", to_date(col("admission_date"), "yyyy-MM-dd")) \
    .withColumn("discharge_date", to_date(col("discharge_date"), "yyyy-MM-dd")) \
    .withColumn("total_bill", col("total_bill").cast("double")) \
    .withColumn("length_of_stay", datediff(col("discharge_date"), col("admission_date"))) \
    .dropDuplicates(["admission_id"]) \
    .na.drop(subset=["admission_id", "patient_id"])

diagnoses_clean = diagnoses_df \
    .dropDuplicates(["diagnosis_id"]) \
    .na.drop(subset=["diagnosis_id", "admission_id"])

doctors_clean = doctors_df \
    .withColumn("experience_years", col("experience_years").cast("int")) \
    .dropDuplicates(["doctor_id"]) \
    .na.drop(subset=["doctor_id"])

print("✅ All dataframes cleaned and types cast")

# COMMAND ----------

# MAGIC %md ### Cell 4 — Join into Silver Master Table

# COMMAND ----------

silver_df = admissions_clean \
    .join(patients_clean, on="patient_id", how="left") \
    .join(doctors_clean, on="doctor_id", how="left") \
    .join(diagnoses_clean, on="admission_id", how="left") \
    .select(
        "admission_id", "patient_id", "patient_name", "gender", "dob",
        "blood_group", "city", "doctor_id", "doctor_name", "department",
        "admission_date", "discharge_date", "length_of_stay",
        "admission_type", "status", "total_bill",
        "icd_code", "diagnosis_description", "severity"
    )

print(f"✅ Silver table rows: {silver_df.count()}")
silver_df.printSchema()

# COMMAND ----------

# MAGIC %md ### Cell 5 — Write Silver Layer as Delta

# COMMAND ----------

silver_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/silver/admissions_master"

silver_df.write.format("delta").mode("overwrite").save(silver_path)

print("✅ Silver layer written to Delta Lake")
print(f"   Path: {silver_path}")
