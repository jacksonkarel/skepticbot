import os
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

def create_watson_session():
    load_dotenv()
        
    watson_api_key = os.getenv("WATSON_API_KEY")
    watson_url = os.getenv("WATSON_URL")

    # Replace 'api_key' and 'url' with your API key and URL from IBM Watson Assistant service
    authenticator = IAMAuthenticator(watson_api_key)
    assistant = AssistantV2(
        version='2023-04-06',  # use the current date for the most recent API version
        authenticator=authenticator
    )
    assistant.set_service_url(watson_url)

    assistant_id = os.getenv("ASSISTANT_ID")

    # Creating a new session
    session_response = assistant.create_session(
        assistant_id=assistant_id
    ).get_result()
    session_id = session_response['session_id']

    return assistant, assistant_id, session_id