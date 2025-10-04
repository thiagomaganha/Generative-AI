from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.document import SearchQuery, SearchResult
from app.services.retrieval_service import RetrievalService
from app.services.vector_store import VectorStore
from app.dependencies import get_retrieval_service, get_vector_store

router = APIRouter()

@router.post("/", response_model=List[SearchResult])
async def search_documents(
    search_query: SearchQuery,
    service: RetrievalService = Depends(get_retrieval_service)
):
    try:
        return await service.search_documents(search_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate results: {str(e)}")
    

@router.get("/stats")
async def get_search_stats(
    vector_store: VectorStore = Depends(get_vector_store)
):
    """Get vector store statistics"""
    try:
        stats = await vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")