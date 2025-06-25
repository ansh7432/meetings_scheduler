from langgraph import LangGraph
from services.calendar_service import CalendarService
from services.nlp_service import NLPService

class BookingAgent:
    def __init__(self):
        self.nlp_service = NLPService()
        self.calendar_service = CalendarService()
        self.conversation_state = {}

    def handle_user_input(self, user_input):
        intent, entities = self.nlp_service.process_input(user_input)
        self.conversation_state['intent'] = intent
        self.conversation_state['entities'] = entities

        if intent == 'schedule_appointment':
            return self.schedule_appointment(entities)
        elif intent == 'check_availability':
            return self.check_availability(entities)
        else:
            return "I'm sorry, I didn't understand that."

    def check_availability(self, entities):
        date = entities.get('date')
        time_range = entities.get('time_range')
        available_slots = self.calendar_service.check_availability(date, time_range)
        
        if available_slots:
            return f"Here are the available slots: {', '.join(available_slots)}"
        else:
            return "Unfortunately, there are no available slots."

    def schedule_appointment(self, entities):
        date = entities.get('date')
        time_slot = entities.get('time_slot')
        
        if self.calendar_service.book_appointment(date, time_slot):
            return f"Your appointment has been booked for {date} at {time_slot}."
        else:
            return "There was an error booking your appointment. Please try again."