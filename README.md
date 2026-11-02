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

## How The System Works

### How real recommenders work

Production systems such as Spotify and YouTube combine two broad signals:

- **Content-based signals**: attributes of the item itself. Spotify exposes audio features such as `energy`, `danceability`, `valence` (musical positivity), `acousticness`, and `tempo` (BPM), plus metadata like genre tags, artist, and release year. YouTube adds video-level features such as title/description text, category, and language.
- **Collaborative signals**: user behavior. Plays, skips, saves, playlist adds, replays, watch time, and likes are logged per user. Users with similar histories are treated as neighbors (matrix factorization / embeddings), so a song can be recommended because similar listeners liked it, even if its audio features look nothing like your favorites.

A large-scale system runs in stages: (1) *candidate generation* narrows millions of items to a few hundred using embeddings, (2) a *ranking model* scores each candidate for the specific user (predicted probability of play, completion, or save), and (3) *re-ranking* applies business rules such as diversity, freshness, and de-duplication. Implicit feedback (a skip within 30 seconds is a strong negative) usually outweighs explicit ratings because there is far more of it.

This project is a small **content-based** simulation. It has no user history and no collaborative filtering; it replaces the learned ranking model with a hand-written scoring rule so every recommendation is explainable.

### (a) Input data: song attributes

Each row of `data/songs.csv` is one song with:

| Attribute | Type | Role in this system |
|---|---|---|
| `genre` | categorical (pop, lofi, rock, ...) | Scored: exact match |
| `mood` | categorical (happy, chill, intense, ...) | Scored: exact match |
| `energy` | float 0-1 | Scored: closeness to the user's target |
| `tempo_bpm` | number | Loaded, not scored in the baseline |
| `valence`, `danceability`, `acousticness` | float 0-1 | Loaded, not scored in the baseline |
| `id`, `title`, `artist` | identifiers | Display only |

### (b) User preferences: the taste profile

A profile is a small dictionary, for example `{"genre": "pop", "mood": "happy", "energy": 0.8}`: one favorite genre, one favorite mood, and a target energy level. There is no listening history; the profile is declared directly and is a single static point in feature space.

### (c) Ranking and selection: score, then sort

1. **Scoring rule** (one song at a time): `score_song(user_prefs, song)` adds up
   - genre match: **+2.0** if `song.genre == user.genre`
   - mood match: **+1.0** if `song.mood == user.mood`
   - energy similarity: **+(1 - |song.energy - target_energy|)**, which lies in 0 to 1 (1.0 is a perfect match)

   The maximum possible score is 4.0. The function returns `(score, reasons)`, where `reasons` lists only the terms that fired.
2. **Ranking rule** (whole catalog): `recommend_songs` scores every song, sorts by score descending (ties keep CSV order), and returns the top `k` (default 5) with a reason string.

Genre is weighted twice as heavily as mood, and a genre match (+2.0) is worth more than a perfect energy score (at most +1.0). So a same-genre song can outrank an off-genre song that is a better match on mood and energy combined, which the experiments below probe.

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

## Sample Recommendation Output

Every recommendation prints the exact scoring terms that fired. Three examples taken from the runs below:

```text
Sunrise City by Neon Echo - Score: 3.92
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.92)
Gym Hero by Max Pulse - Score: 2.97
   Because: genre match (+2.0), energy similarity (+0.97)
Rooftop Lights by Indigo Parade - Score: 1.86
   Because: mood match (+1.0), energy similarity (+0.86)
```

### Baseline profile runs (genre +2.0, mood +1.0, energy similarity)

Produced with `python -m src.main`. Each profile returns its top 5 of 20 songs.

**High-Energy Pop**

```text
=== High-Energy Pop ===
Profile: genre=pop, mood=happy, energy=0.9

1. Sunrise City by Neon Echo - Score: 3.92
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.92)
2. Gym Hero by Max Pulse - Score: 2.97
   Because: genre match (+2.0), energy similarity (+0.97)
3. Neon Ballroom by Velour - Score: 2.78
   Because: genre match (+2.0), energy similarity (+0.78)
4. Rooftop Lights by Indigo Parade - Score: 1.86
   Because: mood match (+1.0), energy similarity (+0.86)
5. Storm Runner by Voltline - Score: 0.99
   Because: energy similarity (+0.99)
```

**Chill Lofi**

```text
=== Chill Lofi ===
Profile: genre=lofi, mood=chill, energy=0.35

1. Library Rain by Paper Lanterns - Score: 4.00
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+1.00)
2. Midnight Coding by LoRoom - Score: 3.93
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.93)
3. Focus Flow by LoRoom - Score: 2.95
   Because: genre match (+2.0), energy similarity (+0.95)
4. Spacewalk Thoughts by Orbit Bloom - Score: 1.93
   Because: mood match (+1.0), energy similarity (+0.93)
5. Coffee Shop Stories by Slow Stereo - Score: 0.98
   Because: energy similarity (+0.98)
```

**Deep Intense Rock**

```text
=== Deep Intense Rock ===
Profile: genre=rock, mood=intense, energy=0.92

1. Storm Runner by Voltline - Score: 3.99
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.99)
2. Gym Hero by Max Pulse - Score: 1.99
   Because: mood match (+1.0), energy similarity (+0.99)
3. Pulse Garden by Kairo Wave - Score: 0.98
   Because: energy similarity (+0.98)
4. Iron Cathedral by Ashen Gate - Score: 0.95
   Because: energy similarity (+0.95)
5. Sunrise City by Neon Echo - Score: 0.90
   Because: energy similarity (+0.90)
```

**Adversarial (sad blues at max energy)**

```text
=== Adversarial (sad blues at max energy) ===
Profile: genre=blues, mood=sad, energy=0.95

1. Porch Light Blues by Delta Mae - Score: 3.50
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.50)
2. Pulse Garden by Kairo Wave - Score: 0.99
   Because: energy similarity (+0.99)
3. Gym Hero by Max Pulse - Score: 0.98
   Because: energy similarity (+0.98)
4. Iron Cathedral by Ashen Gate - Score: 0.98
   Because: energy similarity (+0.98)
5. Storm Runner by Voltline - Score: 0.96
   Because: energy similarity (+0.96)
```

**How the profiles differ.** High-Energy Pop and Chill Lofi both get a full 3-term match at rank 1 (3.92 and 4.00), but Pop has only three pop songs, so its list drops to mood-only and energy-only matches by rank 4-5, while Lofi has three lofi songs and fills ranks 1-3 with genre matches. Deep Intense Rock has just one rock song; after it, rank 2 is a pop song (Gym Hero) that matches only on mood, and ranks 3-5 are pure energy matches from metal, EDM and pop, with scores bunched between 0.90 and 0.98. The adversarial blues/sad/0.95 profile shows the weight problem clearly: the only blues song scores 3.50 despite an energy gap of 0.50, and every other result is below 1.0, so the user gets one on-genre song and four loud songs that are nothing like a sad blues listener's taste.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

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

---

## Personal Reflection

**What I learned about how recommenders turn data into predictions:**

TODO: write 1-2 paragraphs in your own words.

**Where bias or unfairness could show up in a system like this:**

TODO: write 1-2 paragraphs in your own words (hint: think about what you saw in the adversarial profile and the one-song genres).

**Something that surprised me:**

TODO
