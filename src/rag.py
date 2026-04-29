"""
Gemini-backed RAG layer for the music recommender.

Two functions wrap the Gemini API:

  parse_query(text, valid_genres, valid_moods)
      Turn a natural-language request into the dict that
      src.recommender.recommend_songs already expects.

  generate_explanation(query, recommendations)
      Given the top-k recommendations (with lyrics), ask Gemini to write a
      one-sentence-per-song blurb grounded in each song's lyrics excerpt.

Both calls read GEMINI_API_KEY from the environment (or .env at the repo root).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from google import genai
from google.genai import types

_REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_REPO_ROOT / ".env")

GEMINI_MODEL = "gemini-2.5-flash"


def _client() -> genai.Client:
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to .env at the repo root or export it."
        )
    return genai.Client()


def parse_query(text: str, valid_genres: List[str], valid_moods: List[str]) -> Dict:
    """
    Convert a free-text music request into a user_prefs dict matching the
    schema consumed by recommend_songs:
        {genre, mood, energy, acousticness, valence, danceability, tempo_bpm, themes}
    `themes` is a list of lowercase keywords describing the lyrical content the
    user wants (empty list when the query is purely about audio/vibe).
    """
    genre_options = ", ".join(valid_genres)
    mood_options = ", ".join(valid_moods)

    prompt = f"""You convert a free-text music request into a structured user preference profile.

User request: "{text}"

Allowed genres: {genre_options}
Allowed moods:  {mood_options}

Return ONLY a JSON object with these exact keys:
  genre         (string — must be one of the allowed genres, or "" if none clearly fits)
  mood          (string — must be one of the allowed moods, or "" if none clearly fits)
  energy        (float 0.0-1.0, or null if the user did not specify)
  acousticness  (float 0.0-1.0, or null if the user did not specify)
  valence       (float 0.0-1.0; 0=sad, 1=happy, or null if the user did not specify)
  danceability  (float 0.0-1.0, or null if the user did not specify)
  tempo_bpm     (number in 60-180, or null if the user did not specify)
  themes        (list of 1-5 short lowercase keywords/phrases capturing the LYRICAL content the user wants — e.g. ["heartbreak", "moving on"]; [] if the query is purely about audio/vibe with no lyrical theme)

Only set a numeric value when the request clearly implies it (e.g. "fast" → high tempo_bpm, "chill" → low energy, "happy" → high valence). Use null otherwise — do not guess a middle default, since unspecified features should not influence ranking.

For themes: extract only the *content/topic* part of the request, not audio descriptors. E.g. "chill songs about heartbreak" → themes=["heartbreak"], not ["chill", "heartbreak"]. "upbeat workout songs" → themes=[]. Use simple, common words that are likely to literally appear in lyrics (prefer "heartbreak" over "emotional turmoil"). Each theme should be at least 4 characters to avoid spurious substring matches.
No markdown fences, no commentary, no extra keys. JSON only."""

    client = _client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            # Disable thinking — query parsing is a near-template task and
            # thinking tokens would otherwise eat the output budget on 2.5 Flash.
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=400,
        ),
    )

    raw = (response.text or "").strip()
    parsed = json.loads(raw)
    # Drop null-valued features so recommend_songs treats them as unspecified
    # instead of scoring against a 0.5 default.
    return {k: v for k, v in parsed.items() if v is not None}


def generate_explanation(
    query: str,
    recommendations: List[Tuple[Dict, float, List[str]]],
) -> str:
    """
    Write a one-sentence blurb per song explaining why it fits the user's
    natural-language request, grounded in each song's lyrics excerpt.
    """
    if not recommendations:
        return ""

    lines = []
    for rank, (song, _score, _reasons) in enumerate(recommendations, start=1):
        lyrics = (song.get("lyrics") or "").replace("\n", " ").strip()
        if len(lyrics) > 280:
            lyrics = lyrics[:280] + "…"
        if not lyrics:
            lyrics = "(no lyrics available)"
        lines.append(
            f'{rank}. "{song["title"]}" by {song["artist"]} '
            f'[{song["genre"]}, mood={song["mood"]}, '
            f'energy={float(song["energy"]):.2f}, valence={float(song["valence"]):.2f}]\n'
            f'   Lyrics excerpt: {lyrics}'
        )
    songs_block = "\n\n".join(lines)

    prompt = f"""You are a music recommendation expert.

The user asked for: "{query}"

Here are the top {len(recommendations)} matched songs:

{songs_block}

For each song, write ONE sentence (~25 words) explaining why it fits the user's request. Ground your reasoning in the lyrics excerpt — quote a phrase or reference a theme when helpful. Keep it specific, not generic.

Respond as a numbered list (1., 2., ...). No preamble, no closing remarks."""

    client = _client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        # 2.5 Flash spends a slice of max_output_tokens on internal thinking;
        # 2000 leaves enough room for one sentence per recommendation.
        config=types.GenerateContentConfig(max_output_tokens=2000),
    )
    return (response.text or "").strip()
