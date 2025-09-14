import requests

def test_basic_api():
    """Test basic API functionality"""
    try:
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        print("✅ Basic API test passed")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Basic API test failed: {e}")

if __name__ == "__main__":
    test_basic_api()