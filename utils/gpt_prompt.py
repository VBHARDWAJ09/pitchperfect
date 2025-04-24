def build_system_prompt():
    return {
        "role": "system",
        "content": "Analyze the conversation transcript to evaluate the agent's performance. Provide feedback on their communication skills, identify any behavioral issues such as lack of empathy or patience, assess the overall sentiment of the interaction, and note any instances of unnecessary repetitions. Your analysis should include a 150-word description that covers the agent's communication effectiveness, behavioral professionalism, emotional dynamics, and redundancy in information delivery. Provide data in points like 2 point for each problem and dont just include negatives includes positives also as you are an audit bot"
    }

def build_user_prompt(transcripts):
    return {
        "role": "user",
        "content": f"Analyze the following call transcripts and generate a feedback report:\n\n{transcripts}"
    }