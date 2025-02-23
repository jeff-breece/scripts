import json
import requests
import hvac

# ---------------------------
# Vault Configuration
# ---------------------------
VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "your-token-here")
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

# Fetch SERP API Key from Vault
try:
    vault_secrets = client.secrets.kv.v2.read_secret_version(
        path="automation_keys",
        raise_on_deleted_version=True
    )["data"]["data"]
    api_key = vault_secrets["SERP_API_KEY"]
except Exception as e:
    print(f"Error accessing Vault for SERP API Key: {e}")
    exit(1)

# ---------------------------
# Google Search Function
# ---------------------------
def google_search(query, api_key, num_results=3):
    """
    Perform a Google search using SerpAPI.

    Args:
        query (str): The search query.
        api_key (str): SerpAPI API key.
        num_results (int): Number of results to return.

    Returns:
        list: A list of search result dictionaries.
    """
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "num": num_results,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("organic_results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error during Google Search: {e}")
        return []

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    try:
        # Prompt user for search string
        search_query = input("Enter the search query: ")
        
        # Read the spider's JSON result
        input_file = "ohio_state_parks.json"
        output_file = "ohio_state_parks_with_google_results.json"

        try:
            with open(input_file, "r", encoding="utf-8") as infile:
                parks_data = json.load(infile)
        except FileNotFoundError:
            print(f"Error: File {input_file} not found.")
            parks_data = []

        # Loop through parks and perform Google searches
        for park in parks_data:
            park_name = park.get("park_name", "Unknown Park")
            query = f"{search_query} {park_name} Ohio State Parks"
            print(f"Performing Google search for: {query}")
            google_results = google_search(query, api_key)

            # Add Google results to the park data
            park["google_results"] = google_results

        # Save updated data to a new JSON file
        try:
            with open(output_file, "w", encoding="utf-8") as outfile:
                json.dump(parks_data, outfile, indent=4, ensure_ascii=False)
            print(f"✅ Updated data saved to {output_file}")
        except Exception as e:
            print(f"Error saving output file: {e}")

    except Exception as e:
        print(f"🚨 An unexpected error occurred: {e}")
