# 🎵 Music Recommender Simulation

## Project Summary


Resonance 1.0 is a content-based music recommender that matches songs from the catalog to a user's music taste profile. Given preferences like favorite genre, mood, and five numeric audio features (energy, acousticness, valence, danceability, tempo), it scores every song using a weighted point system — genre and mood earn the biggest bonuses (+2.0 and +1.5), while each numeric feature contributes up to +1.0 based on how close the song's value is to the user's target. The top-k results are returned with scores and plain-language explanations.


## How The System Works

In real world senarios, big tech companies like spotify and Youtube would use strategies including collaborative filtering and content-based filtering for recommendation systems. Collaborative filtering uses the idea: "Users who liked what you liked also enjoyed X." The platform finds users with similar taste profiles and recommends what those users loved. For content-based filtering, rather than looking at other users, it analyzes the content itself including musical features like tempo, key, energy, danceability. In this system, we will use content-based filtering, that is to compare the features of the song list and the features of the songs the users like, calcuate the score of the songs based on proximity and recommend the top k scored songs from the list. 

The process flowchart of the system is shown below.
![flowchart](images/flowchart.png)

Each Song object in the system will include the following features:
- id: int
- title: str
- artist: str
- genre: str
- mood: str
- energy: float
- tempo_bpm: float
- valence: float
- danceability: float
- acousticness: float

Each UserProfile object will store the following features:
- favorite_genre: str
- favorite_mood: str
- target_energy: float
- target_acousticness: float
- target_tempo: float
- target_valence: float
- target_danceability: float

The UserProfile object was updated to mirror all available fields in the Song object, increasing the system's ability to match user preferences with song features. Notably, the boolean likes_acousticness field was replaced with a float target_acousticness to capture the user's affinity for acousticness on a continuous scale.

Scoring is handled differently depending on the feature type. Numerical features use a proximity score based on the inverted absolute difference:
score = 1 - |song.feature - user.target_feature|

This ensures that songs closest to the user's target value receive the highest score. Categorical features are scored as an exact match (1.0) or no match (0.0). Weights are applied across all feature types to reflect their relative importance; for example, a genre match contributes more to the final score than a mood match.

The recommender computes a weighted score for each song using the following criteria:

| Criterion               | Max Points | Method                                      |
|-------------------------|------------|---------------------------------------------|
| Genre match             | +2.0       | Exact string match                          |
| Mood match              | +1.5       | Exact string match                          |
| Energy proximity        | +1.0       | `1 - \|song.energy - user.target_energy\|`      |
| Acousticness proximity  | +1.0       | `1 - \|song.acousticness - user.target_acousticness\|` |
| Valence proximity       | +1.0       | `1 - \|song.valence - user.target_valence\|`    |
| Danceability proximity  | +1.0       | `1 - \|song.danceability - user.target_danceability\|` |
| Tempo proximity         | +1.0       | `1 - \|song.tempo - user.target_tempo\| / 200`  |

Genre is treated as a stronger, more persistent signal of user identity than mood, which tends to be situational — so a genre match is awarded +2.0 while a mood match yields +1.5. One trade-off of this design is that the system may over-prioritize genre at the expense of mood alignment.

The four continuous attributes — energy, acousticness, valence, and danceability — are all assumed to fall within a [0, 1] range, so their proximity scores are naturally bounded to the same scale. Tempo operates on a much larger scale (BPM), so its difference is normalized by dividing by 200 before applying the proximity formula. 

The top k highest-scoring songs are then returned as the final recommendations.

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

The starter (pop/happy) profile was tested first, and the recommendations aligned with expectations.

Recommendation result for starter (pop/happy) profile:

<div align="left">
  <img src="images/starter_profile_1.png" alt="starter-profile" width="45%">
  <img src="images/starter_profile_2.png" alt="starter-profile" width="45%">
</div>
<br clear="all">

Six additional user profiles were tested beyond the baseline starter (pop/happy) profile: high_energy_pop, chill_lofi, deep_intense_rock, conflicting_energy_mood, out_of_bounds, and unknown_genre_mood.
The first three profiles all produced intuitive and reasonable recommendations. The remaining three surfaced notable edge cases:

- conflicting_mood_energy — The "sad" mood never triggers the +1.5 mood bonus, yet the numerical features still push recommendations toward upbeat songs, exposing a tension between categorical and continuous scoring signals.
- out_of_bounds — An energy value of 1.5 causes the proximity score 1.0 - |1.5 - song_energy| to go negative for most songs. Clamping warnings fired, and after clamping was applied, results aligned with the rock and high-intensity cluster as expected.
- unknown_genre_mood — No genre or mood bonuses were triggered, leaving rankings driven entirely by numerical proximity. Results were reasonable but genre-blind.

Recommendation result for high_energy_pop profile:

<div align="left">
  <img src="images/highenergy_pop_1.png" alt="high-energy-pop-profile" width="45%">
  <img src="images/highenergy_pop_2.png" alt="high-energy-pop-profile" width="45%">
</div>
<br clear="all">

Recommendation result for chill_lofi profile:

<div align="left">
  <img src="images/chill_lofi_1.png" alt="chill-lofi-profile" width="45%">
  <img src="images/chill_lofi_2.png" alt="chill-lofi-profile" width="45%">
</div>
<br clear="all">

Recommendation result for deep_intense_rock profile:

<div align="left">
  <img src="images/deep_intense_rock_1.png" alt="deep-intense-rock-profile" width="45%">
  <img src="images/deep_intense_rock_2.png" alt="deep-intense-rock-profile" width="45%">
</div>
<br clear="all">

Recommendation result for conflicting_energy_mood profile:

<div align="left">
  <img src="images/conflicting_energy_mood_1.png" alt="conflicting-energy-mood-profile" width="45%">
  <img src="images/conflicting_energy_mood_2.png" alt="conflicting-energy-mood-profile" width="45%">
</div>
<br clear="all">

Recommendation result for out_of_bounds profile (out of bounds and clamped warning is shown as well):

<div align="left">
  <img src="images/outbounds_clamped_1.png" alt="outbounds-profile" width="50%">
  <img src="images/outbounds_clamped_2.png" alt="outbounds-profile" width="50%">
</div>
<br clear="all">

Recommendation result for unknown_genre_mood profile (unknown genre and mood warning is shown as well):

<div align="left">
  <img src="images/unknown_genre_mood_1.png" alt="unknown-genre-mood-profile" width="50%">
  <img src="images/unknown_genre_mood_2.png" alt="unknown-genre-mood-profile" width="50%">
</div>
<br clear="all">

In addition, a weight shift test was also conducted using the starter (pop/happy) profile, doubling the importance of energy while halving the importance of genre. The top 5 recommended songs remained unchanged, though their individual scores shifted. This indicates that reweighting altered each song's absolute score without affecting relative rankings — an expected outcome given the catalog's limited size and diversity. A larger dataset would likely yield more differentiated results under the same adjustment.

Recommendation result for weight shift experiment:

<div align="left">
  <img src="images/experiment_1.png" alt="weight-shift-experiment" width="45%">
  <img src="images/experiment_2.png" alt="weight-shift-experiment" width="45%">
</div>
<br clear="all">

---

## Limitations and Risks

- Tiny catalog
The current catalog only contained 20 different songs
- No diversity enforcement
Nothing prevents the top-k results from being nearly identical songs or all from the same artist.
- Static, stateless profile
There's no listening history, likes, or dislikes. The profile is a fixed dict with no way to learn or adapt over time.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Systems like this demonstrate how data can be transformed into predictions. By using content-based filtering, the recommender matches song features against user profiles, computes scores, and ranks songs accordingly. The choice of features and their assigned weights are central to this process — different combinations will cause the system to favor certain songs over others, making these design decisions critical to the quality of recommendations.

This system also surfaces several visible sources of bias. Genre and mood together account for up to +3.5 points — more than three numeric features combined — meaning users whose preferred genre or mood is absent from the catalog are immediately disadvantaged. A listener who favors "bossa nova" or a "wistful" mood receives no categorical bonuses at all, reducing their recommendations to pure numeric ranking while users with well-represented tastes benefit from the full scoring range. The equal weights applied to all numeric features introduce a further assumption: that energy matters exactly as much as acousticness for every listener, which will not reflect everyone's preferences in practice. At scale, these design choices directly determine whose taste the system serves well and whose it underserves — illustrating how bias can enter recommendation systems through deliberate design decisions, long before any training data is involved.


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
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