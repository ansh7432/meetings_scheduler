from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentRequest(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class AppointmentResponse(BaseModel):
    appointment_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str

class AvailabilityResponse(BaseModel):
    available_slots: list[datetime]