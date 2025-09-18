"""Bluesky client for simple RAG, with search fallback."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import List, Optional

import requests
from atproto import Client
from loguru import logger

from .config import BlueskyCfg
from .utils import Post, clean_text, extract_keywords


class BSky:
    def __init__(self, cfg: BlueskyCfg):
        self.cfg = cfg
        self.client = Client()
        self._auth = False

    def login(self) -> bool:
        try:
            self.client.login(self.cfg.handle, self.cfg.app_password)
            self._auth = True
            logger.info(f"Logged in to Bluesky as {self.cfg.handle}")
            return True
        except Exception as e:
            logger.error(f"Bluesky login failed: {e}")
            self._auth = False
            return False

    def _ensure(self):
        if not self._auth:
            if not self.login():
                raise RuntimeError("Bluesky auth failed")

    def _to_post(self, item) -> Post:
        post = item.post if hasattr(item, "post") else item
        uri = getattr(post, "uri", "")
        cid = getattr(post, "cid", "")
        author = getattr(post, "author", None)
        handle = getattr(author, "handle", "") if author else ""
        display_name = getattr(author, "display_name", handle) if author else handle
        record = getattr(post, "record", None)
        text = clean_text(getattr(record, "text", "") if record else "")
        created_at = getattr(record, "created_at", None) if record else None
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                created_at = datetime.now(timezone.utc)
        if created_at is None:
            created_at = datetime.now(timezone.utc)
        reply_count = getattr(post, "reply_count", 0)
        repost_count = getattr(post, "repost_count", 0)
        like_count = getattr(post, "like_count", 0)
        return Post(
            uri=uri,
            cid=cid,
            author=handle,
            author_display_name=display_name,
            text=text,
            created_at=created_at,
            reply_count=reply_count,
            repost_count=repost_count,
            like_count=like_count,
        )

    def timeline(self, limit: int = 50):
        self._ensure()
        resp = self.client.get_timeline(limit=limit)
        return [self._to_post(it) for it in resp.feed]

    def timeline_paged(self, total_limit: int = 120) -> List[Post]:
        self._ensure()
        cursor = None
        out: List[Post] = []
        while len(out) < total_limit:
            batch_size = min(50, total_limit - len(out))
            resp = self.client.get_timeline(limit=batch_size, cursor=cursor)
            out.extend([self._to_post(it) for it in resp.feed])
            cursor = getattr(resp, 'cursor', None)
            if not cursor or not resp.feed:
                break
            time.sleep(0.2)
        return out

    def popular(self, limit: int = 50):
        self._ensure()
        # What's hot feed
        hot_uri = "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot"
        resp = self.client.app.bsky.feed.get_feed({"feed": hot_uri, "limit": limit})
        return [self._to_post(it) for it in resp.feed]

    def popular_paged(self, total_limit: int = 120) -> List[Post]:
        self._ensure()
        hot_uri = "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot"
        cursor = None
        out: List[Post] = []
        while len(out) < total_limit:
            batch_size = min(50, total_limit - len(out))
            resp = self.client.app.bsky.feed.get_feed({"feed": hot_uri, "limit": batch_size, "cursor": cursor})
            out.extend([self._to_post(it) for it in resp.feed])
            cursor = getattr(resp, 'cursor', None)
            if not cursor or not resp.feed:
                break
            time.sleep(0.2)
        return out

    def author_feed(self, actor: str, limit: int = 50):
        self._ensure()
        resp = self.client.get_author_feed(actor=actor, limit=limit)
        return [self._to_post(it) for it in resp.feed]

    def search_posts_public(self, q: str, limit: int = 25) -> List[Post]:
        """Use the HTTP search posts endpoint when available.
        Note: Public search API may have constraints; we keep this as a best-effort fallback.
        """
        try:
            url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
            params = {"q": q, "limit": str(limit)}
            headers = {
                "User-Agent": "bsrag/1.0 (+https://local)",
                "Accept-Language": "en",
            }
            r = requests.get(url, params=params, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json()
            posts: List[Post] = []
            for it in data.get("posts", []):
                author = it.get("author", {})
                handle = author.get("handle", "")
                display_name = author.get("displayName", handle)
                created_at = it.get("indexedAt") or it.get("createdAt")
                try:
                    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else datetime.now(timezone.utc)
                except Exception:
                    created_dt = datetime.now(timezone.utc)
                posts.append(Post(
                    uri=it.get("uri", ""),
                    cid=it.get("cid", ""),
                    author=handle,
                    author_display_name=display_name,
                    text=clean_text(it.get("text", "")),
                    created_at=created_dt,
                    reply_count=it.get("replyCount", 0),
                    repost_count=it.get("repostCount", 0),
                    like_count=it.get("likeCount", 0),
                ))
            return posts
        except Exception as e:
            logger.warning(f"Public search fallback failed: {e}")
            return []

    def search_posts_auth(self, q: str, limit: int = 25) -> List[Post]:
        """Try authenticated search via atproto XRPC if available."""
        try:
            self._ensure()
            # Some atproto versions support this; headers to prefer English
            data = self.client.app.bsky.feed.search_posts({
                'q': q,
                'limit': limit,
            }, headers={'Accept-Language': 'en'})
            posts = []
            # The response should have a 'posts' attribute similar to public search
            items = getattr(data, 'posts', []) or getattr(data, 'feed', [])
            for it in items:
                posts.append(self._to_post(it))
            return posts
        except Exception as e:
            logger.warning(f"Authenticated search failed: {e}")
            return []

    def hybrid_search(self, query: str, limit: int = 60) -> List[Post]:
        """Combine timeline, popular, and public search results, then filter by keyword presence."""
        terms = extract_keywords(query, max_terms=8)
        results: List[Post] = []
        try:
            results.extend(self.timeline_paged(total_limit=120))
        except Exception:
            pass
        try:
            results.extend(self.popular_paged(total_limit=120))
        except Exception:
            pass
        # Try authenticated search first, then public fallback
        try:
            results.extend(self.search_posts_auth(query, limit=40))
        except Exception:
            pass
        try:
            results.extend(self.search_posts_public(query, limit=40))
        except Exception:
            pass
        # dedupe and filter
        seen = set()
        deduped: List[Post] = []
        filtered: List[Post] = []
        for p in results:
            if p.uri in seen:
                continue
            seen.add(p.uri)
            deduped.append(p)
            if terms:
                text_l = p.text.lower()
                # match plain terms; strip #/@ markers to match mentions/hashtags too
                if any(t.lstrip('#@') in text_l for t in terms):
                    filtered.append(p)
        # choose filtered if available, otherwise use deduped
        final = filtered if filtered else deduped
        return final[:limit]

if __name__ == "__main__":
    print("This module provides BSky client utilities.")
