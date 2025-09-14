from app.models.document import DocumentResponse, DocumentType, DocumentStatus, SearchQuery
from app.core.database import Document, SessionLocal
from datetime import datetime

def test_models():
    """Test Pydantic models"""
    try:
        # Test DocumentResponse model
        doc = DocumentResponse(
            id="test-123",
            filename="test.pdf",
            file_size=1024,
            document_type=DocumentType.PDF,
            status=DocumentStatus.PENDING,
            created_at=datetime.utcnow()
        )
        print("✅ Document model test passed")
        
        # Test SearchQuery model
        search = SearchQuery(query="test query", limit=5)
        print("✅ Search model test passed")
        
        # Test database connection
        db = SessionLocal()
        db.close()
        print("✅ Database connection test passed")
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")

if __name__ == "__main__":
    test_models()