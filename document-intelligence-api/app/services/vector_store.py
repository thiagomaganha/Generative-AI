import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple, Optional, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """FAISS-based vector store for document search"""
    
    def __init__(self):
        self.index = None
        self.documents_metadata = {}
        self.dimension = settings.VECTOR_DIMENSION
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = f"{self.index_path}_metadata.pkl"
    
    async def initialize(self):
        """Initialize or load existing FAISS index"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    self.documents_metadata = pickle.load(f)
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} documents")
            else:
                self.index = faiss.IndexFlatIP(self.dimension)  
                self.documents_metadata = {}
                logger.info("Created new FAISS index")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.documents_metadata = {}
    
    async def add_document(self, document_id: str, text: str, embeddings: List[float], metadata: Dict[str, Any]):
        """Add document to vector store"""
        try:
            # Convert embeddings to numpy array
            embedding_array = np.array([embeddings], dtype=np.float32)
           
            faiss.normalize_L2(embedding_array)
            
            self.index.add(embedding_array)
            
            index_id = self.index.ntotal - 1  # Latest added document
            self.documents_metadata[index_id] = {
                'document_id': document_id,
                'text_preview': text[:500],  # Store preview for search results
                'metadata': metadata
            }
            
            # Save index and metadata
            await self._save_index()
            
            logger.info(f"Added document {document_id} to vector store")
            
        except Exception as e:
            logger.error(f"Failed to add document to vector store: {e}")
            raise
    
    async def search(self, query_embeddings: List[float], k: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if self.index.ntotal == 0:
                return []
            
            query_array = np.array([query_embeddings], dtype=np.float32)
            faiss.normalize_L2(query_array)
            
            scores, indices = self.index.search(query_array, min(k, self.index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and score >= threshold: 
                    doc_metadata = self.documents_metadata.get(idx, {})
                    if not doc_metadata.get('deleted', False):  
                        results.append({
                            'document_id': doc_metadata.get('document_id'),
                            'similarity_score': float(score),
                            'relevant_chunk': doc_metadata.get('text_preview', ''),
                            'metadata': doc_metadata.get('metadata', {})
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        active_docs = sum(1 for meta in self.documents_metadata.values() 
                         if not meta.get('deleted', False))
        
        return {
            'total_documents': self.index.ntotal if self.index else 0,
            'active_documents': active_docs,
            'index_size_mb': os.path.getsize(self.index_path) / (1024*1024) if os.path.exists(self.index_path) else 0
        }
    
    async def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents_metadata, f)
                
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
            raise
    
    async def close(self):
        """Cleanup resources"""
        await self._save_index()
        logger.info("Vector store closed and saved")