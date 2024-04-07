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

if prompt := st.chat_input():
    bot_type_llm = bot_type == "LLM"

    if bot_type_llm and not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if bot_type == "LLM":
        response = handle_llm(prompt, openai_api_key)
    else:
        response_data = handle_rule_based(prompt, assistant, assistant_id, session_id)
        response = response_data['output']['generic'][0]['text']  # Assuming the first 'generic' entry contains the text.
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

        # Check for option type responses and render buttons
        for item in response_data['output']['generic']:
            if item['response_type'] == 'option':
                for option in item['options']:
                    if st.button(option['label']):
                        # Simulate the user selecting the option by adding it as user input
                        st.session_state.messages.append({"role": "user", "content": option['label']})
                        st.chat_message("user").write(option['label'])

                        # Generate the next response based on the option selected
                        response_followup = handle_rule_based(option['value']['input']['text'])
                        followup_text = response_followup['output']['generic'][0]['text']
                        st.session_state.messages.append({"role": "assistant", "content": followup_text})
                        st.chat_message("assistant").write(followup_text)

