from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from .calendar_service import CalendarService

# Define SchedulingState directly here to avoid import issues
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class SchedulingState(TypedDict):
    """State for the LangGraph scheduling conversation workflow"""
    
    # Conversation history
    messages: List[BaseMessage]
    
    # Current user input
    user_input: str
    
    # Extracted information
    intent: str
    date: Optional[str]
    time: Optional[str]
    duration: int
    meeting_title: str
    
    # Calendar data
    available_slots: List[Dict]
    booking_confirmed: bool
    booking_details: Dict
    
    # Response
    response: str
    error: Optional[str]
    
    # Session info
    session_id: str
    
    # Next action for routing
    next_action: str

class LangGraphSchedulingAgent:
    """Real LangGraph implementation for conversational calendar booking"""
    
    def __init__(self):
        self.calendar_service = CalendarService()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow with proper nodes and edges"""
        print("🔧 [LANGGRAPH] Building workflow...")
        
        # Initialize StateGraph with our state schema
        workflow = StateGraph(SchedulingState)
        
        # Add nodes (each node is a function that processes the state)
        workflow.add_node("extract_intent", self._extract_intent_node)
        workflow.add_node("check_availability", self._check_availability_node)
        workflow.add_node("book_appointment", self._book_appointment_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("extract_intent")
        
        # Add conditional edges for routing
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
        
        # Terminal edges
        workflow.add_edge("book_appointment", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        compiled_workflow = workflow.compile()
        print("✅ [LANGGRAPH] Workflow compiled successfully!")
        
        return compiled_workflow
    
    def _extract_intent_node(self, state: SchedulingState) -> SchedulingState:
        """LangGraph Node: Extract intent from user message"""
        try:
            print(f"🔍 [EXTRACT_INTENT] Processing: {state['user_input']}")
            
            message = state['user_input'].lower()
            
            # Intent classification
            if any(word in message for word in ['book', 'schedule', 'meeting', 'appointment', 'call']):
                state['intent'] = 'book_appointment'
            elif any(word in message for word in ['available', 'free', 'availability', 'check', 'when']):
                state['intent'] = 'check_availability'
            elif any(word in message for word in ['cancel', 'delete', 'remove']):
                state['intent'] = 'cancel_appointment'
            else:
                state['intent'] = 'general_chat'
            
            # Extract date
            state['date'] = self._extract_date(message)
            
            # Extract time
            state['time'] = self._extract_time(message)
            
            # Extract duration
            state['duration'] = self._extract_duration(message)
            
            # Add message to conversation history
            if 'messages' not in state:
                state['messages'] = []
            state['messages'].append(HumanMessage(content=state['user_input']))
            
            print(f"✅ [EXTRACT_INTENT] Intent: {state['intent']}, Date: {state['date']}, Time: {state['time']}")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error extracting intent: {str(e)}"
            print(f"❌ [EXTRACT_INTENT] Error: {state['error']}")
            import traceback
            traceback.print_exc()
            return state
    
    def _check_availability_node(self, state: SchedulingState) -> SchedulingState:
        """LangGraph Node: Check calendar availability - TRUST THE CALENDAR SERVICE"""
        try:
            print(f"📅 [CHECK_AVAILABILITY] Checking for date: {state['date']}")
            
            # Get free slots from calendar service (it already filters conflicts properly)
            available_slots = self.calendar_service.get_free_time_slots(state['date'], state['duration'])
            
            # The calendar service already does proper conflict detection
            # No need for double-checking - trust the service
            state['available_slots'] = available_slots
            
            print(f"✅ [CHECK_AVAILABILITY] Found {len(available_slots)} truly available slots")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error checking availability: {str(e)}"
            print(f"❌ [CHECK_AVAILABILITY] Error: {state['error']}")
            import traceback
            traceback.print_exc()
            return state
    
    def _book_appointment_node(self, state: SchedulingState) -> SchedulingState:
        """LangGraph Node: Book the appointment (with availability check)"""
        try:
            print(f"📝 [BOOK_APPOINTMENT] Booking for {state['date']} at {state['time']}")
            
            if state['time'] and state['date']:
                # FIRST: Check if the time slot is available
                datetime_str = f"{state['date']}T{state['time']}:00"
                
                # Parse the datetime to check availability
                from datetime import datetime, timedelta
                import pytz
                
                # Parse the start time
                if datetime_str.endswith('+05:30') or datetime_str.endswith('+00:00'):
                    start_time = datetime.fromisoformat(datetime_str)
                else:
                    # Assume local timezone
                    start_time = datetime.fromisoformat(datetime_str)
                    local_tz = pytz.timezone('Asia/Kolkata')
                    if start_time.tzinfo is None:
                        start_time = local_tz.localize(start_time)
                
                # Calculate end time
                end_time = start_time + timedelta(minutes=state['duration'])
                
                print(f"🔍 [BOOK_APPOINTMENT] Checking availability for {start_time} to {end_time}")
                
                # Check if the slot is available
                is_available = self.calendar_service.check_availability(
                    start_time.isoformat(),
                    end_time.isoformat()
                )
                
                if not is_available:
                    # Time slot is already occupied
                    state['error'] = f"❌ Time slot {state['time']} on {state['date']} is already booked. Please choose a different time."
                    print(f"❌ [BOOK_APPOINTMENT] Time slot unavailable: {state['time']} on {state['date']}")
                    return state
                
                print(f"✅ [BOOK_APPOINTMENT] Time slot is available, proceeding with booking...")
                
                # Proceed with booking since slot is available
                result = self.calendar_service.book_appointment(
                    datetime_str=datetime_str,
                    duration_minutes=state['duration'],
                    title=state['meeting_title'],
                    description="Scheduled via AI Calendar Assistant (LangGraph)"
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
                    print(f"✅ [BOOK_APPOINTMENT] Successfully booked!")
                else:
                    state['error'] = result['message']
                    print(f"❌ [BOOK_APPOINTMENT] Booking failed: {state['error']}")
            else:
                state['error'] = "Missing date or time for booking"
                print(f"❌ [BOOK_APPOINTMENT] Missing info: {state['error']}")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error booking appointment: {str(e)}"
            print(f"❌ [BOOK_APPOINTMENT] Error: {state['error']}")
            import traceback
            traceback.print_exc()
            return state
    
    def _generate_response_node(self, state: SchedulingState) -> SchedulingState:
        """LangGraph Node: Generate final response"""
        try:
            print(f"💬 [GENERATE_RESPONSE] Creating response for intent: {state['intent']}")
            
            if state.get('booking_confirmed', False):
                booking_details = state['booking_details']
                response = f"✅ Perfect! I've successfully booked your meeting:\n\n"
                response += f"📅 **Date:** {booking_details['date']}\n"
                response += f"🕒 **Time:** {booking_details['time']}\n"
                response += f"⏱️ **Duration:** {booking_details['duration']} minutes\n"
                response += f"📝 **Title:** {booking_details['title']}\n"
                
                if booking_details.get('event_link'):
                    response += f"\n🔗 [View in Google Calendar]({booking_details['event_link']})"
                
                response += f"\n\n🎉 Your appointment has been confirmed!"
                
            elif state['intent'] == 'book_appointment' and state.get('error'):
                # Handle booking errors (like time slot conflicts)
                response = state['error']
                
                # If it's a conflict error, suggest alternatives
                if "already booked" in state['error'].lower() or "unavailable" in state['error'].lower():
                    response += f"\n\n💡 **Suggestions:**\n"
                    response += f"• Try asking: 'What times are free on {state['date']}?'\n"
                    response += f"• Choose a different time slot\n"
                    response += f"• Check availability for another day"
            
            elif state['intent'] == 'check_availability' and state.get('available_slots', []):
                available_slots = state['available_slots']
                
                # Format the date nicely
                date_obj = datetime.strptime(state['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')  # e.g., "Friday, June 28, 2025"
                
                response = f"Here are your **AVAILABLE** time slots for **{formatted_date}** (conflict-free times only):\n"
                
                # Group by time of day - ONLY showing free slots
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
                    response += f"\n🌅 **Morning ({len(morning_slots)} slots):**\n"
                    for slot in morning_slots:
                        response += f"• {slot['start']} - {slot['end']}\n"
                
                if afternoon_slots:
                    response += f"\n☀️ **Afternoon ({len(afternoon_slots)} slots):**\n"
                    for slot in afternoon_slots:
                        response += f"• {slot['start']} - {slot['end']}\n"
                
                if evening_slots:
                    response += f"\n🌙 **Evening ({len(evening_slots)} slots):**\n"
                    for slot in evening_slots:
                        response += f"• {slot['start']} - {slot['end']}\n"
                
                response += f"\n📊 **Total available slots: {len(available_slots)}**"
                
                if len(available_slots) > 0:
                    response += "\n\n💡 All conflicts have been filtered out. Click any slot below to book!"
                else:
                    response += "\n\n😔 No free slots available for this day. Try a different date?"
                
            elif state['intent'] == 'check_availability' and not state.get('available_slots', []):
                # Format the date nicely
                date_obj = datetime.strptime(state['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')
                
                response = f"😔 Sorry, no free time slots available for **{formatted_date}**. You seem to be fully booked!\n\nTry checking another date or let me know if you'd like to see tomorrow's availability."
                
            elif state['intent'] == 'book_appointment':
                response = "I'd be happy to help you schedule a meeting! Could you please specify:\n• What date? (today, tomorrow, or specific date)\n• What time? (e.g., 2 PM, 14:00)\n• How long? (30 minutes, 1 hour, etc.)"
                
            else:
                response = "I'm your AI calendar assistant powered by LangGraph! I can help you:\n• Check availability (conflict-free slots only)\n• Schedule meetings\n• Book appointments\n\nWhat would you like to do?"
            
            state['response'] = response
            
            # Add AI response to conversation history
            if 'messages' not in state:
                state['messages'] = []
            state['messages'].append(AIMessage(content=response))
            
            print(f"✅ [GENERATE_RESPONSE] Response created")
            
            return state
            
        except Exception as e:
            state['error'] = f"Error generating response: {str(e)}"
            print(f"❌ [GENERATE_RESPONSE] Error: {state['error']}")
            return state
    
    def _handle_error_node(self, state: SchedulingState) -> SchedulingState:
        """LangGraph Node: Handle errors"""
        error_response = f"Sorry, I encountered an error: {state['error']}"
        state['response'] = error_response
        
        if 'messages' not in state:
            state['messages'] = []
        state['messages'].append(AIMessage(content=error_response))
        
        print(f"❌ [HANDLE_ERROR] {error_response}")
        
        return state
    
    def _route_after_intent(self, state: SchedulingState) -> str:
        """Conditional edge: Route after intent extraction"""
        if state.get('error'):
            return "error"
        elif state['intent'] == 'check_availability':
            return "check_availability"
        elif state['intent'] == 'book_appointment' and state.get('time') and state.get('date'):
            return "book_directly"
        elif state['intent'] == 'book_appointment':
            return "check_availability"
        else:
            return "generate_response"
    
    def _route_after_availability(self, state: SchedulingState) -> str:
        """Conditional edge: Route after checking availability"""
        if state.get('error'):
            return "error"
        elif state['intent'] == 'book_appointment' and state.get('time') and state.get('available_slots'):
            return "book_now"
        else:
            return "show_slots"
    
    def _weekday_to_number(self, weekday_name: str) -> int:
        """Convert weekday name to number (0=Monday, 6=Sunday)"""
        weekday_map = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        return weekday_map.get(weekday_name.lower(), 0)
    
    def _extract_date(self, message: str) -> str:
        """Extract date from message with proper weekday handling"""
        try:
            print(f"🔍 [DATE_EXTRACTION] Processing: {message}")
            
            # Check for specific patterns in order of priority
            
            # Today/Tomorrow
            if re.search(r'\btoday\b', message):
                result = datetime.now().date().isoformat()
                print(f"✅ [DATE_EXTRACTION] Found 'today': {result}")
                return result
            
            if re.search(r'\btomorrow\b', message):
                result = (datetime.now() + timedelta(days=1)).date().isoformat()
                print(f"✅ [DATE_EXTRACTION] Found 'tomorrow': {result}")
                return result
            
            # This + weekday (e.g., "this friday")
            this_weekday_match = re.search(r'\bthis\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', message, re.IGNORECASE)
            if this_weekday_match:
                weekday_name = this_weekday_match.group(1).lower()
                weekday_num = self._weekday_to_number(weekday_name)
                result = self._get_next_weekday(weekday_num)
                print(f"✅ [DATE_EXTRACTION] Found 'this {weekday_name}': {result}")
                return result
            
            # Just weekday name (e.g., "friday", "saturday")
            weekday_match = re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', message, re.IGNORECASE)
            if weekday_match:
                weekday_name = weekday_match.group(1).lower()
                weekday_num = self._weekday_to_number(weekday_name)
                result = self._get_next_weekday(weekday_num)
                print(f"✅ [DATE_EXTRACTION] Found weekday '{weekday_name}': {result}")
                return result
            
            # Next week
            if re.search(r'\bnext week\b', message):
                result = (datetime.now() + timedelta(days=7)).date().isoformat()
                print(f"✅ [DATE_EXTRACTION] Found 'next week': {result}")
                return result
            
            # ISO date format (YYYY-MM-DD)
            iso_date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', message)
            if iso_date_match:
                result = iso_date_match.group(1)
                print(f"✅ [DATE_EXTRACTION] Found ISO date: {result}")
                return result
            
            # US date format (MM/DD/YYYY)
            us_date_match = re.search(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', message)
            if us_date_match:
                month, day, year = us_date_match.groups()
                result = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"✅ [DATE_EXTRACTION] Found US date: {result}")
                return result
            
            # Default to today
            result = datetime.now().date().isoformat()
            print(f"🔄 [DATE_EXTRACTION] No specific date found, defaulting to today: {result}")
            return result
            
        except Exception as e:
            print(f"❌ [DATE_EXTRACTION] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback to today
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
                if len(match.groups()) == 3:  # Hour:minute am/pm
                    hour, minute, period = match.groups()
                    hour = int(hour)
                    if period.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif period.lower() == 'am' and hour == 12:
                        hour = 0
                    return f"{hour:02d}:{minute}"
                elif len(match.groups()) == 2:  # Hour am/pm
                    hour, period = match.groups()
                    hour = int(hour)
                    if period.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif period.lower() == 'am' and hour == 12:
                        hour = 0
                    return f"{hour:02d}:00"
                else:  # 24-hour format
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
        return 60  # Default 1 hour
    
    def _get_next_weekday(self, weekday: int) -> str:
        """Get the next occurrence of a weekday (0=Monday, 6=Sunday)"""
        try:
            today = datetime.now().date()
            days_ahead = weekday - today.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
            print(f"🔍 [WEEKDAY_CALC] Today: {today} (weekday {today.weekday()}), Target weekday: {weekday}, Days ahead: {days_ahead}, Result: {target_date}")
            return target_date.isoformat()
        except Exception as e:
            print(f"❌ [WEEKDAY_CALC] Error: {str(e)}")
            return datetime.now().date().isoformat()
    
    def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a message through the LangGraph workflow"""
        try:
            print(f"\n🚀 [LANGGRAPH] Starting workflow for: {message}")
            
            # Create initial state - initialize all required fields
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
            
            # Run the LangGraph workflow
            final_state = self.workflow.invoke(initial_state)
            
            print(f"✅ [LANGGRAPH] Workflow completed successfully!")
            print(f"📊 [LANGGRAPH] Returning {len(final_state['available_slots'])} available slots")
            
            # Return response in API format
            return {
                "response": final_state["response"],
                "intent": final_state["intent"],
                "available_slots": final_state["available_slots"],  # Only truly free slots
                "booking_info": {
                    "booked": final_state["booking_confirmed"],
                    **final_state["booking_details"]
                } if final_state["booking_confirmed"] else {}
            }
            
        except Exception as e:
            print(f"❌ [LANGGRAPH] Workflow error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "intent": "error",
                "available_slots": [],
                "booking_info": {}
            }

# Alias for backward compatibility
SchedulingWorkflow = LangGraphSchedulingAgent