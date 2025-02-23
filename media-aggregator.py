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
import pandas as pd
from io import BytesIO

# ---------------------------
# Vault Configuration
# ---------------------------
VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "your-token-here")
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

# Updated to use automation_keys
vault_secrets = try:
    vault_secrets = client.secrets.kv.v2.read_secret_version(
        path="automation_keys",
        raise_on_deleted_version=True
    )["data"]["data"]
except Exception as e:
    print(f"Error accessing Vault: {e}")
    exit(1)["data"]["data"]

NEWS_API_KEY = vault_secrets["NEWS_API_KEY"]
MINIO_ACCESS_KEY = vault_secrets["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY = vault_secrets["MINIO_SECRET_KEY"]

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Vault secrets loaded successfully.")

# ---------------------------
# Configuration Parameters
# ---------------------------
OUTPUT_DIR = "/media/jeffbreece/Storage/data/raw/media/"
ARCHIVE_DIR = "/media/jeffbreece/Storage/data/archive/media/"

# MinIO Configurations
MINIO_ENDPOINT = "localhost:9000"
S3_BUCKET = "processed"

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
# Functions
# ---------------------------
def fetch_newsapi():
    url = "https://newsapi.org/v2/everything"
    params = {"q": QUERY, "language": LANGUAGE, "pageSize": PAGE_SIZE, "from": DATE_FROM}
    headers = {"Authorization": f"Bearer {NEWS_API_KEY}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [{
            "title": a.get("title"),
            "url": a.get("url"),
            "source": a.get("source", {}).get("name"),
            "publishedAt": a.get("publishedAt"),
            "description": a.get("description")
        } for a in articles]
    else:
        print("NewsAPI error:", response.status_code, response.text)
        return []

def fetch_google_news():
    encoded_query = urllib.parse.quote(QUERY)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={LANGUAGE}&gl=US&ceid=US:{LANGAGE.upper()}"
    feed = feedparser.parse(rss_url)
    return [{
        "title": entry.get("title"),
        "url": entry.get("link"),
        "source": entry.get("source", {}).get("title", "Google News"),
        "publishedAt": entry.get("published"),
        "description": entry.get("summary")
    } for entry in feed.entries]

def deduplicate_articles(articles):
    seen_urls = set()
    return [a for a in articles if a.get("url") not in seen_urls and not seen_urls.add(a.get("url"))]

def upload_to_s3(file_buffer, s3_key):
    try:
        try:
    s3_client.upload_fileobj(file_buffer, S3_BUCKET, s3_key)
    print(f"File successfully uploaded to S3 as {s3_key}.")
except NoCredentialsError:
    print("Credentials not available for MinIO.")
except Exception as e:
    print(f"Error uploading file to S3: {e}")
        print(f"File successfully uploaded to S3 as {s3_key}.")
    except NoCredentialsError:
        print("Credentials not available for MinIO.")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

def archive_raw_file(file_path):
    archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(file_path))
    shutil.copy(file_path, archive_path)
    print(f"Raw file archived to: {archive_path}")
    os.remove(file_path)

def save_articles(articles):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path_json = os.path.join(OUTPUT_DIR, f"news_combined_{timestamp}.json")

    with open(file_path_json, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=4)

    df = pd.DataFrame(articles)
    parquet_buffer = BytesIO()
    try:
    df.to_parquet(parquet_buffer, engine='pyarrow')
except Exception as e:
    print(f"Error converting to Parquet: {e}")
    return
    parquet_buffer.seek(0)
    s3_key = f"water-news-alerts/media/water-news-alert_{timestamp}.parquet"
    upload_to_s3(parquet_buffer, s3_key)
    archive_raw_file(file_path_json)

def main():
    articles_newsapi = fetch_newsapi()
articles_google_news = fetch_google_news()
articles = articles_newsapi + articles_google_news
if not articles_newsapi:
    print("No articles fetched from NewsAPI.")
if not articles_google_news:
    print("No articles fetched from Google News.")
    print(f"Fetched {len(articles)} articles before deduplication.")
    articles = deduplicate_articles(articles)
    print(f"{len(articles)} articles remain after deduplication.")
    if articles:
        save_articles(articles)
    else:
        print("No articles found.")

if __name__ == "__main__":
    main()
