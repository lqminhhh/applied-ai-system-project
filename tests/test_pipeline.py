from src.music_assistant.config import Settings
from src.music_assistant.llm.gemini_client import GeminiClient
from src.music_assistant.pipeline import parse_query_to_profile, run_recommendation_pipeline


def make_test_settings() -> Settings:
    return Settings(gemini_api_key=None)


def test_parse_query_to_profile_uses_fallback_when_key_missing():
    result = parse_query_to_profile("Need calm acoustic study music", GeminiClient(make_test_settings()))
    assert result.source == "heuristic"
    assert 0.0 <= result.profile.target_energy <= 1.0


def test_pipeline_returns_recommendations_and_narrative():
    result = run_recommendation_pipeline(
        "I need music for deep focus while coding.",
        settings=make_test_settings(),
        client=GeminiClient(make_test_settings()),
    )
    assert result.recommendations
    assert result.narrative.summary


def test_pipeline_handles_empty_query():
    result = run_recommendation_pipeline(
        "",
        settings=make_test_settings(),
        client=GeminiClient(make_test_settings()),
    )
    assert result.parsed_profile.source == "heuristic"
    assert any("fallback" in warning.lower() or "empty query" in warning.lower() for warning in result.warnings)


def test_pipeline_warns_on_catalog_limits():
    result = run_recommendation_pipeline(
        "Give me angry country breakup songs with high energy and acoustic guitar.",
        settings=make_test_settings(),
        client=GeminiClient(make_test_settings()),
    )
    assert result.warnings
