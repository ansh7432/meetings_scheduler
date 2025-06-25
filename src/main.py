from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.calendar_service import CalendarService
from services.langgraph_service import LangGraphSchedulingAgent

app = FastAPI(title="AI Calendar Booking Agent with REAL LangGraph", version="3.0.0")

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
print("🚀 Initializing LangGraph Agent...")
langgraph_agent = LangGraphSchedulingAgent()
print("✅ LangGraph Agent ready!")

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
    return {
        "message": "AI Calendar Booking Agent with REAL LangGraph", 
        "version": "3.0.0", 
        "framework": "LangGraph StateGraph",
        "status": "✅ Ready",
        "config_source": "Environment Variables" if os.getenv('GOOGLE_CLIENT_ID') else "credentials.json"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "framework": "Real LangGraph StateGraph v0.4.9",
        "features": ["State Management", "Conditional Routing", "Conversation Flow"],
        "google_auth": "Environment Variables" if os.getenv('GOOGLE_CLIENT_ID') else "File-based"
    }

@app.post("/api/book")
async def book_appointment(request: BookingRequest):
    """Direct booking endpoint"""
    try:
        datetime_str = f"{request.date}T{request.time}:00"
        
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
    """Chat endpoint using REAL LangGraph workflow"""
    try:
        print(f"\n📨 Received chat request: {request.message}")
        
        # Process message through REAL LangGraph workflow
        result = langgraph_agent.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            available_slots=result["available_slots"],
            booking_info=result["booking_info"]
        )
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {str(e)}")
        return ChatResponse(
            response=f"Sorry, I encountered an error: {str(e)}",
            intent="error"
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Calendar Agent with REAL LangGraph...")
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    log_level = "debug" if debug_mode else "info"
    
    # Use reload instead of debug for development
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        reload=debug_mode,  # Use reload instead of debug
        log_level=log_level
    )