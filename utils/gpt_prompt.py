def build_system_prompt():
    return {
        "role": "system",
        "content": "Based on the provided conversation transcript, conduct a detailed evaluation of your performance in the interaction. Your feedback will be structured into the following categories:\n\n1. Communication Effectiveness (0–3 points):\n   Reflect on how clearly you greeted the customer, how effectively you explained complex concepts, and whether your language was appropriate and easy to understand. Consider your responsiveness to the customer's questions and your ability to adjust communication as needed.\n\n2. Behavioral Professionalism (0–3 points):\n   Assess your tone throughout the conversation. Did you remain patient and professional during customer queries? Were you consistent and aligned with service protocols?\n\n3. Emotional Dynamics (0–2 points):\n   Evaluate how well you built rapport with the customer and whether you demonstrated empathy and emotional awareness during the interaction.\n\n4. Redundancy & Information Delivery (0–2 points):\n   Identify if you repeated any information unnecessarily. Consider whether the repetition helped reinforce understanding or contributed to confusion or frustration.\n\nThen, provide:\n- A 150-word summary that outlines your strengths and areas for improvement. This should highlight your communication clarity, professionalism, emotional engagement, and delivery style.\n- A total score out of 10, broken down by each category. End with specific suggestions on how you can improve future interactions.\n\nUse a formal, professional tone throughout the feedback. use english words in layman and make it easy to understand"
    }

def build_user_prompt(transcripts):
    return {
        "role": "user",
        "content": f"Analyze the following call transcripts and generate a feedback report:\n\n{transcripts}"
    }

def build_previous_context_prompt(previous_feedbacks):
    return {
        "role": "user",
        "content": f"Here are some previous transcripts and their feedback:\n\n{previous_feedbacks}"
    }