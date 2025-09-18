"""Configuration for simple RAG app."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class GeminiCfg:
    api_key: str
    text_model: str = os.getenv("GEMINI_TEXT_MODEL", "models/gemini-2.5-flash")
    embedding_model: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
    temperature: float = float(os.getenv("TEMPERATURE", "0.4"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1536"))


@dataclass
class BlueskyCfg:
    handle: str
    app_password: str
    service: str = os.getenv("BLUESKY_SERVICE", "https://bsky.social")


@dataclass
class ChromaCfg:
    db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma_db_simple")
    collection: str = os.getenv("COLLECTION_NAME", "bluesky_posts_simple")


@dataclass
class RAGCfg:
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "400"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "40"))
    max_results: int = int(os.getenv("MAX_RESULTS", "12"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))
    recent_days: int = int(os.getenv("RECENT_DAYS", "14"))


@dataclass
class AppCfg:
    gemini: GeminiCfg
    bluesky: BlueskyCfg
    chroma: ChromaCfg
    rag: RAGCfg


def get_cfg() -> AppCfg:
    api_key = os.getenv("GEMINI_API_KEY")
    handle = os.getenv("BLUESKY_USERNAME")
    app_password = os.getenv("BLUESKY_PASSWORD")
    if not api_key or not handle or not app_password:
        missing = [name for name, val in [
            ("GEMINI_API_KEY", api_key),
            ("BLUESKY_USERNAME", handle),
            ("BLUESKY_PASSWORD", app_password),
        ] if not val]
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    return AppCfg(
        gemini=GeminiCfg(api_key=api_key),
        bluesky=BlueskyCfg(handle=handle, app_password=app_password),
        chroma=ChromaCfg(),
        rag=RAGCfg(),
    )
