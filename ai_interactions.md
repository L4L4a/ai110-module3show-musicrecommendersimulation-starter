# AI Interactions Log

Tool used: Claude Code (Claude Sonnet 5.5) running as an agent in the project folder.

---

## Agentic Workflow

**What task did you give the agent?**

Build the whole Music Recommender Simulation: the required items 1-8 with one commit per step, then the four stretch features, then run everything and report `git status` and the push command (without pushing).

**Prompt used:**

> This is my AI110 "Music Recommender Simulation" project. Read README.md and everything in src/ and data/ first. Build the required features first and commit after each numbered step. Do the stretch features only after all required items are done and verified.
>
> REQUIRED (21 pts)
> 1. EXPLANATION (README.md, "How The System Works"): Explain how real recommenders (Spotify, YouTube) use data features like genre, mood, tempo, and user history. Clearly separate (a) input data (song attributes), (b) user preferences (the taste profile), and (c) ranking/selection (scoring then sorting). Keep it specific and technically correct, not generic.
> 2. DATASET: Expand data/songs.csv to 18-20 songs, each with genre, mood, energy, tempo_bpm, and the existing columns. Use diverse genres and moods. Make sure it loads without errors.
> 3. SCORING: In src/recommender.py, implement score_song(user_prefs, song) returning (score, reasons) where reasons is a list of strings. Use genre match +2.0, mood match +1.0, and energy similarity 1 - abs(song_energy - target_energy). It must work for every song and return numeric output. Document the scoring rule and ranking rule in README.md.
> 4. RECOMMENDER: Implement load_songs and recommend_songs(user_prefs, songs, k=5), which scores all songs, sorts descending, and returns the top k with reasons. It must work for any profile.
> 5. EXPLANATIONS: For each recommendation, print a reason string that reflects the exact scoring terms that fired (e.g. "genre match (+2.0), energy similarity (+0.92)"). Paste at least 3 of these explanations as text into README.md.
> 6. PROFILES: In main.py, add 4 profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, and one adversarial case. Run all of them, paste each output into README.md in fenced code blocks, and write 2-3 sentences after each set comparing how the outputs differ between profiles, based on the real output.
> 7. MODEL CARD: Create model_card.md with Model Name, Goal/Task, Data Used, Algorithm Summary, Observed Behavior/Biases, Evaluation Process, Intended and Non-Intended Use, and at least one concrete Improvement Idea. Base claims on what was actually run.
> 8. Add a "Personal Reflection" section to README.md with TODO placeholders for me. Do not write it for me.
>
> STRETCH (+8 pts) - do all four
> A. EXTRA ATTRIBUTES (+2): Add 5+ new columns to songs.csv and update scoring and user profiles to use them consistently. Create ai_interactions.md with the prompt I used, a summary of the changes, and a "Manual verification" section listing what I should check.
> B. DIVERSITY (+2): Add an artist/genre repetition penalty so the top-k is not dominated by one artist or genre. Document in model_card.md how it reduces filter bubbles and improves fairness.
> C. RANKING MODES (+2): Implement at least two ranking strategies using the Strategy pattern ... Let me switch modes in main.py with a variable or a CLI argument. Record the design pattern and how AI helped in ai_interactions.md.
> D. TABLE OUTPUT (+2): Use the tabulate library (add it to requirements.txt) to print results as a table with columns for rank, title, artist, score, and reasons. Put one table output in the README.
>
> FINISH: Run `python -m src.main` for every profile and mode to confirm there are no errors. Check that README.md and model_card.md contain the outputs and explanations. Show me `git status` and the exact push command. Do not push without asking me.

(Some of the prompt text is shortened with "..." and in the example lists; the full wording is in the chat history.)

**What did the agent generate or change?**

- `README.md`: "How The System Works" (real-world recommenders; input data / taste profile / scoring-then-sorting), scoring and ranking rules, profile outputs and comparisons, stretch sections, CLI usage, experiments, limitations, and a Personal Reflection section left as TODOs.
- `data/songs.csv`: 10 to 20 songs (16 genres, 14 moods); then 5 new columns: `popularity`, `release_decade`, `mood_tag`, `instrumentalness`, `liveness`.
- `src/recommender.py`: `load_songs`, `score_song`, `recommend_songs`, a working `Recommender` class (so the starter tests exercise real logic), extra-attribute scoring, the Strategy classes, and the diversity re-ranker.
- `src/main.py`: four profiles, argparse CLI (`--mode`, `--profile`, `--diversity`, `--basic`, `--plain`, `-k`), tabulate output. The starter import `from recommender import ...` was changed to `from src.recommender import ...` so `python -m src.main` works.
- `model_card.md`, `requirements.txt` (added `tabulate`), `tests/test_recommender.py` (3 new tests).
- One commit per required step, one commit for the stretch code, one for the stretch docs.

**Stretch summary**

- **A. Extra attributes**: profiles opt in with `mood_tag`, `target_decade`, `target_popularity`, `target_acousticness`, `target_danceability`, `target_instrumentalness`, `target_liveness`. Each adds at most +0.5. All four profiles use a subset of them. `--basic` turns them off so the required baseline output is still reproducible.
- **B. Diversity**: `--diversity` re-ranks greedily with -1.0 per repeated artist and -0.5 per repeated genre. Discussion is in `model_card.md`.
- **C. Ranking modes**: see below.
- **D. Table output**: `tabulate` with columns Rank, Title, Artist, Score, Reasons; sample table in the README.

**What did you verify or fix manually?**

See "Manual verification" below. Things the agent had to correct while working: a README sentence about weights that was confusing, a wrong mood count (18) in the first model card draft (actual: 14), and README claims about how the stretch attributes change the rankings, which were rewritten after comparing the actual outputs.

---

## Design Pattern

**Which design pattern did you use?**

Strategy pattern.

**How did AI help you brainstorm or implement it?**

The prompt asked for ranking modes that can be switched from `main.py`. The agent proposed an abstract base class with one method, `score(user_prefs, song) -> (score, reasons)`, and one small class per mode instead of `if mode == ...` branches inside the scorer. It also noticed that all modes share the same terms and differ only in weights, so each class delegates to the same `score_song` with a weights dictionary. That keeps the explanation strings correct for every mode (they show the weighted contribution of each term).

**How does the pattern appear in your final code?**

- Interface: `RankingStrategy` in [src/recommender.py](src/recommender.py) (abstract `score` method).
- Concrete strategies: `BalancedStrategy` (2.0 / 1.0 / 1.0), `GenreFirstStrategy` (4.0 / 1.0 / 1.0), `MoodFirstStrategy` (1.0 / 3.0 / 1.0), `EnergySimilarityStrategy` (0.5 / 0.5 / 3.0).
- Registry and lookup: `STRATEGIES` and `get_strategy(name)`.
- Context: `recommend_songs(..., strategy=...)` only calls `strategy.score`, so it does not know which mode it runs.
- Switching: `python -m src.main --mode genre-first` (or `mood-first`, `energy-similarity`, `balanced`, `all`).

---

## Manual verification

Check these yourself before you submit:

- [ ] Run `python -m src.main --basic --plain` and confirm the four outputs match the fenced blocks in README.md.
- [ ] Open `data/songs.csv`: 20 rows, no blank cells, and the genres and moods look reasonable to you (the song titles, artists and numbers are invented).
- [ ] Hand-check one score: Sunrise City for High-Energy Pop (baseline) should be 2.0 + 1.0 + (1 - |0.82 - 0.90|) = 3.92.
- [ ] Hand-check one extra-attribute term, e.g. popularity similarity for Sunrise City (popularity 78, target 80): 0.5 * (1 - 2/100) = 0.49.
- [ ] Run every mode and the diversity flag: `python -m src.main --mode all --diversity` (and without `--diversity`) should print without errors.
- [ ] Run `pytest` (5 tests should pass).
- [ ] Read README.md "How The System Works" and the comparison paragraphs after the profile outputs; change any wording that does not sound like you or that you disagree with.
- [ ] Read the model card claims in "Observed Behavior and Biases" against the run output (e.g. Deep Intense Rock has only one rock song; the adversarial blues song scores 3.50 with a 0.50 energy gap in the baseline run).
- [ ] Fill in the three TODOs in "Personal Reflection" in README.md yourself.
- [ ] Decide whether the adversarial profile is the one you want, and whether the diversity penalties (1.0 / 0.5) and the mode weights seem sensible.
- [ ] Confirm `git log` shows one commit per numbered step, then push.
