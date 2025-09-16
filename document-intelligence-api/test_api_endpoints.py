import requests
import io

def test_upload_endpoint():
    """Test document upload endpoint"""
    try:
        # Create a test file
        test_content = "This is a test document for upload."
        test_file = io.BytesIO(test_content.encode())
        
        files = {"file": ("test.txt", test_file, "text/plain")}
        response = requests.post("http://localhost:8000/api/v1/documents/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            document_id = result["id"]
            print(f"✅ Upload test passed. Document ID: {document_id}")
            
            # Test get document
            get_response = requests.get(f"http://localhost:8000/api/v1/documents/{document_id}")
            if get_response.status_code == 200:
                print("✅ Get document test passed")
            else:
                print(f"❌ Get document test failed: {get_response.status_code}")
                
            return document_id
        else:
            print(f"❌ Upload test failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")

if __name__ == "__main__":
    test_upload_endpoint()