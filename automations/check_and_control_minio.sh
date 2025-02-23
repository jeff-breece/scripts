#!/bin/bash

# Define the path for the RAID drive and MinIO service
RAID_PATH="/media/jeffbreece/Storage"
MINIO_SERVICE="minio"

# Check if the RAID drive is mounted
if mountpoint -q $RAID_PATH; then
    echo "RAID drive is mounted at $RAID_PATH."
    
    # Start MinIO service if not already running
    if ! systemctl is-active --quiet $MINIO_SERVICE; then
        echo "MinIO service is not running. Starting MinIO..."
        sudo systemctl start $MINIO_SERVICE
    else
        echo "MinIO service is already running."
    fi
else
    echo "RAID drive is not mounted at $RAID_PATH."
    
    # Stop MinIO service if it's running
    if systemctl is-active --quiet $MINIO_SERVICE; then
        echo "Stopping MinIO service..."
        sudo systemctl stop $MINIO_SERVICE
    else
        echo "MinIO service is not running."
    fi
fi
