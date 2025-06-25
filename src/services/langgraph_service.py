from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from .calendar_service import CalendarService

from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class SchedulingState(TypedDict):
    """State for the LangGraph scheduling conversation workflow"""
    messages: List[BaseMessage]
    user_input: str
    intent: str
    date: Optional[str]
    time: Optional[str]
    duration: int
    meeting_title: str
    available_slots: List[Dict]
    booking_confirmed: bool
    booking_details: Dict
    response: str
    error: Optional[str]
    session_id: str
    next_action: str

class LangGraphSchedulingAgent:
    """LangGraph implementation for conversational calendar booking"""
    
    def __init__(self):
        self.calendar_service = CalendarService()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow with proper nodes and edges"""
        print("Building LangGraph workflow...")
        
        workflow = StateGraph(SchedulingState)
        
        workflow.add_node("extract_intent", self._extract_intent_node)
        workflow.add_node("check_availability", self._check_availability_node)
        workflow.add_node("book_appointment", self._book_appointment_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        workflow.set_entry_point("extract_intent")
        
        workflow.add_conditional_edges(
            "extract_intent",
            self._route_after_intent,
            {
                "check_availability": "check_availability",
                "book_directly": "book_appointment",
                "generate_response": "generate_response",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "check_availability", 
            self._route_after_availability,
            {
                "book_now": "book_appointment",
                "show_slots": "generate_response",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("book_appointment", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        compiled_workflow = workflow.compile()
        print("LangGraph workflow compiled successfully")
        
        return compiled_workflow
    
    def _extract_intent_node(self, state: SchedulingState) -> SchedulingState:
        """Extract intent from user message"""
        try:
            print(f"Extracting intent from: {state['user_input']}")
            
            message = state['user_input'].lower()
            
            if any(word in message for word in ['book', 'schedule', 'meeting', 'appointment', 'call']):
                state['intent'] = 'book_appointment'
            elif any(word in message for word in ['available', 'free', 'availability', 'check', 'when']):
                state['intent'] = 'check_availability'
            elif any(word in message for word in ['cancel', 'delete', 'remove']):
                state['intent'] = 'cancel_appointment'
            else:
                state['intent'] = 'general_chat'
            
            state['date'] = self._extract_date(message)
            state['time'] = self._extract_time(message)
            state['duration'] = self._extract_duration(message)
            
            if 'messages' not in state:
                state['messages'] = []
            state['messages'].append(HumanMessage(content=state['user_input']))
            
            print(f"Intent: {state['intent']}, Date: {state['date']}, Time: {state['time']}")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error extracting intent: {str(e)}"
            print(f"Intent extraction error: {state['error']}")
            import traceback
            traceback.print_exc()
            return state
    
    def _check_availability_node(self, state: SchedulingState) -> SchedulingState:
        """Check calendar availability"""
        try:
            print(f"Checking availability for date: {state['date']}")
            
            available_slots = self.calendar_service.get_free_time_slots(state['date'], state['duration'])
            state['available_slots'] = available_slots
            
            print(f"Found {len(available_slots)} available slots")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error checking availability: {str(e)}"
            print(f"Availability check error: {state['error']}")
            import traceback
            traceback.print_exc()
            return state
    
    def _book_appointment_node(self, state: SchedulingState) -> SchedulingState:
        """Book the appointment with availability check"""
        try:
            print(f"Booking appointment for {state['date']} at {state['time']}")
            
            if state['time'] and state['date']:
                datetime_str = f"{state['date']}T{state['time']}:00"
                
                from datetime import datetime, timedelta
                import pytz
                
                if datetime_str.endswith('+05:30') or datetime_str.endswith('+00:00'):
                    start_time = datetime.fromisoformat(datetime_str)
                else:
                    start_time = datetime.fromisoformat(datetime_str)
                    local_tz = pytz.timezone('Asia/Kolkata')
                    if start_time.tzinfo is None:
                        start_time = local_tz.localize(start_time)
                
                end_time = start_time + timedelta(minutes=state['duration'])
                
                print(f"Checking availability for {start_time} to {end_time}")
                
                is_available = self.calendar_service.check_availability(
                    start_time.isoformat(),
                    end_time.isoformat()
                )
                
                if not is_available:
                    state['error'] = f"Time slot {state['time']} on {state['date']} is already booked. Please choose a different time."
                    print(f"Time slot unavailable: {state['time']} on {state['date']}")
                    return state
                
                print("Time slot is available, proceeding with booking...")
                
                result = self.calendar_service.book_appointment(
                    datetime_str=datetime_str,
                    duration_minutes=state['duration'],
                    title=state['meeting_title'],
                    description="Scheduled via AI Calendar Assistant"
                )
                
                if result['success']:
                    state['booking_confirmed'] = True
                    state['booking_details'] = {
                        'date': state['date'],
                        'time': state['time'],
                        'duration': state['duration'],
                        'title': state['meeting_title'],
                        'event_link': result.get('html_link', '')
                    }
                    print("Booking successful")
                else:
                    state['error'] = result['message']
                    print(f"Booking failed: {state['error']}")
            else:
                state['error'] = "Missing date or time for booking"
                print(f"Missing booking info: {state['error']}")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error booking appointment: {str(e)}"
            print(f"Booking error: {state['error']}")
            import traceback
            traceback.print_exc()
            return state
    
    def _generate_response_node(self, state: SchedulingState) -> SchedulingState:
        """Generate final response"""
        try:
            print(f"Generating response for intent: {state['intent']}")
            
            if state.get('booking_confirmed', False):
                booking_details = state['booking_details']
                response = f"Perfect! I've successfully booked your meeting:\n\n"
                response += f"**Date:** {booking_details['date']}\n"
                response += f"**Time:** {booking_details['time']}\n"
                response += f"**Duration:** {booking_details['duration']} minutes\n"
                response += f"**Title:** {booking_details['title']}\n"
                
                if booking_details.get('event_link'):
                    response += f"\n[View in Google Calendar]({booking_details['event_link']})"
                
                response += f"\n\nYour appointment has been confirmed!"
                
            elif state['intent'] == 'book_appointment' and state.get('available_slots', []):
                available_slots = state['available_slots']
                
                date_obj = datetime.strptime(state['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')
                
                requested_time = state.get('time')
                if requested_time:
                    response = f"I'd be happy to schedule a meeting for **{requested_time}** on **{formatted_date}**!\n\n"
                    response += f"Here are the available time slots for that day. Please click on your preferred slot to book:\n\n"
                else:
                    response = f"I'd be happy to help you schedule a meeting on **{formatted_date}**!\n\n"
                    response += f"Here are the available time slots. Please click on your preferred slot to book:\n\n"
                
                morning_slots = []
                afternoon_slots = []
                evening_slots = []
                
                for slot in available_slots:
                    hour = int(slot['start_24'].split(':')[0])
                    if hour < 12:
                        morning_slots.append(slot)
                    elif 12 <= hour < 17:
                        afternoon_slots.append(slot)
                    else:
                        evening_slots.append(slot)
                
                if morning_slots:
                    response += f"**Morning ({len(morning_slots)} slots):**\n"
                    for slot in morning_slots:
                        response += f"• {slot['start']} - {slot['end']}\n"
                
                if afternoon_slots:
                    response += f"\n**Afternoon ({len(afternoon_slots)} slots):**\n"
                    for slot in afternoon_slots:
                        response += f"• {slot['start']} - {slot['end']}\n"
                
                if evening_slots:
                    response += f"\n**Evening ({len(evening_slots)} slots):**\n"
                    for slot in evening_slots:
                        response += f"• {slot['start']} - {slot['end']}\n"
                
                response += f"\n**Total available slots: {len(available_slots)}**"
                response += f"\n\nClick any slot below to open the booking form!"
                
                if requested_time:
                    requested_time_available = False
                    for slot in available_slots:
                        if requested_time in slot['start'] or requested_time in slot['start_24']:
                            requested_time_available = True
                            break
                    
                    if requested_time_available:
                        response += f"\n\nGood news! Your requested time ({requested_time}) is available!"
                    else:
                        response += f"\n\nSorry, your requested time ({requested_time}) is not available. Please choose from the available slots above."
            
            elif state['intent'] == 'check_availability' and state.get('available_slots', []):
                available_slots = state['available_slots']
                
                date_obj = datetime.strptime(state['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')
                
                response = f"Here are your **AVAILABLE** time slots for **{formatted_date}**:\n\n"
                
                morning_slots = []
                afternoon_slots = []
                evening_slots = []
                
                for slot in available_slots:
                    hour = int(slot['start_24'].split(':')[0])
                    if hour < 12:
                        morning_slots.append(slot)
                    elif 12 <= hour < 17:
                        afternoon_slots.append(slot)
                    else:
                        evening_slots.append(slot)
                
                if morning_slots:
                    response += f"### 🌅 **Morning** ({len(morning_slots)} slots available)\n"
                    for slot in morning_slots:
                        response += f"**⏰ {slot['start']} → {slot['end']}**\n\n"
                
                if afternoon_slots:
                    response += f"### ☀️ **Afternoon** ({len(afternoon_slots)} slots available)\n"
                    for slot in afternoon_slots:
                        response += f"**⏰ {slot['start']} → {slot['end']}**\n\n"
                
                if evening_slots:
                    response += f"### 🌆 **Evening** ({len(evening_slots)} slots available)\n"
                    for slot in evening_slots:
                        response += f"**⏰ {slot['start']} → {slot['end']}**\n\n"
                
                response += f"### 📊 **Summary**\n"
                response += f"**Total Available Slots: {len(available_slots)}**\n\n"
                response += f"*Please book flawlessly!*"
                
            elif (state['intent'] in ['check_availability', 'book_appointment']) and not state.get('available_slots', []):
                date_obj = datetime.strptime(state['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')
                
                response = f"Sorry, no free time slots available for **{formatted_date}**. You seem to be fully booked!\n\nTry checking another date or let me know if you'd like to see tomorrow's availability."
                
            elif state['intent'] == 'book_appointment':
                response = "I'd be happy to help you schedule a meeting! Could you please specify:\n• What date? (today, tomorrow, or specific date)\n• What time? (e.g., 2 PM, 14:00)\n• How long? (30 minutes, 1 hour, etc.)"
                
            else:
                response = "I'm your AI calendar assistant! I can help you:\n• Check availability (conflict-free slots only)\n• Schedule meetings\n• Book appointments\n\nWhat would you like to do?"
            
            state['response'] = response
            
            if 'messages' not in state:
                state['messages'] = []
            state['messages'].append(AIMessage(content=response))
            
            print("Response generated successfully")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error generating response: {str(e)}"
            print(f"Response generation error: {state['error']}")
            return state
    
    def _handle_error_node(self, state: SchedulingState) -> SchedulingState:
        """Handle errors"""
        error_response = f"Sorry, I encountered an error: {state['error']}"
        state['response'] = error_response
        
        if 'messages' not in state:
            state['messages'] = []
        state['messages'].append(AIMessage(content=error_response))
        
        print(f"Error handled: {error_response}")
        
        return state
    
    def _route_after_intent(self, state: SchedulingState) -> str:
        """Route after intent extraction"""
        if state.get('error'):
            return "error"
        elif state['intent'] == 'check_availability':
            return "check_availability"
        elif state['intent'] == 'book_appointment':
            message = state['user_input'].lower()
            
            if 'quickbook' in message or 'quick book' in message:
                return "check_availability"
            elif state.get('time') and state.get('date'):
                return "book_directly"
            else:
                return "check_availability"
        else:
            return "generate_response"
    
    def _route_after_availability(self, state: SchedulingState) -> str:
        """Route after checking availability"""
        if state.get('error'):
            return "error"
        else:
            message = state['user_input'].lower()
            
            if 'quickbook' in message or 'quick book' in message:
                return "show_slots"
            elif state['intent'] == 'book_appointment' and state.get('time'):
                return "book_now"
            else:
                return "show_slots"
    
    def _weekday_to_number(self, weekday_name: str) -> int:
        """Convert weekday name to number (0=Monday, 6=Sunday)"""
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        return weekday_map.get(weekday_name.lower(), 0)
    
    def _extract_date(self, message: str) -> str:
        """Extract date from message"""
        try:
            print(f"Extracting date from: {message}")
            
            if re.search(r'\btoday\b', message):
                result = datetime.now().date().isoformat()
                print(f"Found 'today': {result}")
                return result
            
            if re.search(r'\btomorrow\b', message):
                result = (datetime.now() + timedelta(days=1)).date().isoformat()
                print(f"Found 'tomorrow': {result}")
                return result
            
            this_weekday_match = re.search(r'\bthis\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', message, re.IGNORECASE)
            if this_weekday_match:
                weekday_name = this_weekday_match.group(1).lower()
                weekday_num = self._weekday_to_number(weekday_name)
                result = self._get_next_weekday(weekday_num)
                print(f"Found 'this {weekday_name}': {result}")
                return result
            
            weekday_match = re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', message, re.IGNORECASE)
            if weekday_match:
                weekday_name = weekday_match.group(1).lower()
                weekday_num = self._weekday_to_number(weekday_name)
                result = self._get_next_weekday(weekday_num)
                print(f"Found weekday '{weekday_name}': {result}")
                return result
            
            if re.search(r'\bnext week\b', message):
                result = (datetime.now() + timedelta(days=7)).date().isoformat()
                print(f"Found 'next week': {result}")
                return result
            
            iso_date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', message)
            if iso_date_match:
                result = iso_date_match.group(1)
                print(f"Found ISO date: {result}")
                return result
            
            us_date_match = re.search(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', message)
            if us_date_match:
                month, day, year = us_date_match.groups()
                result = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"Found US date: {result}")
                return result
            
            result = datetime.now().date().isoformat()
            print(f"No specific date found, defaulting to today: {result}")
            return result
            
        except Exception as e:
            print(f"Date extraction error: {str(e)}")
            import traceback
            traceback.print_exc()
            return datetime.now().date().isoformat()
    
    def _extract_time(self, message: str) -> Optional[str]:
        """Extract time from message"""
        time_patterns = [
            r'\b(\d{1,2}):(\d{2})\s*(am|pm)\b',
            r'\b(\d{1,2})\s*(am|pm)\b',
            r'\b(\d{1,2}):(\d{2})\b'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message)
            if match:
                if len(match.groups()) == 3:
                    hour, minute, period = match.groups()
                    hour = int(hour)
                    if period.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif period.lower() == 'am' and hour == 12:
                        hour = 0
                    return f"{hour:02d}:{minute}"
                elif len(match.groups()) == 2:
                    hour, period = match.groups()
                    hour = int(hour)
                    if period.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif period.lower() == 'am' and hour == 12:
                        hour = 0
                    return f"{hour:02d}:00"
                else:
                    hour, minute = match.groups()
                    return f"{int(hour):02d}:{minute}"
        
        return None
    
    def _extract_duration(self, message: str) -> int:
        """Extract duration from message"""
        duration_match = re.search(r'\b(\d+)\s*(hour|hr|minute|min)', message)
        if duration_match:
            duration_value = int(duration_match.group(1))
            duration_unit = duration_match.group(2)
            if 'hour' in duration_unit or 'hr' in duration_unit:
                return duration_value * 60
            else:
                return duration_value
        return 60
    
    def _get_next_weekday(self, weekday: int) -> str:
        """Get the next occurrence of a weekday (0=Monday, 6=Sunday)"""
        try:
            today = datetime.now().date()
            days_ahead = weekday - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
            print(f"Weekday calculation - Today: {today} (weekday {today.weekday()}), Target weekday: {weekday}, Days ahead: {days_ahead}, Result: {target_date}")
            return target_date.isoformat()
        except Exception as e:
            print(f"Weekday calculation error: {str(e)}")
            return datetime.now().date().isoformat()
    
    def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a message through the LangGraph workflow"""
        try:
            print(f"\nStarting LangGraph workflow for: {message}")
            
            initial_state: SchedulingState = {
                "messages": [],
                "user_input": message,
                "intent": "",
                "date": None,
                "time": None,
                "duration": 60,
                "meeting_title": "Meeting",
                "available_slots": [],
                "booking_confirmed": False,
                "booking_details": {},
                "response": "",
                "error": None,
                "session_id": session_id,
                "next_action": ""
            }
            
            final_state = self.workflow.invoke(initial_state)
            
            print("LangGraph workflow completed successfully")
            print(f"Returning {len(final_state['available_slots'])} available slots")
            
            return {
                "response": final_state["response"],
                "intent": final_state["intent"],
                "available_slots": final_state["available_slots"],
                "booking_info": {
                    "booked": final_state["booking_confirmed"],
                    **final_state["booking_details"]
                } if final_state["booking_confirmed"] else {}
            }
            
        except Exception as e:
            print(f"LangGraph workflow error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "intent": "error",
                "available_slots": [],
                "booking_info": {}
            }

SchedulingWorkflow = LangGraphSchedulingAgent()