# AI Interactions Log

Tool used: Claude Code (Claude Sonnet 5.5) running as an agent in the project folder.

---

## Agentic Workflow

**What task did I give the agent?**

I gave the agent the assignment spec as a starting brief and had it scaffold the Music Recommender Simulation — the required items and the stretch features — then reviewed the output step by step and adjusted parts myself.

**How I worked with it:**

I reviewed the output after each step.

**Prompts used:**

**Prompt 1: main build request.** I asked the agent to read the README, `src/` and `data/` first, then build the required items and commit after each numbered step. The required items were:
- the README explanation
- a 20-song dataset
- `score_song`
- `load_songs` and `recommend_songs`
- printed reason strings
- four user profiles with outputs
- a model card
- a Personal Reflection with TODO placeholders for me

I asked for the four stretch features only after those were verified: extra attributes, a diversity penalty, Strategy-pattern ranking modes and `tabulate` table output. I also asked for `ai_interactions.md`, and told it to run every profile and mode, show `git status`, and not push without asking me.

**Prompt 2: follow-up tasks.** I asked the agent to verify its own work by recomputing at least three scores by hand and checking the CSV and the README against real output. I also asked for a Manual verification section, a reflection draft based on what happened in the session, and a final check of every rubric item.

**What the agent generated or changed:**

- `README.md`: "How The System Works", scoring and ranking rules, profile outputs and comparisons, stretch sections, CLI usage, limitations, Personal Reflection as TODOs.
- `data/songs.csv`: expanded to 20 songs (16 genres, 14 moods), plus 5 extra columns (`popularity`, `release_decade`, `mood_tag`, `instrumentalness`, `liveness`).
- `src/recommender.py`: `load_songs`, `score_song`, `recommend_songs`, `Recommender` class, extra-attribute scoring, Strategy classes, diversity re-ranker.
- `src/main.py`: four profiles, argparse CLI, tabulate output, import fixed so `python -m src.main` works.
- `model_card.md`, `requirements.txt` (`tabulate`), `tests/test_recommender.py` (3 new tests).

**What I checked and changed myself:**

- Ran `pytest` and the main entry point to confirm the outputs.
- Hand-checked at least one score against the arithmetic (e.g. Sunrise City / High-Energy Pop: 2.0 + 1.0 + 0.92 = 3.92).
- Read the README comparisons and model card claims against the real run output.
- Ran pytest and python -m src.main, and confirmed the outputs matched the README. The agent caught its own errors during the build (an 18-vs-14 mood count and some inaccurate README claims), which I reviewed and approved.

**Stretch summary**

- **A. Extra attributes**: seven optional similarity terms at most +0.5 each; `--basic` turns them off so the baseline is reproducible.
- **B. Diversity**: `--diversity` re-ranks with -1.0 per repeated artist and -0.5 per repeated genre.
- **C. Ranking modes**: Strategy pattern with four strategies switchable via `--mode`.
- **D. Table output**: `tabulate` with Rank, Title, Artist, Score, Reasons.

---

## Design Pattern

**Which design pattern did I use?**

Strategy pattern.

**How did AI help?**

I asked for ranking modes switchable from `main.py`. The agent proposed an abstract `RankingStrategy` with one `score` method and one class per mode, all delegating to the same `score_song` with different weight dictionaries — so the explanation strings stay correct in every mode. I reviewed the result and kept the structure because it removes the `if mode == ...` branching I would otherwise have written.

**How it appears in the code:**

- Interface: `RankingStrategy` in `src/recommender.py`.
- Concrete strategies: `BalancedStrategy`, `GenreFirstStrategy`, `MoodFirstStrategy`, `EnergySimilarityStrategy`.
- Registry: `STRATEGIES` / `get_strategy(name)`.
- Switching: `python -m src.main --mode genre-first`.

---

## Manual verification

- [x] Ran `python -m src.main --basic --plain` and confirmed the four outputs match README.
- [x] Ran `pytest` — 5 tests pass.
- [x] Opened `data/songs.csv` — 20 rows, no blank cells.
- [x] Hand-checked one score (Sunrise City, High-Energy Pop = 3.92).
- [x] Ran `--mode all --diversity` without errors.
- [x] Read README comparisons and model card claims against run output.
- [x] Filled in Personal Reflection.

---