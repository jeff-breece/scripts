#!/bin/bash

# ========================================
# Data Lake Lab Setup Script (Enhanced)
# Configures MinIO, HashiCorp Vault, and required dependencies
# ========================================

# Ensure the script runs as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Try running: sudo $0"
    exit 1
fi

# ----------------------------------------
# Update System Packages
# ----------------------------------------
echo "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

# Install dependencies
sudo apt install -y wget unzip openjdk-11-jdk scala python3-pip acl jq curl net-tools \
                    software-properties-common apt-transport-https ca-certificates
pip3 install pyspark hvac boto3 feedparser pandas pyarrow

# ----------------------------------------
# Set Up Directories (Restored from Original)
# ----------------------------------------
echo "Setting up data storage directories..."
DATA_DIR="/media/jeffbreece/Storage/data"
RAW_DIR="$DATA_DIR/raw"
PROCESSED_DIR="$DATA_DIR/processed"
ARCHIVE_DIR="$DATA_DIR/archive"
LOG_DIR="/media/jeffbreece/Storage/logs"
MODELS_DIR="/media/jeffbreece/Storage/models"

mkdir -p $RAW_DIR $PROCESSED_DIR $ARCHIVE_DIR $LOG_DIR $MODELS_DIR
chown jeffbreece:jeffbreece $DATA_DIR -R
chmod 750 $DATA_DIR -R

# ----------------------------------------
# Install and Configure MinIO
# ----------------------------------------
echo "Installing MinIO..."
wget -q https://dl.min.io/server/minio/release/linux-amd64/minio -O /usr/local/bin/minio
chmod +x /usr/local/bin/minio

# Create MinIO systemd service
cat <<EOF | sudo tee /etc/systemd/system/minio.service
[Unit]
Description=MinIO Object Storage
After=network.target

[Service]
ExecStart=/usr/local/bin/minio server --console-address ":9001" /media/jeffbreece/Storage/data
User=jeffbreece
Group=jeffbreece
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start MinIO
sudo systemctl daemon-reload
sudo systemctl enable --now minio

# ----------------------------------------
# Install and Configure HashiCorp Vault (Restored Additional Steps)
# ----------------------------------------
echo "Installing HashiCorp Vault..."
wget -qO- https://apt.releases.hashicorp.com/gpg | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install -y vault

# Create Vault Configuration
mkdir -p /etc/vault/
cat <<EOF | sudo tee /etc/vault/config.hcl
storage "file" {{
  path = "/var/lib/vault"
}}
listener "tcp" {{
  address = "127.0.0.1:8200"
  tls_disable = 1
}}
disable_mlock = true
api_addr = "http://127.0.0.1:8200"
EOF

# Create Vault systemd service
cat <<EOF | sudo tee /etc/systemd/system/vault.service
[Unit]
Description=HashiCorp Vault - Secrets Management
Requires=network.target
After=network.target

[Service]
ExecStart=/usr/bin/vault server -config=/etc/vault/config.hcl
Restart=on-failure
User=root
Group=root
WorkingDirectory=/var/lib/vault
ExecReload=/bin/kill --signal HUP $MAINPID
KillSignal=SIGTERM
LimitMEMLOCK=infinity
AmbientCapabilities=CAP_IPC_LOCK

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Vault
sudo systemctl daemon-reload
sudo systemctl enable --now vault

# ----------------------------------------
# Manual Steps Required (Human Input Needed)
# ----------------------------------------
echo "
Manual Steps Required:
1. Initialize Vault: Run 'vault operator init' and save the keys securely.
2. Unseal Vault: Run 'vault operator unseal' three times with different keys.
3. Log into Vault: Run 'vault login <root-token>'.
4. Enable KV Secrets Engine: Run 'vault secrets enable -path=secret kv-v2'.
5. Store MinIO and API Keys in Vault:
   vault kv put secret/news_aggregator NEWS_API_KEY="your-key" MINIO_ACCESS_KEY="your-access-key" MINIO_SECRET_KEY="your-secret-key"
6. Set VAULT_TOKEN for automation: 'export VAULT_TOKEN=<your-token>'"

# Final message
echo "
🚀 Data Lake Lab setup complete! 🚀
- MinIO is running at http://localhost:9001
- Vault is running at http://127.0.0.1:8200
- Run the manual steps above to finalize setup.
"
