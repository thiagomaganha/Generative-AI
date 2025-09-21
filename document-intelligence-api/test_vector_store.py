import asyncio
import numpy as np
from app.services.vector_store import VectorStore

async def test_vector_store():
    """Test vector store functionality"""
    try:
        store = VectorStore()
        await store.initialize()
        
        # Create test embeddings
        test_embeddings_1 = np.random.random(1536).tolist()  # OpenAI embedding dimension
        test_embeddings_2 = np.random.random(1536).tolist()
        
        # Add test documents
        await store.add_document(
            "doc1",
            "This is a test document about machine learning",
            test_embeddings_1,
            {"filename": "test1.txt", "type": "txt"}
        )
        
        await store.add_document(
            "doc2", 
            "This is another test document about artificial intelligence",
            test_embeddings_2,
            {"filename": "test2.txt", "type": "txt"}
        )
        
        print("✅ Documents added to vector store")
        
        # Test search
        results = await store.search(test_embeddings_1, k=5, threshold=0.1)
        print(f"✅ Search completed. Found {len(results)} results")
        
        # Test stats
        stats = await store.get_stats()
        print(f"✅ Vector store stats: {stats}")
        
        await store.close()
        print("✅ Vector store test passed")
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_vector_store())