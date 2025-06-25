from src.services.calendar_service import CalendarService
from src.services.nlp_service import NLPService
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def calendar_service():
    return CalendarService()

@pytest.fixture
def nlp_service():
    return NLPService()

def test_check_availability(calendar_service):
    # Mock the response from the Google Calendar API
    calendar_service.check_availability = MagicMock(return_value=True)
    
    result = calendar_service.check_availability("2023-10-25T15:00:00", "2023-10-25T16:00:00")
    assert result is True

def test_book_appointment(calendar_service):
    # Mock the booking method
    calendar_service.book_appointment = MagicMock(return_value="Appointment booked successfully.")
    
    result = calendar_service.book_appointment("2023-10-25T15:00:00", "2023-10-25T16:00:00", "Test Meeting")
    assert result == "Appointment booked successfully."

def test_extract_intent(nlp_service):
    # Mock the intent extraction
    nlp_service.extract_intent = MagicMock(return_value={"intent": "book_appointment", "time": "tomorrow afternoon"})
    
    result = nlp_service.extract_intent("I want to schedule a call for tomorrow afternoon.")
    assert result["intent"] == "book_appointment"
    assert result["time"] == "tomorrow afternoon"