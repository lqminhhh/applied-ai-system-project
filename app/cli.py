from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.music_assistant.pipeline import run_recommendation_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Playlist Assistant CLI")
    parser.add_argument("query", nargs="+", help="Natural-language music request")
    args = parser.parse_args()

    query = " ".join(args.query)
    result = run_recommendation_pipeline(query)

    print(f"Query: {result.query}")
    print(f"Intent: {result.parsed_profile.intent_summary}")
    print(f"Profile: {result.parsed_profile.profile}")
    print(f"Parser source: {result.parsed_profile.source}")

    print("\nRetrieved candidates:")
    for song in result.retrieved_songs:
        print(f"- {song.title} — {song.artist} [{song.genre} / {song.mood}]")

    print("\nTop recommendations:")
    for index, item in enumerate(result.recommendations, start=1):
        print(f"{index}. {item.song.title} — {item.song.artist} ({item.score:.2f}/10)")
        for reason in item.breakdown.reasons:
            print(f"   - {reason}")

    print("\nNarrative:")
    print(result.narrative.summary)
    for reason in result.narrative.per_song_reasons:
        print(f"- {reason}")

    if result.narrative.caveat:
        print(f"\nCaveat: {result.narrative.caveat}")
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
