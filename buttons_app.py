import streamlit as st
from streamlit_feedback import streamlit_feedback
from create_watson_session import create_watson_session
import uuid
from handle_rule_based import handle_rule_based


assistant, assistant_id, session_id = create_watson_session()

if 'question_state' not in st.session_state:
    st.session_state.question_state = False

if 'fbk' not in st.session_state:
    st.session_state.fbk = str(uuid.uuid4())


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "watson_session" not in st.session_state:
    st.session_state.watson_session = (assistant, assistant_id, session_id)


def display_answer():
    for entry in st.session_state.chat_history:
        with st.chat_message("human"):
            st.write(entry["question"])
        with st.chat_message("ai"):
            st.write(entry["answer"])

        # Do not display the feedback field since
        # we are still about to ask the user.
        if 'feedback' not in entry:
            continue

        # If there is no feedback show N/A
        if "feedback" in entry:
            st.write(f"Feedback: {entry['feedback']}")
        else:
            st.write("Feedback: N/A")


def create_answer(question):
    """Add question/answer to history."""
    # Do not save to history if question is None.
    # We reach this because streamlit reruns to get the feedback.
    if question is None:
        return
    
    message_id = len(st.session_state.chat_history)
    
    response, assistant, response_data = handle_rule_based(question, *st.session_state.watson_session)

    print("Response data: ", response_data)

    st.session_state.chat_history.append({
        "question": question,
        "answer": response,
        "message_id": message_id,
    })


def fbcb(response):
    """Update the history with feedback.
    
    The question and answer are already saved in history.
    Now we will add the feedback in that history entry.
    """
    last_entry = st.session_state.chat_history[-1]  # get the last entry
    last_entry.update({'feedback': response})  # update the last entry
    st.session_state.chat_history[-1] = last_entry  # replace the last entry
    display_answer()  # display hist

    # Create a new feedback by changing the key of feedback component.
    st.session_state.fbk = str(uuid.uuid4())


# Starts here.
question = st.chat_input(placeholder="Ask your question here .... !!!!")
if question:
    # We need this because of feedback. That question above
    # is a stopper. If user hits the feedback button, streamlit
    # reruns the code from top and we cannot enter back because
    # of that chat_input.
    st.session_state.question_state = True

# We are now free because st.session_state.question_state is True.
# But there are consequences. We will have to handle
# the double runs of create_answer() and display_answer()
# just to get the user feedback. 
if st.session_state.question_state:
    create_answer(question)
    display_answer()

    # Pressing a button in feedback reruns the code.
    streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional]",
        align="flex-start",
        key=st.session_state.fbk,
        on_submit=fbcb
    )