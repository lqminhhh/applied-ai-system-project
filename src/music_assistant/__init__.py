"""Music Assistant package."""

from src.music_assistant.catalog import load_catalog
from src.music_assistant.models import Song, UserProfile
from src.music_assistant.pipeline import run_recommendation_pipeline
from src.music_assistant.ranking import rank_songs, score_song

__all__ = [
    "Song",
    "UserProfile",
    "load_catalog",
    "score_song",
    "rank_songs",
    "run_recommendation_pipeline",
]
