from __future__ import annotations

import json

from src.music_assistant.models import ParsedProfileResult, ScoredRecommendation, Song


ALLOWED_GENRES = [
    "ambient",
    "blues",
    "classical",
    "country",
    "electronic",
    "hip-hop",
    "indie pop",
    "jazz",
    "lofi",
    "metal",
    "pop",
    "r&b",
    "reggae",
    "rock",
    "synthwave",
]

ALLOWED_MOODS = [
    "angry",
    "chill",
    "confident",
    "dreamy",
    "focused",
    "happy",
    "intense",
    "melancholic",
    "moody",
    "nostalgic",
    "peaceful",
    "relaxed",
    "romantic",
    "uplifting",
]


def build_profile_parser_prompt(query: str) -> str:
    schema = {
        "favorite_genre": "one of allowed genres",
        "favorite_mood": "one of allowed moods",
        "target_energy": "float between 0.0 and 1.0",
        "likes_acoustic": "boolean",
        "intent_summary": "short natural language summary",
        "confidence": "float between 0.0 and 1.0",
        "warnings": ["optional list of caveats"],
    }
    return (
        "You are extracting structured music preferences from a user query.\n"
        "Return JSON only.\n"
        f"Allowed genres: {', '.join(ALLOWED_GENRES)}.\n"
        f"Allowed moods: {', '.join(ALLOWED_MOODS)}.\n"
        f"JSON schema: {json.dumps(schema)}.\n"
        "If the user is vague, make the safest reasonable choice and lower confidence.\n"
        f"User query: {query}"
    )


def build_explanation_prompt(
    query: str,
    parsed: ParsedProfileResult,
    retrieved_songs: list[Song],
    recommendations: list[ScoredRecommendation],
) -> str:
    retrieved_blob = [
        {
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
        }
        for song in retrieved_songs
    ]
    ranked_blob = [
        {
            "title": item.song.title,
            "artist": item.song.artist,
            "score": item.score,
            "genre": item.song.genre,
            "mood": item.song.mood,
            "energy": item.song.energy,
            "acousticness": item.song.acousticness,
        }
        for item in recommendations
    ]
    return (
        "You are explaining music recommendations.\n"
        "Use only the retrieved songs and recommendation data provided.\n"
        "Do not invent songs, artists, genres, moods, or audio features.\n"
        "Return JSON only with keys: summary, per_song_reasons, caveat.\n"
        f"User query: {query}\n"
        f"Parsed profile: {json.dumps(parsed.profile.__dict__)}\n"
        f"Intent summary: {parsed.intent_summary}\n"
        f"Retrieved songs: {json.dumps(retrieved_blob)}\n"
        f"Recommendations: {json.dumps(ranked_blob)}"
    )
