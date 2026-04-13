# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**Resonance 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---
Resonance 1.0 suggests songs based on a user's musical taste profile. Given a user's preferred genre, mood, and five numeric audio features (energy, acousticness, valence, danceability, tempo), it ranks every song in the catalog by a computed score and returns the top-k matches.

This system uses content-based filtering, comparing the audio features of each song directly against a user's stated preferences. It operates on the assumption that listeners with a defined music profile will gravitate toward songs that closely match it. Given the current dataset size, the system is used for classroom exploration.


## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

Every song is scored against the user's profile using a weighted point system. A song earns full marks on a numeric feature when its value exactly matches the user's target, and loses points proportionally as it drifts away. Genre and mood are all-or-nothing bonuses that carry more weight than any single numeric feature. The detailed scoring criteria are listed below.

| Criterion | Max Points | Methods |
| Genre match |	+2.0 | Exact string match |
| Mood match | +1.5 | Exact string match |
| Energy proximity | +1.0 | `1 - |
| Acousticness proximity | +1.0 | `1 - |
| Valence proximity | +1.0 | `1 - |
| Danceability proximity | +1.0 | `1 - |
| Tempo proximity | +1.0 | `1 - |

Songs are ranked from highest to lowest score, and the top k are returned as recommendations. Compared to the original design, this version introduces numerical proximity features for valence, danceability, and tempo — each measured against the user's profile — and replaces the boolean likes_acousticness flag with a continuous acousticness proximity score. These changes allow for finer-grained matching between the user profile and the available song features.


## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

- **Catalog size:** 20 songs in data/songs.csv
- **Features per song:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, country, metal, folk, electronic, reggae, blues, funk (16 genres)
- **Moods represented:** happy, chill, intense, relaxed, focused, peaceful, confident, romantic, nostalgic, angry, melancholic, energetic, uplifting, sad, groovy, moody (16 moods)


## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

Across all tested user profiles — high_energy_pop, chill_lofi, and deep_intense_rock — the system produced intuitive and reasonable recommendations. For example, the chill_lofi profile returned lo-fi and ambient tracks characterized by low energy and high acousticness, a strong match. Similarly, the deep_intense_rock profile surfaced metal and rock songs at the top of the rankings, confirming that the genre and mood bonus weights are functioning as intended.

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

- **Genre and mood dominate.** Genre and mood together are worth +3.5 points — more than three numeric features combined. A song matching both genre and mood will almost always outrank a song with near-perfect numeric alignment but a different genre/mood.
- **Unknown genres/moods fall back to pure numeric ranking.** A user whose preferences include genres like "bossa nova" or moods like "wistful" will never receive genre or mood bonuses if those categories are absent from the catalog.
- **No diversity enforcement.** All top-5 results can be from the same artist or nearly identical songs — nothing penalizes repetition.
- **Equal weight across all numeric features.** There's no way to express that tempo matters far more than acousticness to a particular user.


## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

Six profiles were tested by running python -m src.main and checking whether the results matched intuition:

| Profile | Observation |
| Starter (pop/happy) | Top results were pop and upbeat — correct |
| Chill Lofi | Returned lofi/ambient with low energy and high acousticness — strong match |
| Deep Intense Rock | Metal and rock ranked highest — genre+mood bonuses worked |
| Conflicting prefs (sad mood + high-energy numbers) | Numeric features overwhelmed the mood bonus; upbeat songs surfaced despite "sad" preference |
| Out-of-bounds (energy 1.5, tempo 260) | Clamping warnings fired; after clamping, results matched rock/intense cluster |
| Unknown genre/mood (bossa nova, wistful) | No bonuses fired; ranking was purely numeric — reasonable but genre-blind |

A weight shift test was also conducted, doubling the importance of energy while halving the importance of genre, using the starter (pop/happy) profile as the baseline. The top 5 recommended songs remained identical after the adjustment; however, the individual scores changed. This suggests that while reweighting altered each song's absolute score, it did not affect their relative ranking within the current catalog. With a larger and more diverse dataset, the same weight shift would likely produce different recommendations.


## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---
- **Expand the dataset** — build a larger, more diverse catalog spanning a wider range of genres, moods, and other audio features.
- **Diversity enforcement** — after scoring, cap how many songs from the same artist or genre appear in the top-k to avoid repetitive results.
- **Per-feature user weights** — let users express that tempo matters more than acousticness by assigning individual multipliers instead of a fixed +1.0 cap per feature.

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

In the real world, tech companies typically employ strategies like collaborative filtering and content-based filtering to power their recommendation systems. This project implements a simple recommendation system using content-based filtering, which works by comparing features from a song catalog against a user's music profile to score and rank songs, then surfacing the top k results.

The accuracy of the system depends on two key factors: the number of features included and the weights assigned to each. More features bring the recommendations closer to a true match, while higher-weighted features have a greater influence on the final rankings.

The current version of the app is intentionally minimal. It operates on a limited song catalog, is stateless, and cannot learn from user feedback. In contrast, commercial platforms like Spotify and YouTube employ far more sophisticated systems — ones that incorporate listening history, massive song databases, artist diversity controls, and many additional signals that make their recommendations feel more personalized and useful.