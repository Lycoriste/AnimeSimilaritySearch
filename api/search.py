import json
import pandas as pd
from sentence_transformers import SentenceTransformer

# Sample anime data
data = {
    'anime_title': [
        'Naruto', 'One Piece', 'Attack on Titan', 'Bleach',
        'My Hero Academia', 'Fullmetal Alchemist', 'Dragon Ball',
        'Death Note', 'Sword Art Online', 'One Punch Man'
    ],
    'review': [
        "Amazing action sequences and deep character development.",
        "A fun, adventurous journey with strong friendship themes.",
        "A dark and intense narrative with impressive visuals.",
        "Unique world-building and memorable character arcs.",
        "Inspiring heroes with intense battles and emotional growth.",
        "A compelling story of sacrifice and adventure in a fantasy world.",
        "Iconic battles and epic power-ups.",
        "A psychological thriller with a clever cat-and-mouse game.",
        "A mix of virtual reality adventures and high-stakes battles.",
        "Hilariously overpowered hero with a satirical twist."
    ]
}
df = pd.DataFrame(data)

# Load the model once at module level for faster cold starts
model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')
review_texts = df['review'].tolist()
review_embeddings = model.encode(review_texts, convert_to_tensor=True, normalize_embeddings=True)

def handler(request):
    if request.method == "POST":
        body = request.get_json()
        query = body.get("query", "")
        
        # Check if the query matches an existing anime title
        if query in df['anime_title'].values:
            idx = df.index[df['anime_title'] == query][0]
            query_review = df.loc[idx, 'review']
        else:
            query_review = query
        
        # Embed the query review
        query_embedding = model.encode([query_review], convert_to_tensor=True, normalize_embeddings=True)
        
        # Compute cosine similarity (using dot product on normalized vectors)
        scores = (query_embedding @ review_embeddings.T) * 100
        scores_list = scores.tolist()[0]
        
        # Build a list of tuples (anime_title, score)
        similarity_results = [(df.loc[i, 'anime_title'], score) for i, score in enumerate(scores_list)]
        
        # If the query is an anime title, exclude it from the results
        if query in df['anime_title'].values:
            similarity_results = [item for item in similarity_results if item[0] != query]
        
        # Sort by similarity score (highest first) and take the top 10
        similarity_results.sort(key=lambda x: x[1], reverse=True)
        top_results = similarity_results[:10]
        
        return {
            "statusCode": 200,
            "body": json.dumps(top_results)
        }
    else:
        return {
            "statusCode": 405,
            "body": "Method not allowed"
        }
