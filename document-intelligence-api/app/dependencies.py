from fastapi import Depends
from app.services.ai_analyzer import AIAnalyzer
from app.services.vector_store import VectorStore

#singleton
_ai_analyzer = AIAnalyzer()
async def get_ai_analyzer() -> AIAnalyzer:
    return _ai_analyzer

# per-request
async def get_vector_store() -> VectorStore:
    store = VectorStore()
    try:
        await store.initialize()   
        yield store
    finally:
        await store.close()        
