from fastapi import APIRouter, HTTPException
from src.services.calendar_service import CalendarService
from src.agents.booking_agent import BookingAgent
from src.models.schemas import AppointmentRequest, AppointmentResponse

router = APIRouter()
calendar_service = CalendarService()
booking_agent = BookingAgent()

@router.post("/book-appointment", response_model=AppointmentResponse)
async def book_appointment(appointment_request: AppointmentRequest):
    try:
        # Use the booking agent to process the request
        available_slots = await calendar_service.check_availability(appointment_request)
        if not available_slots:
            raise HTTPException(status_code=404, detail="No available slots found.")

        # Suggest a suitable time slot
        suggested_slot = booking_agent.suggest_time_slot(available_slots)
        
        # Confirm booking
        booking_confirmation = await calendar_service.book_appointment(suggested_slot)
        
        return AppointmentResponse(confirmation=booking_confirmation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))