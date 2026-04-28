from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    catalog_path: Path = Path("data/songs.csv")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_base_url: str = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
    )
    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
    retrieval_limit: int = int(os.getenv("RETRIEVAL_LIMIT", "8"))
    recommendation_count: int = int(os.getenv("RECOMMENDATION_COUNT", "5"))


def get_settings() -> Settings:
    return Settings()
