# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

Resonance 1.0 is a content-based music recommender that matches songs from the catalog to a user's music taste profile. Given preferences like favorite genre, mood, and five numeric audio features (energy, acousticness, valence, danceability, tempo), it scores every song using a weighted point system — genre and mood earn the biggest bonuses (+2.0 and +1.5), while each numeric feature contributes up to +1.0 based on how close the song's value is to the user's target. The top-k results are returned with scores and plain-language explanations.


## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.


In real world senarios, big tech companies like spotify and Youtube would use strategies including collaborative filtering and content-based filtering for recommendation systems. Collaborative filtering uses the idea: "Users who liked what you liked also enjoyed X." The platform finds users with similar taste profiles and recommends what those users loved. For content-based filtering, rather than looking at other users, it analyzes the content itself including musical features like tempo, key, energy, danceability. In this system, we will use content-based filtering, that is to compare the features of the song list and the features of the songs the users like, calcuate the score of the songs based on proximity and recommend the top k scored songs from the list. 

Each Song object in the system will include the following features:
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

Each UserProfile object will store the following features:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_acousticness: float
    target_tempo: float
    target_valence: float
    target_danceability: float

The UserProfile object was updated to mirror all available fields in the Song object, increasing the system's ability to match user preferences with song features. Notably, the boolean likes_acousticness field was replaced with a float target_acousticness to capture the user's affinity for acousticness on a continuous scale.

Scoring is handled differently depending on the feature type. Numerical features use a proximity score based on the inverted absolute difference:
score = 1 - |song.feature - user.target_feature|

This ensures that songs closest to the user's target value receive the highest score. Categorical features are scored as an exact match (1.0) or no match (0.0). Weights are applied across all feature types to reflect their relative importance; for example, a genre match contributes more to the final score than a mood match.

The recommender computes a weighted score for each song using the following criteria:

| Criterion | Max Points | Methods |
| Genre match |	+2.0 | Exact string match |
| Mood match | +1.5 | Exact string match |
| Energy proximity | +1.0 | `1 - |
| Acousticness proximity | +1.0 | `1 - |
| Valence proximity | +1.0 | `1 - |
| Danceability proximity | +1.0 | `1 - |
| Tempo proximity | +1.0 | `1 - |

Genre is treated as a stronger, more persistent signal of user identity than mood, which tends to be situational — so a genre match is awarded +2.0 while a mood match yields +1.5. One trade-off of this design is that the system may over-prioritize genre at the expense of mood alignment.

The four continuous attributes — energy, acousticness, valence, and danceability — are all assumed to fall within a [0, 1] range, so their proximity scores are naturally bounded to the same scale. Tempo operates on a much larger scale (BPM), so its difference is normalized by dividing by 200 before applying the proximity formula.

The top k highest-scoring songs are then returned as the final recommendations.
---

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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

Recomendation result for starter (pop/happy) profile:
![starter-profile](images/starter_profile_1.png)
![starter-profile](images/starter_profile_2.png)

Six additional user profiles were tested beyond the baseline starter (pop/happy) profile: high_energy_pop, chill_lofi, deep_intense_rock, conflicting_energy_mood, out_of_bounds, and unknown_genre_mood.
The first three profiles all produced intuitive and reasonable recommendations. The remaining three surfaced notable edge cases:

- conflicting_mood_energy — The "sad" mood never triggers the +1.5 mood bonus, yet the numerical features still push recommendations toward upbeat songs, exposing a tension between categorical and continuous scoring signals.
- out_of_bounds — An energy value of 1.5 causes the proximity score 1.0 - |1.5 - song_energy| to go negative for most songs. Clamping warnings fired, and after clamping was applied, results aligned with the rock and high-intensity cluster as expected.
- unknown_genre_mood — No genre or mood bonuses were triggered, leaving rankings driven entirely by numerical proximity. Results were reasonable but genre-blind.

Recomendation result for high_energy_pop profile:
![high-energy-pop-profile](images/highenergy_pop_1.png)
![high-energy-pop-profile](images/highenergy_pop_2.png)

Recomendation result for chill_lofi profile:
![chill-lofi-profile](images/chill_lofi_1.png)
![high-energy-pop-profile](images/chill_lofi_2.png)

Recomendation result for deep_intense_rock profile:
![deep-intense-rock-profile](images/deep_intense_rock_1.png)
![deep-intense-rock-profile](images/deep_intense_rock_2.png)

Recomendation result for conflicting_energy_mood profile:
![conflicting-energy-mood-profile](images/conflicting_energy_mood_1.png)
![conflicting-energy-mood-profile](images/conflicting_energy_mood_2.png)

Recomendation result for out_of_bounds profile:
![outbounds-profile](images/outbounds_clamped_1.png)
![outbounds-profile](images/outbounds_clamped_2.png)

Recomendation result for unknown_genre_mood profile:
![unknown-genre-mood-profile](images/unknown_genre_mood_1.png)
![unknown-genre-mood-profile](images/unknown_genre_mood_2.png)

In addition, a weight shift test was also conducted using the starter (pop/happy) profile, doubling the importance of energy while halving the importance of genre. The top 5 recommended songs remained unchanged, though their individual scores shifted. This indicates that reweighting altered each song's absolute score without affecting relative rankings — an expected outcome given the catalog's limited size and diversity. A larger dataset would likely yield more differentiated results under the same adjustment.

Recomendation result for weight shift experiment:
![weight-shift-experiment-profile](images/experiment_1.png)
![weight-shift-experiment-profile](images/experiment_2.png)

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

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

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

Hard Genre Lock-in the the strongest filter bubble. The genre bonus (+2.0) is a binary cliff — exact string equality only. A "pop" listener gets zero benefit from "indie pop" (song #10) or "funk" even though those may fit their continuous features perfectly. A poorly-matching same-genre song can outscore a near-perfect cross-genre song. 

Unbalanced catalog distribution amplifies bias. "lofi" appears 3× (songs 2, 4, 9) — chill mood 3×
"pop" appears 2×, most other genres appear only 1×. A user preferring lofi/chill has 3 songs eligible for both bonuses (+3.5 each), while a user preferring jazz/relaxed has exactly 1. The filter bubble is literally wider for certain genre/mood combinations.

Tempo Normalization under-weights a perceptually large feature. A 100 BPM difference (e.g., 60 BPM lullaby vs. 160 BPM dance track) only costs 0.5 points — the same as a 0.5 difference in any unit feature. But perceptually, 100 BPM is a massive difference. This makes tempo effectively the weakest feature, letting very tempo-mismatched songs rank highly.

No diversity enforcement-identical results every time. Pure greedy top-k with no randomness or diversity constraint. The same user profile always returns the exact same 5 songs. There's no mechanism to surface discovery or break out of the bubble across sessions.

Tie-breaking by catalog order(positional bias): sorted() is stable — equal-scoring songs resolve in original CSV order. Songs appearing earlier in songs.csv systematically win ties, giving a hidden positional advantage to earlier-added content.

Static profile: The UserProfile is fixed at construction. There's no way to incorporate plays, skips, or ratings to evolve the bubble over time. A user who discovers they actually love jazz after listening to it will still receive the same pop-heavy recommendations until they manually change their profile.

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

