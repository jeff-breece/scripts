#!/bin/bash

# Source and destination directories
SOURCE="/media/jeffbreece/fly-drive/backups"
DEST="/media/jeffbreece/1TB-SATA/backups"
LOGFILE="/media/jeffbreece/1TB-SATA/logs/backup_sync.log"

# Ensure destination directory exists
mkdir -p "$DEST"

# Perform rsync backup
rsync -av --delete "$SOURCE/" "$DEST/" >> "$LOGFILE" 2>&1

# Log completion
echo "Backup sync completed on $(date)" >> "$LOGFILE"
