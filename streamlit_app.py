import streamlit as st
from handle_rule_based import handle_rule_based
from handle_llm import handle_llm
from create_watson_session import create_watson_session

assistant, assistant_id, session_id = create_watson_session()

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

bot_type = st.sidebar.radio("Skepticbot version:", ('LLM', 'Rule-based'))

st.title(f"Skepticbot ({bot_type})")
st.caption(f"A chatbot that questions your ideas")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi I'm Skepticbot. I don't believe much, so if you have any beliefs you want challenged write them below. I bet you can't convince me that you hold a single true belief!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

def process_response(option_text):
    # Fetch session info
    assistant, assistant_id, session_id = st.session_state['watson_session']
    # Handle the user's choice
    response_followup, assistant, response_data = handle_rule_based(option_text, assistant, assistant_id, session_id)
    # Extract and display response text
    st.session_state.messages.append({"role": "assistant", "content": response_followup})
    st.chat_message("assistant").write(response_followup)
    # Update session info
    st.session_state['watson_session'] = (assistant, assistant_id, session_id)
    # Recursively render new buttons if available
    render_option_buttons(response_data)

def render_option_buttons(response_data):
    # Navigate to the nested 'options' within 'generic'
    if 'output' in response_data and 'generic' in response_data['output']:
        for item in response_data['output']['generic']:
            if item.get('response_type') == 'option' and 'options' in item:
                for option in item['options']:
                    button_key = f"btn_{option['label'].replace(' ', '_')}"
                    if st.button(option['label'], key=button_key):
                        # Process the corresponding response when a button is clicked
                        process_response(option['value']['input']['text'])


def handle_chat_input(prompt):
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
            else:
                assistant, assistant_id, session_id = st.session_state['watson_session']

            response, assistant, response_data = handle_rule_based(prompt, assistant, assistant_id, session_id)
            print(response_data)
            st.session_state['response_data'] = response_data
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

            render_option_buttons(response_data)

# Main execution flow
if prompt := st.chat_input():
    handle_chat_input(prompt)
