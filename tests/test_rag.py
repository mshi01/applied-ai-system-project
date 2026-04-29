"""
Tests for src/rag.py — focuses on the JSON post-processing in parse_query.
The Gemini client is monkeypatched so these tests do not hit the network.
"""

import src.rag as rag


class _FakeResponse:
    def __init__(self, text: str):
        self.text = text


class _FakeModels:
    def __init__(self, response_text: str):
        self._response_text = response_text

    def generate_content(self, **_kwargs):
        return _FakeResponse(self._response_text)


class _FakeClient:
    def __init__(self, response_text: str):
        self.models = _FakeModels(response_text)


def _patch_client(monkeypatch, response_text: str) -> None:
    monkeypatch.setattr(rag, "_client", lambda: _FakeClient(response_text))


def test_parse_query_strips_null_features(monkeypatch):
    # Gemini returns nulls for features the user didn't specify; parse_query
    # must drop them so recommend_songs treats them as unspecified.
    payload = (
        '{"genre": "pop", "mood": "sad", '
        '"energy": null, "acousticness": null, "valence": 0.2, '
        '"danceability": null, "tempo_bpm": null, '
        '"themes": ["heartbreak"]}'
    )
    _patch_client(monkeypatch, payload)

    result = rag.parse_query("sad songs about heartbreak", ["pop", "rock"], ["happy", "sad"])

    assert result["genre"] == "pop"
    assert result["mood"] == "sad"
    assert result["valence"] == 0.2
    assert result["themes"] == ["heartbreak"]
    for stripped_key in ("energy", "acousticness", "danceability", "tempo_bpm"):
        assert stripped_key not in result


def test_parse_query_keeps_empty_themes_list(monkeypatch):
    # Empty list is a valid "no lyrical content" signal — must NOT be stripped
    # like null is, so downstream code can distinguish "no themes" from "absent".
    payload = (
        '{"genre": "edm", "mood": "happy", '
        '"energy": 0.9, "acousticness": null, "valence": null, '
        '"danceability": null, "tempo_bpm": null, "themes": []}'
    )
    _patch_client(monkeypatch, payload)

    result = rag.parse_query("upbeat workout songs", ["edm", "pop"], ["happy", "sad"])

    assert result["themes"] == []
    assert result["energy"] == 0.9


def test_parse_query_returns_all_specified_values(monkeypatch):
    payload = (
        '{"genre": "rock", "mood": "neutral", '
        '"energy": 0.8, "acousticness": 0.2, "valence": 0.4, '
        '"danceability": 0.6, "tempo_bpm": 140, "themes": ["rebellion", "freedom"]}'
    )
    _patch_client(monkeypatch, payload)

    result = rag.parse_query(
        "intense rock about rebellion and freedom",
        ["rock", "pop"],
        ["happy", "sad", "neutral"],
    )

    assert result == {
        "genre": "rock",
        "mood": "neutral",
        "energy": 0.8,
        "acousticness": 0.2,
        "valence": 0.4,
        "danceability": 0.6,
        "tempo_bpm": 140,
        "themes": ["rebellion", "freedom"],
    }
