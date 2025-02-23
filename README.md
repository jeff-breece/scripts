# 🚀 Data Lake & Automation Scripts

This repository contains a collection of scripts and automation tools designed to manage data ingestion, analysis, and monitoring tasks within my home data lake & AI (Nvidia Orin Nano 4GB) environment.

---

## 📂 **Scripts Overview**

### **1. Automations**

- **`check_and_control_minio.sh`**  
  Ensures the MinIO instance is operational, manages bucket policies, and verifies access credentials.

- **`cold-storage-backup.sh`**  
  Automates bi-weekly backup replication from the main storage to cold storage for data redundancy.

- **`data-growth-tracker.sh`**  
  Tracks and logs data lake growth over time, monitoring storage utilization.

- **`download_noaa_ghcn_focused.sh`**  
  Downloads Global Historical Climatology Network (GHCN) focused datasets, optimized for environmental data ingestion.

- **`system-monitor.sh`**  
  Monitors CPU, memory, and disk usage, sending Slack alerts via a secure Vault integration if resource thresholds are exceeded.

- **`usgs-nwis-data-ingestion.py`**  
  Automates daily ingestion of USGS NWIS water quality, streamflow, and groundwater data, saving structured files in the raw data lake.

---

### **2. Data Processing & Analysis**

- **`data-analysis-setup.sh`**  
  Sets up the required Python environment and dependencies for running data analysis notebooks and scripts.

- **`datalake-lab-setup.sh`**  
  Initializes and configures the data lake infrastructure, including MinIO, Spark, and Trino services.

- **`audio-log.py`**  
  Transcribes MP3 audio journal files using Whisper and performs local sentiment analysis to track personal mood over time.

- **`flask-bot-api.py`**  
  A Flask-based API that serves as a foundational layer for integrating future chatbot features, potentially including LLM query handling.

- **`garmin.py`**  
  Fetches biometric data from Garmin Connect using secure Vault-stored credentials. Supports user-defined date ranges for data exports.

- **`google_parks_search.py`**  
  Utilizes SerpAPI to enhance park datasets with Google Search results. Integrates Vault for secure API key storage and prompts for custom search queries.

- **`media-aggregator.py`**  
  Aggregates news articles from NewsAPI, Google News RSS, and other sources. De-duplicates, transforms to Parquet, and uploads to MinIO for downstream analysis.

- **`purge-linked-in.py`**  
  Automates the process of cleaning LinkedIn data exports by removing redundant fields and formatting the dataset for further analysis.

- **`water-news-alerts-datalake-test.py`**  
  A testing script for validating the data lake integration of water news alerts, ensuring the correct ingestion and structuring of media data.

---

## 📊 **Data Folders**

- **`data/ohio_state_parks.json`**  
  Source dataset containing Ohio State Parks information.

- **`data/ohio_state_parks_with_google_results.json`**  
  Enhanced dataset with Google Search results appended.

---

## 🔒 **Vault-Managed Secrets**

Several scripts leverage **HashiCorp Vault** for securely storing and accessing API keys, credentials, and sensitive configurations:

- **`automation_keys/serp_api`** → SerpAPI key
- **`automation_keys/garmin_user`** & **`automation_keys/garmin_password`** → Garmin Connect credentials
- **`automation_keys/news_api`**, **`automation_keys/minio_access`**, **`automation_keys/minio_secret`** → News API & MinIO credentials

---

## 📅 **Planned Enhancements**

- **Airflow DAGs** for scheduling ETL jobs.
- **Athena/Trino Integration** for complex querying on the data lake.
- **Real-time Monitoring** for critical systems using Prometheus + Grafana.

---

💡 TODO: I am in the process of paramterizing the various hard coded directories into a global config file. These would need to be adjusted to your purpose in the off chance that anyone does a pull on this repo.

