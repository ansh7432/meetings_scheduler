class ConversationManager:
    def __init__(self):
        self.state = {}
    
    def start_conversation(self, user_id):
        self.state[user_id] = {
            'intent': None,
            'time_slot': None,
            'date': None,
            'confirmation': False
        }
    
    def update_intent(self, user_id, intent):
        if user_id in self.state:
            self.state[user_id]['intent'] = intent
    
    def update_time_slot(self, user_id, time_slot):
        if user_id in self.state:
            self.state[user_id]['time_slot'] = time_slot
    
    def update_date(self, user_id, date):
        if user_id in self.state:
            self.state[user_id]['date'] = date
    
    def confirm_booking(self, user_id):
        if user_id in self.state:
            self.state[user_id]['confirmation'] = True
    
    def get_conversation_state(self, user_id):
        return self.state.get(user_id, None)
    
    def end_conversation(self, user_id):
        if user_id in self.state:
            del self.state[user_id]