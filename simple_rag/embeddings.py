"""Gemini embeddings and generation for simple RAG."""

from __future__ import annotations

import time
from typing import List, Optional, Dict

import google.generativeai as genai
from google.generativeai import GenerativeModel
from loguru import logger

from .config import GeminiCfg
from .utils import Chunk, format_doc_for_prompt


class Gemini:
    def __init__(self, cfg: GeminiCfg):
        self.cfg = cfg
        genai.configure(api_key=cfg.api_key)
        self.text_model = GenerativeModel(cfg.text_model)
        self.embedding_model = cfg.embedding_model

    def _extract_text(self, response) -> Optional[str]:
        try:
            # Preferred quick accessor
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            # Manual extraction if needed
            cand_list = getattr(response, 'candidates', None)
            if cand_list:
                for c in cand_list:
                    # finish_reason 2 often means blocked; skip empty candidates
                    content = getattr(c, 'content', None)
                    parts = getattr(content, 'parts', None) if content else None
                    if parts:
                        texts = [getattr(p, 'text', '') for p in parts if hasattr(p, 'text')]
                        joined = "\n".join([t for t in texts if t]).strip()
                        if joined:
                            return joined
        except Exception:
            pass
        return None

    def _extract_vec(self, result) -> Optional[List[float]]:
        try:
            v = result.get("embedding")
            if isinstance(v, dict) and "values" in v:
                return v["values"]
            if isinstance(v, list):
                return v
        except Exception:
            pass
        return None

    def embed(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> Optional[List[float]]:
        if not text or not text.strip():
            return None
        try:
            res = genai.embed_content(
                model=self.embedding_model,
                content=text.strip(),
                task_type=task_type,
            )
            vec = self._extract_vec(res)
            if vec is None:
                logger.warning("Embedding returned no vector")
            return vec
        except Exception as e:
            logger.error(f"embed error: {e}")
            return None

    def embed_batch(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT", batch_size: int = 16, delay: float = 0.2) -> List[Optional[List[float]]]:
        out: List[Optional[List[float]]] = []
        for i in range(0, len(texts), batch_size):
            b = texts[i : i + batch_size]
            for t in b:
                out.append(self.embed(t, task_type=task_type))
                time.sleep(0.05)
            if i + batch_size < len(texts):
                time.sleep(delay)
        return out

    def query_embed(self, text: str) -> Optional[List[float]]:
        return self.embed(text, task_type="RETRIEVAL_QUERY")

    def build_prompt(self, question: str, chunks: List[Chunk], persona: Optional[str] = None) -> str:
        docs = "\n\n---\n\n".join(
            format_doc_for_prompt(i + 1, ch) for i, ch in enumerate(chunks[:10])
        )
        base_style = (
            "You are a helpful assistant summarizing and citing Bluesky posts. "
            "Use ONLY the provided posts to answer. If unsure, say you couldn't find it. "
            "Cite users with @handle when attributing views."
        )
        if persona:
            base_style += ("\n\nPerspective: " + persona.strip())
        prompt = f"{base_style}\n\nContext:\n{docs}\n\nQuestion: {question}\n\nAnswer:"
        return prompt

    def answer(self, question: str, chunks: List[Chunk], persona: Optional[str] = None) -> Optional[str]:
        prompt = self.build_prompt(question, chunks, persona=persona)
        try:
            cfg = genai.types.GenerationConfig(
                max_output_tokens=self.cfg.max_tokens,
                temperature=self.cfg.temperature,
            )
            resp = self.text_model.generate_content(prompt, generation_config=cfg)
            txt = self._extract_text(resp)
            if txt:
                return txt
            # Fallback: calmer, purely descriptive summary to avoid safety blocks
            safe_persona = (
                "Provide a neutral, respectful summary of the posts. Avoid inflammatory language. "
                "Focus on key arguments and cite @handles."
            )
            prompt2 = self.build_prompt(question, chunks, persona=safe_persona)
            cfg2 = genai.types.GenerationConfig(
                max_output_tokens=self.cfg.max_tokens,
                temperature=0.2,
            )
            resp2 = self.text_model.generate_content(prompt2, generation_config=cfg2)
            return self._extract_text(resp2)
        except Exception as e:
            logger.error(f"gen error: {e}")
            return None
