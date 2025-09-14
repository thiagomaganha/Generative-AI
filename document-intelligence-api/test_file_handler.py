import asyncio
from app.services.file_handler import FileHandler
from app.models.document import DocumentType

async def test_file_handler():
    """Test file handler functionality"""
    try:
        # Create a test text file
        test_content = "This is a test document for the Document Intelligence API."
        with open("test_file.txt", "w") as f:
            f.write(test_content)
        
        # Test text extraction
        extracted_text = FileHandler.extract_text("test_file.txt", DocumentType.TXT)
        assert extracted_text == test_content
        print("✅ Text extraction test passed")
        
        # Cleanup
        os.remove("test_file.txt")
        
    except Exception as e:
        print(f"❌ File handler test failed: {e}")

if __name__ == "__main__":
    import os
    asyncio.run(test_file_handler())