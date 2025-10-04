from fastapi import Depends
from app.services.ai_analyzer import AIAnalyzer
from app.services.vector_store import VectorStore
from app.services.retrieval_service import RetrievalService
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.document_service import DocumentService

#singleton
_ai_analyzer = AIAnalyzer()
_vector_store: VectorStore | None = None

async def get_ai_analyzer() -> AIAnalyzer:
    return _ai_analyzer

async def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        store = VectorStore()
        await store.initialize()
        _vector_store = store
    return _vector_store

def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)

def get_retrieval_service(
        ai_analyzer = Depends(get_ai_analyzer),
        vector_store = Depends(get_vector_store)
) -> RetrievalService:
    return RetrievalService(ai_analyzer, vector_store)