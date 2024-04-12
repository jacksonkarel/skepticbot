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
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi I'm Skepticbot. I don't believe much, so if you have any beliefs you want challenged write them below. I bet you can't convince me that you hold a single true belief!"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

def process_response(option_text):
    print("Processing response for:", option_text)  # Debug print
    assistant, assistant_id, session_id = st.session_state['watson_session']
    response_followup, assistant, response_data = handle_rule_based(option_text, assistant, assistant_id, session_id)
    print("Follow-up response:", response_followup)  # Debug print
    print("Response Data:", response_data)  # Debug print

    st.session_state.messages.append({"role": "assistant", "content": response_followup})
    st.chat_message("assistant").write(response_followup)
    st.session_state['watson_session'] = (assistant, assistant_id, session_id)

    if 'output' in response_data and 'generic' in response_data['output']:
        render_option_buttons(response_data)  # Ensure this function call is correct
    st.experimental_rerun()  # Make sure to rerun to update the UI

def render_option_buttons(response_data):
    print("Rendering buttons for:", response_data)  # Debug print
    if 'output' in response_data and 'generic' in response_data['output']:
        for item in response_data['output']['generic']:
            if item.get('response_type') == 'option' and 'options' in item:
                for option in item['options']:
                    button_key = f"btn_{option['label'].replace(' ', '_')}"
                    if st.button(option['label'], key=button_key):
                        print("Button clicked:", option['label'])  # Additional debug print
                        process_response(option['value']['input']['text'])

def handle_chat_input(prompt):
    print("Handling input:", prompt)  # Debug print
    if prompt:
        bot_type_llm = bot_type == "LLM"
        if bot_type_llm and not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if bot_type == "LLM":
            response = handle_llm(prompt, openai_api_key)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
        else:
            if 'watson_session' not in st.session_state:
                assistant, assistant_id, session_id = create_watson_session()
                st.session_state['watson_session'] = (assistant, assistant_id, session_id)

            response, assistant, response_data = handle_rule_based(prompt, assistant, assistant_id, session_id)
            st.session_state['response_data'] = response_data
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

            render_option_buttons(response_data)

if prompt := st.chat_input():
    handle_chat_input(prompt)
