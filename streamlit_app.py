import streamlit as st
from handle_rule_based import handle_rule_based
from handle_llm import handle_llm
from create_watson_session import create_watson_session

# Initialize Watson session
assistant, assistant_id, session_id = create_watson_session()

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

# Choose the bot type from sidebar options
bot_type = st.sidebar.radio("Skepticbot version:", ('LLM', 'Rule-based'))

st.title(f"Skepticbot ({bot_type})")
st.caption("A chatbot that questions your ideas")

# Initialize session state for messages if not already done
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize or update session variables for response handling
if "watson_session" not in st.session_state:
    st.session_state.watson_session = (assistant, assistant_id, session_id)

def add_message(role, content):
    """Add a message to the session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append({"role": role, "content": content})

def process_response(option_text):
    """Process the chatbot's response after a button click."""
    assistant, assistant_id, session_id = st.session_state.watson_session
    response_followup, assistant, response_data = handle_rule_based(option_text, assistant, assistant_id, session_id)
    add_message("assistant", response_followup)
    st.session_state.watson_session = (assistant, assistant_id, session_id)
    return response_followup

def on_button_click(option_text):
    """Handle button click event."""
    response_followup = process_response(option_text)
    add_message("assistant", response_followup)
    # After processing, we clear the user input to reset the chat input field
    st.session_state.user_input = ''

def render_option_buttons(response_data):
    """Render buttons based on response data and assign click handlers."""
    if 'output' in response_data and 'generic' in response_data['output']:
        for item in response_data['output']['generic']:
            if item.get('response_type') == 'option' and 'options' in item:
                for option in item['options']:
                    st.button(option['label'], on_click=on_button_click, args=[option['value']['input']['text']])

# Function to clear the user input
def clear_user_input():
    st.session_state.user_input = ""

# Handle user input and process the response
def handle_chat_input():
    user_input = st.session_state.get("user_input", "")
    if user_input:  # Check if there's input to process
        if bot_type == "LLM" and openai_api_key:
            response = handle_llm(user_input, openai_api_key)
            add_message("assistant", response)
        else:
            response, assistant, response_data = handle_rule_based(user_input, *st.session_state.watson_session)
            render_option_buttons(response_data)
            add_message("assistant", response)
        add_message("user", user_input)
        st.session_state.user_input = ''  # Reset user_input for the next interaction
        st.experimental_rerun()  # Rerun to clear the input field

def on_submit():
    user_input = st.session_state.user_input  # Get the current input
    if user_input:  # If there's an input, process it
        # Your existing input handling logic
        # ...
        st.session_state.user_input = ''  # Clear the input after processing

# Display the input field and a submit button that triggers the callback
user_input = st.text_input("Enter your belief to challenge:", key="user_input")
submit_button = st.button("Submit", on_click=on_submit)

# Display chat messages
for msg in st.session_state.get("messages", []):
    st.write(f"{msg['role']}: {msg['content']}")


