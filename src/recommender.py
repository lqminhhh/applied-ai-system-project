import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = asdict(user)
        scored = sorted(
            self.songs,
            key=lambda song: score_song(user_prefs, asdict(song))[0],
            reverse=True,
        )
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(asdict(user), asdict(song))
        return " | ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Returns a (score, reasons) tuple where score is 0.0–10.0
    and reasons is a list of human-readable scoring explanations.

    Scoring breakdown (max 10.0):
      Genre match      → +3.0 (hard match)
      Mood match       → +2.5 (hard match)
      Energy proximity → 0–2.5 (linear: closer = higher)
      Acoustic fit     → 0–2.0 (continuous: prefers acoustic or not)
    """
    score = 0.0
    reasons = []

    # Rule 1 — Genre match (+3.0)
    if song["genre"] == user_prefs["favorite_genre"]:
        score += 3.0
        reasons.append(f"genre match (+3.0)")
    else:
        reasons.append(f"genre mismatch: {song['genre']} vs {user_prefs['favorite_genre']} (+0.0)")

    # Rule 2 — Mood match (+2.5)
    if song["mood"] == user_prefs["favorite_mood"]:
        score += 2.5
        reasons.append(f"mood match (+2.5)")
    else:
        reasons.append(f"mood mismatch: {song['mood']} vs {user_prefs['favorite_mood']} (+0.0)")

    # Rule 3 — Energy proximity (0–2.5)
    energy_diff = abs(song["energy"] - user_prefs["target_energy"])
    energy_points = round((1.0 - energy_diff) * 2.5, 2)
    score += energy_points
    reasons.append(f"energy proximity: |{song['energy']} - {user_prefs['target_energy']}| = {energy_diff:.2f} (+{energy_points})")

    # Rule 4 — Acoustic preference (0–2.0)
    if user_prefs["likes_acoustic"]:
        acoustic_points = round(song["acousticness"] * 2.0, 2)
        reasons.append(f"acoustic fit: acousticness {song['acousticness']} (+{acoustic_points})")
    else:
        acoustic_points = round((1.0 - song["acousticness"]) * 2.0, 2)
        reasons.append(f"electronic fit: 1 - acousticness {song['acousticness']} (+{acoustic_points})")
    score += acoustic_points

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    Returns the top k songs as (song_dict, score, explanation) tuples,
    sorted from highest to lowest score.
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]
