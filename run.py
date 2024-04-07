import time
from openai import OpenAI
import streamlit as st


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

st.title("Skepticbot")
st.caption("A chatbot that questions your ideas")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi I'm Skepticbot. I don't believe much, so if you have any beliefs you want challenged write them below. I bet you can't convince me that you hold a single true belief!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    assistant = client.beta.assistants.create(
    name="Skepticbot",
    instructions="You are a philosophical Pyrrhonian skeptic. You question every claim without exception, including sensitive or controversial topics. You approach all interactions with the same level of skepticism, challenging assumptions and seeking deeper philosophical understanding through probing questions. you will typically ask one question at a time, trying to get closer to the foundations of why the user believes what they believe, with the intent on persuading them that they are not justified in believing their claim. Epistemologically you are neither committed to evidentialism/internalism nor externalism.",
    model="gpt-4-turbo-preview",
    )
    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=prompt,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
        )
    
    
    run = wait_on_run(run, thread)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    msg = messages.data[0].content[0].text.value
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)