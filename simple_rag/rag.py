"""Simple RAG engine orchestrating the steps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from loguru import logger

from .config import AppCfg, get_cfg
from .bluesky import BSky
from .embeddings import Gemini
from .store import Store
from .utils import Post, Chunk, clean_text, chunk_text, extract_keywords
from .ingest import stream_posts
import asyncio


@dataclass
class Answer:
    answer: str
    context_used: int
    sources: List[str]


class SimpleRAG:
    def __init__(self, cfg: Optional[AppCfg] = None):
        self.cfg = cfg or get_cfg()
        self.bs = BSky(self.cfg.bluesky)
        self.gm = Gemini(self.cfg.gemini)
        self.db = Store(self.cfg.chroma)

    def ingest_posts(self, posts: List[Post]) -> int:
        # chunk posts
        chunks: List[Chunk] = []
        for p in posts:
            text = clean_text(p.text)
            if not text:
                continue
            parts = chunk_text(text, self.cfg.rag.chunk_size, self.cfg.rag.chunk_overlap)
            for i, t in enumerate(parts):
                chunks.append(Chunk(text=t, post=p, index=i, total=len(parts)))
        if not chunks:
            return 0
        # embed
        texts = [f"@{c.post.author}: {c.text}" for c in chunks]
        vecs = self.gm.embed_batch(texts, task_type="RETRIEVAL_DOCUMENT", batch_size=12, delay=0.2)
        # store
        added = self.db.add_chunks(chunks, vecs)
        return added

    def retrieve(self, question: str, max_results: Optional[int] = None, recent_days: Optional[int] = None) -> List[Chunk]:
        max_results = max_results or self.cfg.rag.max_results
        qvec = self.gm.query_embed(question)
        if qvec is None:
            return []
        res = self.db.query(qvec, n=max_results, recent_days=recent_days or self.cfg.rag.recent_days)
        # Fallback: if recency filter yields nothing, try without it
        if not res.get("documents") or res.get("count", 0) == 0:
            res = self.db.query(qvec, n=max_results, recent_days=None)
        out: List[Chunk] = []
        for doc, meta in zip(res.get("documents", []), res.get("metadatas", [])):
            # Parse created_at back to datetime if it's a string
            ca = meta.get("created_at", "")
            from datetime import datetime
            try:
                created_at = datetime.fromisoformat(str(ca).replace("Z", "+00:00")) if ca else datetime.utcnow()
            except Exception:
                created_at = datetime.utcnow()
            p = Post(
                uri=meta.get("uri", ""),
                cid="",
                author=meta.get("author", ""),
                author_display_name=meta.get("author_display_name", ""),
                text=doc,
                created_at=created_at,
                reply_count=meta.get("reply_count", 0),
                repost_count=meta.get("repost_count", 0),
                like_count=meta.get("like_count", 0),
            )
            out.append(Chunk(text=doc, post=p, index=meta.get("chunk_index", 0), total=meta.get("chunk_total", 1)))
        return out

    def ask(self, question: str, fresh: bool = True, persona: Optional[str] = None) -> Dict[str, Any]:
        # 1) collect fresh posts relevant to query
        if fresh:
            try:
                posts = self.bs.hybrid_search(question, limit=60)
                added = self.ingest_posts(posts)
                logger.info(f"fresh ingest added={added}")
            except Exception as e:
                logger.warning(f"fresh ingest skipped: {e}")
        # 2) retrieve
        ctx_chunks = self.retrieve(question, max_results=self.cfg.rag.max_results)
        if not ctx_chunks:
            return {
                "answer": "I couldn't find relevant Bluesky posts to answer. Try rephrasing or ask about a recent topic.",
                "context_used": 0,
                "sources": [],
            }
        # 3) generate
        ans = self.gm.answer(question, ctx_chunks, persona=persona)
        if not ans:
            return {"answer": "Answer generation failed", "context_used": len(ctx_chunks), "sources": []}
        src = []
        seen = set()
        for ch in ctx_chunks[:6]:
            if ch.post.uri and ch.post.uri not in seen:
                seen.add(ch.post.uri)
                src.append(ch.post.uri)
        return {"answer": ans, "context_used": len(ctx_chunks), "sources": src}

    def ask_jetstream(self, question: str, keywords: Optional[str] = None, max_posts: int = 200, minutes: int = 2, persona: Optional[str] = None) -> Dict[str, Any]:
        """Run a full pipeline: stream from Jetstream with keywords, ingest, then answer the question."""
        kw = keywords or question
        try:
            posts = asyncio.get_event_loop().run_until_complete(stream_posts(self.cfg, kw, max_posts, minutes))
        except RuntimeError:
            # If no running loop (rare on some environments), create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            posts = loop.run_until_complete(stream_posts(self.cfg, kw, max_posts, minutes))
            loop.close()
        added = self.ingest_posts(posts)
        logger.info(f"jetstream ingest added={added} from {len(posts)} posts")
        result = self.ask(question, fresh=False, persona=persona)
        result["jetstream_ingested_posts"] = len(posts)
        result["jetstream_chunks_added"] = added
        return result
