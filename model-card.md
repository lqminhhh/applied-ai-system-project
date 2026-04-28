# Model Card: AI Playlist Assistant

## Model Name

**AI Playlist Assistant**

## Intended Use

AI Playlist Assistant helps a user describe a listening vibe in natural language and receive a small playlist with grounded explanations. It is designed as a portfolio and classroom project to demonstrate how retrieval, rule-based ranking, and LLM-powered explanations can work together inside a real application.

This system is not intended for production music streaming, large-scale personalization, or sensitive decision-making. It works on a very small fixed catalog and does not learn from user behavior over time.

## System Overview

The system combines three main components:

- a Gemini-based parser that converts a natural-language request into a structured music preference profile
- a retrieval layer that narrows the song catalog to likely candidates
- a deterministic ranking layer that scores songs by genre, mood, energy, and acoustic fit

After ranking, Gemini generates a grounded explanation using only the retrieved songs and final recommendations. If Gemini is unavailable, the app falls back to heuristic parsing and explanation logic.

## Data

The catalog is stored in `data/songs.csv` and contains 18 songs with fields such as:

- title
- artist
- genre
- mood
- energy
- tempo
- valence
- danceability
- acousticness

Because the catalog is small and hand-curated, it reflects a narrow view of music taste and does not represent the diversity of real-world listeners.

## Limitations and Biases

The biggest limitation is the dataset itself. With only 18 songs, many requests cannot be satisfied directly, so the system often returns the "closest available match" rather than a truly strong recommendation. This becomes especially noticeable for genres, moods, and cultural traditions that are missing from the catalog.

There is also bias in the ranking logic. Genre and mood are treated as exact matches, which means songs that are close in feeling but labeled differently can be unfairly penalized. The system also assumes that a user can be described by a small fixed profile, even though real music taste is contextual, fluid, and often contradictory.

On the LLM side, Gemini can misread vague prompts or over-interpret short requests. I reduced that risk with validation, grounded explanations, and fallbacks, but the model can still introduce noise in how it summarizes intent.

## Misuse Risk and Mitigation

This app is low-risk compared with systems used in finance, hiring, or health, but it could still be misused if someone treated its output as authoritative or highly personalized. A user might assume the system truly "understands" them when it is really making decisions from a tiny catalog and a simplified profile.

To reduce misuse, the app includes several guardrails:

- it warns when the catalog is limited for a given request
- it falls back safely if the model is unavailable
- it grounds explanations in retrieved songs only
- it keeps the final ranking deterministic and inspectable

If I were extending this project further, I would add clearer confidence messaging in the UI and a more explicit note that the recommendations are demonstrative rather than deeply personalized.

## Reliability Reflection

The most surprising part of testing was how often the deterministic system looked "reasonable" even when the request was not well-covered by the catalog. For example, a prompt with conflicting or underspecified preferences still produced a neat ranked list, which could make the system appear more confident than it should be.

Another important reliability lesson was that fallback paths matter just as much as the ideal AI path. The app became much stronger once it could still parse queries, rank songs, and explain results even when the Gemini API key was missing or the model response was unusable.

## Collaboration With AI

AI was helpful during both the design and implementation process. One especially useful suggestion was the recommendation to keep the ranking engine deterministic while using the LLM only for natural-language parsing and grounded explanations. That split made the system more testable and gave the project a clearer architecture.

One flawed suggestion appeared earlier in the build process around packaging and entrypoint behavior. A first-pass structure looked clean on paper, but it did not fully account for how `python app/cli.py` resolves imports from the project root. That had to be corrected by explicitly bootstrapping the project path in the CLI and UI entrypoints. The experience was a good reminder that AI suggestions can be strong at architectural direction while still missing practical environment details.

## What This Project Taught Me

This project reinforced that responsible AI design is not just about adding a model API. It is about deciding where AI adds value, where deterministic logic should remain in control, and how to communicate limitations honestly.

It also taught me that transparency is a design choice. A system can sound convincing even when its evidence is weak, so building in warnings, testing, and grounded explanations is part of making AI useful in a responsible way.
