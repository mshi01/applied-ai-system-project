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


 For a simple recommender, use the 5 numerical features: energy, valence, danceability, tempo_bpm, acousticness, plus one-hot encoded genre and mood. This gives you a dense feature vector you can compute cosine similarity on directly.

mood and energy tend to dominate user perception, so if you want to simplify further, those two alone will give reasonable results.


A scoring rule is a function that takes one song + one user profile and returns the calculated score of the song. A ranking rule takes the list of all scored songs and decides the order to present them.

The simplest ranking rule is sort by score descending, return top-k.But ranking can be more nuanced than just sorting:

Diversity: don't return 10 songs by the same artist even if they all score high
Novelty: prefer songs the user hasn't heard recently
Freshness: boost new releases even if their raw score is slightly lower.

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

We updated the UserProfile object and mirrored all available features in Song object to increase the recommendation ability and accuracy. We changed the boolean likes_acoustic to a float variable target_acoustincness to better capture user's likeliness on acousticness. 

For numerical features, we will use the proximity score formula and use inverted absolute difference: score = 1 - |song.energy - user.target_energy| 
to calculate the score so that the closest ones will have the highest score.

Boolean features use a simpler rule — match = bonus, no match = no bonus:
acoustic_score = 1.0 if (user.likes_acoustic and song.acousticness > 0.6) else 0.0

For handling categorical data: Exact match = 1.0, no match = 0.0:
genre_score = 1.0 if song.genre == user.favorite_genre else 0.0
mood_score  = 1.0 if song.mood  == user.favorite_mood  else 0.0

In addition, we will add weights to different features, a matching genre will be assigned more score than matching mood.

The recommender will compute the score for each song based on the following scoring criterion: 

| Criterion | Max Points | Methods |
| Genre match |	+2.0 | Exact string match |
| Mood match | +1.5 | Exact string match |
| Energy proximity | +1.0 | `1 - |
| Acousticness proximity | +1.0 | `1 - |
| Valence proximity | +1.0 | `1 - |
| Danceability proximity | +1.0 | `1 - |
| Tempo proximity | +1.0 | `1 - |

Because genre is a more reliable, persistent signal of who the user is, while mood is more situational, a reasonable case is: genre_match → +2.0 and mood_match → +1.5. In this case, This system might over-prioritize genre over mood. 
The four continuous attributes (energy, acousticness, valence, danceability) are all assumed to be in a [0, 1] range, so their proximity scores are also naturally bounded to [0, 1].
Tempo is on a much larger scale (BPM), so it's normalized by dividing the absolute difference by 200 before subtracting from 1.

We will choose the top k scored songs to recommend. 
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

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

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

