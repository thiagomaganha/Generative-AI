import asyncio
import requests
import json

async def test_search_api():
    """Test search API endpoints"""
    try:
        # upload a test document first
        test_content = "This document discusses machine learning algorithms and their applications in artificial intelligence."
        
        # call to upload 
        files = {"file": ("ml_doc.txt", test_content.encode(), "text/plain")}
        upload_response = requests.post("http://localhost:8000/api/v1/documents/upload", files=files)
        
        if upload_response.status_code == 200:
            print("✅ Test document uploaded")
            
            await asyncio.sleep(10)
            
            # Test search stats
            stats_response = requests.get("http://localhost:8000/api/v1/search/stats")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Search stats: {stats}")
            
            # Test search (this will work once we implement processing)
            search_data = {
                "query": "machine learning algorithms",
                "limit": 5,
                "similarity_threshold": 0.5
            }
            
            search_response = requests.post(
                "http://localhost:8000/api/v1/search/", 
                data=json.dumps(search_data),
                headers={"Content-Type": "application/json"}
            )
            
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"✅ Search completed: {len(results)} results")
            else:
                print(f"⚠️  Search returned {search_response.status_code} (expected - no processed documents yet)")
                
        else:
            print(f"❌ Test document upload failed: {upload_response.status_code}")
            
    except Exception as e:
        print(f"❌ Search API test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_search_api())