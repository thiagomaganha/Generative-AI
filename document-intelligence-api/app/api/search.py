from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.document import SearchQuery, SearchResult
from app.services.ai_analyzer import AIAnalyzer
from app.services.vector_store import VectorStore
from app.dependencies import get_ai_analyzer, get_vector_store

router = APIRouter()

@router.post("/", response_model=List[SearchResult])
async def search_documents(
    search_query: SearchQuery,
    ai_analyzer: AIAnalyzer = Depends(get_ai_analyzer),  # singleton
    vector_store: VectorStore = Depends(get_vector_store),  # per-request
):
    query_embeddings = await ai_analyzer.generate_embeddings(search_query.query)
    results = await vector_store.search(
        query_embeddings=query_embeddings,
        k=search_query.limit,
        threshold=search_query.similarity_threshold,
    )
    return [
        SearchResult(
            document_id=result['document_id'],
            filename=result['metadata'].get('filename', 'Unknown'),
            similarity_score=result['similarity_score'],
            relevant_chunk=result['relevant_chunk'],
        )
        for result in results
    ]

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