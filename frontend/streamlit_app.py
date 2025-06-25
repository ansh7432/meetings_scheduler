import streamlit as st
import requests
import json
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="AI Calendar Booking Agent",
    page_icon="📅",
    layout="wide"
)

# Enhanced CSS for proper chatbox with Streamlit components
st.markdown("""
<style>
    /* Clean, minimal styling */
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
    
    /* Chat container styling */
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
    
    /* Streamlit chat message styling */
    .stChatMessage {
        margin: 0.5rem 0;
    }
    
    /* User message styling */
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
    
    /* Assistant message styling */
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
    
    /* Time slots */
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
    
    .time-slot:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }
    
    /* Success message */
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
    
    /* Input styling */
    .stTextInput input {
        border-radius: 15px !important;
        border: 2px solid #e9ecef !important;
        padding: 0.8rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Sidebar styling */
    .sidebar-example {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .sidebar-example:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        transform: translateX(5px);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Chat input container */
    .stChatInputContainer {
        background: white;
        border-radius: 15px;
        padding: 0.5rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

def send_message(message: str):
    """Send message to the FastAPI backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": message, "session_id": st.session_state.session_id},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"response": f"Error: {response.status_code}", "intent": "error"}
    except requests.exceptions.RequestException as e:
        return {"response": f"Connection error: {str(e)}", "intent": "error"}

def book_slot(slot_datetime, duration=60, title="Meeting"):
    """Book a specific time slot"""
    try:
        dt = datetime.fromisoformat(slot_datetime.replace('Z', '+00:00'))
        date_str = dt.date().isoformat()
        time_str = dt.strftime('%H:%M')
        
        response = requests.post(
            f"{API_BASE_URL}/api/book",
            json={
                "date": date_str,
                "time": time_str,
                "duration": duration,
                "description": title
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return {"success": True, "message": "✅ Appointment booked successfully!"}
        else:
            return {"success": False, "message": f"❌ Booking failed: {response.text}"}
    except Exception as e:
        return {"success": False, "message": f"❌ Error: {str(e)}"}

def main():
    # Clean title
    st.markdown('<h1 class="main-title">🤖 AI Calendar Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Schedule appointments with natural language</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your AI calendar assistant. I can help you schedule appointments, check availability, and manage your calendar. How can I help you today?"}
        ]
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create layout - more space for chat
    col1, col2 = st.columns([3.5, 1])
    
    with col1:
        st.markdown("### 💬 Chat")
        
        # Create a contained chat area
        with st.container():
            # Use Streamlit's native chat display with custom height
            chat_container = st.container(height=500)
            
            with chat_container:
                # Display all messages using Streamlit's chat components
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here... 💭"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    response = send_message(prompt)
                    
                    ai_response = response.get("response", "Sorry, I couldn't process that.")
                    booking_info = response.get("booking_info", {})
                    available_slots = response.get("available_slots", [])
                    
                    # Show success message if booking was successful
                    if booking_info.get('booked'):
                        st.markdown(f"""
                        <div class="success-box">
                            🎉 <strong>Booking Confirmed!</strong><br>
                            📅 {booking_info['date']} at {booking_info['time']} ({booking_info['duration']} min)
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    
                    # Display AI response
                    st.markdown(ai_response)
                    
                    # Add AI response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                    # Show booking interface for available slots
                    if available_slots:
                        st.markdown("### 📅 Available Time Slots")
                        st.markdown("Click on any slot to book your meeting:")
                        
                        # Show slots in a nice grid
                        cols = st.columns(3)
                        
                        for i, slot in enumerate(available_slots[:12]):  # Show first 12 slots
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
                                    placeholder="Enter title",
                                    label_visibility="collapsed"
                                )
                                
                                # Book button
                                if st.button(f"📅 Book {slot['start']}", key=f"book_{i}_{slot['start']}_{len(st.session_state.messages)}", use_container_width=True):
                                    with st.spinner("Booking..."):
                                        booking_result = book_slot(slot['datetime'], 60, meeting_title)
                                        if booking_result['success']:
                                            st.success(f"✅ Booked: {meeting_title}")
                                            # Add booking confirmation to chat
                                            st.session_state.messages.append({
                                                "role": "assistant", 
                                                "content": f"✅ Successfully booked '{meeting_title}' for {slot['start']} - {slot['end']}"
                                            })
                                            st.rerun()
                                        else:
                                            st.error(booking_result['message'])
                        
                        # Show more slots info
                        if len(available_slots) > 12:
                            st.info(f"Showing 12 of {len(available_slots)} available slots. Ask for specific times to see more!")
            
            # Rerun to update the chat display
            st.rerun()
        
        # Clear chat button at bottom
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi! I'm your AI calendar assistant. How can I help you today?"}
            ]
            st.rerun()
    
    with col2:
        st.markdown("### 💡 Try These")
        
        examples = [
            "Do you have any free time today?",
            "Schedule a call for tomorrow at 2 PM", 
            "What's available this Friday?",
            "Book a 30-minute meeting at 3 PM",
            "Check my availability for next week",
            "Schedule a team meeting for Monday",
            "I need a 1-hour slot this afternoon",
            "What times are free on Thursday?"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"💬 {example}", key=f"example-btn-{i}", use_container_width=True, help="Click to try this example"):
                st.session_state.messages.append({"role": "user", "content": example})
                response = send_message(example)
                st.session_state.messages.append({"role": "assistant", "content": response.get("response", "No response")})
                st.rerun()

if __name__ == "__main__":
    main()