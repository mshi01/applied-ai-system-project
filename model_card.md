# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**Resonance 1.0**  

## 2. Intended Use  

Resonance 1.0 suggests songs based on a user's musical taste profile. Given a user's preferred genre, mood, and five numeric audio features (energy, acousticness, valence, danceability, tempo), it ranks every song in the catalog by a computed score and returns the top-k matches.

This system uses content-based filtering, comparing the audio features of each song directly against a user's stated preferences. It operates on the assumption that listeners with a defined music profile will gravitate toward songs that closely match it. Given the current dataset size, the system is used for classroom exploration.


## 3. How the Model Works  

Every song is scored against the user's profile using a weighted point system. A song earns full marks on a numeric feature when its value exactly matches the user's target, and loses points proportionally as it drifts away. Genre and mood are all-or-nothing bonuses that carry more weight than any single numeric feature. The detailed scoring criteria are listed below.

| Criterion               | Max Points | Method                                      |
|-------------------------|------------|---------------------------------------------|
| Genre match             | +2.0       | Exact string match                          |
| Mood match              | +1.5       | Exact string match                          |
| Energy proximity        | +1.0       | `1 - \|song.energy - user.target_energy\|`      |
| Acousticness proximity  | +1.0       | `1 - \|song.acousticness - user.target_acousticness\|` |
| Valence proximity       | +1.0       | `1 - \|song.valence - user.target_valence\|`    |
| Danceability proximity  | +1.0       | `1 - \|song.danceability - user.target_danceability\|` |
| Tempo proximity         | +1.0       | `1 - \|song.tempo - user.target_tempo\| / 200`  |

Songs are ranked from highest to lowest score, and the top k are returned as recommendations. Compared to the original design, this version introduces numerical proximity features for valence, danceability, and tempo — each measured against the user's profile — and replaces the boolean likes_acousticness flag with a continuous acousticness proximity score. These changes allow for finer-grained matching between the user profile and the available song features.


## 4. Data  

- **Catalog size:** 20 songs in data/songs.csv
- **Features per song:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, country, metal, folk, electronic, reggae, blues, funk (16 genres)
- **Moods represented:** happy, chill, intense, relaxed, focused, peaceful, confident, romantic, nostalgic, angry, melancholic, energetic, uplifting, sad, groovy, moody (16 moods)


## 5. Strengths  

Across all tested user profiles — high_energy_pop, chill_lofi, and deep_intense_rock — the system produced intuitive and reasonable recommendations. For example, the chill_lofi profile returned lo-fi and ambient tracks characterized by low energy and high acousticness, a strong match. Similarly, the deep_intense_rock profile surfaced metal and rock songs at the top of the rankings, confirming that the genre and mood bonus weights are functioning as intended.

## 6. Limitations and Bias 

- **Genre and mood dominate.** Genre and mood together are worth +3.5 points — more than three numeric features combined. A song matching both genre and mood will almost always outrank a song with near-perfect numeric alignment but a different genre/mood.
- **Unknown genres/moods fall back to pure numeric ranking.** A user whose preferences include genres like "bossa nova" or moods like "wistful" will never receive genre or mood bonuses if those categories are absent from the catalog.
- **No diversity enforcement.** All top-5 results can be from the same artist or nearly identical songs — nothing penalizes repetition.
- **Equal weight across all numeric features.** There's no way to express that tempo matters far more than acousticness to a particular user.


## 7. Evaluation  

Six profiles were tested by running python -m src.main and checking whether the results matched intuition:

| Profile                                          | Observation                                                                                   |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Starter (pop/happy)                              | Top results were pop and upbeat — correct                                                     |
| Chill Lofi                                       | Returned lofi/ambient with low energy and high acousticness — strong match                    |
| Deep Intense Rock                                | Metal and rock ranked highest — genre and mood bonuses worked                                 |
| Conflicting prefs (sad mood + high-energy numbers) | Numeric features overwhelmed the mood bonus; upbeat songs surfaced despite "sad" preference |
| Out-of-bounds (energy 1.5, tempo 260)            | Clamping warnings fired; after clamping, results matched rock/intense cluster                 |
| Unknown genre/mood (bossa nova, wistful)         | No bonuses fired; ranking was purely numeric — reasonable but genre-blind                     |

A weight shift test was also conducted, doubling the importance of energy while halving the importance of genre, using the starter (pop/happy) profile as the baseline. The top 5 recommended songs remained identical after the adjustment; however, the individual scores changed. This suggests that while reweighting altered each song's absolute score, it did not affect their relative ranking within the current catalog. With a larger and more diverse dataset, the same weight shift would likely produce different recommendations.


## 8. Future Work  

- **Expand the dataset** — build a larger, more diverse catalog spanning a wider range of genres, moods, and other audio features.
- **Diversity enforcement** — after scoring, cap how many songs from the same artist or genre or have recently played appear in the top-k to avoid repetitive results.
- **Per-feature user weights** — let users express that tempo matters more than acousticness by assigning individual multipliers instead of a fixed +1.0 cap per feature.

## 9. Personal Reflection  

In the real world, tech companies typically employ strategies like collaborative filtering and content-based filtering to power their recommendation systems. This project implements a simple recommendation system using content-based filtering, which works by comparing features from a song catalog against a user's music profile to score and rank songs, then surfacing the top k results.

The accuracy of the system depends on two key factors: the number of features included and the weights assigned to each. More features bring the recommendations closer to a true match, while higher-weighted features have a greater influence on the final rankings.

The current version of the app is intentionally minimal. It operates on a limited song catalog, is stateless, and cannot learn from user feedback. In contrast, commercial platforms like Spotify and YouTube employ far more sophisticated systems — ones that incorporate listening history, massive song databases, artist diversity controls, and many additional signals that make their recommendations feel more personalized and useful.