import os
import fireducks.pandas as pd
import torch
from flask import Flask, jsonify, request
from flask_cors import CORS
from anilist import fetch_anime_id, fetch_anime_name
from sentence_transformers import SentenceTransformer
from api_search import compare_embeddings

app = Flask(__name__)
cors = CORS(app, origins="*")

# Keep the data and model loaded by defining it here
df = pd.read_csv('data/reviews_data.csv')
desc_df = pd.read_csv('data/desc_data.csv')
model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')

# Pre-compute or load review embeddings
embedding_file = 'data/review_embeddings.pt'
review_texts = df['top_review'].tolist()

desc_embedding_file = 'data/desc_embeddings.pt'
desc_txts = desc_df['description'].tolist()

if os.path.exists(embedding_file):
    print("Loading pre-computed review embeddings...")
    review_embeddings = torch.load(embedding_file)
else:
    print("Computing review embeddings...")
    review_embeddings = model.encode(review_texts, convert_to_tensor=True, normalize_embeddings=True)
    torch.save(review_embeddings, embedding_file)

if os.path.exists(desc_embedding_file):
    print("Loading pre-computed description embeddings...")
    desc_embeddings = torch.load(desc_embedding_file)
else:
    print("Computing description embeddings...")
    desc_embeddings = model.encode(desc_txts, convert_to_tensor=True, normalize_embeddings=True)
    torch.save(desc_embeddings, desc_embedding_file)

@app.route("/api/search", methods=["GET"])
def search():
    anime_name = request.args.get("anime", "").strip()
    if not anime_name:
        return jsonify({"error": "Missing anime query parameter"}), 400
    results = compare_embeddings(anime_name, df, desc_df, model, review_embeddings, desc_embeddings)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=8080)