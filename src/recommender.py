import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, replace as _dc_replace

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

# Unit-range features that must stay within [0.0, 1.0].
_UNIT_FEATURES = ("energy", "acousticness", "valence", "danceability")


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


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
        # Clamp out-of-bounds numeric fields and warn.
        profile_ranges = {
            "target_energy":       (0.0, 1.0),
            "target_acousticness": (0.0, 1.0),
            "target_valence":      (0.0, 1.0),
            "target_danceability": (0.0, 1.0),
            "target_tempo":        (0.0, _MAX_TEMPO_BPM),
        }
        changes = {}
        for field, (lo, hi) in profile_ranges.items():
            val = getattr(user, field)
            if not (lo <= val <= hi):
                clamped = _clamp(val, lo, hi)
                print(f"Warning: '{field}' value {val} out of [{lo}, {hi:.0f}]; clamping to {clamped:.2f}.")
                changes[field] = clamped
        if changes:
            user = _dc_replace(user, **changes)

        # Warn if genre or mood won't match any song in the catalog.
        catalog_genres = {s.genre for s in self.songs}
        catalog_moods  = {s.mood  for s in self.songs}
        if user.favorite_genre not in catalog_genres:
            print(f"Warning: genre '{user.favorite_genre}' not found in catalog; genre bonus will never apply.")
        if user.favorite_mood not in catalog_moods:
            print(f"Warning: mood '{user.favorite_mood}' not found in catalog; mood bonus will never apply.")

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

    user_prefs keys used: "genre", "mood", "energy", "acousticness", "valence",
        "danceability", "tempo_bpm", "themes" (list of lowercase lyric keywords).
    Returns a list of (song_dict, score, reasons) tuples sorted by score descending,
    where reasons is a list of individual explanation strings.
    """
    # Clamp out-of-bounds numeric prefs and warn.
    prefs = dict(user_prefs)
    for feat in _UNIT_FEATURES:
        if feat in prefs and not (0.0 <= prefs[feat] <= 1.0):
            clamped = _clamp(prefs[feat], 0.0, 1.0)
            print(f"Warning: '{feat}' value {prefs[feat]} out of [0, 1]; clamping to {clamped:.2f}.")
            prefs[feat] = clamped
    if "tempo_bpm" in prefs and not (0.0 <= prefs["tempo_bpm"] <= _MAX_TEMPO_BPM):
        clamped = _clamp(prefs["tempo_bpm"], 0.0, _MAX_TEMPO_BPM)
        print(f"Warning: 'tempo_bpm' value {prefs['tempo_bpm']} out of [0, {_MAX_TEMPO_BPM:.0f}]; clamping to {clamped:.0f}.")
        prefs["tempo_bpm"] = clamped

    # Warn if genre or mood won't match any song in the catalog.
    catalog_genres = {s.get("genre") for s in songs}
    catalog_moods  = {s.get("mood")  for s in songs}
    if prefs.get("genre") and prefs["genre"] not in catalog_genres:
        print(f"Warning: genre '{prefs['genre']}' not found in catalog; genre bonus will never apply.")
    if prefs.get("mood") and prefs["mood"] not in catalog_moods:
        print(f"Warning: mood '{prefs['mood']}' not found in catalog; mood bonus will never apply.")

    raw_themes = prefs.get("themes") or []
    themes_lc = [t.lower().strip() for t in raw_themes if isinstance(t, str) and t.strip()]

    def matched_themes(song: Dict) -> List[str]:
        if not themes_lc:
            return []
        lyrics = (song.get("lyrics") or "").lower()
        if not lyrics:
            return []
        return [t for t in themes_lc if t in lyrics]

    def score(song: Dict) -> float:
        s = 0.0
        if song.get("genre") == prefs.get("genre"):
            s += 2.0
        if song.get("mood") == prefs.get("mood"):
            s += 1.5
        if "energy" in prefs:
            s += 1.0 - abs(song["energy"] - prefs["energy"])
        if "acousticness" in prefs:
            s += 1.0 - abs(song["acousticness"] - prefs["acousticness"])
        if "valence" in prefs:
            s += 1.0 - abs(song["valence"] - prefs["valence"])
        if "danceability" in prefs:
            s += 1.0 - abs(song["danceability"] - prefs["danceability"])
        if "tempo_bpm" in prefs:
            s += 1.0 - abs(song["tempo_bpm"] - prefs["tempo_bpm"]) / _MAX_TEMPO_BPM
        if themes_lc:
            s += 2.0 * (len(matched_themes(song)) / len(themes_lc))
        return s

    def explain(song: Dict) -> List[str]:
        reasons = []
        if song.get("genre") == prefs.get("genre"):
            reasons.append(f"matches your favorite genre ({song['genre']})")
        if song.get("mood") == prefs.get("mood"):
            reasons.append(f"matches your preferred mood ({song['mood']})")
        if "energy" in prefs and abs(song["energy"] - prefs["energy"]) <= 0.15:
            reasons.append(f"energy is close to your target ({song['energy']:.2f})")
        if "acousticness" in prefs and abs(song["acousticness"] - prefs["acousticness"]) <= 0.15:
            reasons.append(f"acousticness fits your preference ({song['acousticness']:.2f})")
        if "valence" in prefs and abs(song["valence"] - prefs["valence"]) <= 0.15:
            reasons.append(f"valence is near your target ({song['valence']:.2f})")
        if "danceability" in prefs and abs(song["danceability"] - prefs["danceability"]) <= 0.15:
            reasons.append(f"danceability matches your preference ({song['danceability']:.2f})")
        if "tempo_bpm" in prefs and abs(song["tempo_bpm"] - prefs["tempo_bpm"]) <= 15:
            reasons.append(f"tempo is close to your target ({song['tempo_bpm']:.0f} BPM)")
        matched = matched_themes(song)
        if matched:
            quoted = ", ".join(f"'{t}'" for t in matched)
            reasons.append(f"lyrics mention {quoted}")
        if not reasons:
            reasons.append("overall profile is a reasonable match")
        return reasons

    ranked = sorted(songs, key=score, reverse=True)[:k]
    return [(song, score(song), explain(song)) for song in ranked]
