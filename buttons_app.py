import streamlit as st
from create_watson_session import create_watson_session
import uuid
from handle_rule_based import handle_rule_based

# Initialize session
assistant, assistant_id, session_id = create_watson_session()

# Initialize session state if not already present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if "watson_session" not in st.session_state:
    st.session_state.watson_session = (assistant, assistant_id, session_id)

def create_answer(question):
    """Add question/answer to history and handle AI response."""
    if question is None:
        return
    
    message_id = len(st.session_state.chat_history)
    response, assistant, response_data = handle_rule_based(question, *st.session_state.watson_session)

    # Extracting button labels from response_data
    options = response_data['output']['generic']
    print(options)
    button_labels = [option['label'] for item in options if item['response_type'] == 'option' for option in item['options']]

    st.session_state.chat_history.append({
        "question": question,
        "answer": response,
        "message_id": message_id,
        "button_labels": button_labels  # Store button labels for next interaction
    })

def display_answer():
    for entry in st.session_state.chat_history:
        with st.chat_message("human"):
            st.write(entry["question"])
        with st.chat_message("ai"):
            st.write(entry["answer"])

        # Display buttons as user response options
        if 'button_labels' in entry:
            for label in entry['button_labels']:
                print("\nLabel:", label)
                print("Key:", f"{entry['message_id']}-{label}")
                if st.button(label, key=f"{entry['message_id']}-{label}"):
                    print("Button clicked. Label: ", label)
                    handle_user_response(label)

def handle_user_response(label):
    """Handle the user response when a button is clicked."""
    create_answer(label)  # Process the label as a new question
    display_answer()  # Update the display

# Main interaction loop
question = st.chat_input("Ask your question here .... !!!!")
if question:
    create_answer(question)
    display_answer()
