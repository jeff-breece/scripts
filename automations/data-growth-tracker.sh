#!/bin/bash

# Define paths
RAW_DIR="/media/jeffbreece/Storage/data/raw"
RAID_MOUNT="/media/jeffbreece/Storage"  # Base mount for RAID
LOG_FILE="/home/jeffbreece/Logs/raw_folder_size.log"

# Get the current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S") 

# Get total raw folder size
SIZE_HR=$(du -sh "$RAW_DIR" 2>/dev/null | awk '{print $1}')

# Get free space on RAID drive
FREE_SPACE=$(df -h "$RAID_MOUNT" | awk 'NR==2 {print $4}')

# Get sizes of specific subfolders
FOOD_IMPORTS_SIZE=$(du -sh "$RAW_DIR/foood_imports" 2>/dev/null | awk '{print $1}')
GARMIN_SIZE=$(du -sh "$RAW_DIR/garmin_biometrics_data" 2>/dev/null | awk '{print $1}')
NOAA_GHCN_SIZE=$(du -sh "$RAW_DIR/noaa_ghcn" 2>/dev/null | awk '{print $1}')
USGS_NWIS_SIZE=$(du -sh "$RAW_DIR/usgs_nwis" 2>/dev/null | awk '{print $1}')

# Append results to the log file
echo "$TIMESTAMP - Size: $SIZE_HR | Free Space: $FREE_SPACE | Food Imports: $FOOD_IMPORTS_SIZE | Garmin: $GARMIN_SIZE | NOAA GHCN: $NOAA_GHCN_SIZE | USGS NWIS: $USGS_NWIS_SIZE" >> "$LOG_FILE"

# Print result to terminal
echo "Logged: $TIMESTAMP - Size: $SIZE_HR | Free Space: $FREE_SPACE | Food Imports: $FOOD_IMPORTS_SIZE | Garmin: $GARMIN_SIZE | NOAA GHCN: $NOAA_GHCN_SIZE | USGS NWIS: $USGS_NWIS_SIZE to $LOG_FILE"

