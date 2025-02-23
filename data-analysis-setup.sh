#!/bin/bash
# Script I am working on to do some data anlysis on stream dynamics on a precompiled data set

# Exit on errors
set -e

echo "Starting installation of Anaconda, R, and Mamba on your Pangolin..."

# Define installation directories
ANACONDA_INSTALLER="Anaconda3-latest-Linux-x86_64.sh"
ANACONDA_URL="https://repo.anaconda.com/archive/$ANACONDA_INSTALLER"
ANACONDA_ALT_URL="https://repo.anaconda.com/archive/Anaconda3-2023.11-Linux-x86_64.sh"  # Fallback URL

# Function to check if URL is accessible
check_url() {
  curl --head --silent --fail "$1" > /dev/null
}

# Check if primary Anaconda URL is reachable
if check_url "$ANACONDA_URL"; then
  echo "Primary Anaconda URL is accessible, downloading..."
  wget "$ANACONDA_URL"
else
  echo "Primary Anaconda URL failed, attempting fallback URL..."
  if check_url "$ANACONDA_ALT_URL"; then
    echo "Fallback URL is accessible, downloading..."
    wget "$ANACONDA_ALT_URL" -O "$ANACONDA_INSTALLER"
  else
    echo "Both URLs are unavailable. Please check your network connection and try again."
    exit 1
  fi
fi

# Run the Anaconda installer
bash "$ANACONDA_INSTALLER"

# Initialize Conda
echo "Initializing Conda..."
~/anaconda3/bin/conda init

# Update Conda to the latest version
echo "Updating Conda..."
conda update -n base -c defaults conda -y

# Install Mamba for faster package management
echo "Installing Mamba..."
conda install -n base -c conda-forge mamba -y

# Install R (add the repository and key)
echo "Installing R..."
sudo apt-get update
sudo apt-get install -y r-base

echo "Installation completed successfully!"

