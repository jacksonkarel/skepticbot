import time
from openai import OpenAI

def wait_on_run(run, thread, client):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

# Function to handle Skepticbot logic
def handle_llm(prompt, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
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
    run = wait_on_run(run, thread, client)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    msg = messages.data[0].content[0].text.value
    return msg