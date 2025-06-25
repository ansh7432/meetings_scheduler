from fastapi import Depends
from .services.calendar_service import CalendarService
from .services.nlp_service import NLPService

def get_calendar_service() -> CalendarService:
    return CalendarService()

def get_nlp_service() -> NLPService:
    return NLPService()