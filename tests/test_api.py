from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_book_appointment():
    response = client.post("/api/book", json={
        "date": "2023-10-10",
        "time": "15:00",
        "duration": 30,
        "description": "Meeting with client"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Appointment booked successfully"}

def test_check_availability():
    response = client.get("/api/availability", params={
        "date": "2023-10-10",
        "time": "15:00",
        "duration": 30
    })
    assert response.status_code == 200
    assert response.json() == {"available": True}

def test_invalid_booking():
    response = client.post("/api/book", json={
        "date": "2023-10-10",
        "time": "25:00",  # Invalid time
        "duration": 30,
        "description": "Invalid meeting"
    })
    assert response.status_code == 400
    assert "error" in response.json()

def test_no_availability():
    response = client.get("/api/availability", params={
        "date": "2023-10-10",
        "time": "15:00",
        "duration": 60  # Assuming no availability for this duration
    })
    assert response.status_code == 200
    assert response.json() == {"available": False}