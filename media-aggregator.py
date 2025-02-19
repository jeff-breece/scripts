import hvac
import os
import requests
import json
import shutil
from datetime import datetime, timedelta
import feedparser
import urllib.parse
import boto3
from botocore.exceptions import NoCredentialsError
import pandas as pd  # Import pandas for Parquet conversion
from io import BytesIO

# ---------------------------
# Vault Configuration
# ---------------------------
VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "your-token-here")
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
vault_secrets = client.secrets.kv.v2.read_secret_version(path="news_aggregator")["data"]["data"]
NEWS_API_KEY = vault_secrets["NEWS_API_KEY"]
MINIO_ACCESS_KEY = vault_secrets["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY = vault_secrets["MINIO_SECRET_KEY"]

# Print to verify (remove in production)
print("Vault secrets loaded successfully.")

# ---------------------------
# Configuration Parameters
# ---------------------------
OUTPUT_DIR = "/media/jeffbreece/Storage/data/raw/media/"
ARCHIVE_DIR = "/media/jeffbreece/Storage/data/archive/media/"

# MinIO (S3) Configurations
MINIO_ENDPOINT = "localhost:9000"
S3_BUCKET = "water-news-alerts"

# Common search parameters
SEARCH_TERMS = [
    "water resources", "freshwater", "surface water", "groundwater", "water supply",
    "river flow", "streamflow", "watershed", "hydrology", "reservoir levels"
]
QUERY = " OR ".join(SEARCH_TERMS)
LANGUAGE = "en"
PAGE_SIZE = 20
DATE_FROM = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# ---------------------------
# MinIO Client Setup
# ---------------------------
s3_client = boto3.client(
    's3',
    endpoint_url=f'http://{MINIO_ENDPOINT}',
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name='us-east-1'
)

# ---------------------------
# Functions to fetch articles
# ---------------------------

def fetch_newsapi():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": QUERY,
        "language": LANGUAGE,
        "pageSize": PAGE_SIZE,
        "from": DATE_FROM
    }
    headers = {
        "Authorization": f"Bearer {NEWS_API_KEY}"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        normalized = []
        for a in articles:
            normalized.append({
                "title": a.get("title"),
                "url": a.get("url"),
                "source": a.get("source", {}).get("name"),
                "publishedAt": a.get("publishedAt"),
                "description": a.get("description")
            })
        return normalized
    else:
        print("NewsAPI error:", response.status_code, response.text)
        return []


def fetch_google_news():
    encoded_query = urllib.parse.quote(QUERY)  # URL encode the query string
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={LANGUAGE}&gl=US&ceid=US:{LANGUAGE.upper()}"
    feed = feedparser.parse(rss_url)
    normalized = []
    for entry in feed.entries:
        normalized.append({
            "title": entry.get("title"),
            "url": entry.get("link"),
            "source": entry.get("source", {}).get("title") if "source" in entry else "Google News",
            "publishedAt": entry.get("published"),
            "description": entry.get("summary")
        })
    return normalized

# ---------------------------
# Deduplication Function
# ---------------------------
def deduplicate_articles(articles):
    seen_urls = set()
    deduped = []
    for article in articles:
        url = article.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(article)
    return deduped

# ---------------------------
# MinIO (S3) Upload Function
# ---------------------------
def upload_to_s3(file_buffer, s3_key):
    try:
        s3_client.upload_fileobj(file_buffer, S3_BUCKET, s3_key)
        print(f"File successfully uploaded to S3 as {s3_key}.")
    except NoCredentialsError:
        print("Credentials not available for MinIO.")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

# ---------------------------
# File Archival Function
# ---------------------------
def archive_raw_file(file_path):
    archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(file_path))
    shutil.copy(file_path, archive_path)
    print(f"Raw file archived to: {archive_path}")
    os.remove(file_path)  # Optionally delete the raw file after archiving

# ---------------------------
# Saving Function (Direct Upload to S3)
# ---------------------------
def save_articles(articles):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path_json = os.path.join(OUTPUT_DIR, f"news_combined_{timestamp}.json")
    
    # Save raw JSON file locally first
    with open(file_path_json, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=4)
    print(f"Saved raw {len(articles)} articles to {file_path_json}")
    
    # Convert to Parquet format (in memory) and upload directly to MinIO
    df = pd.DataFrame(articles)
    
    # Generate S3 key for the Parquet file with topic prefix
    s3_key = f"processed/media/water-news-alert_{timestamp}.parquet"
    
    # Upload the Parquet file to MinIO directly (in memory)
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, engine='pyarrow')
    parquet_buffer.seek(0)  # Reset buffer pointer to the start
    
    upload_to_s3(parquet_buffer, s3_key)
    
    # Archive raw file after upload
    archive_raw_file(file_path_json)

# ---------------------------
# Main function
# ---------------------------
def main():
    articles = []
    print("Fetching articles from NewsAPI...")
    articles.extend(fetch_newsapi())
    
    print("Fetching articles from Google News RSS...")
    articles.extend(fetch_google_news())
    
    print(f"Fetched a total of {len(articles)} articles before deduplication.")
    articles = deduplicate_articles(articles)
    print(f"{len(articles)} articles remain after deduplication.")
    
    if articles:
        save_articles(articles)
    else:
        print("No articles found.")

if __name__ == "__main__":
    main()