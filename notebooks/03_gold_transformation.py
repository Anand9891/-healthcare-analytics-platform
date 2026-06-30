# Databricks notebook source
# MAGIC %md
# MAGIC # Silver → Gold Transformation
# MAGIC Aggregates the Silver `admissions_master` table into 4 business-ready
# MAGIC KPI Delta tables for reporting / Synapse / Power BI consumption.

# COMMAND ----------

# MAGIC %md ### Cell 1 — Configure ADLS Gen2 access

# COMMAND ----------

storage_account = "adlshealthcaredevs"
container = "healthcare"

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

# MAGIC %md ### Cell 2 — Read Silver Layer

# COMMAND ----------

silver_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/silver/admissions_master"

silver_df = spark.read.format("delta").load(silver_path)

print(f"✅ Silver table loaded: {silver_df.count()} rows")
silver_df.printSchema()

# COMMAND ----------

# MAGIC %md ### Cell 3 — Gold Table 1: Admissions by Department

# COMMAND ----------

from pyspark.sql.functions import count, round, avg

gold_dept = silver_df \
    .groupBy("department") \
    .agg(
        count("admission_id").alias("total_admissions"),
        round(avg("total_bill"), 2).alias("avg_bill"),
        round(avg("length_of_stay"), 2).alias("avg_length_of_stay")
    ) \
    .orderBy("total_admissions", ascending=False)

gold_dept.show()

# COMMAND ----------

# MAGIC %md ### Cell 4 — Gold Table 2: Monthly Admissions Trend

# COMMAND ----------

from pyspark.sql.functions import date_format

gold_monthly = silver_df \
    .withColumn("month", date_format("admission_date", "yyyy-MM")) \
    .groupBy("month") \
    .agg(
        count("admission_id").alias("total_admissions"),
        round(avg("total_bill"), 2).alias("avg_bill")
    ) \
    .orderBy("month")

gold_monthly.show()

# COMMAND ----------

# MAGIC %md ### Cell 5 — Gold Table 3: Top Diagnoses

# COMMAND ----------

gold_diagnoses = silver_df \
    .groupBy("icd_code", "diagnosis_description") \
    .agg(
        count("admission_id").alias("total_cases"),
        round(avg("total_bill"), 2).alias("avg_bill")
    ) \
    .orderBy("total_cases", ascending=False)

gold_diagnoses.show()

# COMMAND ----------

# MAGIC %md ### Cell 6 — Gold Table 4: Severity Summary

# COMMAND ----------

gold_severity = silver_df \
    .groupBy("severity", "status") \
    .agg(
        count("admission_id").alias("total_admissions"),
        round(avg("total_bill"), 2).alias("avg_bill")
    ) \
    .orderBy("severity", "status")

gold_severity.show()

# COMMAND ----------

# MAGIC %md ### Cell 7 — Write All Gold Tables to Delta Lake

# COMMAND ----------

gold_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/gold"

gold_dept.write.format("delta").mode("overwrite").save(f"{gold_path}/admissions_by_department")
gold_monthly.write.format("delta").mode("overwrite").save(f"{gold_path}/monthly_admissions_trend")
gold_diagnoses.write.format("delta").mode("overwrite").save(f"{gold_path}/top_diagnoses")
gold_severity.write.format("delta").mode("overwrite").save(f"{gold_path}/severity_summary")

print("✅ Gold layer written successfully!")
print("   gold/admissions_by_department")
print("   gold/monthly_admissions_trend")
print("   gold/top_diagnoses")
print("   gold/severity_summary")
