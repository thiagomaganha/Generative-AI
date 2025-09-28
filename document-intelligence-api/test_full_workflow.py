import requests
import time
import json

def test_full_document_workflow():
    """Test complete document processing workflow"""
    try:
        # 1. Upload document
        test_content = """
        Artificial Intelligence and Machine Learning in Healthcare
        
        Machine learning algorithms are revolutionizing healthcare by enabling 
        predictive analytics, personalized treatment plans, and automated diagnosis. 
        Companies like Google Health, IBM Watson, and Microsoft are leading this 
        transformation with innovative AI solutions.
        
        Key applications include:
        - Medical image analysis
        - Drug discovery and development  
        - Electronic health record analysis
        - Personalized medicine
        - Clinical decision support systems
        """
        
        files = {"file": ("ai_healthcare.txt", test_content.encode(), "text/plain")}
        upload_response = requests.post("http://localhost:8000/api/v1/documents/upload", files=files)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            document_id = upload_data["id"]
            job_id = upload_data["job_id"]
            
            print(f"✅ Document uploaded successfully")
            print(f"   Document ID: {document_id}")
            print(f"   Job ID: {job_id}")
            
            # 2. Monitor job progress
            print("\n⏳ Monitoring job progress...")
            for i in range(60):  # Wait up to 60 seconds
                job_response = requests.get(f"http://localhost:8000/api/v1/jobs/{job_id}")
                
                if job_response.status_code == 200:
                    job_data = job_response.json()
                    status = job_data["status"]
                    progress = job_data["progress"]
                    
                    print(f"   Status: {status} ({progress}%)")
                    
                    if status == "completed":
                        print("✅ Document processing completed!")
                        print(f"   Result: {job_data.get('result', {}).get('analysis', {}).get('summary', 'No summary')[:100]}...")
                        break
                    elif status == "failed":
                        print(f"❌ Document processing failed: {job_data.get('error_message')}")
                        return False
                
                time.sleep(2)
            
            # 3. Get processed document
            doc_response = requests.get(f"http://localhost:8000/api/v1/documents/{document_id}")
            if doc_response.status_code == 200:
                doc_data = doc_response.json()
                print(f"\n✅ Document retrieved:")
                print(f"   Status: {doc_data['status']}")
                if doc_data.get('analysis'):
                    analysis = doc_data['analysis']
                    print(f"   Summary: {analysis.get('summary', 'N/A')[:100]}...")
                    print(f"   Topics: {analysis.get('topics', [])}")
                    print(f"   Entities: {analysis.get('key_entities', [])[:5]}")
            
            # 4. Test search
            search_data = {
                "query": "machine learning healthcare applications",
                "limit": 5,
                "similarity_threshold": 0.3
            }
            
            search_response = requests.post(
                "http://localhost:8000/api/v1/search/", 
                data=json.dumps(search_data),
                headers={"Content-Type": "application/json"}
            )
            
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"\n✅ Search completed: {len(results)} results found")
                for result in results:
                    print(f"   - {result['filename']}: {result['similarity_score']:.3f}")
            
            return True
            
        else:
            print(f"❌ Upload failed: {upload_response.status_code} - {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing complete document processing workflow...")
    print("Make sure Redis and Celery worker are running!")
    print("="*60)
    
    success = test_full_document_workflow()
    if success:
        print("\n🎉 Complete workflow test passed!")
    else:
        print("\n❌ Workflow test failed. Check Redis and Celery worker.")