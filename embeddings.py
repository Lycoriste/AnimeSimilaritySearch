import torch
from torch import Tensor
import fireducks.pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

device = (
    "cuda" if torch.cuda.is_available() else
    "mps" if torch.backends.mps.is_available() else
    "cpu"
)

# Sample DataFrame with anime titles and reviews
data = {
    'title': ['Naruto', 'One Piece', 'Attack on Titan'],
    'review': [
        'An amazing story about ninjas full of action and heart.',
        'A long-running saga about pirates, adventure, and camaraderie on the high seas.',
        'A dark and intense series about survival in a world overrun by titans.'
    ]
}
df = pd.DataFrame(data)

# Load the model from Hugging Face Hub
model = SentenceTransformer("Linq-AI-Research/Linq-Embed-Mistral", trust_remote_code=True)

# Embed the reviews; we can compute embeddings for all reviews at once
review_texts = df['review'].tolist()
review_embeddings = model.encode(review_texts)

# (Optional) Save the embeddings in the DataFrame if you need to use them later
df['embedding'] = list(review_embeddings)

# Define a query review (this can be a user's input)
query_review = "A thrilling tale of ninjas and intense battles."
query_embedding = model.encode(query_review)

# Compute cosine similarity between the query embedding and each review embedding
similarity_scores = cosine_similarity([query_embedding], review_embeddings)[0]

# Add the similarity scores to the DataFrame
df['similarity'] = similarity_scores

# Sort the DataFrame by similarity in descending order (higher score = more similar)
df_sorted = df.sort_values(by='similarity', ascending=False)

print("Anime reviews sorted by similarity to the query:")
print(df_sorted[['title', 'review', 'similarity']])