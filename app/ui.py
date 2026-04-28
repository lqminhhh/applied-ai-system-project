from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.music_assistant.pipeline import run_recommendation_pipeline

st.set_page_config(page_title="AI Playlist Assistant", page_icon="🎧", layout="wide")

st.title("AI Playlist Assistant")
st.write(
    "Describe the listening vibe you want, and the app will parse your request, retrieve "
    "candidate songs, rank them with the rule-based recommender, and explain the picks."
)

default_query = "I need calm, acoustic music for a quiet Sunday morning coffee."
query = st.text_area("What kind of music are you looking for?", value=default_query, height=120)
run = st.button("Generate Playlist")

if run:
    with st.spinner("Building your playlist..."):
        result = run_recommendation_pipeline(query)

    profile = result.parsed_profile.profile
    st.subheader("Parsed Preferences")
    left, right = st.columns(2)
    left.metric("Genre", profile.favorite_genre)
    left.metric("Mood", profile.favorite_mood)
    right.metric("Energy", f"{profile.target_energy:.2f}")
    right.metric("Acoustic", "Yes" if profile.likes_acoustic else "No")
    st.caption(
        f"Intent summary: {result.parsed_profile.intent_summary} "
        f"({result.parsed_profile.source}, confidence {result.parsed_profile.confidence:.2f})"
    )

    st.subheader("Top Recommendations")
    for item in result.recommendations:
        with st.container(border=True):
            st.markdown(f"**{item.song.title}** by {item.song.artist}")
            st.write(
                f"{item.song.genre} | {item.song.mood} | energy {item.song.energy:.2f} | "
                f"acousticness {item.song.acousticness:.2f}"
            )
            st.write(f"Final score: {item.score:.2f} / 10")
            st.write("Reasons:")
            for reason in item.breakdown.reasons:
                st.write(f"- {reason}")

    st.subheader("Grounded Explanation")
    st.write(result.narrative.summary)
    for reason in result.narrative.per_song_reasons:
        st.write(f"- {reason}")

    if result.narrative.caveat:
        st.warning(result.narrative.caveat)
    if result.warnings:
        for warning in result.warnings:
            st.info(warning)

    with st.expander("Debug View"):
        st.write("Retrieved candidates:")
        for song in result.retrieved_songs:
            st.write(f"- {song.title} — {song.artist} [{song.genre}/{song.mood}]")
