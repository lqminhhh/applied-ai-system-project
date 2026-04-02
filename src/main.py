"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood":  "intense",
        "target_energy":  0.90,
        "likes_acoustic": False,
    },
    "Chill Lofi Studier": {
        "favorite_genre": "lofi",
        "favorite_mood":  "focused",
        "target_energy":  0.40,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood":  "intense",
        "target_energy":  0.92,
        "likes_acoustic": False,
    },
    "Sunday Morning Jazz": {
        "favorite_genre": "jazz",
        "favorite_mood":  "relaxed",
        "target_energy":  0.35,
        "likes_acoustic": True,
    },
}


def print_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 52)
    print(f"  Profile : {profile_name}")
    print("=" * 52)
    print(f"  Genre: {user_prefs['favorite_genre']}  |  Mood: {user_prefs['favorite_mood']}")
    print(f"  Energy: {user_prefs['target_energy']}  |  Acoustic: {user_prefs['likes_acoustic']}")
    print("=" * 52)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  —  {song['artist']}")
        print(f"    Score : {score:.2f} / 10.00")
        print(f"    Genre : {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        print("    Reasons:")
        for reason in explanation.split(" | "):
            print(f"      • {reason}")

    print("\n" + "=" * 52)


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile_name, user_prefs in PROFILES.items():
        print_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()
