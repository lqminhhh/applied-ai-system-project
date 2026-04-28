from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

    def to_retrieval_text(self) -> str:
        return (
            f"{self.title} by {self.artist}. Genre {self.genre}. Mood {self.mood}. "
            f"Energy {self.energy:.2f}. Tempo {self.tempo_bpm:.0f} bpm. "
            f"Valence {self.valence:.2f}. Danceability {self.danceability:.2f}. "
            f"Acousticness {self.acousticness:.2f}."
        )


@dataclass(frozen=True)
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


@dataclass(frozen=True)
class ScoreBreakdown:
    genre_points: float
    mood_points: float
    energy_points: float
    acoustic_points: float
    reasons: list[str]


@dataclass(frozen=True)
class ScoredRecommendation:
    song: Song
    score: float
    breakdown: ScoreBreakdown


@dataclass(frozen=True)
class ParsedProfileResult:
    profile: UserProfile
    intent_summary: str
    confidence: float
    source: str
    raw_response: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecommendationNarrative:
    summary: str
    per_song_reasons: list[str]
    caveat: str | None
    source: str
    raw_response: dict[str, Any] | None = None


@dataclass(frozen=True)
class PipelineResult:
    query: str
    parsed_profile: ParsedProfileResult
    retrieved_songs: list[Song]
    recommendations: list[ScoredRecommendation]
    narrative: RecommendationNarrative
    warnings: list[str]

