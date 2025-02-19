#!/bin/bash

# Define the NOAA GHCN source URL
SOURCE_URL="https://www.ncei.noaa.gov/pub/data/ghcn/daily/"

# Define the local destination directory
LOCAL_DIR="/home/jeff/data/noaa_ghcn/"

# Create the directory if it doesn't exist
mkdir -p "$LOCAL_DIR"

# Use wget to recursively download all files while preserving structure
wget --mirror --no-parent --convert-links --relative --continue --timestamping \
     --no-check-certificate --execute robots=off --quiet \
     --directory-prefix="$LOCAL_DIR" "$SOURCE_URL"

# Print completion message
echo "✅ NOAA GHCN Daily dataset downloaded successfully to: $LOCAL_DIR"
