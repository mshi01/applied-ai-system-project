from src.recommender import Song, UserProfile, Recommender, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_acousticness=0.2,
        target_tempo=120,
        target_valence=0.9,
        target_danceability=0.8,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_acousticness=0.2,
        target_tempo=120,
        target_valence=0.9,
        target_danceability=0.8,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# Tests for the functional `recommend_songs` path used by src/main.py
# ---------------------------------------------------------------------------

def make_dict_catalog():
    return [
        {
            "id": 1, "title": "Heartbreak Hotel", "artist": "A",
            "genre": "pop", "mood": "sad",
            "energy": 0.4, "acousticness": 0.5, "valence": 0.2,
            "danceability": 0.5, "tempo_bpm": 100,
            "lyrics": "since my baby left me i found a new place to dwell heartbreak hotel",
        },
        {
            "id": 2, "title": "Sunshine", "artist": "B",
            "genre": "pop", "mood": "happy",
            "energy": 0.9, "acousticness": 0.1, "valence": 0.95,
            "danceability": 0.9, "tempo_bpm": 130,
            "lyrics": "walking on sunshine feeling great today",
        },
        {
            "id": 3, "title": "Heart of Stone", "artist": "C",
            "genre": "rock", "mood": "neutral",
            "energy": 0.7, "acousticness": 0.2, "valence": 0.5,
            "danceability": 0.5, "tempo_bpm": 120,
            "lyrics": "she walked away with my heartbreak in her hands",
        },
        {
            "id": 4, "title": "Workout", "artist": "D",
            "genre": "edm", "mood": "happy",
            "energy": 0.95, "acousticness": 0.05, "valence": 0.8,
            "danceability": 0.95, "tempo_bpm": 140,
            "lyrics": "lets go to the gym and lift heavy",
        },
    ]


def test_recommend_songs_returns_sorted_top_k():
    songs = make_dict_catalog()
    prefs = {"genre": "pop", "mood": "happy"}
    results = recommend_songs(prefs, songs, k=3)

    assert len(results) == 3
    titles = [r[0]["title"] for r in results]
    assert titles[0] == "Sunshine"  # only song with both genre AND mood match
    scores = [r[1] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_songs_skips_unspecified_features():
    # Two songs identical except for energy. With no `energy` in prefs,
    # scoring must NOT depend on energy — both should tie.
    songs = [
        {"id": 1, "title": "Low", "artist": "X",
         "genre": "pop", "mood": "happy",
         "energy": 0.05, "acousticness": 0.5, "valence": 0.5,
         "danceability": 0.5, "tempo_bpm": 100, "lyrics": ""},
        {"id": 2, "title": "High", "artist": "Y",
         "genre": "pop", "mood": "happy",
         "energy": 0.95, "acousticness": 0.5, "valence": 0.5,
         "danceability": 0.5, "tempo_bpm": 100, "lyrics": ""},
    ]
    prefs = {"genre": "pop", "mood": "happy"}
    results = recommend_songs(prefs, songs, k=2)
    assert results[0][1] == results[1][1]

    # When energy IS specified, the matching song should win.
    prefs_with_energy = {"genre": "pop", "mood": "happy", "energy": 0.95}
    results = recommend_songs(prefs_with_energy, songs, k=2)
    assert results[0][0]["title"] == "High"


def test_themes_boost_lyrics_matching_songs():
    songs = make_dict_catalog()
    # Pure-themes query — no audio/genre/mood signal.
    prefs = {"themes": ["heartbreak"]}
    results = recommend_songs(prefs, songs, k=4)

    top_two_titles = {r[0]["title"] for r in results[:2]}
    # Songs 1 and 3 have "heartbreak" in lyrics; 2 and 4 don't.
    assert top_two_titles == {"Heartbreak Hotel", "Heart of Stone"}
    # Top scores should beat the no-match scores.
    assert results[0][1] > results[2][1]


def test_themes_appear_in_reasons():
    songs = make_dict_catalog()
    prefs = {"themes": ["heartbreak"]}
    results = recommend_songs(prefs, songs, k=1)
    reasons = results[0][2]
    assert any("lyrics mention" in r and "heartbreak" in r for r in reasons)


def test_themes_match_is_case_insensitive():
    songs = [{
        "id": 1, "title": "T1", "artist": "A",
        "genre": "pop", "mood": "happy",
        "energy": 0.5, "acousticness": 0.5, "valence": 0.5,
        "danceability": 0.5, "tempo_bpm": 100,
        "lyrics": "I felt HEARTBREAK that day",
    }]
    prefs = {"themes": ["Heartbreak"]}
    results = recommend_songs(prefs, songs, k=1)
    reasons = results[0][2]
    assert any("heartbreak" in r.lower() for r in reasons)


def test_empty_or_missing_themes_is_noop():
    songs = make_dict_catalog()
    prefs_a = {"genre": "pop", "mood": "happy"}
    prefs_b = {"genre": "pop", "mood": "happy", "themes": []}
    a = recommend_songs(prefs_a, songs, k=4)
    b = recommend_songs(prefs_b, songs, k=4)
    assert [r[1] for r in a] == [r[1] for r in b]
    assert [r[0]["id"] for r in a] == [r[0]["id"] for r in b]


def test_recommend_songs_handles_missing_lyrics_field():
    # A song dict with no "lyrics" key shouldn't crash when themes are set.
    songs = [{
        "id": 1, "title": "No Lyrics", "artist": "A",
        "genre": "pop", "mood": "happy",
        "energy": 0.5, "acousticness": 0.5, "valence": 0.5,
        "danceability": 0.5, "tempo_bpm": 100,
    }]
    prefs = {"themes": ["heartbreak"]}
    results = recommend_songs(prefs, songs, k=1)
    assert len(results) == 1
    assert not any("lyrics mention" in r for r in results[0][2])


def test_out_of_bounds_features_are_clamped(capsys):
    songs = make_dict_catalog()
    prefs = {"energy": 1.5, "tempo_bpm": 250}
    recommend_songs(prefs, songs, k=1)
    out = capsys.readouterr().out
    assert "energy" in out and "clamping" in out
    assert "tempo_bpm" in out
