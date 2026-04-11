"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile — covers all features used by recommend_songs
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "acousticness": 0.2,
        "valence": 0.7,
        "danceability": 0.75,
        "tempo_bpm": 120,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 52
    divider  = "=" * width
    thin_div = "-" * width

    print(f"\n{'Top Recommendations':^{width}}\n")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(divider)
        print(f"  #{rank}  {song['title']}")
        print(f"       {song['artist']}")
        print(f"       Score: {score:.2f}")
        print(thin_div)
        print("  Why this song?")
        for reason in reasons:
            print(f"    • {reason}")
    print(divider)


if __name__ == "__main__":
    main()
