from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.calendar_service import CalendarService
from services.nlp_service import NLPService

app = FastAPI(title="AI Calendar Booking Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
calendar_service = CalendarService()
nlp_service = NLPService()

# Pydantic models
class BookingRequest(BaseModel):
    date: str
    time: str
    duration: int
    description: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    intent: str = None
    available_slots: list = []
    booking_info: dict = {}

@app.get("/")
async def root():
    return {"message": "AI Calendar Booking Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/book")
async def book_appointment(request: BookingRequest):
    try:
        # Create datetime string
        datetime_str = f"{request.date}T{request.time}:00"
        
        # Book the appointment
        result = calendar_service.book_appointment(
            datetime_str=datetime_str,
            duration_minutes=request.duration,
            title=request.description,
            description=request.description
        )
        
        if result['success']:
            return {"message": "Appointment booked successfully", "event_link": result.get('html_link')}
        else:
            raise HTTPException(status_code=400, detail={"error": result['message']})
            
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Extract intent and information from user message
        intent_info = nlp_service.extract_intent(request.message)
        
        response_text = ""
        available_slots = []
        booking_info = {}
        
        if intent_info['intent'] == 'book_appointment' and 'time' in intent_info and 'date' in intent_info:
            # User wants to book a specific time
            date_str = intent_info['date']
            requested_time = intent_info['time']
            duration = intent_info.get('duration', 60)
            
            # Check if the specific time is available
            datetime_str = f"{date_str}T{requested_time}:00"
            start_dt = datetime.fromisoformat(datetime_str)
            end_dt = start_dt + timedelta(minutes=duration)
            
            is_available = calendar_service.check_availability(
                start_dt.isoformat() + 'Z',
                end_dt.isoformat() + 'Z'
            )
            
            if is_available:
                # Book the appointment
                result = calendar_service.book_appointment(
                    datetime_str=datetime_str,
                    duration_minutes=duration,
                    title=f"Meeting - {request.message[:50]}",
                    description="Scheduled via AI Calendar Assistant"
                )
                
                if result['success']:
                    response_text = f"✅ Perfect! I've booked your meeting for {date_str} at {requested_time}. {result['message']}"
                    booking_info = {
                        'booked': True,
                        'date': date_str,
                        'time': requested_time,
                        'duration': duration
                    }
                else:
                    response_text = f"❌ Sorry, I couldn't book the appointment: {result['message']}"
            else:
                response_text = f"❌ Sorry, {requested_time} on {date_str} is not available. Let me show you some alternatives:"
                slots = calendar_service.get_free_time_slots(date_str, duration)
                available_slots = slots  # Show ALL available slots
                
                if available_slots:
                    response_text += f"\n\nHere are all {len(available_slots)} available times:"
                    # Show first 15 in the response text
                    for slot in available_slots[:15]:
                        response_text += f"\n• {slot['start']} - {slot['end']}"
                    
                    if len(available_slots) > 15:
                        response_text += f"\n... and {len(available_slots) - 15} more slots available!"
        
        elif intent_info['intent'] == 'check_availability':
            # Get date from the extracted info
            date_str = intent_info.get('date', datetime.now().date().isoformat())
            
            # Get ALL available slots for the ENTIRE day
            all_slots = calendar_service.get_free_time_slots(date_str)
            available_slots = all_slots  # Return ALL slots to frontend
            
            if all_slots:
                response_text = f"Here are ALL available time slots for {date_str} (9 AM - 9 PM):\n"
                
                # Group by time of day - Show ALL slots in each category
                morning_slots = []
                afternoon_slots = []
                evening_slots = []
                
                for slot in all_slots:
                    hour = int(slot['start_24'].split(':')[0])
                    if hour < 12:
                        morning_slots.append(slot)
                    elif 12 <= hour < 17:
                        afternoon_slots.append(slot)
                    else:
                        evening_slots.append(slot)
                
                # Show ALL morning slots
                if morning_slots:
                    response_text += f"\n🌅 **Morning ({len(morning_slots)} slots):**\n"
                    for slot in morning_slots:  # Show ALL morning slots
                        response_text += f"• {slot['start']} - {slot['end']}\n"
                
                # Show ALL afternoon slots
                if afternoon_slots:
                    response_text += f"\n☀️ **Afternoon ({len(afternoon_slots)} slots):**\n"
                    for slot in afternoon_slots:  # Show ALL afternoon slots
                        response_text += f"• {slot['start']} - {slot['end']}\n"
                
                # Show ALL evening slots
                if evening_slots:
                    response_text += f"\n🌙 **Evening ({len(evening_slots)} slots):**\n"
                    for slot in evening_slots:  # Show ALL evening slots
                        response_text += f"• {slot['start']} - {slot['end']}\n"
                
                # Show total count
                total_slots = len(all_slots)
                response_text += f"\n📊 **Total available slots: {total_slots}**"
                response_text += "\n\nWhich time works best for you?"
            else:
                response_text = f"Sorry, no available slots found for {date_str}. Would you like to try a different date?"
        
        elif intent_info['intent'] == 'book_appointment':
            response_text = "I'd be happy to help you schedule a meeting! Could you please specify:"
            response_text += "\n• What date? (today, tomorrow, or specific date)"
            response_text += "\n• What time? (e.g., 2 PM, 14:00)"
            response_text += "\n• How long? (30 minutes, 1 hour, etc.)"
            
            # Show today's availability as a starting point
            date_str = datetime.now().date().isoformat()
            slots = calendar_service.get_free_time_slots(date_str)
            available_slots = slots  # Show ALL available slots
        
        else:
            response_text = nlp_service.generate_response(intent_info['intent'], intent_info)
        
        return ChatResponse(
            response=response_text,
            intent=intent_info['intent'],
            available_slots=available_slots,
            booking_info=booking_info
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"Sorry, I encountered an error: {str(e)}",
            intent="error"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)