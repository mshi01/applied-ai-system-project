import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_acousticness: float
    target_tempo: float
    target_valence: float
    target_danceability: float


# Maximum BPM used to normalize tempo difference into a 0-1 range.
_MAX_TEMPO_BPM = 200.0


def _score_song(user: UserProfile, song: Song) -> float:
    """
    Scores a song against a UserProfile.

    Scoring breakdown (max ≈ 8.5):
      - Genre match:       +2.0
      - Mood match:        +1.5
      - Energy proximity:  up to +1.0  (1 - |target - song|)
      - Acousticness:      up to +1.0
      - Valence:           up to +1.0
      - Danceability:      up to +1.0
      - Tempo:             up to +1.0  (difference normalized by _MAX_TEMPO_BPM)
    """
    score = 0.0

    if song.genre == user.favorite_genre:
        score += 2.0
    if song.mood == user.favorite_mood:
        score += 1.5

    score += 1.0 - abs(song.energy - user.target_energy)
    score += 1.0 - abs(song.acousticness - user.target_acousticness)
    score += 1.0 - abs(song.valence - user.target_valence)
    score += 1.0 - abs(song.danceability - user.target_danceability)
    score += 1.0 - abs(song.tempo_bpm - user.target_tempo) / _MAX_TEMPO_BPM

    return score


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: _score_song(user, s), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"matches your favorite genre ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"matches your preferred mood ({song.mood})")
        if abs(song.energy - user.target_energy) <= 0.15:
            reasons.append(f"energy is close to your target ({song.energy:.2f})")
        if abs(song.acousticness - user.target_acousticness) <= 0.15:
            reasons.append(f"acousticness fits your preference ({song.acousticness:.2f})")
        if abs(song.valence - user.target_valence) <= 0.15:
            reasons.append(f"valence is near your target ({song.valence:.2f})")
        if abs(song.danceability - user.target_danceability) <= 0.15:
            reasons.append(f"danceability matches your preference ({song.danceability:.2f})")
        if abs(song.tempo_bpm - user.target_tempo) <= 15:
            reasons.append(f"tempo is close to your target ({song.tempo_bpm:.0f} BPM)")

        if not reasons:
            reasons.append("overall profile is a reasonable match")

        return "Recommended because it " + ", ".join(reasons) + "."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    user_prefs keys used: "genre", "mood", "energy"
    Returns a list of (song_dict, score, reasons) tuples sorted by score descending,
    where reasons is a list of individual explanation strings.
    """
    def score(song: Dict) -> float:
        s = 0.0
        if song.get("genre") == user_prefs.get("genre"):
            s += 2.0
        if song.get("mood") == user_prefs.get("mood"):
            s += 2.0
        if "energy" in user_prefs:
            s += 1.0 - abs(song["energy"] - user_prefs["energy"])
        if "acousticness" in user_prefs:
            s += 1.0 - abs(song["acousticness"] - user_prefs["acousticness"])
        if "valence" in user_prefs:
            s += 1.0 - abs(song["valence"] - user_prefs["valence"])
        if "danceability" in user_prefs:
            s += 1.0 - abs(song["danceability"] - user_prefs["danceability"])
        if "tempo_bpm" in user_prefs:
            s += 1.0 - abs(song["tempo_bpm"] - user_prefs["tempo_bpm"]) / _MAX_TEMPO_BPM
        return s

    def explain(song: Dict) -> List[str]:
        reasons = []
        if song.get("genre") == user_prefs.get("genre"):
            reasons.append(f"matches your favorite genre ({song['genre']})")
        if song.get("mood") == user_prefs.get("mood"):
            reasons.append(f"matches your preferred mood ({song['mood']})")
        if "energy" in user_prefs and abs(song["energy"] - user_prefs["energy"]) <= 0.15:
            reasons.append(f"energy is close to your target ({song['energy']:.2f})")
        if "acousticness" in user_prefs and abs(song["acousticness"] - user_prefs["acousticness"]) <= 0.15:
            reasons.append(f"acousticness fits your preference ({song['acousticness']:.2f})")
        if "valence" in user_prefs and abs(song["valence"] - user_prefs["valence"]) <= 0.15:
            reasons.append(f"valence is near your target ({song['valence']:.2f})")
        if "danceability" in user_prefs and abs(song["danceability"] - user_prefs["danceability"]) <= 0.15:
            reasons.append(f"danceability matches your preference ({song['danceability']:.2f})")
        if "tempo_bpm" in user_prefs and abs(song["tempo_bpm"] - user_prefs["tempo_bpm"]) <= 15:
            reasons.append(f"tempo is close to your target ({song['tempo_bpm']:.0f} BPM)")
        if not reasons:
            reasons.append("overall profile is a reasonable match")
        return reasons

    ranked = sorted(songs, key=score, reverse=True)[:k]
    return [(song, score(song), explain(song)) for song in ranked]
