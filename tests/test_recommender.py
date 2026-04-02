from src.recommender import Song, UserProfile, Recommender, score_song
from dataclasses import asdict

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


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Score tests for pop/happy profile ---

def make_pop_happy_user():
    return UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )

def test_perfect_match_scores_9_6():
    """Pop/happy song with matching energy and low acousticness should score 9.6."""
    user = make_pop_happy_user()
    pop_song = Song(id=1, title="Test Pop Track", artist="Test Artist",
                    genre="pop", mood="happy", energy=0.8,
                    tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2)
    score, _ = score_song(asdict(user), asdict(pop_song))
    assert score == 9.6

def test_genre_mood_mismatch_scores_low():
    """Lofi/chill song should score much lower than the pop/happy match."""
    user = make_pop_happy_user()
    lofi_song = Song(id=2, title="Chill Lofi Loop", artist="Test Artist",
                     genre="lofi", mood="chill", energy=0.4,
                     tempo_bpm=80, valence=0.6, danceability=0.5, acousticness=0.9)
    score, _ = score_song(asdict(user), asdict(lofi_song))
    assert score == 1.7

def test_pop_song_ranks_above_lofi():
    """Pop/happy song must be ranked #1 over lofi/chill for a pop/happy user."""
    user = make_pop_happy_user()
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)
    assert results[0].genre == "pop"
    assert results[1].genre == "lofi"

def test_score_reasons_include_genre_and_mood():
    """Reasons list must mention both genre and mood outcomes."""
    user = make_pop_happy_user()
    pop_song = Song(id=1, title="Test Pop Track", artist="Test Artist",
                    genre="pop", mood="happy", energy=0.8,
                    tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2)
    _, reasons = score_song(asdict(user), asdict(pop_song))
    joined = " ".join(reasons)
    assert "genre match" in joined
    assert "mood match" in joined
