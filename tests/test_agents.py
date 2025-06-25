from fastapi import FastAPI
from agents.booking_agent import BookingAgent
from agents.conversation_manager import ConversationManager
from services.calendar_service import CalendarService
from services.nlp_service import NLPService

# Initialize FastAPI app
app = FastAPI()

# Initialize services and agents
calendar_service = CalendarService()
nlp_service = NLPService()
booking_agent = BookingAgent(calendar_service, nlp_service)
conversation_manager = ConversationManager()

# Example test cases for BookingAgent
def test_booking_agent():
    # Test case 1: Schedule a call for tomorrow afternoon
    response = booking_agent.handle_user_input("Hey, I want to schedule a call for tomorrow afternoon.")
    assert response == "Sure! Let me check the availability for tomorrow afternoon."

    # Test case 2: Check availability for this Friday
    response = booking_agent.handle_user_input("Do you have any free time this Friday?")
    assert response == "Let me check the availability for this Friday."

    # Test case 3: Book a meeting between 3-5 PM next week
    response = booking_agent.handle_user_input("Book a meeting between 3-5 PM next week.")
    assert response == "I will check the availability for a meeting between 3-5 PM next week."

# Run tests
if __name__ == "__main__":
    test_booking_agent()