"""
Streamlit UI for the music recommender + Gemini RAG layer.

Run from the repo root:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from src.recommender import load_songs, recommend_songs

DEFAULT_CSV = "data/spotify_sample.csv"

EXAMPLE_QUERIES = [
    "chill songs about heartbreak",
    "upbeat workout music",
    "sad rock about loneliness",
    "happy pop for summer",
]

GENRE_COLORS = {
    "pop": "#3b6db5",
    "rock": "#b85450",
    "rap": "#6b46c1",
    "r&b": "#9b3a6b",
    "latin": "#e07b3c",
    "edm": "#2ea58e",
}
MOOD_COLORS = {
    "happy": "#e8a13f",
    "sad": "#5b7ba0",
    "neutral": "#888888",
}
RANK_COLOR = "#3b6db5"


def _badge(text: str, color: str) -> str:
    return (
        f"<span style='background:{color};color:white;padding:5px 14px;"
        "border-radius:14px;font-size:0.85em;font-weight:600;"
        "display:inline-block;margin-right:8px;letter-spacing:0.02em'>"
        f"{text}</span>"
    )


@st.cache_data(show_spinner="Loading catalog...")
def _load_catalog(path: str):
    songs = load_songs(path)
    valid_genres = sorted({s["genre"] for s in songs if s.get("genre")})
    valid_moods = sorted({s["mood"] for s in songs if s.get("mood")})
    return songs, valid_genres, valid_moods


def _render_song(rank, song, score, reasons):
    genre = song.get("genre", "—")
    mood = song.get("mood", "—")
    genre_color = GENRE_COLORS.get(genre, RANK_COLOR)
    mood_color = MOOD_COLORS.get(mood, "#888888")

    with st.container(border=True):
        cols = st.columns([1, 11])
        with cols[0]:
            st.markdown(
                f"<div style='font-size:2.6em;font-weight:800;color:{RANK_COLOR};"
                "text-align:center;padding-top:8px;line-height:1'>"
                f"#{rank}</div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(
                f"<div style='font-size:1.4em;font-weight:700;margin-bottom:2px'>"
                f"{song['title']}</div>"
                f"<div style='color:#666;margin-bottom:12px'>"
                f"by <strong>{song['artist']}</strong></div>"
                f"<div style='margin-bottom:6px'>"
                f"{_badge(genre, genre_color)}"
                f"{_badge(f'mood · {mood}', mood_color)}"
                f"</div>",
                unsafe_allow_html=True,
            )
            with st.expander("Show match details"):
                st.metric("Score", f"{score:.2f}")
                st.markdown("**Why this song?**")
                for reason in reasons:
                    st.markdown(f"- {reason}")


def main():
    st.set_page_config(page_title="Music RAG", layout="wide")

    st.title("Song recommender - Resonance 2.0")
    st.caption(
        "Hybrid scoring (audio features + lyric themes) with a Gemini RAG layer "
        "for natural-language queries and per-song explanations."
    )

    try:
        songs, valid_genres, valid_moods = _load_catalog(DEFAULT_CSV)
    except FileNotFoundError:
        st.error(
            f"Catalog not found at `{DEFAULT_CSV}`. "
            "Run `python scripts/ingest_kaggle.py` to build it from the raw Kaggle CSV."
        )
        st.stop()

    with st.sidebar:
        st.header("Settings")
        k = st.slider("Number of recommendations", min_value=1, max_value=10, value=5)
        use_llm = st.checkbox("Generate Gemini blurbs", value=True)
        st.divider()
        st.subheader("Catalog")
        st.markdown(f"**Songs**: {len(songs)}")
        st.markdown(f"**Genres**: {', '.join(valid_genres)}")
        st.markdown(f"**Moods**: {', '.join(valid_moods)}")

    st.markdown("**Try one of these:**")
    example_clicked = None
    cols = st.columns(len(EXAMPLE_QUERIES))
    for col, example in zip(cols, EXAMPLE_QUERIES):
        if col.button(example, use_container_width=True):
            example_clicked = example

    with st.form("search_form", clear_on_submit=False):
        typed = st.text_input(
            "What do you want to listen to?",
            placeholder="describe a vibe, theme, or genre",
        )
        submitted = st.form_submit_button("Find songs", type="primary")

    query = example_clicked or (typed if submitted else None)

    if not query:
        st.info("Type a request above or click an example to get recommendations.")
        return

    st.markdown(f"**Query:** *{query}*")

    try:
        with st.spinner("Asking Gemini to parse your request..."):
            from src.rag import parse_query
            prefs = parse_query(query, valid_genres, valid_moods)
    except Exception as e:
        st.error(f"Could not parse the query: {e}")
        st.info("Make sure `GEMINI_API_KEY` is set in `.env` at the repo root.")
        return

    with st.expander("Parsed preferences (debug)"):
        st.json(prefs)

    recs = recommend_songs(prefs, songs, k=k)

    if not recs:
        st.warning("No songs matched your query.")
        return

    st.subheader("Top picks")
    for rank, (song, score, reasons) in enumerate(recs, start=1):
        _render_song(rank, song, score, reasons)

    if use_llm:
        try:
            with st.spinner("Asking Gemini to write blurbs..."):
                from src.rag import generate_explanation
                blurb = generate_explanation(query, recs)
            st.subheader("Gemini take")
            st.write(blurb)
        except Exception as e:
            st.warning(f"Could not generate blurbs: {e}")


if __name__ == "__main__":
    main()
