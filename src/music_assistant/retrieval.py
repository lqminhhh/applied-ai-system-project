from __future__ import annotations

import re

from src.music_assistant.models import Song, UserProfile

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "i",
    "im",
    "is",
    "it",
    "me",
    "music",
    "need",
    "of",
    "playlist",
    "please",
    "something",
    "songs",
    "that",
    "the",
    "to",
    "want",
    "with",
}


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9']+", text.lower())
        if token and token not in STOPWORDS
    }


def retrieve_candidate_songs(
    query: str,
    songs: list[Song],
    limit: int = 8,
    profile: UserProfile | None = None,
) -> list[Song]:
    query_tokens = _tokenize(query)
    scored: list[tuple[float, Song]] = []

    for song in songs:
        text_tokens = _tokenize(song.to_retrieval_text())
        overlap = len(query_tokens & text_tokens)
        score = float(overlap)

        if profile:
            if song.genre == profile.favorite_genre:
                score += 3.0
            if song.mood == profile.favorite_mood:
                score += 2.0
            score += max(0.0, 1.5 - abs(song.energy - profile.target_energy) * 1.5)
            if profile.likes_acoustic:
                score += song.acousticness
            else:
                score += 1.0 - song.acousticness

        if "study" in query_tokens or "focus" in query_tokens or "coding" in query_tokens:
            if song.mood in {"focused", "chill", "peaceful"}:
                score += 2.0
            if song.energy <= 0.45:
                score += 1.5

        if "workout" in query_tokens or "gym" in query_tokens or "run" in query_tokens:
            if song.energy >= 0.75:
                score += 2.0
            if song.mood in {"intense", "confident", "uplifting"}:
                score += 1.5

        if "coffee" in query_tokens or "morning" in query_tokens:
            if song.mood in {"relaxed", "peaceful", "nostalgic", "chill"}:
                score += 1.5
            if 0.25 <= song.energy <= 0.55:
                score += 1.0

        scored.append((score, song))

    ranked = sorted(scored, key=lambda item: item[0], reverse=True)
    return [song for score, song in ranked[:limit] if score > 0] or songs[:limit]
