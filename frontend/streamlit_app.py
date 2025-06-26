import streamlit as st
import requests
import json
from datetime import datetime
import os
import time
import uuid

st.set_page_config(
    page_title="AI Calendar Assistant",
    page_icon="📅",
    layout="wide"
)

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
    message_lower = message.lower()
    
    if "quickbook" in message_lower or "quick book" in message_lower:
        return {
            "response": """🚀 **Quickbook Mode Activated!**

Select a time slot and fill in your meeting details all in one place.

**Available slots loaded below:**
• Morning, afternoon, and evening options
• Click any slot to activate the booking form
• Complete all details in the unified interface

*Scroll down to see the quickbook interface.*""",
            "intent": "quickbook",
            "available_slots": [
                {"start": "9:00 AM", "end": "10:00 AM", "datetime": "2025-06-25T09:00:00"},
                {"start": "10:30 AM", "end": "11:30 AM", "datetime": "2025-06-25T10:30:00"},
                {"start": "11:00 AM", "end": "12:00 PM", "datetime": "2025-06-25T11:00:00"},
                {"start": "2:00 PM", "end": "3:00 PM", "datetime": "2025-06-25T14:00:00"},
                {"start": "2:30 PM", "end": "3:30 PM", "datetime": "2025-06-25T14:30:00"},
                {"start": "3:00 PM", "end": "4:00 PM", "datetime": "2025-06-25T15:00:00"},
                {"start": "4:30 PM", "end": "5:30 PM", "datetime": "2025-06-25T16:30:00"},
                {"start": "5:30 PM", "end": "6:30 PM", "datetime": "2025-06-25T17:30:00"}
            ]
        }
    elif any(word in message_lower for word in ['free', 'available', 'availability', 'check']):
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
• **Quick booking** - Try "Quickbook" for unified interface

Try asking about your calendar availability!""",
            "intent": "general_chat"
        }

def book_meeting_with_details(booking_data):
    try:
        booking_request = {
            "datetime": booking_data["slot"]["datetime"],
            "duration": booking_data["duration"],
            "title": booking_data["title"],
            "description": booking_data["description"],
            "add_meet_link": booking_data["add_meet_link"],
            "attendees": booking_data["attendees"]
        }
        
        if check_api_health():
            response = requests.post(
                f"{API_BASE_URL}/api/book",
                json=booking_request,
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"success": False, "message": f"API Error: {response.status_code}"}
        else:
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
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    if len(user_messages) == 0:
        return
    
    current_session_id = st.session_state.session_id
    existing_chat_index = None
    
    for i, chat in enumerate(st.session_state.chat_history):
        if chat["session_id"] == current_session_id:
            existing_chat_index = i
            break
    
    chat_data = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%b %d"),
        "title": get_chat_title(st.session_state.messages),
        "messages": st.session_state.messages.copy(),
        "session_id": current_session_id,
        "last_updated": time.time()
    }
    
    if existing_chat_index is not None:
        st.session_state.chat_history[existing_chat_index] = chat_data
    else:
        st.session_state.chat_history.append(chat_data)
    
    st.session_state.chat_history.sort(key=lambda x: x["last_updated"], reverse=True)

def get_chat_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"][:35]
            return title + "..." if len(msg["content"]) > 35 else title
    return f"New Chat"

def load_chat_from_history(chat_id):
    if "chat_history" in st.session_state:
        for chat in st.session_state.chat_history:
            if chat["id"] == chat_id:
                st.session_state.messages = chat["messages"].copy()
                st.session_state.session_id = chat["session_id"]
                

def start_new_chat():
    welcome_msg = """👋 **Welcome!**

I can help you schedule meetings using natural language.

**What would you like to do?**
• Check your calendar availability
• Schedule a new meeting  
• Find available time slots
• Try "quickbook" for detailed form

Just ask me in plain English!"""
    
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    # Reset all interface states when starting new chat
    st.session_state.show_quickbook_interface = False
    st.session_state.show_booking_dialog = False
    st.session_state.selected_slot = None
    st.session_state.current_available_slots = []
    


def clear_all_history():
    st.session_state.chat_history = []
    
    # Reset all interface states when clearing history
    st.session_state.show_quickbook_interface = False
    st.session_state.show_booking_dialog = False
    st.session_state.selected_slot = None
    st.session_state.current_available_slots = []
    
    start_new_chat()

def handle_quick_action(example):
    st.session_state.messages.append({"role": "user", "content": example})
    auto_save_chat()
    
    api_available = check_api_health()
    response = send_message(example) if api_available else demo_response(example)
    
    ai_response = response.get("response", "Sorry, I couldn't process that.")
    booking_info = response.get("booking_info", {})
    available_slots = response.get("available_slots", [])
    
    if "quickbook" in example.lower() or "quick book" in example.lower():
        st.session_state.current_available_slots = available_slots or demo_response("availability")["available_slots"]
        st.session_state.show_quickbook_interface = True
        st.session_state.selected_slot = None
        st.session_state.show_booking_dialog = False
   
    else:
        st.session_state.current_available_slots = []
        st.session_state.show_quickbook_interface = False
    
    if booking_info.get('booked'):
        st.success("🎉 Meeting booked successfully!")
        st.balloons()
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    auto_save_chat()
    
    

def main():
    load_css()
    
    if "messages" not in st.session_state:
        welcome_msg = """👋 **Welcome!**

I can help you schedule meetings using natural language.

**What would you like to do?**
• Check your calendar availability
• Schedule a new meeting  
• Find available time slots
• Try **"quickbook"** for unified interface

Just ask me in plain English!"""
        
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_available_slots" not in st.session_state:
        st.session_state.current_available_slots = []
    
    if "show_booking_dialog" not in st.session_state:
        st.session_state.show_booking_dialog = False
    
    if "selected_slot" not in st.session_state:
        st.session_state.selected_slot = None
    
    if "show_quickbook_interface" not in st.session_state:
        st.session_state.show_quickbook_interface = False

    with st.sidebar:
        st.markdown('<div class="chat-sidebar">', unsafe_allow_html=True)
        
        if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
            start_new_chat()
        
        st.markdown("---")
        
        if st.session_state.chat_history:
            st.markdown("### 📚 Recent Chats")
            
            for i, chat in enumerate(st.session_state.chat_history):
                is_active = chat["session_id"] == st.session_state.session_id
                button_key = f"chat_btn_{chat['id']}_{i}"
                
                if st.button(
                    chat["title"], 
                    key=button_key, 
                    use_container_width=True,
                    help=f"{chat['date']} at {chat['timestamp']}"
                ):
                    load_chat_from_history(chat['id'])
                
                if is_active:
                    st.markdown('<div class="active-indicator">📍 Current Chat</div>', unsafe_allow_html=True)
        
        else:
            st.markdown("### 📚 Chat History")
            st.markdown("*No previous chats*")
            st.markdown("Start a conversation to see your chat history here!")
        
        st.markdown("---")
        
        st.markdown("### 💡 Quick Actions")
        examples = [
            "Quickbook", 
            "What times are free today?",
            "Schedule a call for 2 PM", 
            "Book a 30-minute meeting tomorrow at 3 PM",
            "Check tomorrow's availability"
        ]
        
        for i, example in enumerate(examples):
            if st.button(example, key=f"quick_action_{i}_{st.session_state.session_id}", use_container_width=True):
                handle_quick_action(example)
        
        if st.session_state.chat_history:
            st.markdown("---")
            if st.button("🗑️ Clear All History", key="clear_all_btn", use_container_width=True):
                clear_all_history()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-title">📅 AI Calendar Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Schedule meetings with natural language</p>', unsafe_allow_html=True)
    
    api_available = check_api_health()
    
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
    
    st.markdown('<div class="section-header">💬 Conversation</div>', unsafe_allow_html=True)
    
    if st.session_state.get("show_quickbook_interface", False):
        with st.expander("💬 Conversation (Minimized)", expanded=False):
            
            recent_messages = st.session_state.messages[-3:] if len(st.session_state.messages) > 3 else st.session_state.messages
            for message in recent_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            if len(st.session_state.messages) > 3:
                st.markdown("*... (showing last 3 messages)*")
            
    else:
  
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
  
    
    if st.session_state.current_available_slots and not st.session_state.get("show_quickbook_interface", False):
        st.markdown("---")
        
        # Header with close button positioned to the far right
        slot_header_col1, slot_header_col2 = st.columns([4, 1])
        with slot_header_col1:
            st.markdown("### 📅 Available Time Slots - Click to Book")
        with slot_header_col2:
            if st.button("✕ Close Slots", key="close_slots_btn", help="Hide time slots", use_container_width=True):
                st.session_state.current_available_slots = []
                st.session_state.show_booking_dialog = False
                st.session_state.selected_slot = None
                st.rerun()
        
        slots = st.session_state.current_available_slots
        num_cols = 4
        
        for i in range(0, len(slots), num_cols):
            cols = st.columns(num_cols)
            
            for j in range(num_cols):
                slot_index = i + j
                if slot_index < len(slots):
                    slot = slots[slot_index]
                    
                    with cols[j]:
                        button_key = f"book_btn_{slot_index}_{st.session_state.session_id}_{int(time.time())}"
                        if st.button(f"🕐 {slot['start']}", key=button_key, use_container_width=True, help=f"Book {slot['start']} - {slot['end']}"):
                            st.session_state.selected_slot = slot
                            st.session_state.show_booking_dialog = True
                            st.rerun()
    
    # Chat input should always be available (except in quickbook mode)
    if not st.session_state.get("show_quickbook_interface", False):
        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            auto_save_chat()
            
            with st.spinner("Processing..."):
                response = send_message(prompt) if api_available else demo_response(prompt)
                ai_response = response.get("response", "Sorry, I couldn't process that.")
                booking_info = response.get("booking_info", {})
                available_slots = response.get("available_slots", [])
                
                if "quickbook" in prompt.lower() or "quick book" in prompt.lower():
                    st.session_state.current_available_slots = available_slots or demo_response("availability")["available_slots"]
                    st.session_state.show_quickbook_interface = True
                    st.session_state.selected_slot = None
                else:
                    st.session_state.current_available_slots = []
                    st.session_state.show_quickbook_interface = False
                
                if booking_info.get('booked'):
                    st.success("🎉 Meeting booked successfully!")
                    st.balloons()
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                auto_save_chat()
            
           

    if st.session_state.current_available_slots and not st.session_state.get("show_quickbook_interface", False):
        st.markdown("---")
        
        # Header with close button positioned to the far right
        slot_header_col1, slot_header_col2 = st.columns([4, 1])
        with slot_header_col1:
            st.markdown("### 📅 Available Time Slots - Click to Book")
        with slot_header_col2:
            if st.button("✕ Close Slots", key="close_slots_btn", help="Hide time slots", use_container_width=True):
                st.session_state.current_available_slots = []
                st.session_state.show_booking_dialog = False
                st.session_state.selected_slot = None
                st.rerun()
        
        slots = st.session_state.current_available_slots
        num_cols = 4
        
        for i in range(0, len(slots), num_cols):
            cols = st.columns(num_cols)
            
            for j in range(num_cols):
                slot_index = i + j
                if slot_index < len(slots):
                    slot = slots[slot_index]
                    
                    with cols[j]:
                        button_key = f"book_btn_{slot_index}_{st.session_state.session_id}_{int(time.time())}"
                        if st.button(f"🕐 {slot['start']}", key=button_key, use_container_width=True, help=f"Book {slot['start']} - {slot['end']}"):
                            st.session_state.selected_slot = slot
                            st.session_state.show_booking_dialog = True
                            st.rerun()
        
        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            auto_save_chat()
            
            with st.spinner("Processing..."):
                response = send_message(prompt) if api_available else demo_response(prompt)
                ai_response = response.get("response", "Sorry, I couldn't process that.")
                booking_info = response.get("booking_info", {})
                available_slots = response.get("available_slots", [])
                
                if "quickbook" in prompt.lower() or "quick book" in prompt.lower():
                    st.session_state.current_available_slots = available_slots or demo_response("availability")["available_slots"]
                    st.session_state.show_quickbook_interface = True
                    st.session_state.selected_slot = None
                
                else:
                    st.session_state.current_available_slots = []
                    st.session_state.show_quickbook_interface = False
                
                if booking_info.get('booked'):
                    st.success("🎉 Meeting booked successfully!")
                    st.balloons()
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                auto_save_chat()
            
            st.rerun()

    if st.session_state.get("show_quickbook_interface", False) and st.session_state.current_available_slots:
        
        st.markdown("---")
        
        header_col1, header_col2 = st.columns([4, 1])
        
        with header_col1:
            st.markdown("## Quick Book - Select Time & Fill Details")
            st.markdown("*Conversation minimized above - focus on booking*")
        
        with header_col2:
            if st.button("✕ Exit Quickbook", key="close_quickbook_btn", help="Return to conversation", type="secondary", use_container_width=True):
                st.session_state.show_quickbook_interface = False
                st.session_state.current_available_slots = []
                st.session_state.selected_slot = None
                st.success("👍 Returned to conversation mode")
                st.rerun()
        
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            height: 3px;
            border-radius: 2px;
            margin: 20px 0;
        "></div>
        """, unsafe_allow_html=True)
        
        slot_col, form_col = st.columns([1, 1.2])
        
        with slot_col:
            st.markdown("### 📅 Available Time Slots")
            st.markdown("*Click a time slot to select it for booking*")
            
            slots = st.session_state.current_available_slots
            
            with st.container():
                for i, slot in enumerate(slots):
                    slot_key = f"quickbook_slot_{i}_{st.session_state.session_id}"
                    
                    is_selected = (st.session_state.selected_slot and 
                                 st.session_state.selected_slot.get("start") == slot["start"])
                    
                    button_style = "🟢 ✓" if is_selected else "🕐"
                    button_text = f"{button_style} {slot['start']} - {slot['end']}"
                    
                    if st.button(
                        button_text, 
                        key=slot_key, 
                        use_container_width=True,
                        help=f"Select {slot['start']} - {slot['end']} for booking",
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_slot = slot
                        st.rerun()
        
        with form_col:
            st.markdown("### 📝 Meeting Details")
            
            if st.session_state.selected_slot:
                selected_slot = st.session_state.selected_slot
                st.markdown(f"""
                <div class="booking-selected-time" style="
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 12px;
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                ">
                    🟢 Selected: {selected_slot['start']} - {selected_slot['end']}
                </div>
                """, unsafe_allow_html=True)
                
                with st.form(key="quickbook_form", clear_on_submit=False):
                    
                    title_col, duration_col = st.columns(2)
                    
                    with title_col:
                        meeting_title = st.text_input(
                            "📝 Meeting Title *", 
                            value="Team Meeting",
                            placeholder="Enter meeting title",
                            help="Required field"
                        )
                    
                    with duration_col:
                        duration = st.selectbox(
                            "⏱️ Duration",
                            [15, 30, 45, 60, 90, 120],
                            index=3,
                            format_func=lambda x: f"{x} minutes",
                            help="How long will the meeting last?"
                        )
                    
                    type_col, priority_col = st.columns(2)
                    
                    with type_col:
                        meeting_type = st.selectbox(
                            "📋 Meeting Type",
                            ["Team Meeting", "1-on-1", "Client Call", "Interview", "Other"],
                            help="Select the type of meeting"
                        )
                    
                    with priority_col:
                        priority = st.selectbox(
                            "⚡ Priority",
                            ["Normal", "High", "Urgent"],
                            help="Set meeting priority"
                        )
                    
                    attendees = st.text_input(
                        "👥 Attendees (Optional)",
                        placeholder="email1@example.com, email2@example.com",
                        help="Enter email addresses separated by commas"
                    )
                    
                    description = st.text_area(
                        "📄 Description (Optional)",
                        placeholder="Add meeting agenda, notes, or other details...",
                        height=80,
                        help="Provide additional context for the meeting"
                    )
                    
                    location_col, meet_col = st.columns([2, 1])
                    
                    with location_col:
                        location = st.text_input(
                            "📍 Location (Optional)",
                            placeholder="Conference Room A, Online, etc.",
                            help="Physical or virtual meeting location"
                        )
                    
                    with meet_col:
                        add_meet_link = st.checkbox(
                            "🔗 Add Google Meet Link",
                            value=True,
                            help="Automatically generate a Google Meet link"
                        )
                    
                    st.markdown("---")
                    
                    button_col1, button_col2, button_col3 = st.columns([2, 1, 1])
                    
                    with button_col1:
                        if st.form_submit_button("✅ Book Meeting", use_container_width=True, type="primary"):
                            if not meeting_title.strip():
                                st.error("❌ Please enter a meeting title")
                            else:
                                booking_data = {
                                    "slot": selected_slot,
                                    "title": meeting_title.strip(),
                                    "duration": duration,
                                    "description": description.strip(),
                                    "add_meet_link": add_meet_link,
                                    "attendees": [email.strip() for email in attendees.split(",") if email.strip()] if attendees else [],
                                    "meeting_type": meeting_type,
                                    "priority": priority,
                                    "location": location.strip()
                                }
                                
                                with st.spinner("Booking your meeting..."):
                                    booking_response = book_meeting_with_details(booking_data)
                                
                                if booking_response.get("success"):
                                    st.success("🎉 Meeting booked successfully!")
                                    
                                    confirmation_msg = f"""✅ **Meeting Booked via Quickbook!**

📅 **{meeting_title}** ({meeting_type})
🕒 **Time:** {selected_slot['start']} - {selected_slot['end']}
⏱️ **Duration:** {duration} minutes
⚡ **Priority:** {priority}"""
                                    
                                    if location:
                                        confirmation_msg += f"\n📍 **Location:** {location}"
                                    
                                    if description:
                                        confirmation_msg += f"\n📄 **Description:** {description}"
                                    
                                    if booking_response.get("meet_link"):
                                        confirmation_msg += f"\n🔗 **Meet Link:** {booking_response['meet_link']}"
                                    
                                    if attendees:
                                        confirmation_msg += f"\n👥 **Attendees:** {', '.join([email.strip() for email in attendees.split(',') if email.strip()])}"
                                    
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": confirmation_msg
                                    })
                                    auto_save_chat()
                                    
                                    st.session_state.show_quickbook_interface = False
                                    st.session_state.current_available_slots = []
                                    st.session_state.selected_slot = None
                                    
                                    st.balloons()
                                    st.success("📱 Returning to conversation...")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Booking failed: {booking_response.get('message', 'Unknown error')}")
                    
                    with button_col2:
                        if st.form_submit_button("🔄 Reset", use_container_width=True):
                            st.session_state.selected_slot = None
                            st.rerun()
                    
                    with button_col3:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.show_quickbook_interface = False
                            st.session_state.current_available_slots = []
                            st.session_state.selected_slot = None
                            st.info("📱 Returned to conversation")
                            st.rerun()
            
            else:
                st.info("👈 Please select a time slot from the left to fill in meeting details")
                
                st.markdown("""
                **📋 Quickbook Form Features:**
                
                • ✅ Meeting title & duration selection
                
                • 📊 Meeting type & priority settings  
                
                • 🚀 One-click booking experience
                
                
                """)
        
        st.markdown("---")
        st.markdown("💡 **Tip:** Your conversation is minimized above. Complete booking or click 'Exit Quickbook' to return to full chat view.")

    elif st.session_state.show_booking_dialog and st.session_state.selected_slot:
        
        slot = st.session_state.selected_slot
        
        st.markdown("---")
        st.markdown("### 📅 Book Your Meeting")
        
        st.markdown(f"""
        <div class="booking-selected-time">
            🕐 {slot['start']} - {slot['end']}
        </div>
        """, unsafe_allow_html=True)
        
        col_close1, col_close2, col_close3 = st.columns([4, 1, 1])
        with col_close3:
            if st.button("✕ Close", key="close_modal_btn", help="Close dialog"):
                st.session_state.show_booking_dialog = False
                st.session_state.selected_slot = None
                st.rerun()
        
        with st.container():
            with st.form(key="booking_form_modal", clear_on_submit=False):
                st.markdown("#### 📝 Meeting Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    meeting_title = st.text_input(
                        "📝 Meeting Title *", 
                        value="Team Meeting",
                        placeholder="Enter meeting title",
                        help="Required field"
                    )
                    
                    duration = st.selectbox(
                        "⏱️ Duration",
                        [15, 30, 45, 60, 90, 120],
                        index=3,
                        format_func=lambda x: f"{x} minutes",
                        help="How long will the meeting last?"
                    )
                    
                    add_meet_link = st.checkbox(
                        "🔗 Add Google Meet Link",
                        value=True,
                        help="Automatically generate a Google Meet link"
                    )
                
                with col2:
                    attendees = st.text_input(
                        "👥 Attendees (Optional)",
                        placeholder="email1@example.com, email2@example.com",
                        help="Enter email addresses separated by commas"
                    )
                    
                    meeting_type = st.selectbox(
                        "📋 Meeting Type",
                        ["Team Meeting", "1-on-1", "Client Call", "Interview", "Other"],
                        help="Select the type of meeting"
                    )
                    
                    priority = st.selectbox(
                        "⚡ Priority",
                        ["Normal", "High", "Urgent"],
                        help="Set meeting priority"
                    )
                
                description = st.text_area(
                    "📄 Description (Optional)",
                    placeholder="Add meeting agenda, notes, or other details...",
                    height=80,
                    help="Provide additional context for the meeting"
                )
                
                location = st.text_input(
                    "📍 Location (Optional)",
                    placeholder="Conference Room A, Online, etc.",
                    help="Physical or virtual meeting location"
                )
                
                st.markdown("---")
                
                button_col1, button_col2, button_col3 = st.columns([2, 1, 2])
                
                with button_col1:
                    if st.form_submit_button("✅ Confirm Booking", use_container_width=True, type="primary"):
                        if not meeting_title.strip():
                            st.error("❌ Please enter a meeting title")
                        else:
                            booking_data = {
                                "slot": slot,
                                "title": meeting_title.strip(),
                                "duration": duration,
                                "description": description.strip(),
                                "add_meet_link": add_meet_link,
                                "attendees": [email.strip() for email in attendees.split(",") if email.strip()] if attendees else [],
                                "meeting_type": meeting_type,
                                "priority": priority,
                                "location": location.strip()
                            }
                            
                            with st.spinner("Booking your meeting..."):
                                booking_response = book_meeting_with_details(booking_data)
                            
                            if booking_response.get("success"):
                                st.success("🎉 Meeting booked successfully!")
                                
                                confirmation_msg = f"""✅ **Meeting Confirmed!**

📅 **{meeting_title}** ({meeting_type})
🕒 **Time:** {slot['start']} - {slot['end']}
⏱️ **Duration:** {duration} minutes
⚡ **Priority:** {priority}"""
                                
                                if location:
                                    confirmation_msg += f"\n📍 **Location:** {location}"
                                
                                if description:
                                    confirmation_msg += f"\n📄 **Description:** {description}"
                                
                                if booking_response.get("meet_link"):
                                    confirmation_msg += f"\n🔗 **Meet Link:** {booking_response['meet_link']}"
                                
                                if attendees:
                                    confirmation_msg += f"\n👥 **Attendees:** {', '.join([email.strip() for email in attendees.split(',') if email.strip()])}"
                                
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": confirmation_msg
                                })
                                auto_save_chat()
                                
                                st.session_state.show_booking_dialog = False
                                st.session_state.selected_slot = None
                                st.session_state.current_available_slots = []
                                
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ Booking failed: {booking_response.get('message', 'Unknown error')}")
                
                with button_col3:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_booking_dialog = False
                        st.session_state.selected_slot = None
                        st.rerun()
        
        st.markdown("---")

if __name__ == "__main__":
    main()
