from flask import Flask, request, jsonify
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz
import spacy
import json
import re

# Initialize Flask app
app = Flask(__name__)

# Initialize NLP models
nlp = spacy.load("en_core_web_sm")
similarity_pipeline = pipeline("text-classification", model="cross-encoder/ms-marco-MiniLM-L-12-v2")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load your parks dataset
try:
    with open("ohio_state_parks_with_google_results.json", "r") as file:
        parks_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading JSON data: {e}")
    parks_data = []

# Preprocessing function for normalization
def preprocess_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)  # Remove punctuation
    return text

# Define your routes after app is created
@app.route("/ask", methods=["GET", "POST"])
def ask():
    if request.method == "GET":
        query = request.args.get("query", "").strip()
    elif request.method == "POST":
        data = request.get_json()
        query = data.get("query", "").strip() if data else ""
    else:
        return jsonify({"error": "Invalid method"}), 405

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Preprocess query
    query = preprocess_text(query)
    query_doc = nlp(query)
    query_phrases = {chunk.text.lower() for chunk in query_doc.noun_chunks}
    query_keywords = {token.lemma_ for token in query_doc if not token.is_stop}

    print(f"Query Phrases: {query_phrases}")
    print(f"Query Keywords: {query_keywords}")

    results = []

    for park in parks_data:
        park_name = preprocess_text(park.get("park_name", ""))
        description = preprocess_text(park.get("description", ""))
        features = preprocess_text(park.get("google_results", [{}])[0].get("snippet", ""))
        comparison_text = f"{park_name} {description} {features}"

        # Option 1: Check for exact phrase matches
        if any(phrase in comparison_text for phrase in query_phrases):
            results.append({
                "park_name": park.get("park_name", "Unknown"),
                "description": park.get("description", "No description available."),
                "features": park.get("google_results", [{}])[0].get("snippet", "No features available"),
                "url": park.get("url", "No URL available"),
                "matching_method": "Exact Phrase Match"
            })

        # Option 2: Sentence Embeddings for contextual similarity
        try:
            query_embedding = embedding_model.encode(query, convert_to_tensor=True)
            park_embedding = embedding_model.encode(comparison_text, convert_to_tensor=True)
            embedding_similarity_score = util.pytorch_cos_sim(query_embedding, park_embedding).item()
            if embedding_similarity_score > 0.5:  # Adjust threshold for context relevance
                results.append({
                    "park_name": park.get("park_name", "Unknown"),
                    "description": park.get("description", "No description available."),
                    "features": park.get("google_results", [{}])[0].get("snippet", "No features available"),
                    "url": park.get("url", "No URL available"),
                    "similarity_score": round(embedding_similarity_score, 2),
                    "matching_method": "Embedding Similarity"
                })
        except Exception as e:
            print(f"Error during embedding similarity scoring for {park_name}: {e}")

        # Option 3: Keyword Overlap with expanded context
        park_doc = nlp(comparison_text)
        park_phrases = {chunk.text.lower() for chunk in park_doc.noun_chunks}
        park_keywords = {token.lemma_ for token in park_doc if not token.is_stop}

        if query_phrases & park_phrases or query_keywords & park_keywords:
            overlap_score = len(query_phrases & park_phrases) + len(query_keywords & park_keywords)
            results.append({
                "park_name": park.get("park_name", "Unknown"),
                "description": park.get("description", "No description available."),
                "features": park.get("google_results", [{}])[0].get("snippet", "No features available"),
                "url": park.get("url", "No URL available"),
                "overlap_score": overlap_score,
                "matching_method": "Keyword Overlap"
            })

        # Option 4: Fuzzy Matching for lenient text match
        fuzzy_score = fuzz.partial_ratio(query, comparison_text)
        if fuzzy_score > 80:  # Adjust threshold for fuzzy matching
            results.append({
                "park_name": park.get("park_name", "Unknown"),
                "description": park.get("description", "No description available."),
                "features": park.get("google_results", [{}])[0].get("snippet", "No features available"),
                "url": park.get("url", "No URL available"),
                "fuzzy_score": fuzzy_score,
                "matching_method": "Fuzzy Matching"
            })

    if not results:
        return jsonify({"message": "No parks found matching your query. Please try rephrasing or providing more details."}), 204

    # Sort and filter results for relevance
    results = sorted(results, key=lambda x: x.get("similarity_score", 0), reverse=True)

    return jsonify(results)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
