#!/bin/bash

# ---------------------------
# Vault Configuration
# ---------------------------
VAULT_ADDR="http://127.0.0.1:8200"
VAULT_TOKEN=$(cat ~/.vault-token)  # Ensure this token exists and has access

# Fetch SLACK_WEBHOOK_URL from Vault
SLACK_WEBHOOK_URL=$(vault kv get -field=SLACK_WEBHOOK_URL automation_keys/slack_monitor)

if [ -z "$SLACK_WEBHOOK_URL" ]; then
  echo "❌ Failed to retrieve SLACK_WEBHOOK_URL from Vault."
  exit 1
fi

# ---------------------------
# System Monitoring Parameters
# ---------------------------
CPU_THRESHOLD=85
MEM_THRESHOLD=80
DISK_THRESHOLD=80
ALERT_TRIGGERED=false

# ---------------------------
# System Monitoring Functions
# ---------------------------

# Function to check CPU usage
check_cpu_usage() {
  CPU_LOAD=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
  CPU_LOAD_INT=${CPU_LOAD%.*}

  if [ "$CPU_LOAD_INT" -gt "$CPU_THRESHOLD" ]; then
    ALERT_TRIGGERED=true
    echo "⚠️ High CPU Usage: ${CPU_LOAD}%"
    send_slack_alert "⚠️ *CPU Alert*: CPU usage is at ${CPU_LOAD}% on $(hostname)."
  fi
}

# Function to check memory usage
check_memory_usage() {
  MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
  MEM_USAGE_INT=${MEM_USAGE%.*}

  if [ "$MEM_USAGE_INT" -gt "$MEM_THRESHOLD" ]; then
    ALERT_TRIGGERED=true
    echo "⚠️ High Memory Usage: ${MEM_USAGE_INT}%"
    send_slack_alert "⚠️ *Memory Alert*: Memory usage is at ${MEM_USAGE_INT}% on $(hostname)."
  fi
}

# Function to check disk usage
check_disk_usage() {
  DISK_USAGE=$(df -h / | grep '/' | awk '{ print $5 }' | sed 's/%//g')

  if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    ALERT_TRIGGERED=true
    echo "⚠️ High Disk Usage: ${DISK_USAGE}%"
    send_slack_alert "⚠️ *Disk Alert*: Disk usage is at ${DISK_USAGE}% on $(hostname)."
  fi
}

# Function to send alerts to Slack
send_slack_alert() {
  MESSAGE=$1
  curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"${MESSAGE}\"}" "$SLACK_WEBHOOK_URL"
}

# ---------------------------
# Main Monitoring Logic
# ---------------------------
echo "🔍 Starting System Monitoring..."

check_cpu_usage
check_memory_usage
check_disk_usage

if [ "$ALERT_TRIGGERED" = false ]; then
  echo "✅ System health is normal."
else
  echo "🚨 Alerts have been triggered. Check Slack for details."
fi

echo "📊 Monitoring complete."
