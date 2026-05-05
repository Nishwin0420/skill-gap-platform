from fastapi.testclient import TestClient
from backend.main import app

def test_app():
    print("Initializing TestClient...")
    client = TestClient(app)
    
    print("Testing GET / ...")
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        test_app()
        print("Backend verified successfully!")
    except Exception as e:
        print(f"Backend verification failed: {e}")
