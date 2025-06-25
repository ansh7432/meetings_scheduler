import os
import json
import tempfile
from datetime import datetime, timedelta, timezone
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        # Use timezone from env or default
        timezone_str = os.getenv('TIMEZONE', 'Asia/Kolkata')
        self.local_timezone = pytz.timezone(timezone_str)

    def _create_credentials_from_env(self):
        """Create credentials.json content from environment variables"""
        credentials_data = {
            "installed": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URIS', 'http://localhost')]
            }
        }
        
        # Validate required fields
        required_fields = ['client_id', 'client_secret', 'project_id']
        missing_fields = [field for field in required_fields if not credentials_data['installed'].get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required Google OAuth environment variables: {', '.join(missing_fields)}")
        
        return credentials_data

    def authenticate(self):
        """Authenticate with Google Calendar API using environment variables"""
        if self.service is not None:
            return self.service
            
        creds = None
        
        # Try to load existing token
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("✅ Google Calendar token refreshed successfully!")
                except Exception as e:
                    print(f"⚠️ Token refresh failed: {e}. Creating new credentials...")
                    creds = None
            
            if not creds:
                try:
                    # Try environment variables first
                    credentials_data = self._create_credentials_from_env()
                    
                    # Create temporary credentials file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                        json.dump(credentials_data, temp_file)
                        temp_credentials_path = temp_file.name
                    
                    # Use temporary file for OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        temp_credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                    
                    # Clean up temporary file
                    os.unlink(temp_credentials_path)
                    
                    print("✅ Google Calendar authenticated using environment variables!")
                    
                except (ValueError, FileNotFoundError) as e:
                    print(f"⚠️ Environment variables not found or incomplete: {e}")
                    
                    # Fallback to credentials.json file
                    if os.path.exists('credentials.json'):
                        print("🔄 Falling back to credentials.json file...")
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        print("✅ Google Calendar authenticated using credentials.json!")
                    else:
                        raise Exception(
                            "❌ No valid Google OAuth credentials found! "
                            "Please either:\n"
                            "1. Set environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, etc.)\n"
                            "2. Place credentials.json in the project root"
                        )
            
            # Save credentials for future use
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar service initialized successfully!")
        return self.service

    def check_availability(self, start_time_str, end_time_str):
        """Check if a specific time slot is available (NO CONFLICTS)"""
        try:
            if not self.service:
                self.authenticate()
            
            # Parse times and ensure they have timezone info
            if isinstance(start_time_str, str):
                if start_time_str.endswith('+05:30') or start_time_str.endswith('+00:00'):
                    start_time = datetime.fromisoformat(start_time_str)
                else:
                    # Parse and add local timezone
                    start_time = datetime.fromisoformat(start_time_str)
                    if start_time.tzinfo is None:
                        start_time = self.local_timezone.localize(start_time)
            else:
                start_time = start_time_str
            
            if isinstance(end_time_str, str):
                if end_time_str.endswith('+05:30') or end_time_str.endswith('+00:00'):
                    end_time = datetime.fromisoformat(end_time_str)
                else:
                    # Parse and add local timezone
                    end_time = datetime.fromisoformat(end_time_str)
                    if end_time.tzinfo is None:
                        end_time = self.local_timezone.localize(end_time)
            else:
                end_time = end_time_str
            
            # Convert to UTC for API call
            start_utc = start_time.astimezone(pytz.UTC)
            end_utc = end_time.astimezone(pytz.UTC)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_utc.isoformat(),
                timeMax=end_utc.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # If there are ANY events in this time range, it's NOT available
            is_available = len(events) == 0
            
            if not is_available:
                print(f"🔍 [CHECK_AVAILABILITY] Conflict found for {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}: {len(events)} events")
            else:
                print(f"✅ [CHECK_AVAILABILITY] Slot is free: {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}")
            
            return is_available
            
        except Exception as e:
            print(f"❌ Error checking availability: {e}")
            return False

    def convert_to_12_hour_format(self, time_24):
        """Convert 24-hour time to 12-hour format"""
        try:
            hour, minute = map(int, time_24.split(':'))
            if hour == 0:
                return f"12:{minute:02d} AM"
            elif hour < 12:
                return f"{hour}:{minute:02d} AM"
            elif hour == 12:
                return f"12:{minute:02d} PM"
            else:
                return f"{hour-12}:{minute:02d} PM"
        except:
            return time_24

    def get_free_time_slots(self, date_str: str, duration_minutes: int = 60):
        """Get ONLY truly available time slots for a given date"""
        try:
            if not self.service:
                self.authenticate()
            
            # Use duration from env if not specified
            if duration_minutes == 60:
                duration_minutes = int(os.getenv('DEFAULT_MEETING_DURATION', 60))
                
            # Parse the date
            if date_str.lower() == 'today':
                target_date = datetime.now(self.local_timezone).date()
            elif date_str.lower() == 'tomorrow':
                target_date = (datetime.now(self.local_timezone) + timedelta(days=1)).date()
            else:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Use business hours from environment
            start_hour = int(os.getenv('BUSINESS_HOURS_START', 9))
            end_hour = int(os.getenv('BUSINESS_HOURS_END', 21))
            
            start_datetime = self.local_timezone.localize(
                datetime.combine(target_date, datetime.min.time().replace(hour=start_hour, minute=0))
            )
            end_datetime = self.local_timezone.localize(
                datetime.combine(target_date, datetime.min.time().replace(hour=end_hour, minute=0))
            )
            
            print(f"DEBUG: Checking availability from {start_datetime} to {end_datetime} (local)")
            
            # Get existing events for the ENTIRE day
            start_utc = start_datetime.astimezone(pytz.UTC)
            end_utc = end_datetime.astimezone(pytz.UTC)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_utc.isoformat(),
                timeMax=end_utc.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"DEBUG: Found {len(events)} existing events")
            
            # Print existing events for debugging
            for event in events:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                print(f"DEBUG: Existing event: {event.get('summary', 'No title')} from {event_start} to {event_end}")
            
            # Create time slots every 30 minutes throughout the day
            free_slots = []
            current_time = start_datetime
            slot_duration = timedelta(minutes=duration_minutes)
            
            while current_time + slot_duration <= end_datetime:
                slot_end = current_time + slot_duration
                
                # Check if this slot conflicts with any existing event
                is_free = True
                for event in events:
                    event_start_str = event['start'].get('dateTime', event['start'].get('date'))
                    event_end_str = event['end'].get('dateTime', event['end'].get('date'))
                    
                    # Parse event times and convert to local timezone
                    if 'T' in event_start_str:
                        if event_start_str.endswith('Z'):
                            event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                        else:
                            event_start = datetime.fromisoformat(event_start_str)
                        
                        # Convert to local timezone if it has timezone info
                        if event_start.tzinfo:
                            event_start = event_start.astimezone(self.local_timezone)
                        else:
                            event_start = self.local_timezone.localize(event_start)
                    else:
                        event_start = self.local_timezone.localize(
                            datetime.fromisoformat(event_start_str + 'T00:00:00')
                        )
                    
                    if 'T' in event_end_str:
                        if event_end_str.endswith('Z'):
                            event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
                        else:
                            event_end = datetime.fromisoformat(event_end_str)
                        
                        # Convert to local timezone if it has timezone info
                        if event_end.tzinfo:
                            event_end = event_end.astimezone(self.local_timezone)
                        else:
                            event_end = self.local_timezone.localize(event_end)
                    else:
                        event_end = self.local_timezone.localize(
                            datetime.fromisoformat(event_end_str + 'T23:59:59')
                        )
                    
                    # Check for overlap - ANY OVERLAP means conflict
                    if (current_time < event_end and slot_end > event_start):
                        is_free = False
                        print(f"DEBUG: Slot {current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')} conflicts with event {event_start.strftime('%H:%M')}-{event_end.strftime('%H:%M')}")
                        break
                
                # ONLY ADD IF TRULY FREE
                if is_free:
                    # Convert to 12-hour format for display
                    start_12hr = self.convert_to_12_hour_format(current_time.strftime('%H:%M'))
                    end_12hr = self.convert_to_12_hour_format(slot_end.strftime('%H:%M'))
                    
                    free_slots.append({
                        'start': start_12hr,
                        'end': end_12hr,
                        'start_24': current_time.strftime('%H:%M'),
                        'end_24': slot_end.strftime('%H:%M'),
                        'datetime': current_time.isoformat()
                    })
                    print(f"DEBUG: Free slot found: {start_12hr} - {end_12hr}")
                
                # Move to next 30-minute slot
                current_time += timedelta(minutes=30)
            
            print(f"DEBUG: Total TRULY FREE slots found: {len(free_slots)}")
            
            return free_slots
            
        except Exception as e:
            print(f"Error getting availability: {e}")
            import traceback
            traceback.print_exc()
            return []

    def book_appointment(self, datetime_str: str, duration_minutes: int, title: str, description: str = "", add_meet_link: bool = True, attendees: list = None):
        """Book an appointment with Google Meet link and attendees"""
        try:
            if not self.service:
                self.authenticate()
            
            print(f"🔄 [BOOKING] Scheduling: {title} at {datetime_str} for {duration_minutes} minutes")
            
            # Parse the datetime string and handle timezone
            if datetime_str.endswith('+05:30') or datetime_str.endswith('+00:00'):
                start_time = datetime.fromisoformat(datetime_str)
            else:
                start_time = self.local_timezone.localize(datetime.fromisoformat(datetime_str))
            
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Build event object
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': str(start_time.tzinfo),
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': str(end_time.tzinfo),
                },
            }
            
            # Add Google Meet conference link
            if add_meet_link:
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': f"meet-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                }
            
            # Add attendees if provided
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create the event with conference data
            event_result = self.service.events().insert(
                calendarId='primary', 
                body=event,
                conferenceDataVersion=1 if add_meet_link else 0,
                sendUpdates='all' if attendees else 'none'
            ).execute()
            
            print(f"✅ [BOOKING] Successfully created event: {event_result.get('id')}")
            
            # Extract Google Meet link if available
            meet_link = None
            if 'conferenceData' in event_result and 'entryPoints' in event_result['conferenceData']:
                for entry in event_result['conferenceData']['entryPoints']:
                    if entry['entryPointType'] == 'video':
                        meet_link = entry['uri']
                        break
            
            # Force refresh service to get updated calendar data
            self.service = None
            
            return {
                'success': True,
                'event_id': event_result['id'],
                'html_link': event_result.get('htmlLink', ''),
                'meet_link': meet_link,
                'calendar_link': event_result.get('htmlLink', ''),
                'message': f"✅ Meeting '{title}' booked successfully!",
                'details': {
                    'title': title,
                    'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
                    'duration': duration_minutes,
                    'attendees_count': len(attendees) if attendees else 0
                }
            }
            
        except Exception as e:
            print(f"❌ [BOOKING] Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f"❌ Booking failed: {str(e)}"
            }