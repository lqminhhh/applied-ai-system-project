from __future__ import annotations

from src.music_assistant.llm.gemini_client import GeminiClient, GeminiClientError
from src.music_assistant.llm.prompts import build_explanation_prompt
from src.music_assistant.models import (
    ParsedProfileResult,
    RecommendationNarrative,
    ScoredRecommendation,
    Song,
)


def build_fallback_narrative(
    query: str,
    parsed: ParsedProfileResult,
    recommendations: list[ScoredRecommendation],
    caveat: str | None = None,
) -> RecommendationNarrative:
    if recommendations:
        top = recommendations[0].song
        summary = (
            f"For '{query}', I prioritized {parsed.intent_summary.lower()} and ranked songs by "
            f"genre, mood, energy, and acoustic fit. {top.title} is the closest overall match."
        )
        per_song_reasons = [
            (
                f"{item.song.title} fits because it combines {item.song.genre} / {item.song.mood} "
                f"traits with an energy score of {item.song.energy:.2f} and a final score of "
                f"{item.score:.2f}/10."
            )
            for item in recommendations
        ]
    else:
        summary = "No recommendations were produced."
        per_song_reasons = []

    return RecommendationNarrative(
        summary=summary,
        per_song_reasons=per_song_reasons,
        caveat=caveat,
        source="fallback",
        raw_response=None,
    )


def generate_grounded_explanation(
    query: str,
    parsed: ParsedProfileResult,
    retrieved_songs: list[Song],
    recommendations: list[ScoredRecommendation],
    client: GeminiClient,
    caveat: str | None = None,
) -> RecommendationNarrative:
    if not client.is_enabled():
        return build_fallback_narrative(query, parsed, recommendations, caveat=caveat)

    prompt = build_explanation_prompt(query, parsed, retrieved_songs, recommendations)
    try:
        payload = client.generate_json(prompt)
        per_song_reasons = payload.get("per_song_reasons") or []
        if not isinstance(per_song_reasons, list):
            per_song_reasons = []
        return RecommendationNarrative(
            summary=str(payload.get("summary", "")).strip(),
            per_song_reasons=[str(item) for item in per_song_reasons],
            caveat=str(payload.get("caveat")).strip() if payload.get("caveat") else caveat,
            source="gemini",
            raw_response=payload,
        )
    except GeminiClientError:
        return build_fallback_narrative(query, parsed, recommendations, caveat=caveat)
