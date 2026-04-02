# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests songs from a small catalog based on a user's preferred genre, mood, energy level, and whether they like acoustic or electronic sound. It is built for classroom exploration — not for real-world deployment — and is meant to demonstrate how a simple rule-based recommender translates user preferences into ranked results.

The system assumes every user can be described by four fixed preferences. It does not learn from listening history, adapt over time, or handle multiple users at once.

---

## 3. How the Model Works

For each song in the catalog, the system asks four questions and awards points based on the answers:

1. **Does the song's genre match what the user prefers?** If yes, the song earns 3 points. If not, it earns nothing. Genre is the strongest single signal.

2. **Does the song's mood match what the user wants?** A match earns 2.5 points. No match earns nothing.

3. **How close is the song's energy level to the user's target?** A perfect match earns the full 2.5 points. The further away the song's energy is, the fewer points it receives — linearly, like a sliding scale.

4. **Does the song's acoustic quality fit the user's taste?** If the user likes acoustic music, songs with higher acousticness score higher (up to 2 points). If the user prefers electronic sound, the opposite applies.

All four point totals are added up to produce a final score out of 10. Every song in the catalog is scored this way, and the top 5 highest-scoring songs are returned as recommendations.

---

## 4. Data

The catalog contains **18 songs** stored in `data/songs.csv`. Each song has a title, artist, genre, mood, and five numerical audio features: energy, tempo, valence, danceability, and acousticness.

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, reggae, metal, r&b, country, blues, electronic

**Moods represented:** happy, chill, intense, relaxed, moody, focused, confident, peaceful, uplifting, angry, romantic, nostalgic, melancholic, dreamy

The starter dataset had 10 songs covering 7 genres and 6 moods. Eight additional songs were added to improve coverage across genres and moods that were missing. Despite this, the catalog is still very small and reflects a narrow, mostly English-language, Western-centric view of music. Entire traditions — K-pop, Afrobeats, Latin, classical Indian music, and many others — are absent.

---

## 5. Strengths

- **Clear user intent profiles:** When a user's preferences closely match songs in the catalog (e.g., a lofi/focused listener or a rock/intense listener), the top results feel intuitive and well-ranked.
- **Transparent scoring:** Every recommendation comes with a plain-English explanation of exactly why each song scored what it did, making the system easy to audit and understand.
- **Energy and acousticness work well as continuous signals:** Unlike genre and mood, these features reward near-matches rather than requiring an exact hit, which produces more nuanced rankings within a matched genre.
- **Diverse catalog:** With 15 genres and 14 moods, most user profiles will find at least one strong match.

---

## 6. Limitations and Bias

- **Genre and mood are all-or-nothing:** A song that is a near-perfect energy and acoustic match but belongs to the wrong genre is capped at 4.5 out of 10. This means the top results are almost always dominated by genre, even when a cross-genre song might genuinely suit the listener.
- **Sparse genres:** Several genres (synthwave, reggae, r&b, country, blues, classical) have only one song each. A user who prefers those genres will always see that one song ranked first, with little variety below it.
- **No listening history:** The system treats every session identically. It cannot learn that a user skipped the recommended songs or played one on repeat.
- **Four preferences cannot capture real taste:** Real listeners have complex, context-dependent preferences. The same person might want high-energy metal while commuting but quiet jazz while cooking — this system has no context awareness.
- **Acousticness as an electronic proxy:** Using acousticness as a stand-in for "electronic vs. organic" is a rough approximation. A heavily produced acoustic ballad and an ambient synth track could score identically on this feature.
- **Catalog bias:** The 18 songs reflect a limited, culturally narrow sample. Users whose tastes fall outside Western pop, rock, and lofi traditions will receive poor recommendations regardless of how well the scoring logic works.

---

## 7. Evaluation

The recommender was tested against five distinct user profiles:

- **Chill Lofi Studier** — The system correctly ranked "Focus Flow" and "Library Rain" in the top two slots. Both are lofi/focused with energy near 0.40, exactly matching the profile.
- **High-Energy Pop** — "Gym Hero" ranked first. Expected, since it is the only pop/intense song with energy 0.93.
- **Deep Intense Rock** — "Storm Runner" ranked first, with metal song "Shatter the Crown" second despite being a genre mismatch, because its energy (0.95) is extremely close to the target.
- **Ghost Combo (country + angry)** — No song matched on genre or mood, so the entire ranking was decided by energy and acousticness alone. The top result was a synthwave song with similar energy — a reasonable but unexpected pick that highlighted how the numerical rules still produce a coherent (if arbitrary) ranking.
- **Contradiction (acoustic + high energy)** — The system picked a compromise: no song scored perfectly, and the top result balanced the two conflicting signals rather than fully satisfying either. This was the most revealing test — it showed that the scoring rules compete rather than cooperate when preferences conflict.

Six automated tests also verify that exact score values and ranking order match hand-calculated expectations for the pop/happy profile.

---

## 8. Future Work

- **Partial genre/mood credit:** Instead of a hard binary, similar genres (e.g., "lofi" and "ambient") could earn partial points. This would reduce the winner-takes-all dominance of the genre rule.
- **Expand the catalog:** A larger, more diverse dataset would make recommendations less predictable and more genuinely useful across different taste profiles.
- **Add valence and danceability to the user profile:** These features are already tracked per song but are ignored during scoring because the user profile has no corresponding preference fields. Adding `target_valence` and `target_danceability` would make the scoring more expressive.
- **Diversity enforcement:** The current system can return five nearly identical songs if a genre has enough entries. A diversity penalty (e.g., no more than two songs from the same artist) would improve the variety of results.
- **Context awareness:** Allow the user to specify a context (workout, study, sleep) that automatically adjusts the weights — for example, boosting energy weight during a workout profile.

---

## 9. Personal Reflection

Building this system made it clear how much of a recommender's behavior is determined before a single user interaction happens — by the choice of features, the weights assigned to them, and the composition of the catalog. The scoring rules feel neutral and mathematical, but every design decision embeds an assumption about what makes a good recommendation. Weighting genre at 30% is not a fact; it is a judgment call.

The edge case testing was the most instructive part. Profiles with conflicting preferences (high energy + acoustic) or missing catalog coverage (country + angry) revealed that the system does not fail gracefully — it just picks whatever song loses least. That behavior is invisible to a user who only sees a ranked list of titles. It is a reminder that real recommendation systems can appear confident while actually operating far outside the conditions they were designed for.
