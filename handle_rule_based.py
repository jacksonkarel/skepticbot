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

    return message_response
