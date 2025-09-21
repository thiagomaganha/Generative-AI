import asyncio
from app.services.ai_analyzer import AIAnalyzer

async def test_ai_analyzer():
    """Test AI analyzer functionality"""
    try:
        analyzer = AIAnalyzer()
        
        # Test text
        test_text = """
        Machine learning is a subset of artificial intelligence that enables computers 
        to learn and make decisions from data without being explicitly programmed. 
        Companies like Google, Microsoft, and Apple use machine learning for various 
        applications including image recognition, natural language processing, and 
        predictive analytics.
        """
        
        print("Testing AI analysis...")
        analysis = await analyzer.analyze_document(test_text, "test.txt")
        
        print(f"✅ Summary: {analysis.summary}")
        print(f"✅ Entities: {analysis.key_entities}")
        print(f"✅ Topics: {analysis.topics}")
        print(f"✅ Sentiment: {analysis.sentiment}")
        
        # Test embeddings
        print("Testing embeddings generation...")
        embeddings = await analyzer.generate_embeddings(test_text)
        print(f"✅ Embeddings generated: {len(embeddings)} dimensions")
        
        print("✅ AI analyzer test passed")
        
    except Exception as e:
        print(f"❌ AI analyzer test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_analyzer())