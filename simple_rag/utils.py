"""Utilities, models, and text helpers for simple Bluesky RAG."""

from __future__ import annotations

import re
import html
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Iterable

from loguru import logger


@dataclass
class Post:
    uri: str
    cid: str
    author: str
    author_display_name: str
    text: str
    created_at: datetime
    reply_count: int = 0
    repost_count: int = 0
    like_count: int = 0


@dataclass
class Chunk:
    text: str
    post: Post
    index: int
    total: int


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +\n", "\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 40) -> List[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


STOP_WORDS = set(
    """
    what how why when where who which is are was were do does did will would could should the a an and or but in on at to for of with by about people saying talking discussing latest trending trends news update updates tell me me about
    """.split()
)


def extract_keywords(query: str, max_terms: int = 6) -> List[str]:
    words = re.findall(r"#\w+|@\w+|\w+", query.lower())
    terms: List[str] = []
    for w in words:
        if w.startswith(("#", "@")):
            terms.append(w)
        elif len(w) > 2 and w not in STOP_WORDS:
            terms.append(w)
    # keep unique order
    seen = set()
    uniq: List[str] = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq[:max_terms]


def format_doc_for_prompt(i: int, chunk: Chunk) -> str:
    p = chunk.post
    meta = f"Post #{i} by @{p.author} ({p.author_display_name}) on {p.created_at.isoformat()}\n\"{chunk.text}\"\n"
    return meta


def bsky_uri_to_web(uri: str) -> str:
    # Convert at://did:plc:.../app.bsky.feed.post/xyz to https://bsky.app/profile/did:plc:.../post/xyz
    try:
        if uri.startswith("at://"):
            parts = uri.replace("at://", "").split("/")
            did = parts[0]
            if len(parts) >= 3 and parts[1] == "app.bsky.feed.post":
                rkey = parts[2]
                return f"https://bsky.app/profile/{did}/post/{rkey}"
        return uri
    except Exception:
        return uri
