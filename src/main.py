"""
Command line runner for the Music Recommender + RAG layer.

Usage:
    python -m src.main "chill songs about heartbreak"
    python -m src.main                              # interactive prompt
    python -m src.main --demo starter               # run a hard-coded profile
    python -m src.main --csv data/songs.csv         # use the small fixture catalog
    python -m src.main "..." --no-llm               # skip Gemini explanations
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Tuple

from src.recommender import load_songs, recommend_songs


DEFAULT_CSV = "data/spotify_sample.csv"


# Hard-coded demo profiles, kept for parity with the original starter app.
# Most use genres present in the new spotify_sample.csv (pop, rock, rap, r&b,
# latin, edm). The deliberately-out-of-catalog ones still demonstrate the
# clamp / unknown-genre warnings emitted by recommend_songs.
DEMO_PROFILES: Dict[str, Dict] = {
    "starter": {
        "genre": "pop", "mood": "happy",
        "energy": 0.8, "acousticness": 0.2,
        "valence": 0.7, "danceability": 0.75, "tempo_bpm": 120,
    },
    "high_energy_pop": {
        "genre": "pop", "mood": "happy",
        "energy": 0.90, "acousticness": 0.10,
        "valence": 0.88, "danceability": 0.90, "tempo_bpm": 125,
    },
    "deep_intense_rock": {
        "genre": "rock", "mood": "neutral",
        "energy": 0.92, "acousticness": 0.08,
        "valence": 0.30, "danceability": 0.55, "tempo_bpm": 148,
    },
    "conflicting": {
        "genre": "pop", "mood": "sad",
        "energy": 0.95, "acousticness": 0.05,
        "valence": 0.90, "danceability": 0.90, "tempo_bpm": 130,
    },
    "out_of_bounds": {
        "genre": "rock", "mood": "neutral",
        "energy": 1.5, "acousticness": -0.2,
        "valence": 0.5, "danceability": 0.5, "tempo_bpm": 260,
    },
    "unknown": {
        "genre": "bossa nova", "mood": "wistful",
        "energy": 0.5, "acousticness": 0.5,
        "valence": 0.5, "danceability": 0.5, "tempo_bpm": 100,
    },
}


def _render(
    recommendations: List[Tuple[Dict, float, List[str]]],
    llm_text: str | None = None,
) -> None:
    width = 60
    divider = "=" * width
    thin = "-" * width

    print(f"\n{'Top Recommendations':^{width}}\n")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(divider)
        print(f"  #{rank}  {song['title']}")
        print(f"       {song['artist']}")
        print(f"       Score: {score:.2f}   Genre: {song['genre']}   Mood: {song['mood']}")
        print(thin)
        print("  Why this song?")
        for reason in reasons:
            print(f"    • {reason}")
    print(divider)

    if llm_text:
        print(f"\n{'Gemini Explanation':^{width}}")
        print(divider)
        print(llm_text)
        print(divider)


def _run_demo(name: str, songs: List[Dict], k: int) -> None:
    prefs = DEMO_PROFILES[name]
    print(f"\nRunning demo profile: {name}")
    print(f"Profile: {prefs}")
    recs = recommend_songs(prefs, songs, k=k)
    _render(recs)


def _run_query(query: str, songs: List[Dict], k: int, use_llm: bool) -> None:
    # Imported lazily so demo / --no-llm runs don't require google-genai.
    from src.rag import parse_query, generate_explanation

    valid_genres = sorted({s["genre"] for s in songs if s.get("genre")})
    valid_moods = sorted({s["mood"] for s in songs if s.get("mood")})

    print(f"\nQuery: {query!r}")
    print("Asking Gemini to parse your request…")
    prefs = parse_query(query, valid_genres, valid_moods)
    print(f"Parsed preferences: {prefs}")

    recs = recommend_songs(prefs, songs, k=k)

    llm_text = None
    if use_llm:
        print("Asking Gemini to explain the top picks…")
        llm_text = generate_explanation(query, recs)

    _render(recs, llm_text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Music Recommender + Gemini RAG layer.",
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural-language music request (e.g. 'sad songs about heartbreak').",
    )
    parser.add_argument(
        "--csv",
        default=DEFAULT_CSV,
        help=f"Path to song catalog CSV (default: {DEFAULT_CSV}).",
    )
    parser.add_argument(
        "--k", type=int, default=5,
        help="Number of recommendations to return (default: 5).",
    )
    parser.add_argument(
        "--demo",
        choices=list(DEMO_PROFILES.keys()),
        help="Run a hard-coded demo profile instead of a natural-language query.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip Gemini explanation (parse_query is still used for NL input).",
    )
    args = parser.parse_args()

    songs = load_songs(args.csv)
    print(f"Loaded {len(songs)} songs from {args.csv}")

    if args.demo:
        _run_demo(args.demo, songs, args.k)
        return

    query = args.query
    if not query:
        try:
            query = input("\nWhat do you want to listen to? ").strip()
        except EOFError:
            query = ""

    if not query:
        print(
            "\nNo query provided. Either pass one as an argument:\n"
            "    python -m src.main \"upbeat songs for a road trip\"\n"
            "or run a demo profile:\n"
            f"    python -m src.main --demo {next(iter(DEMO_PROFILES))}"
        )
        sys.exit(1)

    _run_query(query, songs, args.k, use_llm=not args.no_llm)


if __name__ == "__main__":
    main()
