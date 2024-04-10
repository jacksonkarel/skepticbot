def handle_rule_based(prompt, assistant, assistant_id, session_id):
    # Sending a message
    message_response = assistant.message(
        assistant_id=assistant_id,
        session_id=session_id,
        input={
            'message_type': 'text',
            'text': prompt
        }
    ).get_result()

    message_text = message_response['output']['generic'][0]['text']
    
    if message_text == "{}" and len(message_response['output']['generic']) > 1:
        message_text = message_response['output']['generic'][1]['text']
       
    return message_text, assistant, message_response
