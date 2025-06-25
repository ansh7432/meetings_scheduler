import streamlit as st
import requests
import json
from datetime import datetime
import os

# Configure Streamlit page
st.set_page_config(
    page_title="AI Calendar Booking Agent",
    page_icon="📅",
    layout="wide"
)

# API configuration - fix the detection logic
try:
    # Check if running locally vs cloud
    is_local = not st.get_option("server.headless")  # headless=True in cloud, False locally
    if is_local:
        API_BASE_URL = "http://localhost:8000"
    else:
        API_BASE_URL = os.getenv("API_BASE_URL", "https://your-fastapi-app.herokuapp.com")
except:
    # Fallback - assume local if can't determine
    API_BASE_URL = "http://localhost:8000"

# Check if API is available
def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Enhanced CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2e3440;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #5e81ac;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .demo-mode {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .demo-chat {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    [data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 18px 18px 5px 18px;
        padding: 0.8rem 1rem;
        margin-left: 25%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    [data-testid="chat-message-user"] p {
        color: white !important;
        font-weight: 500;
        margin: 0;
    }
    
    [data-testid="chat-message-assistant"] {
        background: white;
        border-radius: 18px 18px 18px 5px;
        padding: 0.8rem 1rem;
        margin-right: 25%;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="chat-message-assistant"] p {
        color: #333 !important;
        margin: 0;
    }
    
    .time-slot {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        font-weight: 600;
        transition: transform 0.2s ease;
    }
    
    .success-box {
        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        font-weight: 600;
    }
    
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

def send_message(message: str):
    """Send message to the FastAPI backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": message, "session_id": st.session_state.session_id},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"response": f"Error: {response.status_code}", "intent": "error"}
    except requests.exceptions.RequestException as e:
        return {"response": f"Connection error: {str(e)}", "intent": "error"}

def demo_response(message: str):
    """Demo responses when API is not available"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['free', 'available', 'availability', 'check']):
        return {
            "response": """Here are your **AVAILABLE** time slots for **Today** (Demo Mode):

🌅 **Morning (3 slots):**
• ✅ 9:00 AM - 10:00 AM (FREE)
• ✅ 10:30 AM - 11:30 AM (FREE)
• ✅ 11:00 AM - 12:00 PM (FREE)

☀️ **Afternoon (4 slots):**
• ✅ 2:00 PM - 3:00 PM (FREE)
• ✅ 2:30 PM - 3:30 PM (FREE)
• ✅ 3:00 PM - 4:00 PM (FREE)
• ✅ 4:30 PM - 5:30 PM (FREE)

📊 **Total available: 7 slots**

💡 **Demo Mode**: In full version, these would be your real Google Calendar slots with live conflict checking!""",
            "intent": "check_availability",
            "available_slots": [
                {"start": "9:00 AM", "end": "10:00 AM", "datetime": "2025-06-25T09:00:00"},
                {"start": "10:30 AM", "end": "11:30 AM", "datetime": "2025-06-25T10:30:00"},
                {"start": "11:00 AM", "end": "12:00 PM", "datetime": "2025-06-25T11:00:00"},
                {"start": "2:00 PM", "end": "3:00 PM", "datetime": "2025-06-25T14:00:00"},
                {"start": "2:30 PM", "end": "3:30 PM", "datetime": "2025-06-25T14:30:00"},
                {"start": "3:00 PM", "end": "4:00 PM", "datetime": "2025-06-25T15:00:00"},
                {"start": "4:30 PM", "end": "5:30 PM", "datetime": "2025-06-25T16:30:00"}
            ]
        }
    elif any(word in message_lower for word in ['book', 'schedule', 'meeting', 'appointment']):
        return {
            "response": """✅ **Demo Booking Successful!**

📅 **Meeting Details:**
• **Date:** Today  
• **Time:** 2:00 PM - 3:00 PM
• **Duration:** 60 minutes
• **Title:** Demo Meeting
• **Status:** ✅ Confirmed (Demo)

🎉 **In the full version:**
- Creates real Google Calendar event
- Sends email confirmations  
- Prevents actual scheduling conflicts
- Integrates with your live calendar

**This demonstrates the complete booking flow!**""",
            "intent": "book_appointment",
            "booking_info": {"booked": True, "date": "2025-06-25", "time": "14:00", "duration": 60}
        }
    else:
        return {
            "response": f"""🤖 **AI Calendar Assistant** (Demo Mode)

I understand: *"{message}"*

**I can help you with:**
• 📅 **Check availability**: "What times are free today?"
• 📝 **Schedule meetings**: "Book a meeting at 2 PM"  
• 🔍 **Find slots**: "Do you have time this Friday?"
• ⏰ **Manage calendar**: "Cancel my 3 PM meeting"

**🚀 This demo showcases:**
- Natural language understanding with LangGraph
- Smart scheduling logic and conflict detection
- Conversational AI with multi-turn dialogue
- Professional booking interface

**Try asking:** "What times are free today?" or "Schedule a meeting at 2 PM"

**In production:** Connects to real Google Calendar API for live scheduling!""",
            "intent": "general_chat"
        }

def book_slot(slot_datetime, duration=60, title="Meeting"):
    """Book a specific time slot (demo version)"""
    return {
        "success": True, 
        "message": f"✅ Demo: Would book '{title}' for {slot_datetime} ({duration} min). In full version, this creates a real calendar event!"
    }

def main():
    # Header
    st.markdown('<h1 class="main-title">🤖 AI Calendar Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Natural Language Calendar Booking with LangGraph</p>', unsafe_allow_html=True)
    
    # Check API availability
    api_available = check_api_health()
    
    # Show demo mode banner
    if not api_available:
        st.markdown("""
        <div class="demo-mode">
            🚀 <strong>Live Demo Mode</strong><br>
            Experience the full AI conversation flow! This showcases LangGraph workflows, natural language processing, and smart booking logic.
        </div>
        """, unsafe_allow_html=True)
        
        # Feature badges
        st.markdown("""
        <div style="text-align: center; margin: 1rem 0;">
            <span class="feature-badge">🤖 LangGraph AI</span>
            <span class="feature-badge">💬 Natural Language</span>
            <span class="feature-badge">📅 Smart Booking</span>
            <span class="feature-badge">🔍 Conflict Detection</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        welcome_msg = """👋 **Welcome to the AI Calendar Assistant!**

I'm powered by **LangGraph** and can help you schedule appointments using natural language. 

**What I can do:**
• 📅 Check your calendar availability
• 📝 Schedule meetings and appointments  
• 🔍 Find suitable time slots
• 💬 Have natural conversations about your calendar

**How can I help you today?**"""
        
        if not api_available:
            welcome_msg += """\n\n🚀 **Demo Mode**: Try asking:
• "What times are free today?"
• "Schedule a meeting at 2 PM"
• "Do you have any slots this afternoon?"

*This demo showcases the complete AI booking workflow!*"""
        
        st.session_state.messages = [
            {"role": "assistant", "content": welcome_msg}
        ]
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create layout
    col1, col2 = st.columns([3.5, 1])
    
    with col1:
        st.markdown("### 💬 Conversation")
        
        # Chat container
        chat_container = st.container(height=500)
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me about scheduling... 💭"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get AI response
            with st.spinner("🤔 Processing with LangGraph..."):
                if api_available:
                    response = send_message(prompt)
                else:
                    response = demo_response(prompt)
                
                ai_response = response.get("response", "Sorry, I couldn't process that.")
                booking_info = response.get("booking_info", {})
                available_slots = response.get("available_slots", [])
                
                # Show success message if booking was successful
                if booking_info.get('booked'):
                    st.markdown(f"""
                    <div class="success-box">
                        🎉 <strong>Demo Booking Confirmed!</strong><br>
                        📅 {booking_info.get('date', 'Today')} at {booking_info.get('time', '2:00 PM')} ({booking_info.get('duration', 60)} min)
                    </div>
                    """, unsafe_allow_html=True)
                    if not api_available:
                        st.balloons()
                
                # Display AI response
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # Show booking interface for available slots
                if available_slots:
                    st.markdown("### 📅 Available Time Slots")
                    if not api_available:
                        st.info("🚀 Demo Mode: These are sample time slots. Full version shows your real Google Calendar availability!")
                    
                    # Show slots in a nice grid
                    cols = st.columns(3)
                    
                    for i, slot in enumerate(available_slots[:12]):
                        col_idx = i % 3
                        
                        with cols[col_idx]:
                            st.markdown(f'''
                            <div class="time-slot">
                                🕐 {slot['start']} - {slot['end']}
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Meeting title input
                            meeting_title = st.text_input(
                                "Meeting Title", 
                                value="Meeting", 
                                key=f"title_{i}_{slot['start']}_{len(st.session_state.messages)}",
                                placeholder="Enter meeting title",
                                label_visibility="collapsed"
                            )
                            
                            # Book button
                            button_text = f"📅 Demo Book {slot['start']}" if not api_available else f"📅 Book {slot['start']}"
                            if st.button(button_text, key=f"book_{i}_{slot['start']}_{len(st.session_state.messages)}", use_container_width=True):
                                with st.spinner("Booking..."):
                                    booking_result = book_slot(slot['datetime'], 60, meeting_title)
                                    if booking_result['success']:
                                        success_msg = f"✅ Demo: Would book '{meeting_title}' for {slot['start']}" if not api_available else f"✅ Booked: {meeting_title}"
                                        st.success(success_msg)
                                        
                                        # Add booking confirmation to chat
                                        confirmation_msg = f"✅ **Demo Booking Confirmed!**\n\n📅 '{meeting_title}' scheduled for {slot['start']} - {slot['end']}\n\n🎉 In the full version, this would create a real Google Calendar event with email notifications!"
                                        
                                        st.session_state.messages.append({
                                            "role": "assistant", 
                                            "content": confirmation_msg
                                        })
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error(booking_result['message'])
                    
                    # Show more slots info
                    if len(available_slots) > 12:
                        st.info(f"Showing 12 of {len(available_slots)} available slots. Ask for specific times to see more!")
            
            st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            welcome_msg = """👋 **Welcome back!**

I'm your AI calendar assistant. How can I help you today?"""
            
            if not api_available:
                welcome_msg += """\n\n🚀 **Demo Mode**: Try asking about availability or booking meetings!"""
            
            st.session_state.messages = [
                {"role": "assistant", "content": welcome_msg}
            ]
            st.rerun()
    
    with col2:
        st.markdown("### 💡 Try These Examples")
        
        examples = [
            "What times are free today?",
            "Schedule a call for 2 PM", 
            "Do you have slots this Friday?",
            "Book a 30-minute meeting",
            "Check tomorrow's availability",
            "Schedule a team meeting",
            "I need a 1-hour slot",
            "What's free this afternoon?"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"💬 {example}", key=f"example-btn-{i}", use_container_width=True, help="Click to try this example"):
                st.session_state.messages.append({"role": "user", "content": example})
                if api_available:
                    response = send_message(example)
                else:
                    response = demo_response(example)
                st.session_state.messages.append({"role": "assistant", "content": response.get("response", "No response")})
                st.rerun()
        
        # Status and info section
        st.markdown("---")
        st.markdown("### 📊 Status")
        
        if api_available:
            st.success("🟢 Connected to Live Backend")
            st.markdown("- Real Google Calendar integration")
            st.markdown("- Live conflict checking")
        else:
            st.info("🟡 Demo Mode Active")
            st.markdown("- Showcasing AI conversation flow")
            st.markdown("- Simulated booking responses")
        
        st.markdown("### 🛠️ Technical Stack")
        st.markdown("""
        **Backend:**
        - 🤖 **LangGraph** - AI workflow management
        - ⚡ **FastAPI** - REST API framework
        - 📅 **Google Calendar API** - Calendar integration
        
        **Frontend:**
        - 🎨 **Streamlit** - Interactive web interface
        - 💬 **Chat Interface** - Real-time conversations
        
        **Features:**
        - Natural language processing
        - Multi-turn conversations
        - Conflict detection
        - Real-time availability
        """)

if __name__ == "__main__":
    main()