import os
import json
from datetime import datetime, timedelta, timezone
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        # Use your local timezone (India Standard Time)
        self.local_timezone = pytz.timezone('Asia/Kolkata')

    def authenticate(self):
        """Authenticate with Google Calendar API"""
        if self.service is not None:
            return self.service
            
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("❌ credentials.json not found! Please place it in the project root.")
                    return None
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar authenticated successfully!")
        return self.service

    def check_availability(self, start_time, end_time):
        """Check if a time slot is available"""
        try:
            if not self.service:
                self.authenticate()
                
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return len(events) == 0
        except Exception as e:
            print(f"Error checking availability: {e}")
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
        """Get ALL available time slots for a given date - NO LIMITS"""
        try:
            if not self.service:
                self.authenticate()
                
            # Parse the date
            if date_str.lower() == 'today':
                target_date = datetime.now(self.local_timezone).date()
            elif date_str.lower() == 'tomorrow':
                target_date = (datetime.now(self.local_timezone) + timedelta(days=1)).date()
            else:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # EXTENDED BUSINESS HOURS: 9 AM to 9 PM (as requested)
            start_datetime = self.local_timezone.localize(
                datetime.combine(target_date, datetime.min.time().replace(hour=9, minute=0))
            )
            end_datetime = self.local_timezone.localize(
                datetime.combine(target_date, datetime.min.time().replace(hour=21, minute=0))  # 9 PM
            )
            
            # Convert to UTC for API call
            start_utc = start_datetime.astimezone(pytz.UTC)
            end_utc = end_datetime.astimezone(pytz.UTC)
            
            print(f"DEBUG: Checking availability from {start_datetime} to {end_datetime} (local)")
            print(f"DEBUG: UTC times: {start_utc} to {end_utc}")
            
            # Get existing events for the ENTIRE day
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
                    
                    # Check for overlap
                    if (current_time < event_end and slot_end > event_start):
                        is_free = False
                        print(f"DEBUG: Slot {current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')} conflicts with event {event_start.strftime('%H:%M')}-{event_end.strftime('%H:%M')}")
                        break
                
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
            
            print(f"DEBUG: Total free slots found: {len(free_slots)}")
            
            # RETURN ALL SLOTS - NO LIMIT!
            return free_slots
            
        except Exception as e:
            print(f"Error getting availability: {e}")
            import traceback
            traceback.print_exc()
            return []

    def book_appointment(self, datetime_str: str, duration_minutes: int, title: str, description: str = ""):
        """Book an appointment with proper timezone handling"""
        try:
            if not self.service:
                self.authenticate()
            
            print(f"DEBUG: Booking appointment at {datetime_str}")
            
            # Parse the datetime string and handle timezone
            if datetime_str.endswith('+05:30') or datetime_str.endswith('+00:00'):
                start_time = datetime.fromisoformat(datetime_str)
            else:
                # Assume local timezone if no timezone info
                start_time = self.local_timezone.localize(datetime.fromisoformat(datetime_str))
            
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            print(f"DEBUG: Booking from {start_time} to {end_time}")
            
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

            event_result = self.service.events().insert(calendarId='primary', body=event).execute()
            
            print(f"DEBUG: Successfully booked event: {event_result.get('htmlLink')}")
            
            # Force refresh service to get updated calendar data
            self.service = None
            
            return {
                'success': True,
                'event_id': event_result['id'],
                'html_link': event_result.get('htmlLink', ''),
                'message': f"✅ Appointment '{title}' booked successfully!"
            }
            
        except Exception as e:
            print(f"Error booking appointment: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f"❌ Error booking appointment: {str(e)}"
            }