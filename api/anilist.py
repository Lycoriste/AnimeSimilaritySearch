import requests, csv, time, random
from helper.html_cleaning import clean_html
from helper.rate_bypass import exponential_backoff_fetch

API_URL = "https://graphql.anilist.co"

ANIME_ID_QUERY = """
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

REVIEW_QUERY = """
    query ($animeId: Int, $page: Int, $perPage: Int) {
        Media(id: $animeId) {
            reviews(page: $page, perPage: $perPage, sort: RATING_DESC) {
                pageInfo { hasNextPage }
                nodes { id summary body rating user { name } }
            }
        }
    }
"""

ANIME_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, sort: [POPULARITY_DESC, ID_DESC]) {
      id
      title { romaji }
    }
  }
}
"""

# Returns anime_id from anime_name
def fetch_anime_id(anime_name: str):
    resp = exponential_backoff_fetch(API_URL, json={
        "query": ANIME_ID_QUERY,
        "variables": {"search": anime_name}
    })
    resp.raise_for_status()
    payload = resp.json()
    anime = payload.get("data", {}).get("Media")

    return anime["id"]

# Returns the best review from the anime
def fetch_top_review(anime, page:int = 1, per_page:int = 1, clean: bool = True):
    if (type(anime) == str):
        anime_id = fetch_anime_id(anime)
    elif (type(anime) == int):
        anime_id = anime
    else:
        raise Exception("Bombaclat, this is not valid.")
    
    resp = exponential_backoff_fetch(API_URL, {
        "query": REVIEW_QUERY,
        "variables": {"animeId": anime_id, "page": page, "perPage": per_page}
    })
    resp.raise_for_status()
    payload = resp.json()
    media = payload.get("data", {}).get("Media")
    if not media:
        print(f"No media found for anime ID: {anime_id}")
        return None

    reviews = media.get("reviews", {})
    nodes = reviews.get("nodes", [])

    if not nodes:   # If there are no reviews available
        return None

    top_review = nodes[0]["body"]

    if clean:
        top_review = clean_html(top_review)

    return top_review

# Get animes from Anilist pages
def get_anime(page:int = 1, per_page: int = 50):
    resp = exponential_backoff_fetch(API_URL, {
            "query": ANIME_QUERY,
            "variables": { "page": page, "perPage": per_page }
        }
    )
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data", {}).get("Page", {}).get("media", [])

    return [anime["id"] for anime in data] 

def collect_anime_review(filename: str, num_anime: int = 500):
    current = 0
    page = 1
    per_page = 50

    with open(f"data/{filename}", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["anime_id", "top_review"])
        while current < num_anime:
            try:
                anime_ids = get_anime(page, per_page)
                if not (anime_ids):
                    break

                for anime_id in anime_ids:
                    if current >= num_anime:
                        break
                    top_review = fetch_top_review(anime_id)
                    if top_review:
                        writer.writerow([anime_id, top_review])
                        current += 1
                        print(f"Page: {page}, Anime_ID: {anime_id}")
                    else:
                        print(f"Skipped anime {anime_id} (no reviews)")

                page += 1
                time.sleep(random.uniform(4, 8))
            except Exception as e:
                print(f"Error on page {page}: {e}")
                time.sleep(10)

collect_anime_review("data.csv")