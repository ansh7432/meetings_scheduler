# 🤖 AI Calendar Booking Agent

A conversational AI agent built with **LangGraph** that assists users in booking appointments on Google Calendar through natural language conversations.

## 🚀 Mission Statement

This agent engages in natural, back-and-forth conversations to understand user intent, check calendar availability, suggest suitable time slots, and confirm bookings — all seamlessly through chat interface.

## 📸 Project Screenshots & Demo

### **🎥 Assignment Walkthrough Video**
**Google Drive Link**: [AI Calendar Agent - Complete Walkthrough](https://drive.google.com/file/d/15Se1KxJpIpwJy_YuLG3HSxZyL908mOqy/view?usp=sharing)

*This video demonstrates:*
- Complete setup process
- Natural language conversation examples
- Quickbook interface functionality
- Calendar integration in action
- Error handling scenarios
- Deployment process

![Screenshot 2025-06-26 at 3 31 20 PM](https://github.com/user-attachments/assets/e9a31d94-d30d-44a2-9f71-26799708c69e)
![Screenshot 2025-06-26 at 3 31 31 PM](https://github.com/user-attachments/assets/20d634a0-0974-4758-8156-ad7183988167)
![Screenshot 2025-06-26 at 3 31 51 PM](https://github.com/user-attachments/assets/1eef5c8f-2589-4578-8270-2f9083c7dfde)



## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python with FastAPI |
| **Agent Framework** | LangGraph (StateGraph workflows) |
| **Frontend** | Streamlit (chat interface) |
| **Calendar Integration** | Google Calendar API |
| **State Management** | LangGraph conversation flows |
| **Deployment** | Streamlit Cloud + ngrok tunnel |

## 💬 What the Agent Can Do

✅ **Natural Language Processing**: Understands conversational booking requests  
✅ **Intent Recognition**: Identifies booking vs. availability check requests  
✅ **Calendar Integration**: Real-time Google Calendar availability checking  
✅ **Conflict Prevention**: Automatically prevents double-booking  
✅ **Smart Suggestions**: Recommends available time slots  
✅ **Conversational Flow**: Maintains context across multi-turn conversations  
✅ **Quickbook Interface**: Unified booking form with advanced features  
✅ **Chat History**: Persistent conversation history with sidebar navigation  

## 🎯 Key Features

### **🌟 Enhanced Chat Interface**
- **Responsive Design**: Dark theme with professional styling
- **Chat History**: Persistent conversation storage with quick access
- **Quick Actions**: Pre-defined prompts for common requests
- **Status Indicators**: Live/Demo mode indicators
- **Scrollable Chat**: Fixed-height chat container with custom scrollbars

### **⚡ Quickbook Interface**
- **Smart Form**: Dynamic form with meeting details
- **Duration Selection**: Flexible meeting duration options
- **Attendees Management**: Multiple attendees support
- **Google Meet Integration**: Automatic meet link generation
- **Priority Settings**: Meeting priority classification
- **Location Support**: Physical and virtual meeting locations

### **🔄 Advanced State Management**
- **Session Persistence**: Maintains state across page refreshes
- **Multi-turn Conversations**: Context-aware dialogue flows
- **Error Recovery**: Graceful handling of API failures
- **Auto-save**: Automatic conversation backup

## 🤔 Example Conversations the Agent Handles

### **Basic Availability Check**
```
User: "What times are free today?"
Agent: Here are your AVAILABLE time slots for Thursday, June 26, 2025:

🌅 Morning (3 slots available)
⏰ 10:30 AM → 11:30 AM

⏰ 11:00 AM → 12:00 PM

⏰ 11:30 AM → 12:30 PM

☀️ Afternoon (7 slots available)
⏰ 12:00 PM → 1:00 PM

⏰ 12:30 PM → 1:30 PM

📊 Summary
Total Available Slots: 15

All conflicts have been filtered out. Click any slot below to book instantly!
```

### **Quickbook Interface**
```
User: "Quickbook"
Agent: 🚀 Quickbook Interface Activated!

[Shows unified interface with:]
- Available time slots grid
- Meeting details form
- Duration selection
- Attendees management
- Google Meet integration
- Priority settings
```

### **Smart Booking Flow**
```
User: "Schedule a team meeting tomorrow at 2 PM"
Agent: I can help you schedule a team meeting! I found these available slots around 2 PM tomorrow:

✅ 2:00 PM → 3:00 PM (Available)
✅ 2:30 PM → 3:30 PM (Available)
✅ 3:00 PM → 4:00 PM (Available)

Which time slot works best for your team meeting?
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │  Google         │
│   Frontend      │◄──►│   Backend       │◄──►│  Calendar       │
│   (Chat UI)     │    │   (REST API)    │    │  API            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LangGraph     │
                       │   StateGraph    │
                       │   Workflows     │
                       └─────────────────┘
```

### **Enhanced Frontend Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sidebar       │    │  Main Chat      │    │  Quickbook      │
│   Navigation    │    │  Interface      │    │  Interface      │
│                 │    │                 │    │                 │
│ • New Chat      │    │ • Chat Messages │    │ • Time Slots    │
│ • Chat History  │    │ • Input Field   │    │ • Booking Form  │
│ • Quick Actions │    │ • Scroll Area   │    │ • Validation    │
│ • Clear History │    │ • Status Banner │    │ • Confirmation  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **LangGraph Workflow**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Extract   │───►│   Check     │───►│   Book      │
│   Intent    │    │ Availability│    │Appointment  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Generate   │    │  Generate   │    │  Generate   │
│  Response   │    │  Response   │    │  Response   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📁 Project Structure

```
ai-calendar-booking-agent/
├── frontend/
│   ├── streamlit_app.py          # Main Streamlit application
│   └── style.css                 # Custom CSS styling
├── src/
│   ├── main.py                   # FastAPI server with LangGraph
│   ├── models/
│   │   └── state.py              # LangGraph state definitions
│   └── services/
│       ├── calendar_service.py   # Google Calendar integration
│       ├── langgraph_service.py  # LangGraph conversation workflows
│       └── nlp_service.py        # NLP utilities
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
├── token.json                    # Google OAuth token (generated)
├── credentials.json              # Google OAuth credentials
└── README.md                     # This file
```

## 🛠️ Setup & Installation

### **1. Clone Repository**
```bash
git clone <repository-url>
cd ai-calendar-booking-agent
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Google Calendar API**

#### **Step 1: Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

#### **Step 2: Configure Environment Variables**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Google OAuth credentials
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_PROJECT_ID=your_google_project_id_here
```

#### **Step 3: Place Credentials File**
- Place downloaded `credentials.json` in the project root directory

### **5. Start the Application**

#### **Terminal 1: Start API Server**
```bash
cd src
python main.py
```
**Expected Output:**
```
🚀 Initializing LangGraph Agent...
🔧 [LANGGRAPH] Building workflow...
✅ [LANGGRAPH] Workflow compiled successfully!
✅ LangGraph Agent ready!
🚀 Starting AI Calendar Agent with REAL LangGraph...
INFO: Uvicorn running on http://0.0.0.0:8000
```

#### **Terminal 2: Start Streamlit Frontend**
```bash
streamlit run frontend/streamlit_app.py
```
**Expected Output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```

#### **Terminal 3: Expose Backend with ngrok (for deployment)**
```bash
ngrok http 8000
```

## 🌐 Access the Application

- **Chat Interface**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **ngrok Dashboard**: http://127.0.0.1:4040

## 🚀 Deployment

### **Streamlit Cloud Deployment**

1. **Push to GitHub**
2. **Connect Streamlit Cloud to your repository**
3. **Update API_BASE_URL in streamlit_app.py**:
   ```python
   API_BASE_URL = "https://your-ngrok-url.ngrok-free.app"
   ```
4. **Deploy to Streamlit Cloud**

### **Backend Exposure with ngrok**
```bash
# Start ngrok tunnel
ngrok http 8000

# Get public URL from ngrok dashboard
# Update Streamlit app with the ngrok URL
```

## 🎯 Key Features & Edge Cases Handled

### **Natural Language Understanding**
- ✅ Multiple date formats ("today", "tomorrow", "this Friday", "2025-06-25")
- ✅ Various time formats ("2 PM", "14:00", "2:30 PM")
- ✅ Duration extraction ("30 minutes", "2 hours")
- ✅ Intent classification (booking vs. availability checking)
- ✅ Context-aware conversations

### **Calendar Conflict Management**
- ✅ Real-time availability checking
- ✅ Automatic conflict detection
- ✅ Double-booking prevention
- ✅ Smart slot suggestions
- ✅ Business hours enforcement

### **Enhanced User Experience**
- ✅ Responsive design with dark theme
- ✅ Persistent chat history
- ✅ Quick action buttons
- ✅ Real-time status indicators
- ✅ Error handling with user-friendly messages
- ✅ Auto-scroll in chat containers

### **Edge Cases Handled**
- ✅ Invalid date/time inputs
- ✅ Booking conflicts
- ✅ API authentication failures
- ✅ Network connectivity issues
- ✅ Malformed user inputs
- ✅ Calendar service errors
- ✅ Infinite loop prevention in Streamlit Cloud
- ✅ Rate limiting for API calls

## 🧪 Testing the Agent

### **Test Scenarios**

1. **Basic Availability Check**
   ```
   "What times are free today?"
   ```

2. **Quickbook Interface**
   ```
   "Quickbook"
   ```

3. **Specific Day Booking**
   ```
   "Schedule a meeting this Friday at 2 PM"
   ```

4. **Conflict Handling**
   ```
   "Book at 3 PM today" (when 3 PM is already booked)
   ```

5. **Natural Language Variations**
   ```
   "Do you have any slots tomorrow afternoon?"
   "I need to schedule a call next week"
   "Book me between 3-5 PM on Monday"
   ```

## 📊 API Endpoints

### **Chat Endpoint**
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Schedule a meeting tomorrow at 2 PM",
  "session_id": "user123"
}
```

### **Direct Booking**
```http
POST /api/book
Content-Type: application/json

{
  "slot": {
    "start": "2025-06-27T14:00:00",
    "end": "2025-06-27T15:00:00"
  },
  "title": "Team Meeting",
  "duration": 60,
  "description": "Weekly team sync",
  "add_meet_link": true,
  "attendees": ["john@example.com", "jane@example.com"],
  "meeting_type": "Business",
  "priority": "High",
  "location": "Conference Room A"
}
```

### **Health Check**
```http
GET /health

Response: {"status": "healthy", "timestamp": "2025-06-26T10:30:00Z"}
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Google Calendar API
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_PROJECT_ID=your_project_id

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
TIMEZONE=Asia/Kolkata
BUSINESS_HOURS_START=9
BUSINESS_HOURS_END=21
DEFAULT_MEETING_DURATION=60
```

### **Streamlit Configuration**
```python
# In streamlit_app.py
API_BASE_URL = "http://localhost:8000"  # For local development
# API_BASE_URL = "https://your-ngrok-url.ngrok-free.app"  # For deployment
```

### **Business Logic Configuration**
- **Business Hours**: 9 AM - 9 PM (configurable)
- **Default Duration**: 60 minutes
- **Slot Intervals**: 30-minute increments
- **Timezone**: Asia/Kolkata (configurable)
- **Max Slots**: 20 per availability check

## 🏆 Code Quality Features

### **Type Safety**
- Full type hints throughout codebase
- Pydantic models for data validation
- TypedDict for state management

### **Error Handling**
- Custom exception classes
- Comprehensive logging
- Graceful degradation
- Rate limiting protection

### **Frontend Engineering**
- Custom CSS styling
- Responsive design patterns
- State management best practices
- Performance optimization

### **Documentation**
- Comprehensive docstrings
- API documentation with FastAPI
- Architecture diagrams
- User guide examples

## 🏅 Evaluation Criteria Met

### **✅ Code Quality**
- Clean, well-documented code with type hints
- Modular architecture with separation of concerns
- Comprehensive error handling and logging
- Professional UI/UX design

### **✅ Edge Case Handling**
- Robust input validation and sanitization
- Conflict detection and resolution
- Network failure recovery
- Rate limiting and abuse prevention

### **✅ Functionality**
- Natural language understanding with LangGraph
- Real Google Calendar integration
- Conversational AI with context preservation
- Multi-turn conversation support
- Advanced booking interface

### **✅ User Experience**
- Intuitive chat interface
- Responsive design for all devices
- Persistent chat history
- Quick action shortcuts
- Real-time status updates

### **✅ Technical Excellence**
- Scalable FastAPI backend
- Efficient state management
- Production-ready deployment
- Comprehensive API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **LangGraph** for powerful conversation workflows
- **FastAPI** for robust API development
- **Streamlit** for rapid frontend development
- **Google Calendar API** for calendar integration
- **ngrok** for secure tunneling
## NOTE:

please update the requirements.txt file 

```
FastAPI==0.104.1
uvicorn==0.24.0
Streamlit==1.28.0
# Environment Management
python-dotenv==1.0.0
# LangGraph and LangChain (Core AI)
langgraph==0.2.16
langchain-core==0.3.15
# Google Calendar API
google-auth==2.23.4
google-api-python-client==2.108.0
google-auth-oauthlib==1.1.0
# Core Dependencies
pydantic==2.5.0
requests==2.31.0
pytz==2023.3
# Development
pytest==7.4.3
```
if found any langgraph dependency error just do
```
pip install langgraph

```
---

**Built with ❤️ using LangGraph, FastAPI, and Streamlit**

*For support or questions, please open an issue in the repository.*
