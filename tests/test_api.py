from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_video_validation_error():
    # Missing required fields
    response = client.post("/generate", json={})
    assert response.status_code == 422

@patch("src.main.generate_video")
def test_generate_video_success(mock_generate):
    mock_generate.return_value = "/tmp/fake_video.mp4"
    
    payload = {
        "name": "test-video",
        "duration": 5,
        "visuals": [
            {
                "type": "TEXT",
                "text": "Hello Test",
                "enterStart": 0,
                "enterEnd": 1
            }
        ]
    }
    
    # We mock FileResponse to avoid actual file read errors in this unit test
    # or we can write a test that doesn't check the response content but just the status code
    # However, FileResponse reads the file. So we need the file to exist or mock FileResponse.
    # Simpler: just ensure mock returns a file that exists or mock the response entirely.
    
    # Let's create a dummy file
    with open("dummy_video.mp4", "w") as f:
        f.write("fake video content")
        
    mock_generate.return_value = "dummy_video.mp4"

    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "video/mp4"
    
    # Cleanup
    import os
    if os.path.exists("dummy_video.mp4"):
        os.remove("dummy_video.mp4")
