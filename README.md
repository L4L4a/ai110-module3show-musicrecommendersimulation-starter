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
python -m src.main                                   # all profiles, balanced mode, table output
python -m src.main --mode mood-first                 # genre-first | mood-first | energy-similarity | balanced | all
python -m src.main --diversity                       # artist/genre repetition penalty
python -m src.main --profile "Chill Lofi" -k 5       # one profile (name or unique substring)
python -m src.main --basic --plain                   # baseline 3-term scoring, plain text
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

Produced with `python -m src.main --basic --plain` (`--basic` ignores the stretch attributes so only the three baseline terms are used). Each profile returns its top 5 of 20 songs.

**High-Energy Pop**

```text
=== High-Energy Pop | mode=balanced | diversity=off ===
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
=== Chill Lofi | mode=balanced | diversity=off ===
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
=== Deep Intense Rock | mode=balanced | diversity=off ===
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
=== Adversarial (sad blues at max energy) | mode=balanced | diversity=off ===
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

## Stretch Features

### A. Extra attributes

`data/songs.csv` has five more columns: `popularity` (0-100), `release_decade`, `mood_tag` (a detailed mood such as *cozy* or *gritty*), `instrumentalness` and `liveness`. A profile can opt in to any of them, and each one adds at most **+0.5**, so the three core terms still dominate:

| Profile key | Song column | Term |
|---|---|---|
| `mood_tag` | `mood_tag` | +0.5 on exact match |
| `target_decade` | `release_decade` | +0.5 on exact match |
| `target_popularity` | `popularity` | 0.5 * (1 - abs(diff) / 100) |
| `target_acousticness`, `target_danceability`, `target_instrumentalness`, `target_liveness` | same-named column | 0.5 * (1 - abs(diff)) |

Terms only fire when the profile has the key, so the baseline outputs above stay reproducible with `--basic`.

### B. Diversity penalty (`--diversity`)

After scoring, the top k is built greedily: each pick subtracts **1.0** per earlier pick by the same artist and **0.5** per earlier pick in the same genre. The penalties appear in the reason string. Chill Lofi with the extra attributes, with the penalty off and on (note that Focus Flow, a second LoRoom song, slides from rank 3 to rank 4 and loses 2.0 points: -1.0 artist repeat, -1.0 for two earlier lofi picks):

```text
=== Chill Lofi | mode=balanced | diversity=off ===
Profile: genre=lofi, mood=chill, energy=0.35, mood_tag=cozy, target_decade=2020, target_popularity=55, target_acousticness=0.8, target_instrumentalness=0.6

|   Rank | Title               | Artist         |   Score | Reasons                                                                                                                                                                                                                     |
|--------|---------------------|----------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Midnight Coding     | LoRoom         |    6.31 | genre match (+2.0), mood match (+1.0), energy similarity (+0.93), mood tag 'cozy' match (+0.50), 2020s release (+0.50), popularity similarity (+0.46), acousticness similarity (+0.45), instrumentalness similarity (+0.48) |
|      2 | Library Rain        | Paper Lanterns |    5.92 | genre match (+2.0), mood match (+1.0), energy similarity (+1.00), 2020s release (+0.50), popularity similarity (+0.50), acousticness similarity (+0.47), instrumentalness similarity (+0.45)                                |
|      3 | Focus Flow          | LoRoom         |    4.82 | genre match (+2.0), energy similarity (+0.95), 2020s release (+0.50), popularity similarity (+0.47), acousticness similarity (+0.49), instrumentalness similarity (+0.40)                                                   |
|      4 | Spacewalk Thoughts  | Orbit Bloom    |    3.15 | mood match (+1.0), energy similarity (+0.93), popularity similarity (+0.42), acousticness similarity (+0.44), instrumentalness similarity (+0.35)                                                                           |
|      5 | Coffee Shop Stories | Slow Stereo    |    2.69 | energy similarity (+0.98), mood tag 'cozy' match (+0.50), popularity similarity (+0.47), acousticness similarity (+0.46), instrumentalness similarity (+0.28)                                                               |
```

```text
=== Chill Lofi | mode=balanced | diversity=on ===
Profile: genre=lofi, mood=chill, energy=0.35, mood_tag=cozy, target_decade=2020, target_popularity=55, target_acousticness=0.8, target_instrumentalness=0.6

|   Rank | Title               | Artist         |   Score | Reasons                                                                                                                                                                                                                     |
|--------|---------------------|----------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Midnight Coding     | LoRoom         |    6.31 | genre match (+2.0), mood match (+1.0), energy similarity (+0.93), mood tag 'cozy' match (+0.50), 2020s release (+0.50), popularity similarity (+0.46), acousticness similarity (+0.45), instrumentalness similarity (+0.48) |
|      2 | Library Rain        | Paper Lanterns |    5.42 | genre match (+2.0), mood match (+1.0), energy similarity (+1.00), 2020s release (+0.50), popularity similarity (+0.50), acousticness similarity (+0.47), instrumentalness similarity (+0.45), genre repeat (-0.5)           |
|      3 | Spacewalk Thoughts  | Orbit Bloom    |    3.15 | mood match (+1.0), energy similarity (+0.93), popularity similarity (+0.42), acousticness similarity (+0.44), instrumentalness similarity (+0.35)                                                                           |
|      4 | Focus Flow          | LoRoom         |    2.82 | genre match (+2.0), energy similarity (+0.95), 2020s release (+0.50), popularity similarity (+0.47), acousticness similarity (+0.49), instrumentalness similarity (+0.40), artist repeat (-1.0), genre repeat (-1.0)        |
|      5 | Coffee Shop Stories | Slow Stereo    |    2.69 | energy similarity (+0.98), mood tag 'cozy' match (+0.50), popularity similarity (+0.47), acousticness similarity (+0.46), instrumentalness similarity (+0.28)                                                               |
```

### C. Ranking modes (`--mode`)

Four strategies sit behind one `RankingStrategy.score(user_prefs, song)` interface in `src/recommender.py`: `balanced` (genre 2.0 / mood 1.0 / energy 1.0), `genre-first` (4.0 / 1.0 / 1.0), `mood-first` (1.0 / 3.0 / 1.0) and `energy-similarity` (0.5 / 0.5 / 3.0). The adversarial profile is where they differ: balanced, genre-first and mood-first all keep the blues song first (it matches genre and mood), whereas `energy-similarity` puts the loud Pulse Garden first by a hair (Porch Light Blues drops to rank 2):

```text
=== Adversarial (sad blues at max energy) | mode=energy-similarity | diversity=off ===
Profile: genre=blues, mood=sad, energy=0.95, mood_tag=gritty, target_decade=1970, target_popularity=90, target_acousticness=0.1

|   Rank | Title             | Artist     |   Score | Reasons                                                                                                                                                                                  |
|--------|-------------------|------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Pulse Garden      | Kairo Wave |    3.94 | energy similarity (+2.97), popularity similarity (+0.49), acousticness similarity (+0.48)                                                                                                |
|      2 | Porch Light Blues | Delta Mae  |    3.94 | genre match (+0.5), mood match (+0.5), energy similarity (+1.50), mood tag 'gritty' match (+0.50), 1970s release (+0.50), popularity similarity (+0.26), acousticness similarity (+0.18) |
|      3 | Gym Hero          | Max Pulse  |    3.89 | energy similarity (+2.94), popularity similarity (+0.47), acousticness similarity (+0.47)                                                                                                |
|      4 | Storm Runner      | Voltline   |    3.72 | energy similarity (+2.88), popularity similarity (+0.34), acousticness similarity (+0.50)                                                                                                |
|      5 | Iron Cathedral    | Ashen Gate |    3.68 | energy similarity (+2.94), popularity similarity (+0.28), acousticness similarity (+0.47)                                                                                                |
```

### D. Table output

All of the stretch output above is printed with `tabulate` (columns: Rank, Title, Artist, Score, Reasons). The Chill Lofi table in section B is the sample table; pass `--plain` for the text format used in the baseline runs.

---

## Experiments You Tried

- **Switching ranking mode on the adversarial profile**: only `energy-similarity` changes the winner (Pulse Garden and Porch Light Blues both print as 3.94, with Pulse Garden a fraction higher); genre-first and mood-first only inflate the blues song's lead (6.94 and 5.94 vs 4.94 balanced) without changing what follows it.
- **Turning on the diversity penalty for Chill Lofi**: the second LoRoom song drops out of the top 3 and a different-artist song takes its place, at the cost of showing a lower-scoring recommendation.
- **Adding the stretch attributes**: scores rise (a full match goes from 4.0 to about 5.9-6.3), and the top 2 stay mostly stable (Chill Lofi swaps ranks 1 and 2), but ranks 3-5 change: for Deep Intense Rock, all three of Pulse Garden, Iron Cathedral and Sunrise City are replaced by Concrete Crown, Night Drive Loop and Rooftop Lights, because the extra terms (up to +0.5 each) outweigh the 0.1-0.2 energy differences that separated them.
- Not yet tried: lowering the genre weight from 2.0 to 0.5, or adding tempo/valence terms.

---

## Limitations and Risks

- The catalog is 20 invented songs; only lofi and pop have more than one entry, so most users get one on-genre song and filler.
- Genre and mood are exact-match strings (`pop` vs `indie pop` counts as no match at all).
- It does not understand lyrics, language, or listening history, and each profile is one static taste.
- Genre weight dominates: a same-genre song with a poor energy match still outranks better-fitting songs from another genre.

See `model_card.md` for details.

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
