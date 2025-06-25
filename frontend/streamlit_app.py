import streamlit as st
import requests
import json
from datetime import datetime
import os
import time
import uuid

# Configure Streamlit page
st.set_page_config(
    page_title="AI Calendar Assistant",
    page_icon="📅",
    layout="wide"
)

# Load CSS
def load_css():
    try:
        css_path = os.path.join(os.path.dirname(__file__), 'style.css')
        with open(css_path, 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        try:
            with open('style.css', 'r') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            pass

# API configuration
try:
    is_local = not st.get_option("server.headless")
    API_BASE_URL = "http://localhost:8000" if is_local else os.getenv("API_BASE_URL", "demo_mode")
except:
    API_BASE_URL = "demo_mode"

def check_api_health():
    if API_BASE_URL == "demo_mode":
        return False
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message: str):
    """Send message to the FastAPI backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": message, "session_id": st.session_state.session_id},
            timeout=30
        )
        return response.json() if response.status_code == 200 else {"response": f"Error: {response.status_code}", "intent": "error"}
    except requests.exceptions.RequestException as e:
        return {"response": f"Connection error: {str(e)}", "intent": "error"}

def demo_response(message: str):
    """Demo responses when API is not available"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['free', 'available', 'availability', 'check']):
        return {
            "response": """**Available time slots for today:**

**Morning:**
• 9:00 AM - 10:00 AM
• 10:30 AM - 11:30 AM  
• 11:00 AM - 12:00 PM

**Afternoon:**
• 2:00 PM - 3:00 PM
• 2:30 PM - 3:30 PM
• 3:00 PM - 4:00 PM
• 4:30 PM - 5:30 PM

Would you like to book one of these slots?""",
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
            "response": """✅ **Meeting scheduled successfully!**

**Details:**
• Date: Today
• Time: 2:00 PM - 3:00 PM
• Duration: 60 minutes
• Status: Confirmed

*In demo mode - this would create a real calendar event.*""",
            "intent": "book_appointment",
            "booking_info": {"booked": True, "date": "2025-06-25", "time": "14:00", "duration": 60}
        }
    else:
        return {
            "response": f"""I can help you with:

• **Check availability** - "What times are free today?"
• **Schedule meetings** - "Book a meeting at 2 PM"  
• **Find time slots** - "Do you have time this Friday?"

Try asking about your calendar availability!""",
            "intent": "general_chat"
        }

def book_meeting_with_details(booking_data):
    """Book meeting with enhanced details including Meet link"""
    try:
        # Prepare booking request
        booking_request = {
            "datetime": booking_data["slot"]["datetime"],
            "duration": booking_data["duration"],
            "title": booking_data["title"],
            "description": booking_data["description"],
            "add_meet_link": booking_data["add_meet_link"],
            "attendees": booking_data["attendees"]
        }
        
        if check_api_health():
            # Send to live API
            response = requests.post(
                f"{API_BASE_URL}/api/book",
                json=booking_request,
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"success": False, "message": f"API Error: {response.status_code}"}
        else:
            # Demo mode response
            return {
                "success": True,
                "message": "Meeting booked successfully (Demo Mode)",
                "meet_link": "https://meet.google.com/demo-meeting-link",
                "calendar_link": "https://calendar.google.com/calendar/demo-event",
                "event_id": "demo_event_123"
            }
            
    except Exception as e:
        return {"success": False, "message": str(e)}

def auto_save_chat():
    """Auto-save current chat to history when user sends a message"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Only save if there's actual conversation (more than welcome message)
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    if len(user_messages) == 0:
        return
    
    # Check if current session already exists in history
    current_session_id = st.session_state.session_id
    existing_chat_index = None
    
    for i, chat in enumerate(st.session_state.chat_history):
        if chat["session_id"] == current_session_id:
            existing_chat_index = i
            break
    
    chat_data = {
        "id": str(uuid.uuid4()),  # Use UUID for unique IDs
        "timestamp": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%b %d"),
        "title": get_chat_title(st.session_state.messages),
        "messages": st.session_state.messages.copy(),
        "session_id": current_session_id,
        "last_updated": time.time()
    }
    
    if existing_chat_index is not None:
        # Update existing chat
        st.session_state.chat_history[existing_chat_index] = chat_data
    else:
        # Add new chat
        st.session_state.chat_history.append(chat_data)
    
    # Sort by last updated (most recent first)
    st.session_state.chat_history.sort(key=lambda x: x["last_updated"], reverse=True)

def get_chat_title(messages):
    """Generate a title for the chat based on first user message"""
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"][:35]
            return title + "..." if len(msg["content"]) > 35 else title
    return f"New Chat"

def load_chat_from_history(chat_id):
    """Load a specific chat from history"""
    if "chat_history" in st.session_state:
        for chat in st.session_state.chat_history:
            if chat["id"] == chat_id:
                st.session_state.messages = chat["messages"].copy()
                st.session_state.session_id = chat["session_id"]
                st.rerun()

def start_new_chat():
    """Start a new chat conversation"""
    welcome_msg = """👋 **Welcome!**

I can help you schedule meetings using natural language.

**What would you like to do?**
• Check your calendar availability
• Schedule a new meeting
• Find available time slots

Just ask me in plain English!"""
    
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    st.rerun()

def clear_all_history():
    """Clear all chat history"""
    st.session_state.chat_history = []
    start_new_chat()

def handle_quick_action(example):
    """Handle quick action button clicks"""
    st.session_state.messages.append({"role": "user", "content": example})
    auto_save_chat()
    response = send_message(example) if check_api_health() else demo_response(example)
    st.session_state.messages.append({"role": "assistant", "content": response.get("response", "")})
    auto_save_chat()
    st.rerun()

def main():
    load_css()
    
    # Initialize session
    if "messages" not in st.session_state:
        welcome_msg = """👋 **Welcome!**

I can help you schedule meetings using natural language.

**What would you like to do?**
• Check your calendar availability
• Schedule a new meeting
• Find available time slots

Just ask me in plain English!"""
        
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Create sidebar for chat history and quick actions
    with st.sidebar:
        st.markdown('<div class="chat-sidebar">', unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
            start_new_chat()
        
        st.markdown("---")
        
        # Chat History
        if st.session_state.chat_history:
            st.markdown("### 📚 Recent Chats")
            
            for i, chat in enumerate(st.session_state.chat_history):
                # Check if this is the current active chat
                is_active = chat["session_id"] == st.session_state.session_id
                
                # Create unique key for each button
                button_key = f"chat_btn_{chat['id']}_{i}"
                
                if st.button(
                    chat["title"], 
                    key=button_key, 
                    use_container_width=True,
                    help=f"{chat['date']} at {chat['timestamp']}"
                ):
                    load_chat_from_history(chat['id'])
                
                # Show active indicator
                if is_active:
                    st.markdown('<div class="active-indicator">📍 Current Chat</div>', unsafe_allow_html=True)
        
        else:
            st.markdown("### 📚 Chat History")
            st.markdown("*No previous chats*")
            st.markdown("Start a conversation to see your chat history here!")
        
        st.markdown("---")
        
        # Quick Actions in Sidebar
        st.markdown("### 💡 Quick Actions")
        examples = [
            "What times are free today?",
            "Schedule a call for 2 PM", 
            "Do you have slots Friday?",
            "Book a 30-minute meeting",
            "Check tomorrow's availability"
        ]
        
        for i, example in enumerate(examples):
            if st.button(example, key=f"quick_action_{i}_{st.session_state.session_id}", use_container_width=True):
                handle_quick_action(example)
        
        # Clear History Button at bottom
        if st.session_state.chat_history:
            st.markdown("---")
            if st.button("🗑️ Clear All History", key="clear_all_btn", use_container_width=True):
                clear_all_history()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    # Header
    st.markdown('<h1 class="main-title">📅 AI Calendar Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Schedule meetings with natural language</p>', unsafe_allow_html=True)
    
    # Check API
    api_available = check_api_health()
    
    # Status
    if api_available:
        st.markdown("""
        <div class="status-banner status-live">
            🟢 <strong>Connected</strong> - Live backend active
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-banner status-demo">
            🟡 <strong>Demo Mode</strong> - Try the conversation flow
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown('<div class="section-header">💬 Conversation</div>', unsafe_allow_html=True)
    
    # Chat container with messages and input inside
    with st.container():
        # Display messages
        messages_container = st.container(height=700)
        with messages_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat Input inside the container
        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Auto-save after user sends message
            auto_save_chat()
            
            with st.spinner("Processing..."):
                response = send_message(prompt) if api_available else demo_response(prompt)
                ai_response = response.get("response", "Sorry, I couldn't process that.")
                booking_info = response.get("booking_info", {})
                available_slots = response.get("available_slots", [])
                
                if booking_info.get('booked'):
                    st.success("🎉 Meeting booked successfully!")
                    st.balloons()
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # Auto-save after assistant responds
                auto_save_chat()
                
                # Show time slots with enhanced booking form
                if available_slots:
                    st.markdown("---")
                    st.markdown("**📅 Available Times - Click to Book**")
                    
                    # Create booking form for each slot
                    cols = st.columns(2)  # Changed to 2 columns for better spacing
                    for i, slot in enumerate(available_slots[:8]):  # Show max 8 slots
                        with cols[i % 2]:
                            # Time slot display card
                            st.markdown(f"""
                            <div class="time-slot-card">
                                <div class="time-slot-time">🕐 {slot['start']} - {slot['end']}</div>
                                <div class="time-slot-duration">{slot.get('duration', '60')} minutes</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Book button that opens booking form
                            if st.button(f"📅 Book {slot['start']}", key=f"book_btn_{i}_{st.session_state.session_id}", use_container_width=True):
                                st.session_state[f"booking_form_{i}"] = True
                            
                            # Show booking form if button was clicked
                            if st.session_state.get(f"booking_form_{i}", False):
                                with st.expander(f"📝 Book Meeting at {slot['start']}", expanded=True):
                                    with st.form(key=f"booking_form_{i}_{st.session_state.session_id}"):
                                        st.write(f"**📅 Selected Time:** {slot['start']} - {slot['end']}")
                                        
                                        # Meeting details form
                                        meeting_title = st.text_input(
                                            "Meeting Title*", 
                                            value="Team Meeting",
                                            key=f"title_{i}_{st.session_state.session_id}",
                                            placeholder="Enter meeting title"
                                        )
                                        
                                        # Duration selection
                                        duration_options = [30, 45, 60, 90, 120]
                                        default_duration = 60
                                        duration = st.selectbox(
                                            "Duration (minutes)*",
                                            duration_options,
                                            index=duration_options.index(default_duration),
                                            key=f"duration_{i}_{st.session_state.session_id}"
                                        )
                                        
                                        # Meeting description
                                        description = st.text_area(
                                            "Description (Optional)",
                                            placeholder="Add meeting agenda or notes...",
                                            key=f"description_{i}_{st.session_state.session_id}",
                                            height=80
                                        )
                                        
                                        # Add Google Meet link option
                                        add_meet_link = st.checkbox(
                                            "🔗 Add Google Meet link",
                                            value=True,
                                            key=f"meet_link_{i}_{st.session_state.session_id}",
                                            help="Automatically generate a Google Meet link for the meeting"
                                        )
                                        
                                        # Attendees (optional)
                                        attendees = st.text_input(
                                            "Attendees (Optional)",
                                            placeholder="Enter email addresses separated by commas",
                                            key=f"attendees_{i}_{st.session_state.session_id}",
                                            help="Add attendees who will receive calendar invitations"
                                        )
                                        
                                        # Form buttons
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if st.form_submit_button("✅ Confirm Booking", use_container_width=True):
                                                # Validate form
                                                if not meeting_title.strip():
                                                    st.error("Please enter a meeting title")
                                                else:
                                                    # Process booking
                                                    booking_data = {
                                                        "slot": slot,
                                                        "title": meeting_title.strip(),
                                                        "duration": duration,
                                                        "description": description.strip(),
                                                        "add_meet_link": add_meet_link,
                                                        "attendees": [email.strip() for email in attendees.split(",") if email.strip()] if attendees else []
                                                    }
                                                    
                                                    # Send booking request
                                                    booking_response = book_meeting_with_details(booking_data)
                                                    
                                                    if booking_response.get("success"):
                                                        st.success("🎉 Meeting booked successfully!")
                                                        
                                                        # Create confirmation message
                                                        confirmation_msg = f"""✅ **Meeting Confirmed!**

📅 **{meeting_title}**
🕒 **Time:** {slot['start']} - {slot['end']}
⏱️ **Duration:** {duration} minutes
📝 **Description:** {description if description else 'No description'}"""
                                                        
                                                        if booking_response.get("meet_link"):
                                                            confirmation_msg += f"\n🔗 **Google Meet:** {booking_response['meet_link']}"
                                                        
                                                        if booking_response.get("calendar_link"):
                                                            confirmation_msg += f"\n📅 **[View in Calendar]({booking_response['calendar_link']})**"
                                                        
                                                        # Add to chat history
                                                        st.session_state.messages.append({
                                                            "role": "assistant", 
                                                            "content": confirmation_msg
                                                        })
                                                        auto_save_chat()
                                                        
                                                        # Clear form state
                                                        st.session_state[f"booking_form_{i}"] = False
                                                        
                                                        st.balloons()
                                                        st.rerun()
                                                    else:
                                                        st.error(f"❌ Booking failed: {booking_response.get('message', 'Unknown error')}")
                                        
                                        with col2:
                                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                                st.session_state[f"booking_form_{i}"] = False
                                                st.rerun()
            st.rerun()

if __name__ == "__main__":
    main()