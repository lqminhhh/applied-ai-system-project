from dataclasses import asdict

from src.music_assistant.models import Song, UserProfile
from src.music_assistant.ranking import Recommender, rank_songs, score_song


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def make_pop_happy_user() -> UserProfile:
    return UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )


def test_recommend_returns_songs_sorted_by_score():
    rec = make_small_recommender()
    results = rec.recommend(make_pop_happy_user(), k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(make_pop_happy_user(), rec.songs[0])

    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_perfect_match_scores_9_6():
    user = make_pop_happy_user()
    pop_song = Song(
        id=1,
        title="Test Pop Track",
        artist="Test Artist",
        genre="pop",
        mood="happy",
        energy=0.8,
        tempo_bpm=120,
        valence=0.9,
        danceability=0.8,
        acousticness=0.2,
    )
    score, _ = score_song(asdict(user), asdict(pop_song))
    assert score == 9.6


def test_genre_mood_mismatch_scores_low():
    user = make_pop_happy_user()
    lofi_song = Song(
        id=2,
        title="Chill Lofi Loop",
        artist="Test Artist",
        genre="lofi",
        mood="chill",
        energy=0.4,
        tempo_bpm=80,
        valence=0.6,
        danceability=0.5,
        acousticness=0.9,
    )
    score, _ = score_song(asdict(user), asdict(lofi_song))
    assert score == 1.7


def test_rank_songs_preserves_expected_order():
    rec = make_small_recommender()
    ranked = rank_songs(make_pop_happy_user(), rec.songs, k=2)
    assert ranked[0].song.genre == "pop"
    assert ranked[1].song.genre == "lofi"


def test_score_reasons_include_genre_and_mood():
    user = make_pop_happy_user()
    pop_song = Song(
        id=1,
        title="Test Pop Track",
        artist="Test Artist",
        genre="pop",
        mood="happy",
        energy=0.8,
        tempo_bpm=120,
        valence=0.9,
        danceability=0.8,
        acousticness=0.2,
    )
    _, breakdown = score_song(asdict(user), asdict(pop_song))
    joined = " ".join(breakdown.reasons)
    assert "genre match" in joined
    assert "mood match" in joined
