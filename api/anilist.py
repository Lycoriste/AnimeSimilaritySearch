import requests, time, csv

API_URL = "https://graphql.anilist.co"
REVIEW_QUERY = """
    query ($animeId: Int, $page: Int, $perPage: Int) {
    Media(id: $animeId) {
        reviews(page: $page, perPage: $perPage, sort: RATING_DESC) {
        pageInfo { hasNextPage }
        nodes {
            id summary body rating user { name }
        }
        }
    }
    }
"""

ANIME_QUERY = """
query ($search: String) {
    Media(search: $search, type: ANIME) {
    id
    title {
      romaji
      english
      native
    }
    description(asHtml: false)
    episodes
    status
    genres
    averageScore
  }
}
"""

def fetch_reviews(anime_id: int, per_page:int = 25):
    page = 1
    all_reviews = []
    while True:
        resp = requests.post(API_URL, json={
            "query": REVIEW_QUERY,
            "variables": {"animeId": anime_id, "page": page, "perPage": per_page}
        })
        data = resp.json()["data"]["Media"]["reviews"]
        all_reviews.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            break
        page += 1
        time.sleep(1)
    return all_reviews

def fetch_anime(anime: str):
    resp = requests.post(API_URL, json={
        "query": ANIME_QUERY,
        
    })
    

# Example: fetch and write to CSV
reviews = fetch_reviews(1, per_page=50)
with open("reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
    writer.writeheader()
    writer.writerows(reviews)