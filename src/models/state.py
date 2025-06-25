from typing import List, Optional, Dict, Any
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