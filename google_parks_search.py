import json
import requests

# Define your Google Search function
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
        "num": num_results,  # Limit results to top N
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json().get("organic_results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error during Google Search: {e}")
        return []


# Read the spider's JSON result
input_file = "ohio_state_parks.json"
output_file = "ohio_state_parks_with_google_results.json"
api_key = "ed7919256c62983b981f23dc99881597c8db058d58142bab1dd8024631939ccc"

try:
    with open(input_file, "r", encoding="utf-8") as infile:
        parks_data = json.load(infile)
except FileNotFoundError:
    print(f"Error: File {input_file} not found.")
    parks_data = []

# Loop through the parks and perform Google searches
for park in parks_data:
    park_name = park.get("park_name", "Unknown Park")
    if park_name:
        query = f"{park_name} Ohio State Parks"
        print(f"Performing Google search for: {query}")
        google_results = google_search(query, api_key)

        # Add Google results to the park data
        park["google_results"] = google_results

# Save the updated data to a new JSON file
try:
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(parks_data, outfile, indent=4, ensure_ascii=False)
    print(f"Updated data saved to {output_file}")
except Exception as e:
    print(f"Error saving output file: {e}")
