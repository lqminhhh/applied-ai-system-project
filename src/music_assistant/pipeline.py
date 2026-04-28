from __future__ import annotations

import re
from dataclasses import asdict

from src.music_assistant.catalog import load_catalog
from src.music_assistant.config import Settings, get_settings
from src.music_assistant.explanation import generate_grounded_explanation
from src.music_assistant.llm.gemini_client import GeminiClient, GeminiClientError
from src.music_assistant.llm.prompts import ALLOWED_GENRES, ALLOWED_MOODS, build_profile_parser_prompt
from src.music_assistant.logging_utils import configure_logging
from src.music_assistant.models import ParsedProfileResult, PipelineResult, UserProfile
from src.music_assistant.ranking import rank_songs
from src.music_assistant.retrieval import retrieve_candidate_songs

LOGGER = configure_logging()


GENRE_KEYWORDS = {
    "ambient": {"ambient"},
    "blues": {"blues"},
    "classical": {"classical", "piano", "orchestral"},
    "country": {"country", "americana", "folk"},
    "electronic": {"electronic", "edm"},
    "hip-hop": {"hip-hop", "hiphop", "rap"},
    "indie pop": {"indie", "indie pop"},
    "jazz": {"jazz"},
    "lofi": {"lofi", "lo-fi"},
    "metal": {"metal"},
    "pop": {"pop"},
    "r&b": {"r&b", "rnb", "soul"},
    "reggae": {"reggae"},
    "rock": {"rock"},
    "synthwave": {"synthwave", "retro"},
}

MOOD_KEYWORDS = {
    "angry": {"angry", "rage"},
    "chill": {"chill", "calm", "laid-back"},
    "confident": {"confident", "bold"},
    "dreamy": {"dreamy", "floaty"},
    "focused": {"focus", "focused", "study", "coding", "deep work"},
    "happy": {"happy", "cheerful"},
    "intense": {"intense", "energetic", "workout", "gym", "hype"},
    "melancholic": {"melancholic", "sad"},
    "moody": {"moody", "night drive"},
    "nostalgic": {"nostalgic", "throwback"},
    "peaceful": {"peaceful", "quiet"},
    "relaxed": {"relaxed", "coffee", "easy"},
    "romantic": {"romantic", "date"},
    "uplifting": {"uplifting", "inspiring"},
}


def _normalize_choice(value: str, allowed: list[str], default: str) -> str:
    lowered = value.strip().lower()
    return lowered if lowered in allowed else default


def _heuristic_profile_from_query(query: str) -> ParsedProfileResult:
    lowered = query.lower()

    favorite_genre = "lofi"
    for genre, keywords in GENRE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            favorite_genre = genre
            break

    favorite_mood = "chill"
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            favorite_mood = mood
            break

    target_energy = 0.45
    if re.search(r"\b(workout|gym|run|hype|intense|party)\b", lowered):
        target_energy = 0.85
    elif re.search(r"\b(study|focus|coding|quiet|sleep|calm)\b", lowered):
        target_energy = 0.35
    elif re.search(r"\b(morning|coffee|easy|relaxed)\b", lowered):
        target_energy = 0.48

    likes_acoustic = not bool(re.search(r"\b(edm|electronic|synth|club)\b", lowered))
    summary = query.strip() if query.strip() else "A general low-pressure listening session"

    return ParsedProfileResult(
        profile=UserProfile(
            favorite_genre=favorite_genre,
            favorite_mood=favorite_mood,
            target_energy=target_energy,
            likes_acoustic=likes_acoustic,
        ),
        intent_summary=summary,
        confidence=0.45 if query.strip() else 0.2,
        source="heuristic",
        warnings=["Used deterministic fallback parsing."],
    )


def _validate_profile_payload(payload: dict) -> ParsedProfileResult:
    profile = UserProfile(
        favorite_genre=_normalize_choice(payload.get("favorite_genre", ""), ALLOWED_GENRES, "lofi"),
        favorite_mood=_normalize_choice(payload.get("favorite_mood", ""), ALLOWED_MOODS, "chill"),
        target_energy=min(1.0, max(0.0, float(payload.get("target_energy", 0.45)))),
        likes_acoustic=bool(payload.get("likes_acoustic", True)),
    )
    warnings = payload.get("warnings") or []
    if not isinstance(warnings, list):
        warnings = [str(warnings)]
    return ParsedProfileResult(
        profile=profile,
        intent_summary=str(payload.get("intent_summary", "Music matched to the user's request")).strip(),
        confidence=min(1.0, max(0.0, float(payload.get("confidence", 0.6)))),
        source="gemini",
        raw_response=payload,
        warnings=[str(item) for item in warnings],
    )


def parse_query_to_profile(query: str, client: GeminiClient) -> ParsedProfileResult:
    if not query.strip():
        fallback = _heuristic_profile_from_query(query)
        return ParsedProfileResult(
            profile=fallback.profile,
            intent_summary="A general low-pressure listening session",
            confidence=0.2,
            source="heuristic",
            warnings=["Empty query received; using fallback profile."],
        )

    if not client.is_enabled():
        return _heuristic_profile_from_query(query)

    try:
        payload = client.generate_json(build_profile_parser_prompt(query))
        return _validate_profile_payload(payload)
    except (GeminiClientError, ValueError, TypeError):
        return _heuristic_profile_from_query(query)


def _build_catalog_caveat(recommendations: list, parsed: ParsedProfileResult) -> str | None:
    if not recommendations:
        return "The catalog is too small to produce a reliable recommendation."
    top_score = recommendations[0].score
    if top_score < 6.0:
        return (
            "The catalog has limited coverage for this request, so these are the closest "
            "available matches rather than strong matches."
        )
    if parsed.confidence < 0.4:
        return "The request was vague, so the profile was inferred with low confidence."
    return None


def run_recommendation_pipeline(
    query: str,
    k: int | None = None,
    settings: Settings | None = None,
    client: GeminiClient | None = None,
) -> PipelineResult:
    settings = settings or get_settings()
    client = client or GeminiClient(settings)
    songs = load_catalog(settings.catalog_path)

    parsed = parse_query_to_profile(query, client)
    retrieved = retrieve_candidate_songs(
        query=query,
        songs=songs,
        limit=settings.retrieval_limit,
        profile=parsed.profile,
    )
    recommendations = rank_songs(parsed.profile, retrieved, k=k or settings.recommendation_count)
    caveat = _build_catalog_caveat(recommendations, parsed)
    narrative = generate_grounded_explanation(
        query=query,
        parsed=parsed,
        retrieved_songs=retrieved,
        recommendations=recommendations,
        client=client,
        caveat=caveat,
    )

    warnings = list(parsed.warnings)
    if narrative.source == "fallback" and client.is_enabled():
        warnings.append("LLM explanation failed; used fallback explanation.")
    if caveat:
        warnings.append(caveat)

    LOGGER.info("query=%s", query)
    LOGGER.info("parsed_profile=%s", asdict(parsed.profile))
    LOGGER.info("retrieved_titles=%s", [song.title for song in retrieved])
    LOGGER.info(
        "recommendations=%s",
        [{"title": item.song.title, "score": item.score} for item in recommendations],
    )

    return PipelineResult(
        query=query,
        parsed_profile=parsed,
        retrieved_songs=retrieved,
        recommendations=recommendations,
        narrative=narrative,
        warnings=warnings,
    )
