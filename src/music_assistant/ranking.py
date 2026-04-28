from __future__ import annotations

from dataclasses import asdict

from src.music_assistant.models import ScoreBreakdown, ScoredRecommendation, Song, UserProfile


class Recommender:
    """Compatibility wrapper around the ranking functions."""

    def __init__(self, songs: list[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> list[Song]:
        return [recommendation.song for recommendation in rank_songs(user, self.songs, k=k)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, breakdown = score_song(asdict(user), asdict(song))
        return " | ".join(breakdown.reasons)


def score_song(user_prefs: dict, song: dict) -> tuple[float, ScoreBreakdown]:
    score = 0.0
    reasons: list[str] = []

    if song["genre"] == user_prefs["favorite_genre"]:
        genre_points = 3.0
        reasons.append("genre match (+3.0)")
    else:
        genre_points = 0.0
        reasons.append(
            f"genre mismatch: {song['genre']} vs {user_prefs['favorite_genre']} (+0.0)"
        )
    score += genre_points

    if song["mood"] == user_prefs["favorite_mood"]:
        mood_points = 2.5
        reasons.append("mood match (+2.5)")
    else:
        mood_points = 0.0
        reasons.append(
            f"mood mismatch: {song['mood']} vs {user_prefs['favorite_mood']} (+0.0)"
        )
    score += mood_points

    energy_diff = abs(song["energy"] - user_prefs["target_energy"])
    energy_points = round((1.0 - energy_diff) * 2.5, 2)
    score += energy_points
    reasons.append(
        f"energy proximity: |{song['energy']} - {user_prefs['target_energy']}| = "
        f"{energy_diff:.2f} (+{energy_points})"
    )

    if user_prefs["likes_acoustic"]:
        acoustic_points = round(song["acousticness"] * 2.0, 2)
        reasons.append(f"acoustic fit: acousticness {song['acousticness']} (+{acoustic_points})")
    else:
        acoustic_points = round((1.0 - song["acousticness"]) * 2.0, 2)
        reasons.append(
            f"electronic fit: 1 - acousticness {song['acousticness']} (+{acoustic_points})"
        )
    score += acoustic_points

    return round(score, 2), ScoreBreakdown(
        genre_points=genre_points,
        mood_points=mood_points,
        energy_points=energy_points,
        acoustic_points=acoustic_points,
        reasons=reasons,
    )


def rank_songs(user: UserProfile, songs: list[Song], k: int = 5) -> list[ScoredRecommendation]:
    user_prefs = asdict(user)
    scored: list[ScoredRecommendation] = []
    for song in songs:
        score, breakdown = score_song(user_prefs, asdict(song))
        scored.append(ScoredRecommendation(song=song, score=score, breakdown=breakdown))
    return sorted(scored, key=lambda item: item.score, reverse=True)[:k]
