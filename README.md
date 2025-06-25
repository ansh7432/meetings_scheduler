# AI Calendar Booking Agent

This project is an AI-powered conversational agent designed to assist users in booking appointments through a chat interface. The agent utilizes natural language processing to understand user intents and interacts with Google Calendar to check availability and confirm bookings.

## Project Structure

```
ai-calendar-booking-agent
├── src
│   ├── main.py                # Entry point for the FastAPI application
│   ├── api                    # API module for handling requests
│   │   ├── routes.py          # Defines API routes for booking appointments
│   │   └── dependencies.py     # Dependency injection functions
│   ├── agents                 # Contains the booking agent and conversation manager
│   │   ├── booking_agent.py    # Manages conversation flow for booking
│   │   └── conversation_manager.py # Manages conversation state
│   ├── services               # Services for calendar and NLP functionalities
│   │   ├── calendar_service.py  # Interacts with Google Calendar API
│   │   └── nlp_service.py      # Processes natural language input
│   ├── models                 # Pydantic models for request and response schemas
│   │   └── schemas.py          # Defines request and response schemas
│   ├── config                 # Configuration settings
│   │   └── settings.py         # Contains API keys and environment variables
│   └── utils                  # Utility functions
│       └── helpers.py          # Assists with various tasks
├── frontend                   # Frontend application using Streamlit
│   ├── streamlit_app.py        # Main entry point for the Streamlit app
│   ├── components              # UI components for the frontend
│   │   └── chat_interface.py    # Defines the chat interface component
│   └── styles                 # CSS styles for the frontend
│       └── main.css            # Styles for the Streamlit application
├── tests                      # Unit tests for the application
│   ├── test_agents.py          # Tests for booking agent functionalities
│   ├── test_services.py        # Tests for calendar and NLP services
│   └── test_api.py            # Tests for API routes
├── requirements.txt           # Lists project dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Files to ignore in Git
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd ai-calendar-booking-agent
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in the required API keys and settings.

5. **Run the FastAPI application:**
   ```
   uvicorn src.main:app --reload
   ```

6. **Run the Streamlit frontend:**
   ```
   streamlit run frontend/streamlit_app.py
   ```

## Usage

- Open the Streamlit application in your browser.
- Interact with the chat interface to book appointments by typing natural language requests.
- The agent will check your Google Calendar for availability and confirm bookings.

## Example Conversations

- "Hey, I want to schedule a call for tomorrow afternoon."
- "Do you have any free time this Friday?"
- "Book a meeting between 3-5 PM next week."

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.# meetings_scheduler
