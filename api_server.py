"""FastAPI server for the BlueSearch RAG application."""

import asyncio
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from loguru import logger

from simple_rag.config import get_cfg
from simple_rag.rag import SimpleRAG
from simple_rag.utils import bsky_uri_to_web

app = FastAPI(
    title="LeftLeak API",
    description="API for retrieving leftist perspectives from Bluesky",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    context_used: int
    followUpQuestions: List[str]

DEFAULT_PERSONA = (
    "You are aggregating and summarizing real leftist opinions from Bluesky. Present what actual leftists are saying about topics. "
    "Focus on showing the genuine progressive, pro-LGBTQ+, pro-diversity perspectives found on Bluesky. "
    "Be clear that these are real views from real people in the leftist community. Always cite @handles to show authenticity. "
    "Present the information as 'This is what leftists on Bluesky are actually saying' rather than roleplaying as a character."
)

# Follow-up questions to suggest based on topics
FOLLOW_UP_SUGGESTIONS = {
    "default": [
        "What are the policy implications?",
        "How does this affect marginalized communities?",
        "What's the historical context?",
        "What are activists saying about this?"
    ],
    "politics": [
        "What are progressives saying about this policy?",
        "How does this impact voting rights?",
        "What's the grassroots response?",
        "What are the alternatives being proposed?"
    ],
    "social": [
        "What's the LGBTQ+ perspective on this?",
        "How does this relate to social justice?",
        "What are community organizers saying?",
        "What actions are being taken?"
    ],
    "economic": [
        "How does this affect income inequality?",
        "What's the labor movement's stance?",
        "What about universal basic income?",
        "How does this impact workers' rights?"
    ]
}

def get_follow_up_questions(question: str, answer: str) -> List[str]:
    """Generate relevant follow-up questions based on the context."""
    question_lower = question.lower()
    
    # Detect topic
    if any(word in question_lower for word in ["policy", "politics", "election", "vote", "democrat", "republican"]):
        return FOLLOW_UP_SUGGESTIONS["politics"]
    elif any(word in question_lower for word in ["lgbt", "trans", "gender", "identity", "community", "social"]):
        return FOLLOW_UP_SUGGESTIONS["social"]
    elif any(word in question_lower for word in ["economy", "wage", "work", "job", "money", "income"]):
        return FOLLOW_UP_SUGGESTIONS["economic"]
    else:
        return FOLLOW_UP_SUGGESTIONS["default"]

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "active", "message": "LeftLeak API is running"}

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system for leftist perspectives on a topic.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        cfg = get_cfg()
        rag = SimpleRAG(cfg)
        
        # Quick attempt: fast hybrid retrieval first
        logger.info(f"Processing query: {request.question}")
        
        try:
            quick = rag.ask(request.question, fresh=True, persona=DEFAULT_PERSONA)
        except Exception as e:
            logger.warning(f"Quick retrieval failed: {e}")
            quick = {"answer": None, "context_used": 0, "sources": []}
        
        # If quick retrieval got good results, use them
        if quick.get("context_used", 0) >= 3 and quick.get("answer"):
            result = quick
        else:
            # Fall back to Jetstream streaming
            logger.info("Using Jetstream for better results...")
            try:
                result = await asyncio.to_thread(
                    rag.ask_jetstream,
                    request.question,
                    keywords=None,
                    max_posts=300,
                    minutes=2,
                    persona=DEFAULT_PERSONA
                )
            except Exception as e:
                logger.error(f"Jetstream query failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Convert sources to web URLs
        sources = result.get("sources", [])
        web_sources = [bsky_uri_to_web(uri) for uri in sources]
        
        # Generate follow-up questions
        follow_up_questions = get_follow_up_questions(
            request.question,
            result.get("answer", "")
        )
        
        return QueryResponse(
            answer=result.get("answer", "No answer found"),
            sources=web_sources,
            context_used=result.get("context_used", 0),
            followUpQuestions=follow_up_questions
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/status")
async def status():
    """Get system status and configuration."""
    try:
        cfg = get_cfg()
        return {
            "status": "operational",
            "config": {
                "text_model": cfg.gemini.text_model,
                "embedding_model": cfg.gemini.embedding_model,
                "db_path": str(cfg.chroma.db_path),
                "collection": cfg.chroma.collection,
                "chunk_size": cfg.rag.chunk_size,
                "max_results": cfg.rag.max_results,
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )