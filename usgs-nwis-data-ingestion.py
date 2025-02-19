import os
import requests
from datetime import datetime

# Base directory for raw data storage on RAID drive
BASE_DIR = "/media/jeffbreece/Storage/data/raw/usgs_nwis"
STATE = "OH"  # Ohio

# USGS NWIS Daily Values API endpoint
API_URL = "https://waterservices.usgs.gov/nwis/dv/"

# Define parameter codes for daily values
PARAM_CODES = {
    "water_quality": ["00010", "00300", "00400", "99133", "63680"],
    "streamflow": ["00060", "00065"],
    "groundwater": ["72019", "62610"]
}

# Set date parameters for Year-to-Date (YTD)
current_date = datetime.today()
year = current_date.strftime("%Y")
month = current_date.strftime("%m")
start_date = f"{year}-01-01"
end_date = current_date.strftime("%Y-%m-%d")

# Function to create directories if they don't exist
def ensure_directory(topic):
    dir_path = os.path.join(BASE_DIR, topic, year, month)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

# Function to download data
def download_data(topic):
    parameters = ",".join(PARAM_CODES[topic])
    url = (
        f"{API_URL}?format=json&stateCd={STATE}"
        f"&startDT={start_date}&endDT={end_date}&parameterCd={parameters}"
    )
    
    response = requests.get(url)
    
    if response.status_code == 200 and "value" in response.text:
        save_path = os.path.join(ensure_directory(topic), f"{topic}_{year}_{month}.json")
        with open(save_path, "w") as file:
            file.write(response.text)
        print(f"✅ {topic.capitalize()} data saved to: {save_path}")
    else:
        print(f"❌ Failed to download {topic} data. Status Code: {response.status_code}")
        print(f"   URL: {url}")
        print(f"   Response: {response.text[:500]}")  # Print first 500 chars of response for debugging

# Download datasets
download_data("water_quality")
download_data("streamflow")
download_data("groundwater")

print("🎯 USGS NWIS Ohio daily values data ingestion completed successfully!")