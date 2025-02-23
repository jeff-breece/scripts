#!/bin/bash
# ========================================
# 📊 Data Lake Lab Setup Script (Enhanced)
# ========================================
# 🎯 Purpose:
#   This script automates the setup of a **Data Lake Lab** AI environment, ensuring
#   all core tools, services, and dependencies are installed, configured, and ready 
#   for use while maintaining system hygiene and efficiency. Note, the AI components 
#   will be running on an Nvidia Orion Nano (primariluy Hugging Face for NLP and
#   vision experiments. The Datalake is based out of a external high performance
#   RAID drive surfaced inside a MinIo S3 storage layer.

# 🛠️ Core System & Productivity Tools:
#   - **Deja Dup** → Backup solution for safeguarding data.
#   - **Slack** → Communication and team collaboration.
#   - **Git** → Version control system for managing codebases.
#   - **Visual Studio Code** → Lightweight IDE for development tasks.
#   - **Thunderbird** → Email client for personal and professional use.

# 💾 Data Lake Core Components:
#   - **MinIO** → S3-compatible object storage for your data lake.
#   - **HashiCorp Vault** → Secrets management and secure access control.
#   - **ClamAV** → Antivirus scanner for data integrity and system security.

# 💡 Development Ecosystem:
#   - **Node.js & NPM** → JavaScript runtime for backend and frontend development.
#   - **Jekyll & Bundler** → Static site generator for web development.
#   - **.NET SDK** → .NET Core framework for cross-platform development.
#   - **Java 17** → Required for Spark and other JVM-based tools.
#   - **PySpark** → Python API for Apache Spark, enabling big data analytics.

# 📊 Data Engineering & Orchestration:
#   - **Apache Airflow** → Workflow orchestration for ETL processes.
#   - **Trino** → Distributed SQL query engine for fast data lake queries.

# 🧹 System Integrity & Maintenance:
#   - **Repository Cleanup** → Detects and removes outdated or broken repositories.
#   - **Slack Installer Check** → Skips reinstallation if Slack is already present.
#   - **Orphaned Package Removal** → Keeps the system clean with autoremove.
#   - **Temporary File Cleanup** → Removes leftover installation files post-setup.

# 📌 Notes:
#   - The script checks for existing installations to avoid duplicates.
#   - It handles known repository issues and ensures system package integrity.
#   - Designed for **Pop!_OS 22.04** but adaptable to other Ubuntu-based systems.

# 🚀 Run with:
#   sudo ./datalake-lab-setup.sh

# 🟢 Hardware Requirements (Jetson Orin Nano + Data Lake Workloads):
# - NVIDIA Jetson Orin Nano 4GB (Minimum) — 8GB or higher (Recommended)
# - External RAID Array (18TB WD Red Pro Drives) — for Parquet storage and raw data
# - 1TB NVMe SSD or MicroSD (for OS and local app data)
# - 5V 4A Power Supply (ensure stable power for Orin and peripherals)
# - At least 32GB swap space (to handle memory-intensive tasks with PySpark/Trino)

# 🟢 Networking:
# - Gigabit Ethernet recommended (for MinIO and distributed queries)
# - Configure local network for internal IP addressing if clustering later

# --------------------------------------------------------------------------------------
# 📁 MinIO — Object Storage for Parquet Files
# --------------------------------------------------------------------------------------
# - CPU: 2 cores minimum (4+ recommended for concurrent reads/writes)
# - RAM: 2GB minimum (4GB recommended for high I/O)
# - Disk: Direct access to RAID array for raw and processed data
# - Network: Gigabit Ethernet (to handle multiple ETL tasks)
# - Configuration:
#   - Run in distributed mode if scaling is planned
#   - Enable versioning and bucket policies for data governance
#   - S3-compatible — can integrate directly with PySpark and Trino

# --------------------------------------------------------------------------------------
# 🔥 PySpark — ETL & Batch Processing
# --------------------------------------------------------------------------------------
# - CPU: 4 cores minimum (8+ for large batch jobs)
# - RAM: 8GB minimum (16GB recommended for large datasets)
# - Disk: Access to RAID array and high-speed SSD for temp files
# - Java: OpenJDK 11 or 17 (compatible with Spark 3.x)
# - Configuration:
#   - Use Spark’s native support for Parquet files
#   - Set optimized partitioning strategies (avoid small file issues)
#   - Leverage GPU for ML/AI if extending Spark MLlib

# --------------------------------------------------------------------------------------
# ⏰ Airflow — Workflow Orchestration
# --------------------------------------------------------------------------------------
# - CPU: 2 cores minimum (4+ recommended for heavy DAGs)
# - RAM: 4GB minimum (8GB recommended for concurrent tasks)
# - Database: PostgreSQL or MySQL backend for Airflow metadata (SQLite not recommended for production)
# - Web Server: Flask-based, runs on port 8080 by default
# - Scheduler: Handles task queues and DAG executions
# - Configuration:
#   - Use Celery Executor for distributed task management if scaling
#   - Set up environment variables for DAGs, connections, and secrets

# --------------------------------------------------------------------------------------
# 🦌 Trino — Distributed SQL Query Engine
# --------------------------------------------------------------------------------------
# - CPU: 4 cores minimum (8+ for complex queries)
# - RAM: 8GB minimum (16GB recommended for complex joins and aggregations)
# - Disk: Fast SSD for query temp files and cache
# - Java: OpenJDK 17 (officially supported)
# - Configuration:
#   - Connect Trino to MinIO (as an S3-compatible storage) and query Parquet directly
#   - Set up catalogs for MinIO and local storage
#   - Enable parallel processing and optimize memory settings in `jvm.config`

# --------------------------------------------------------------------------------------
# ⚡ System-Wide Considerations:
# --------------------------------------------------------------------------------------
# - Docker (or Podman) for containerized deployments of MinIO, Airflow, and Trino
# - Use Nginx or Traefik as a reverse proxy if exposing services externally
# - GPU Acceleration: Use Orin’s GPU for AI/ML tasks (if expanding PySpark or Trino ML capabilities)
# - Monitoring: Integrate Prometheus + Grafana for tracking resource usage and performance
# - Backup Strategies: Regular snapshots of Parquet datasets and Airflow metadata DB

# 🟢 Recommended Deployment Order:
# 1. MinIO (to establish object storage)
# 2. PySpark (for ETL and data prep)
# 3. Airflow (to orchestrate workflows and automate tasks)
# 4. Trino (for federated querying across Parquet files and external data sources)


# ========================================
# Data Lake Lab Setup Script (Enhanced)
# Configures MinIO, HashiCorp Vault, and required dependencies
# ========================================

# Ensure the script runs as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Try running: sudo $0"
    exit 1
fi

# -----------------------------------------------
# Remove OpenProject Repository Completely - oops
# -----------------------------------------------
echo "Searching for OpenProject repository references..."
openproject_files=$(grep -rl "openproject" /etc/apt/sources.list /etc/apt/sources.list.d/)

if [ -n "$openproject_files" ]; then
    echo "Removing OpenProject repository files..."
    for file in $openproject_files; do
        sudo rm "$file"
        echo "Removed $file"
    done
    sudo apt clean
    sudo apt update
else
    echo "No OpenProject repository references found."
fi

# ----------------------------------------
# Update System Packages
# ----------------------------------------
echo "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

# ----------------------------------------
# Install Deja Dup (Backup Tool)
# ----------------------------------------
echo "Installing Deja Dup..."
sudo apt install -y deja-dup

# ----------------------------------------
# Install Slack (with check)
# ----------------------------------------
if ! command -v slack &> /dev/null; then
    echo "Installing Slack..."
    wget -O /tmp/slack.deb https://downloads.slack-edge.com/releases/linux/4.36.140/prod/x64/slack-desktop-4.36.140-amd64.deb
    if [ -f /tmp/slack.deb ]; then
        sudo apt install -y /tmp/slack.deb
    else
        echo "Failed to download Slack. Skipping installation."
    fi
else
    echo "Slack is already installed. Skipping."
fi

# ----------------------------------------
# Install Git
# ----------------------------------------
if ! command -v git &> /dev/null; then
    echo "Installing Git..."
    sudo apt install -y git
else
    echo "Git is already installed."
fi

# ----------------------------------------
# Install Node.js and NPM
# ----------------------------------------
if ! command -v node &> /dev/null; then
    echo "Installing Node.js and NPM..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
else
    echo "Node.js is already installed."
fi

# ----------------------------------------
# Install Jekyll and Bundler
# ----------------------------------------
if ! gem list -i jekyll &> /dev/null; then
    echo "Installing Jekyll and Bundler..."
    sudo apt install -y ruby-full build-essential zlib1g-dev
    gem install jekyll bundler
else
    echo "Jekyll is already installed."
fi

# ----------------------------------------
# Install ClamAV (Antivirus Scanner)
# ----------------------------------------
if ! command -v clamscan &> /dev/null; then
    echo "Installing ClamAV..."
    sudo apt install -y clamav clamav-daemon
    sudo systemctl stop clamav-freshclam
    sudo freshclam
    sudo systemctl start clamav-freshclam
else
    echo "ClamAV is already installed."
fi

# ----------------------------------------
# Install MinIO
# ----------------------------------------
if ! command -v minio &> /dev/null; then
    echo "Installing MinIO..."
    wget https://dl.min.io/server/minio/release/linux-amd64/minio -O /usr/local/bin/minio
    chmod +x /usr/local/bin/minio
else
    echo "MinIO is already installed."
fi

# ----------------------------------------
# Install HashiCorp Vault
# ----------------------------------------
if ! command -v vault &> /dev/null; then
    echo "Installing HashiCorp Vault..."
    wget https://releases.hashicorp.com/vault/1.14.4/vault_1.14.4_linux_amd64.zip -O /tmp/vault.zip
    unzip /tmp/vault.zip -d /usr/local/bin/
    chmod +x /usr/local/bin/vault
else
    echo "HashiCorp Vault is already installed."
fi

# ----------------------------------------
# Cleanup
# ----------------------------------------
echo "Cleaning up temporary files..."
sudo rm -f /tmp/slack.deb /tmp/vault.zip packages.microsoft.gpg packages-microsoft-prod.deb

echo "Data Lake Lab Setup Completed Successfully!"

