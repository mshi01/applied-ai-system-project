# 🎧 Model Card: RAG Music Recommender

## 1. Model Name

**Resonance 2.0**

A music recommender that pairs a deterministic rule-based scorer with a Gemini-powered RAG layer. Resonance 1.0 (the predecessor) ranked 20 hand-curated songs against a structured user profile; 2.0 keeps the same readable scoring formula and adds three things — natural-language query parsing, a 50× larger catalog of real Spotify songs with lyrics, and a lyric-theme matching component that grounds recommendations in song content rather than just audio features.

## 2. Intended Use

Resonance 2.0 takes a free-text query — a mood, an activity, a lyrical theme, or a stylistic reference — and returns a ranked list of songs with one-sentence explanations grounded in each track's lyrics excerpt. It operates on a fixed 1,002-song catalog, is designed for exploration of RAG systems and small-scale music discovery.

## 3. How the Model Works

The pipeline has five stages:

| Stage | What happens |
|-------|--------------|
| Ingest | Filter the raw 18K Kaggle CSV to English + non-null-lyrics rows, dedupe on `(track_name, track_artist)` keeping the highest-popularity occurrence, take the top-167 per genre, derive mood from valence, truncate lyrics to 500 chars |
| Parse query | Send the user's free-text query to Gemini 2.5 Flash with the catalog's valid genres / moods. Gemini returns a JSON profile: `{genre, mood, energy, acousticness, valence, danceability, tempo_bpm, themes}` where unspecified features are `null` and `themes` is a list of lyrical keywords |
| Score | For each of the 1,002 songs, accumulate points: +2.0 genre match, +1.5 mood match, up to +1.0 each for proximity on every audio feature the user actually specified, and up to +2.0 for lyric-theme overlap (fraction of `themes` that appear as substrings in the song's lyrics) |
| Rank | Sort songs by score descending, take top-K |
| Explain | Optionally send the top-K back to Gemini 2.5 Flash with their lyrics excerpts and ask for one-sentence-per-song blurbs that quote or reference the lyrics |

The scorer is the ranker. Gemini parses queries and writes explanations. 

### Scoring formula

```
score(song) =
    2.0 × [genre matches user's genre]
  + 1.5 × [mood matches user's mood]
  + Σ_{f ∈ specified}  ( 1.0  -  |song[f] - user[f]| / scale[f] )
  + 2.0 × ( |matched_themes| / |total_themes| )      if total_themes > 0
```

Maximum possible score ≈ 10.5 (when every component fires).

### Lyric-theme matching

When Gemini extracts `themes=["heartbreak", "moving on"]` from a query, the scorer lower-cases each theme and checks for substring presence in each song's `lyrics` field. This is intentionally cheap — substring matching catches morphology accidentally ("heartbreak" hits "heartbreaks" and "heartbroken") and relies on Gemini to canonicalize synonyms upstream.

## 4. Data

- **Source:** the Kaggle dataset titled **"Audio features and lyrics of Spotify songs"** (~18,000 tracks across 6 playlist genres, with audio features and English lyric strings).
- **Working catalog size:** 1,002 tracks (167 per genre × 6 genres) after sampling, dedup, and English-language filter. Persisted at `data/spotify_sample.csv`.
- **Genres:** `pop`, `latin`, `rap`, `r&b`, `rock`, `edm`.
- **Mood labels:** `happy` (valence ≥ 0.6), `sad` (valence ≤ 0.4), `neutral` (otherwise). Coarse 3-bucket derivation from valence.
- **Per-song columns retained:** `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`, `popularity`, `lyrics` (first 500 chars).

## 5. Model Components

- **Recommender / scorer:** `src/recommender.py`. Includes both a functional `recommend_songs(prefs, songs, k)` (used by the CLI and Streamlit UI) and an OOP `Recommender` class (kept for the starter test contract).
- **Query parser:** `src/rag.py:parse_query`. Single Gemini 2.5 Flash call with `response_mime_type="application/json"` and `thinking_budget=0` (parsing is a near-template task — thinking tokens would otherwise eat the output budget on Flash). Null-valued features are stripped before returning so the scorer treats them as unspecified.
- **Explanation writer:** `src/rag.py:generate_explanation`. Single Gemini 2.5 Flash call with `max_output_tokens=2000` to leave room for one sentence per recommendation. Each song's lyrics excerpt is included in the prompt as grounding.
- **UI:** CLI or Streamlit (`app.py`). Sidebar settings, four example-query chips, search form, results rendered as bordered cards with track and artist name, genre / mood badges, and a collapsed "Why this song?" reasons, score progress bars and lyrics excerpt. 
- **Test suite:** `pytest` over `tests/test_recommender.py` (functional + OOP scorer behavior including the new themes feature) and `tests/test_rag.py` (`parse_query` JSON post-processing with the Gemini client monkey-patched).

## 6. Strengths

- **Auditable ranking.** The score for any song against any query reduces to a sum of named, weighted components, each of which can be printed alongside the result. Bad recommendations are debuggable to a specific scoring decision rather than a vector-space anomaly.
- **Two-axis matching.** The system uses both audio features (the structured signal Spotify provides) and lyric content (the unstructured signal that actually answers "songs about X" queries). Most rule-based recommenders do only the first; most embedding-based RAG systems do only the second.
- **Cheap RAG.** No embeddings model, no vector store, no extra deps for the retrieval layer. Lyric matching is `theme.lower() in lyrics.lower()` against 1,002 short strings — microseconds at query time.
- **Bounded API budget.** A typical query costs at most two Gemini calls (parse + explain). Pure-audio queries with `--no-llm` cost one. Demo profiles cost zero. The full ingest is a one-time pandas job with no network.
- **Null-default semantics.** Unspecified features are not silently filled with 0.5 defaults — they're truly unspecified, so a query like "sad rock songs" doesn't accidentally penalize tracks whose energy or danceability differs from a made-up midpoint.

## 7. Limitations and Bias

- **Coarse mood.** A 3-bucket function of valence loses substantial signal. Songs near a threshold land in different buckets despite being nearly identical, and "neutral" is a catch-all that mixes mid-energy ballads with chill-but-positive tracks.
- **Lyric matching is substring-only.** Catches morphology by accident, misses true synonyms and metaphor. A song that's *about* heartbreak without using the word will score zero on lyrics regardless of how perfectly it fits.
- **Lyric truncation.** First 500 characters means later sections (bridge, outro) are invisible to both the theme matcher and the explanation generator.
- **Catalog skew.** The Kaggle dataset is itself a snapshot weighted toward commercially popular Western music. Genres and languages outside that scope are absent. The English-only filter sharpens this further.
- **Coarse genre labels.** "pop" includes everything from Carly Rae Jepsen to Lewis Capaldi; "rock" spans Queen to Imagine Dragons. Sub-genre nuance is not represented.
- **LLM explanation unreliability.** `generate_explanation` is grounded in lyrics, but Gemini can still produce plausible-sounding rationales that emphasize attributes not actually salient. The retrieval / ranking is auditable; the explanations should be read as suggestions, not verified facts.
- **No personalization.** Two users issuing the same query get the same results. No history, no feedback, no contrastive signal.
- **No diversity reranking.** Top-K can contain multiple tracks by the same artist or near-identical feature profiles.

## 8. Evaluation

Resonance 2.0 has been evaluated qualitatively via a small set of representative queries and demo profiles, with the goal of confirming that each scoring component is exercised end-to-end:

| Query / Demo | What it exercises | Expected behavior |
|--------------|-------------------|-------------------|
| `"chill songs about heartbreak"` | Lyric theme + low-energy preference | Top results contain "heartbreak" in lyrics; lower-energy songs surface |
| `"upbeat workout music"` | Pure-audio query (no themes) | `themes=[]`; ranking driven by genre + audio feature proximity |
| `"sad rock about loneliness"` | Genre + mood + theme stacking | Rock songs whose lyrics mention "loneliness" |
| `--demo starter` | Rule-based scorer in isolation | Top result is a high-energy happy pop song |
| `--demo conflicting` | Mood / valence inconsistency handling | Returns results without crashing; mood bonus competes with valence proximity |
| `--demo out_of_bounds` | Clamping logic | Prints clamping warnings; falls back to valid range |
| `--demo unknown` | Unknown genre / mood handling | Prints catalog-mismatch warnings; falls back to feature-proximity ranking |

There is no formal offline evaluation set — that would require human relevance judgments or a held-out user-playlist dataset, neither of which is part of this project. The unit tests in `tests/` cover scorer mechanics (sorted top-K, null-default features, theme overlap, missing-lyrics graceful handling, out-of-bounds clamping) and `parse_query`'s JSON post-processing.

## 9. Future Work

- **Embeddings-based lyric retrieval.** Replace substring matching with precomputed Gemini embeddings on each song's lyrics, query embedding at runtime, cosine similarity as the lyric score. Higher quality on metaphor and oblique themes; adds ~10 batched API calls at ingest time and one extra call per query when themes are present.
- **Diversity reranker.** Apply MMR or a per-artist cap before returning top-K to avoid clustering by artist or playlist.
- **Finer-grained mood.** Replace the 3-bucket mood with a 4-quadrant Russell's circumplex (valence × arousal/energy) or a continuous similarity over (valence, energy, danceability).
- **Larger / multilingual catalog.** Drop the English-only filter, raise `PER_GENRE`, or swap to a larger source dataset.
- **Lightweight personalization.** Persist accepted / rejected recommendations and use them as positive / negative signals in a contrastive reranker.
- **Offline evaluation harness.** A small set of (query, expected-property) pairs and a `pytest` check on retrieval hit rate at K — gives a reproducible quality signal beyond ad-hoc query inspection.

## 10. Personal Reflection

The biggest takeaway from this project is that architecture is exactly where a human in the loop matters most. The first design AI proposed was to embed each song with `all-MiniLM-L6-v2` and rank by cosine similarity against the embedded query. I tried it, and the results were shallow — "songs for a rainy night" surfaced tracks with "rain" in the title rather than tracks that captured the *vibe* of a rainy night. Another proposal was to embed the full catalog with Gemini and embed the query at runtime (Gemini embeddings + a `.npy` matrix + cosine similarity), which would have produced richer semantic matches but would also have spent an extra API call per query plus a one-time embedding pass over all 1,002 songs — both at real risk of tripping the free-tier quota. After weighing the options, I kept the current approach: let Gemini translate the query into structured preferences and a short list of lyric themes, and let the rule-based scorer combine feature proximity with substring theme matches. The trade-off is honest — "chill songs about heartbreak" reliably surfaces tracks with the word "heartbreak" in the lyrics but misses songs that are *about* heartbreak without naming it. For the queries this app is meant to handle, that compromise is acceptable, and the system stays cheap enough to run on a free API tier without rationing.

Second, most of the difficulty in adding an LLM is figuring out what *not* to give it. It would have been easy to push the LLM into the ranking loop — "given these 30 candidates and the user's query, pick 5 and order them" — and the system would have looked impressive. But the resulting ranker would be opaque, non-deterministic, and bottlenecked by Gemini's prior about what makes a "good match." Keeping the LLM out of ranking and limiting it to translation (`parse_query`) and presentation (`generate_explanation`) preserved the property that any score can be audited to a line of code. The natural-language input felt magical; the underneath stayed boring on purpose.

Third, null defaults matter more than I expected. An early version had `parse_query` fill unspecified features with 0.5 — Gemini's instructions said "pick reasonable middle values for any feature the user did not specify." The result was that "songs about heartbreak" silently penalized tracks whose energy or danceability differed from 0.5, even though the user had said nothing about energy or danceability. Switching to explicit null-and-strip made the scoring honest: an unspecified feature contributes zero, not noise. It was a small change to one prompt and one dict comprehension, and it improved every lyric-flavored query by removing a hidden bias I couldn't see in the output.
