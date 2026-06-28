import requests
import pandas as pd
import time
import os

# ── CONFIG ──────────────────────────────────────────
API_KEY = "6da83a367960cfe397c268fcd7acc947"   # paste your TMDB key
BASE_URL = "https://api.themoviedb.org/3"

# ── FETCH TRENDING CONTENT ───────────────────────────
def fetch_trending(media_type="all", time_window="week", pages=5):
    """
    media_type: 'all', 'movie', 'tv'
    time_window: 'day' or 'week'
    """
    results = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}/trending/{media_type}/{time_window}"
        params = {"api_key": API_KEY, "page": page}
        response = requests.get(url, params=params)
        data = response.json()

        if "results" in data:
            results.extend(data["results"])
            print(f"Fetched page {page} — {len(data['results'])} items")

        time.sleep(0.3)  # be polite to the API

    return pd.DataFrame(results)


# ── FETCH BY GENRE ────────────────────────────────────
def fetch_genre_list(media_type="movie"):
    url = f"{BASE_URL}/genre/{media_type}/list"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    genres = response.json().get("genres", [])
    return pd.DataFrame(genres)


# ── FETCH POPULAR MOVIES ──────────────────────────────
def fetch_popular(media_type="movie", pages=5):
    results = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}/{media_type}/popular"
        params = {"api_key": API_KEY, "page": page}
        response = requests.get(url, params=params)
        data = response.json()

        if "results" in data:
            results.extend(data["results"])
            print(f"Fetched page {page} — {len(data['results'])} items")

        time.sleep(0.3)

    return pd.DataFrame(results)


# ── RUN & SAVE ────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("\n📥 Fetching trending content...")
    trending_df = fetch_trending(media_type="all", time_window="week", pages=5)
    trending_df.to_csv("data/tmdb_trending.csv", index=False)
    print(f"✅ Saved {len(trending_df)} trending items")

    print("\n📥 Fetching popular movies...")
    movies_df = fetch_popular(media_type="movie", pages=10)
    movies_df.to_csv("data/tmdb_movies.csv", index=False)
    print(f"✅ Saved {len(movies_df)} movies")

    print("\n📥 Fetching popular TV shows...")
    tv_df = fetch_popular(media_type="tv", pages=10)
    tv_df.to_csv("data/tmdb_tv.csv", index=False)
    print(f"✅ Saved {len(tv_df)} TV shows")

    print("\n📥 Fetching genre lists...")
    movie_genres = fetch_genre_list("movie")
    tv_genres = fetch_genre_list("tv")
    movie_genres.to_csv("data/movie_genres.csv", index=False)
    tv_genres.to_csv("data/tv_genres.csv", index=False)
    print("✅ Saved genre lists")

    print("\n🎉 All data collected successfully!")