from streamlit import st

class ChatInterface:
    def __init__(self):
        self.messages = []

    def display_messages(self):
        for message in self.messages:
            st.write(message)

    def get_user_input(self):
        user_input = st.text_input("You: ", "")
        return user_input

    def add_message(self, message):
        self.messages.append(message)

def main():
    st.title("AI Calendar Booking Agent")
    chat_interface = ChatInterface()

    while True:
        chat_interface.display_messages()
        user_input = chat_interface.get_user_input()

        if user_input:
            chat_interface.add_message(f"You: {user_input}")
            # Here you would typically send the user_input to the backend for processing
            # For now, we will just echo the input
            chat_interface.add_message(f"Agent: You said '{user_input}'")

if __name__ == "__main__":
    main()