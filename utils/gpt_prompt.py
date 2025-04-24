def build_system_prompt():
    return {
        "role": "system",
        "content": "You are an AI auditor that analyzes sales agent calls to detect repetition, interruptions, and pitch issues..."
    }

def build_user_prompt(transcripts):
    return {
        "role": "user",
        "content": f"Analyze the following call transcripts and generate a feedback report:\n\n{transcripts}"
    }