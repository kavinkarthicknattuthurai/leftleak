"""Jetstream firehose ingestion for simple_rag."""

from __future__ import annotations

import asyncio
import json
import time
from typing import List, Optional, Dict

import websockets
from loguru import logger

from .bluesky import BSky
from .config import AppCfg
from .utils import Post, clean_text, extract_keywords


JETSTREAM_URL = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"


class DIDCache:
    def __init__(self, bs: BSky, ttl_sec: int = 3600):
        self.bs = bs
        self.ttl = ttl_sec
        self.cache: Dict[str, Dict[str, str]] = {}
        self.times: Dict[str, float] = {}

    def get(self, did: str) -> Dict[str, str]:
        now = time.time()
        if did in self.cache and now - self.times.get(did, 0) < self.ttl:
            return self.cache[did]
        # Resolve via profile
        try:
            prof = self.bs.client.get_profile(actor=did)
            handle = getattr(prof, 'handle', did)
            display = getattr(prof, 'display_name', handle)
        except Exception:
            handle = did
            display = did
        self.cache[did] = {"handle": handle, "display": display}
        self.times[did] = now
        return self.cache[did]


async def stream_posts(cfg: AppCfg, keywords: Optional[str], max_posts: Optional[int], minutes: Optional[int]) -> List[Post]:
    bs = BSky(cfg.bluesky)
    if not bs.login():
        raise RuntimeError("Bluesky auth failed for Jetstream ingestion")
    did_cache = DIDCache(bs)

    terms = extract_keywords(keywords, max_terms=10) if keywords else []
    collected: List[Post] = []
    deadline = time.time() + (minutes * 60) if minutes else None

    attempts = 0
    while True:
        if max_posts and len(collected) >= max_posts:
            break
        if deadline and time.time() > deadline:
            break
        if attempts > 3:
            break
        attempts += 1
        logger.info(f"Connecting to Jetstream: {JETSTREAM_URL} (attempt {attempts})")
        try:
            async with websockets.connect(
                JETSTREAM_URL,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10,
                max_queue=1024,
            ) as ws:
                while True:
                    if max_posts and len(collected) >= max_posts:
                        break
                    if deadline and time.time() > deadline:
                        break
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=30)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.warning(f"WebSocket recv error: {e}")
                        break
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        continue

                    # Expect a commit-like structure with op(s) and record
                    commit = msg.get("commit") or msg
                    repo = commit.get("repo") or msg.get("repo")
                    ops = commit.get("ops") or commit.get("operations") or []
                    record = commit.get("record") or msg.get("record")

                    if not ops and not record:
                        # Some Jetstream variants include 'kind' and 'evt' fields; skip if no record
                        continue

                    # Try to build posts from operations
                    texts: List[Dict] = []
                    if record and isinstance(record, dict) and record.get("$type", "").endswith("app.bsky.feed.post"):
                        texts.append(record)
                    for op in ops:
                        if not isinstance(op, dict):
                            continue
                        path = op.get("path", "")
                        if "app.bsky.feed.post" in path and (op.get("action") or op.get("op")) == "create":
                            rec = op.get("record") or record
                            if isinstance(rec, dict) and rec.get("text"):
                                texts.append(rec)

                    for rec in texts:
                        text = clean_text(rec.get("text", ""))
                        if not text:
                            continue
                        if terms:
                            tl = text.lower()
                            if not any(t.lstrip('#@') in tl for t in terms):
                                continue
                        try:
                            created_at = rec.get("createdAt") or rec.get("indexedAt")
                            from datetime import datetime, timezone
                            if created_at:
                                created_dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
                            else:
                                created_dt = datetime.now(timezone.utc)
                        except Exception:
                            from datetime import datetime, timezone
                            created_dt = datetime.now(timezone.utc)

                        author_meta = did_cache.get(repo) if repo else {"handle": repo or "unknown", "display": repo or "unknown"}
                        p = Post(
                            uri=f"at://{repo}/app.bsky.feed.post/unknown",
                            cid="",
                            author=author_meta["handle"],
                            author_display_name=author_meta["display"],
                            text=text,
                            created_at=created_dt,
                        )
                        collected.append(p)
                        if max_posts and len(collected) >= max_posts:
                            break
        except Exception as e:
            logger.warning(f"Jetstream connect error: {e}")
            await asyncio.sleep(0.5)
            continue

    logger.info(f"Jetstream collected {len(collected)} posts")
    return collected
