"""ChromaDB store for simple RAG."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from loguru import logger

from .config import ChromaCfg
from .utils import Chunk


class Store:
    def __init__(self, cfg: ChromaCfg):
        self.cfg = cfg
        os.makedirs(self.cfg.db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=self.cfg.db_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
        self.col = self.client.get_or_create_collection(
            name=self.cfg.collection,
            metadata={"description": "Bluesky chunks (simple_rag)"},
        )

    def clear(self):
        self.client.delete_collection(self.cfg.collection)
        self.col = self.client.create_collection(
            name=self.cfg.collection,
            metadata={"description": "Bluesky chunks (simple_rag)"},
        )

    def add_chunks(self, chunks: List[Chunk], embeddings: List[Optional[List[float]]]) -> int:
        docs: List[str] = []
        metas: List[Dict[str, Any]] = []
        ids: List[str] = []
        vecs: List[List[float]] = []
        added = 0
        for ch, vec in zip(chunks, embeddings):
            if vec is None or not ch.text.strip():
                continue
            p = ch.post
            doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{p.uri}#{ch.index}"))
            docs.append(ch.text)
            metas.append({
                "uri": p.uri,
                "author": p.author,
                "author_display_name": p.author_display_name,
                "created_at": p.created_at.isoformat(),
                "created_at_ts": p.created_at.timestamp(),
                "reply_count": p.reply_count,
                "repost_count": p.repost_count,
                "like_count": p.like_count,
                "chunk_index": ch.index,
                "chunk_total": ch.total,
            })
            ids.append(doc_id)
            vecs.append(vec)
            added += 1
        if not docs:
            return 0
        self.col.add(embeddings=vecs, documents=docs, metadatas=metas, ids=ids)
        return added

    def query(self, query_vec: List[float], n: int = 10, recent_days: Optional[int] = None, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        where_filter = where or {}
        if recent_days is not None:
            cutoff_ts = (datetime.utcnow() - timedelta(days=recent_days)).timestamp()
            where_filter = {**where_filter, "created_at_ts": {"$gte": cutoff_ts}}
        try:
            res = self.col.query(
                query_embeddings=[query_vec],
                n_results=n,
                where=where_filter or None,
                include=["documents", "metadatas", "distances"],
            )
            return {
                "documents": res.get("documents", [[]])[0],
                "metadatas": res.get("metadatas", [[]])[0],
                "distances": res.get("distances", [[]])[0],
                "count": len(res.get("documents", [[]])[0]),
            }
        except Exception as e:
            logger.error(f"chroma query error: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "count": 0}
