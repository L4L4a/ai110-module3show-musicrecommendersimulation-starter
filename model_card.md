# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**, a rule-based, content-only music recommender.

## 2. Goal / Task

Given a user's declared taste (one favorite genre, one favorite mood, one target energy level), rank a small catalog of songs and return the top 5, each with a reason string that shows exactly which scoring terms fired.

## 3. Data Used

- **Source**: `data/songs.csv`, hand-written for this classroom project (not real listening data).
- **Size**: 20 songs, 16 distinct genres, 14 distinct moods.
- **Attributes per song**: `id`, `title`, `artist`, `genre`, `mood`, `energy` (0-1), `tempo_bpm`, `valence`, `danceability`, `acousticness` (all 0-1).
- **Used by the scorer**: `genre`, `mood`, `energy`. The rest are loaded but not scored in the baseline.
- **Genre counts**: lofi 3, pop 3 (counting the two pop songs plus "Neon Ballroom"), and every other genre exactly 1 song (`indie pop` is a separate genre from `pop`).

## 4. Algorithm Summary

For every song the system awards points: 2.0 if its genre equals the user's favorite genre, 1.0 if its mood equals the favorite mood, and up to 1.0 for how close its energy is to the user's target (1 minus the absolute difference). Points are added up (maximum 4.0), all 20 songs are sorted from highest to lowest score, and the top 5 are shown. Ties keep the order of the CSV file.

## 5. Observed Behavior and Biases

Everything below comes from the four baseline runs in the README (High-Energy Pop, Chill Lofi, Deep Intense Rock, Adversarial sad blues at 0.95 energy).

- **Genre imbalance / tiny catalog**: only lofi and pop have more than one song. Deep Intense Rock has exactly one rock song, so after rank 1 the list is no longer "rock-like": rank 2 is a pop song (Gym Hero, mood match only) and ranks 3-5 are metal, EDM and pop matched purely on energy (0.90-0.98). Users whose genre has one song get one good result and four filler results.
- **Weight dominance**: genre (+2.0) is worth twice a mood match and up to twice a perfect energy score. In the adversarial run the single blues song scored 3.50 even though its energy was 0.50 away from the target, while the next four songs, which actually matched the energy, scored below 1.0. A genre label overrides everything else.
- **Energy is the only continuous term, so it acts as the tie-breaker**: whenever no genre or mood matches, the list is simply "songs closest in energy", which is why Gym Hero, Storm Runner, Pulse Garden and Iron Cathedral keep reappearing for different high-energy profiles.
- **Exact-match categories**: `pop` and `indie pop`, or `chill` and `relaxed`, are treated as completely unrelated, although a listener would see them as close. Rooftop Lights (indie pop, happy) only gets the mood point for a pop/happy user.
- **Artist repetition**: The same artist can fill several slots, because nothing in the baseline penalizes repeats (e.g. two of the top 3 Chill Lofi results, Midnight Coding and Focus Flow, are both by LoRoom).
- **Single static taste**: one genre, one mood, one energy per profile. No history, no multi-taste users, no negative signals like skips.

## 6. Evaluation Process

I ran `python -m src.main` for four hand-built profiles and read the top 5 for each, checking three things: (1) is the song a human would call the best match ranked first (yes for Pop, Lofi and Rock, where one song matches all three terms), (2) do the reason strings add up to the printed score (they do, to rounding), and (3) what happens when the profile cannot be satisfied (the adversarial case, see above). I also ran the two starter pytest tests, which pass. There is no numeric metric and no real-user feedback, so "reasonable" here means my own judgment on a 20-song catalog.

## 7. Intended and Non-Intended Use

- **Intended**: classroom exploration of how a transparent scoring rule turns song attributes and a taste profile into a ranked list, and of where bias appears.
- **Not intended**: recommending music to real users, making claims about real musical taste, or anything that requires fairness guarantees for artists. The catalog is tiny and invented, the profile has no history, and the genre weight was chosen by hand, not learned from data.

## 8. Improvement Ideas

- **Soften categorical matching**: replace exact genre/mood equality with a similarity table (e.g. pop to indie pop = 0.7, chill to relaxed = 0.6) so near-genres are not scored as zero.
- **Use more attributes** (tempo, valence, acousticness, danceability) as continuous closeness terms so that songs outside the favorite genre can still be ranked meaningfully.
- **Rebalance the weights** (for example genre 1.0, mood 1.0, energy 1.5) and re-run the adversarial profile to see whether the one-song-then-filler pattern improves.
- **Re-rank for diversity** so the same artist or genre cannot take every slot.
