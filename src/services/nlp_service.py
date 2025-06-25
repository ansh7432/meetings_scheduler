import re
from datetime import datetime, timedelta
from dateutil import parser
import calendar

class NLPService:
    def _get_next_weekday(self, weekday):
        """Get the next occurrence of a weekday (0=Monday, 6=Sunday)"""
        today = datetime.now().date()
        days_ahead = weekday - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days_ahead)

    def __init__(self):
        self.intent_patterns = {
            'book_appointment': [
                r'schedule.*call|book.*meeting|set.*appointment|arrange.*meeting',
                r'want.*schedule|need.*book|plan.*meeting',
                r'schedule.*at|book.*at|meeting.*at|book.*between'
            ],
            'check_availability': [
                r'available|free time|open slots|any time',
                r'what.*time|when.*free|check.*calendar',
                r'availability.*for'
            ],
            'cancel_appointment': [
                r'cancel.*meeting|delete.*appointment|remove.*booking'
            ]
        }
        
        self.time_patterns = {
            'today': datetime.now().date(),
            'tomorrow': (datetime.now() + timedelta(days=1)).date(),
            'next week': (datetime.now() + timedelta(weeks=1)).date(),
            'this friday': self._get_next_weekday(4),
            'friday': self._get_next_weekday(4),
            'this monday': self._get_next_weekday(0),
            'monday': self._get_next_weekday(0),
            'this tuesday': self._get_next_weekday(1),
            'tuesday': self._get_next_weekday(1),
            'this wednesday': self._get_next_weekday(2),
            'wednesday': self._get_next_weekday(2),
            'this thursday': self._get_next_weekday(3),
            'thursday': self._get_next_weekday(3),
            'this saturday': self._get_next_weekday(5),
            'saturday': self._get_next_weekday(5),
            'this sunday': self._get_next_weekday(6),
            'sunday': self._get_next_weekday(6),
        }

    def extract_intent(self, user_input: str) -> dict:
        """Extract intent from user input"""
        user_input_lower = user_input.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    result = {
                        'intent': intent,
                        'confidence': 0.8,
                        'original_text': user_input
                    }
                    
                    time_info = self.extract_datetime(user_input)
                    if time_info:
                        result.update(time_info)
                    
                    return result
        
        return {
            'intent': 'unknown',
            'confidence': 0.0,
            'original_text': user_input
        }

    def extract_datetime(self, user_input: str) -> dict:
        """Extract date and time information from user input"""
        user_input_lower = user_input.lower()
        result = {}
        
        for time_phrase, date_obj in self.time_patterns.items():
            if time_phrase in user_input_lower:
                result['date'] = date_obj.isoformat()
                result['time_phrase'] = time_phrase
                break
        
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(pm|am|p\.m\.|a\.m\.)',
            r'(\d{1,2})\s*(pm|am|p\.m\.|a\.m\.)',
            r'(\d{1,2}):(\d{2})',
            r'at\s+(\d{1,2}):?(\d{2})?\s*(pm|am)?',
            r'between\s+(\d{1,2}):?(\d{2})?\s*(pm|am)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                hour = int(match.group(1))
                
                if len(match.groups()) >= 2 and match.group(2) and match.group(2).isdigit():
                    minute = int(match.group(2))
                else:
                    minute = 0
                
                am_pm = None
                for group in match.groups():
                    if group and ('am' in group or 'pm' in group):
                        am_pm = group
                        break
                
                if am_pm:
                    if 'pm' in am_pm.lower() and hour != 12:
                        hour += 12
                    elif 'am' in am_pm.lower() and hour == 12:
                        hour = 0
                
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    result['time'] = f"{hour:02d}:{minute:02d}"
                    result['requested_hour'] = hour
                    break
        
        duration_match = re.search(r'(\d+)\s*[-–]?\s*(hour|minute|hr|min)', user_input_lower)
        if duration_match:
            duration_value = int(duration_match.group(1))
            duration_unit = duration_match.group(2)
            
            if 'hour' in duration_unit or 'hr' in duration_unit:
                result['duration'] = duration_value * 60
            else:
                result['duration'] = duration_value
        else:
            result['duration'] = 60
        
        return result

    def parse_natural_language_date(self, date_string: str) -> str:
        """Parse natural language date to ISO format"""
        date_string_lower = date_string.lower()
        
        for phrase, date_obj in self.time_patterns.items():
            if phrase in date_string_lower:
                return date_obj.isoformat()
        
        try:
            parsed_date = parser.parse(date_string, fuzzy=True)
            return parsed_date.date().isoformat()
        except:
            return datetime.now().date().isoformat()

    def generate_response(self, intent: str, context: dict) -> str:
        """Generate appropriate response based on intent and context"""
        responses = {
            'book_appointment': [
                "I'll help you schedule that appointment. Let me check availability.",
                "Sure! Let me find the best time for your meeting.",
                "I can help you book that. Checking calendar availability now."
            ],
            'check_availability': [
                "Let me check your calendar for available times.",
                "I'll look for free slots in your schedule.",
                "Checking availability now..."
            ],
            'unknown': [
                "I'd be happy to help you schedule an appointment. Could you tell me when you'd like to meet?",
                "I can help you book meetings. What date and time work for you?",
                "Let me help you with scheduling. When would you like to meet?"
            ]
        }
        
        import random
        return random.choice(responses.get(intent, responses['unknown']))