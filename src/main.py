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
    starter_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "acousticness": 0.2,
        "valence": 0.7,
        "danceability": 0.75,
        "tempo_bpm": 120,
    }
   
    high_energy_pop = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90,
        "acousticness": 0.10,
        "valence": 0.88,
        "danceability": 0.90,
        "tempo_bpm": 125,
    }

    chill_lofi = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "acousticness": 0.80,
        "valence": 0.55,
        "danceability": 0.50,
        "tempo_bpm": 78,
    }

    deep_intense_rock = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "acousticness": 0.08,
        "valence": 0.30,
        "danceability": 0.55,
        "tempo_bpm": 148,
    }

    # --- Adversarial / edge-case profiles ---

    # #1 Conflicting energy + mood: high-energy numeric features vs. "sad" mood bonus
    conflicting_prefs = {
        "genre": "pop", "mood": "sad",
        "energy": 0.95, "acousticness": 0.05,
        "valence": 0.90, "danceability": 0.90, "tempo_bpm": 130,
    }

    # #2 Out-of-bounds values: energy > 1.0 and tempo > _MAX_TEMPO_BPM can produce negative score components
    out_of_bounds_prefs = {
        "genre": "rock", "mood": "intense",
        "energy": 1.5, "acousticness": -0.2,
        "valence": 0.5, "danceability": 0.5, "tempo_bpm": 260,
    }

    # #3 Unknown genre + mood: neither bonus ever fires; ranking is purely numeric
    unknown_prefs = {
        "genre": "bossa nova", "mood": "wistful",
        "energy": 0.5, "acousticness": 0.5,
        "valence": 0.5, "danceability": 0.5, "tempo_bpm": 100,
    }

    user_prefs = starter_prefs # change to chill_lofi or deep_intense_rock or conflicting_prefs or out_of_bounds_prefs or unknown_prefs

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
