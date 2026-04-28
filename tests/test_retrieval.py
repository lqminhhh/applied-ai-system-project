from src.music_assistant.catalog import load_catalog
from src.music_assistant.models import UserProfile
from src.music_assistant.retrieval import retrieve_candidate_songs


def test_load_catalog_returns_song_objects():
    songs = load_catalog("data/songs.csv")
    assert len(songs) == 18
    assert songs[0].title == "Sunrise City"


def test_retrieval_finds_focus_music():
    songs = load_catalog("data/songs.csv")
    profile = UserProfile("lofi", "focused", 0.4, True)
    results = retrieve_candidate_songs("study focus coding music", songs, limit=5, profile=profile)
    titles = [song.title for song in results]
    assert "Focus Flow" in titles


def test_retrieval_finds_workout_music():
    songs = load_catalog("data/songs.csv")
    profile = UserProfile("pop", "intense", 0.9, False)
    results = retrieve_candidate_songs("workout gym hype playlist", songs, limit=5, profile=profile)
    titles = [song.title for song in results]
    assert "Gym Hero" in titles


def test_retrieval_finds_quiet_morning_music():
    songs = load_catalog("data/songs.csv")
    profile = UserProfile("jazz", "relaxed", 0.35, True)
    results = retrieve_candidate_songs("quiet Sunday morning coffee", songs, limit=5, profile=profile)
    titles = [song.title for song in results]
    assert "Coffee Shop Stories" in titles
