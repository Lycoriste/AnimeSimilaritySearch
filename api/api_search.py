import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import numpy as np
import fireducks.pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from anilist import fetch_anime_id, fetch_anime_name, fetch_anime_media, fetch_top_review, prod_fetch


def compare_embeddings(anime_name: str, 
                       df: pd.DataFrame, 
                       df_desc: pd.DataFrame, 
                       model: SentenceTransformer, 
                       review_embeddings,
                       desc_embeddings, 
                       top_g: int = 15):
    anime_id = fetch_anime_id(anime_name)
    if anime_id is None:
        return

    if anime_id not in df['anime_id'].values:
        query_review, query_desc = prod_fetch(anime_id)
    else:
        # Get the index and review corresponding to the anime_id in the DataFrame
        selected_index = df.index[df['anime_id'] == anime_id][0]
        query_review = df.loc[selected_index, 'top_review']
        selected_index_desc = df_desc.index[df_desc['anime_id'] == anime_id][0]
        query_desc = df_desc.loc[selected_index_desc, 'description']
    
    # Encode the review for the selected anime
    query_embedding = model.encode([query_review], convert_to_tensor=True, normalize_embeddings=True)
    query_desc_embedding = model.encode([query_desc], convert_to_tensor=True, normalize_embeddings=True)

    # Compute cosine similarity scores between the selected review and all other reviews
    scores = (query_embedding @ review_embeddings.T) * 100  # cosine similarity scaled by 100
    scores_list = scores.tolist()[0]

    desc_scores = (query_desc_embedding @ desc_embeddings.T) * 100
    desc_scores_list = desc_scores.tolist()[0]
    
    # Prepare similarity results, excluding the selected anime itself
    similarity_results = []
    for idx, score in enumerate(scores_list):
        if idx != selected_index:
            similarity_results.append((df.loc[idx, 'anime_id'], score))
    
    desc_similarity_results = []
    for idx, score in enumerate(desc_scores_list):
        if idx != selected_index_desc:
            desc_similarity_results.append((df_desc.loc[idx, 'anime_id'], score))
    
    # # Sort the results by similarity score in descending order
    # similarity_results.sort(key=lambda x: x[1], reverse=True)

    review_df = pd.DataFrame(similarity_results, columns=['anime_id', 'review_score'])
    desc_df = pd.DataFrame(desc_similarity_results, columns=['anime_id', 'desc_score'])

    # Merge the dataframes
    combined_df = pd.merge(review_df, desc_df, on='anime_id', how='outer').fillna(0)

    REVIEW_WEIGHT = 0.3
    DESC_WEIGHT = 0.7

    # Calculate weighted score
    combined_df['combined_score'] = (
        combined_df['review_score'] * REVIEW_WEIGHT +
        combined_df['desc_score'] * DESC_WEIGHT
    )

    # Sort and filter out self-comparison
    final_df = combined_df[combined_df['anime_id'] != anime_id] \
        .sort_values('combined_score', ascending=False) \
        .reset_index(drop=True)

    # Convert to list of tuples if needed
    combined_results = list(final_df[['anime_id', 'combined_score']].itertuples(index=False, name=None))
    
    # Get the top #g most similar anime and use the API to get their names
    top = combined_results[:top_g]
    # print(f"\nTop {top_g} similar anime to '{anime_name}' (Anime id {anime_id}):")
    out = []
    for other_anime_id, score in top:
        print(other_anime_id)
        anime_name, cover_image, site_url = fetch_anime_media(other_anime_id)

        out.append({
            "anime_id": int(other_anime_id),
            "anime_name": anime_name,
            "similarity": float(score),
            "image_url": cover_image,
            "site_url": site_url
        })

    return out