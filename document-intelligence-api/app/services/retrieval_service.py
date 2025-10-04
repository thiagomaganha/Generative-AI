from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.document import SearchQuery, SearchResult
from app.services.ai_analyzer import AIAnalyzer
from app.services.vector_store import VectorStore

class RetrievalService:
    def __init__(self, ai_analyzer: AIAnalyzer, vector_store: VectorStore):
        self.ai_analyzer = ai_analyzer
        self.vector_store = vector_store


    async def search_documents(self, search_query: SearchQuery) -> List[SearchResult]:
        
        query_embeddings = await self.ai_analyzer.generate_embeddings(search_query.query)
        
        results = await self.vector_store.search(
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