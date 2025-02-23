#!/bin/bash

# Set the base URL for GHCN-Daily data
BASE_URL="https://www.ncei.noaa.gov/pub/data/ghcn/daily/"

# Define directories containing data files
DATA_DIRS=("all" "by_year" "by_station")

# Define specific metadata files to download
METADATA_FILES=("ghcnd-stations.txt" "ghcnd-inventory.txt" "ghcnd-countries.txt" "ghcnd-states.txt" "readme.txt" "readme-by_year.txt" "readme-by_station.txt")

# Define the target directory for downloads
TARGET_DIR="/media/jeffbreece/Storage/data/raw/noaa_ghcn/second-attempt"

# Create the target directory if it doesn’t exist
mkdir -p "$TARGET_DIR"

# Function to check if a file exists before downloading
download_if_missing() {
    local url="$1"
    local filepath="$2"

    if [[ -f "$filepath" ]]; then
        echo "Skipping: $filepath (already exists)"
    else
        echo "Downloading: $url"
        wget -q --show-progress -P "$(dirname "$filepath")" "$url"
        if [[ $? -ne 0 ]]; then
            echo "⚠️ Error downloading $url"
        fi
    fi
}

# Download metadata files only if they are missing
for file in "${METADATA_FILES[@]}"; do
    download_if_missing "${BASE_URL}${file}" "$TARGET_DIR/$file"
done

# Download data files from selected directories
for dir in "${DATA_DIRS[@]}"; do
    DIR_PATH="$TARGET_DIR/$dir"
    mkdir -p "$DIR_PATH"

    echo "Checking directory: $dir"

    # Get the file list from the NOAA server
    FILE_LIST=$(wget -qO- "${BASE_URL}${dir}/" | grep -oE 'href="[^"]+"' | cut -d '"' -f2)

    for file in $FILE_LIST; do
        # Ensure we're only downloading data files
        if [[ "$file" == *.dly || "$file" == *.csv ]]; then
            download_if_missing "${BASE_URL}${dir}/$file" "$DIR_PATH/$file"
        fi
    done
done

echo "✅ GHCN-Daily data and metadata files updated successfully in $TARGET_DIR!"

