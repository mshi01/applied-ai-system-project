"""
Sample the 18k Spotify+lyrics dataset down to a small, balanced catalog
that matches the schema used by src/recommender.py.

Sampling strategy:
  1. Keep only English-language rows that have non-null lyrics.
  2. Within each playlist_genre, take the top-N rows by track_popularity.
  3. Map columns to the recommender schema and derive a coarse `mood` from valence.
  4. Truncate lyrics to LYRICS_MAX_CHARS so downstream LLM prompts stay small.

Run from the repo root:
    python scripts/ingest_kaggle.py
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = REPO_ROOT / "data" / "spotify_18k_songs.csv"
OUTPUT_CSV = REPO_ROOT / "data" / "spotify_sample.csv"

PER_GENRE = 167          # 167 * 6 genres ≈ 1000 rows
LYRICS_MAX_CHARS = 500
TEMPO_MAX_BPM = 200.0    # matches _MAX_TEMPO_BPM in src/recommender.py


def derive_mood(valence: float) -> str:
    if valence >= 0.6:
        return "happy"
    if valence <= 0.4:
        return "sad"
    return "neutral"


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Input not found: {INPUT_CSV}\n"
            "Place the Kaggle 'Audio features and lyrics of Spotify songs' CSV here."
        )

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df):,} rows from {INPUT_CSV.name}")

    df = df[df["language"] == "en"]
    df = df.dropna(subset=["lyrics", "track_name", "track_artist", "playlist_genre"])
    print(f"After English + non-null filter: {len(df):,} rows")

    df = df.sort_values("track_popularity", ascending=False)
    # The source lists each track once per playlist it appears on, and Spotify
    # often has multiple track_ids for the same song (single vs. album version,
    # remasters, etc). Dedupe on (track_name, track_artist) so the same song
    # cannot occupy multiple recommendation slots.
    df = df.drop_duplicates(subset=["track_name", "track_artist"], keep="first")
    print(f"After dedup by (track_name, track_artist): {len(df):,} rows")
    sampled = df.groupby("playlist_genre", group_keys=False).head(PER_GENRE)
    print(f"After top-{PER_GENRE}-by-popularity per genre: {len(sampled):,} rows")
    print("Per-genre counts:")
    print(sampled["playlist_genre"].value_counts().to_string())

    out = pd.DataFrame({
        "id": range(1, len(sampled) + 1),
        "title": sampled["track_name"].values,
        "artist": sampled["track_artist"].values,
        "genre": sampled["playlist_genre"].values,
        "mood": sampled["valence"].apply(derive_mood).values,
        "energy": sampled["energy"].values,
        "tempo_bpm": sampled["tempo"].clip(0, TEMPO_MAX_BPM).round(2).values,
        "valence": sampled["valence"].round(3).values,
        "danceability": sampled["danceability"].round(3).values,
        "acousticness": sampled["acousticness"].round(3).values,
        "popularity": sampled["track_popularity"].astype(int).values,
        "lyrics": sampled["lyrics"].astype(str).str.replace(r"\s+", " ", regex=True).str[:LYRICS_MAX_CHARS].values,
    })

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(out):,} rows to {OUTPUT_CSV}")
    print(f"Mood distribution: {out['mood'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
