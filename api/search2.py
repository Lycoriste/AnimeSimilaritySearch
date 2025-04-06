import os
import requests
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from anilist import fetch_anime_id, fetch_anime_name


# Load the multilingual model
model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')

# def get_anime_id(anime_name):
#     """
#     Query the AniList API to find the anime ID for the given anime name.
#     """
#     url = "https://graphql.anilist.co"
#     query = '''
#     query ($search: String) {
#       Media(search: $search, type: ANIME) {
#         id
#       }
#     }
#     '''
#     variables = {'search': anime_name}
#     response = requests.post(url, json={'query': query, 'variables': variables})
#     if response.status_code == 200:
#         data = response.json()
#         return data.get('data', {}).get('Media', {}).get('id', None)
#     else:
#         print("Error querying AniList API for ID")
#         return None

# def get_anime_name(anime_id):
#     """
#     Query the AniList API to get the anime name given an anime id.
#     Convert the anime_id to a standard Python int to avoid JSON serialization issues.
#     """
#     url = "https://graphql.anilist.co"
#     query = '''
#     query ($id: Int) {
#       Media(id: $id, type: ANIME) {
#         title {
#           romaji
#           english
#           native
#         }
#       }
#     }
#     '''
#     variables = {'id': int(anime_id)}  # Convert to Python int to ensure JSON serialization
#     response = requests.post(url, json={'query': query, 'variables': variables})
#     if response.status_code == 200:
#         data = response.json()
#         title_info = data.get('data', {}).get('Media', {}).get('title', {})
#         # Prefer English title if available, else romaji, then native
#         anime_name = title_info.get('english') or title_info.get('romaji') or title_info.get('native')
#         return anime_name
#     else:
#         print("Error querying AniList API for anime name")
#         return None



# Load the DataFrame which has columns: anime_id and top_review
df = pd.read_csv('./data/data.csv')

# Pre-compute or load review embeddings
embedding_file = './data/review_embeddings.pt'
review_texts = df['top_review'].tolist()

if os.path.exists(embedding_file):
    print("Loading pre-computed review embeddings...")
    review_embeddings = torch.load(embedding_file)
else:
    print("Computing review embeddings...")
    review_embeddings = model.encode(review_texts, convert_to_tensor=True, normalize_embeddings=True)
    torch.save(review_embeddings, embedding_file)

# Prompt the user for an anime name
user_anime = input("Enter an anime name: ")

# Use AniList API to get the anime id for the given anime name
anime_id = fetch_anime_id(user_anime)
if anime_id is None:
    print(f"Anime '{user_anime}' not found on AniList.")
else:
    # Check if the anime id exists in the DataFrame
    if anime_id not in df['anime_id'].values:
        print(f"Anime '{user_anime}' with id {anime_id} not found in the dataframe.")
    else:
        # Get the index and review corresponding to the anime_id in the DataFrame
        selected_index = df.index[df['anime_id'] == anime_id][0]
        query_review = df.loc[selected_index, 'top_review']
        
        # Encode the review for the selected anime
        query_embedding = model.encode([query_review], convert_to_tensor=True, normalize_embeddings=True)
        
        # Compute cosine similarity scores between the selected review and all other reviews
        scores = (query_embedding @ review_embeddings.T) * 100  # cosine similarity scaled by 100
        scores_list = scores.tolist()[0]
        
        # Prepare similarity results, excluding the selected anime itself
        similarity_results = []
        for idx, score in enumerate(scores_list):
            if idx != selected_index:
                similarity_results.append((df.loc[idx, 'anime_id'], score))
        
        # Sort the results by similarity score in descending order
        similarity_results.sort(key=lambda x: x[1], reverse=True)
        
        # Get the top 20 most similar anime and use the API to get their names
        top_20 = similarity_results[:20]
        print(f"\nTop 20 similar anime to '{user_anime}' (Anime id {anime_id}):")
        for other_anime_id, score in top_20:
            anime_name_result = fetch_anime_name(other_anime_id)
            if anime_name_result:
                print(f"{anime_name_result} (ID: {other_anime_id}) - Similarity: {score:.2f}")
            else:
                print(f"Anime ID {other_anime_id} - Similarity: {score:.2f} (Name not found)")