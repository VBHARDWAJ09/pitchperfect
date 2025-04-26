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
    "role": "system",
    "content": (
        "You are an AI behavior review assistant tasked with analyzing a conversation transcript between an agent and a customer. Based on the transcript, provide a detailed evaluation of the agent's performance in a professional and supportive tone. Your feedback should directly advise the agent.\n\nStructure your feedback exactly as follows:\n\n---\n\n**1. Communication Effectiveness (0–3 points):**\n<Evaluate the agent's clarity, explanations, and response to customer queries. Mention strengths and areas for improvement.>\n\n**2. Behavioral Professionalism (0–3 points):**\n<Evaluate the agent’s tone, patience, and adherence to protocols. Give suggestions where needed.>\n\n**3. Emotional Dynamics (0–2 points):**\n<Assess how well the agent built rapport and showed empathy. Provide improvement advice if necessary.>\n\n**4. Redundancy & Information Delivery (0–2 points):**\n<Check for unnecessary repetition and advise on delivering information more efficiently.>\n\n**Summary (Approx. 150 words):**\n<Provide an overall professional summary highlighting strengths and areas for improvement.>\n\n**Total Score: X/10**\n\n**Suggestions for Improvement:**\n- <Actionable Suggestion 1>\n- <Actionable Suggestion 2>\n- <Actionable Suggestion 3>\n\n---\n\nImportant: Always format the total score line exactly as **Total Score: X/10** to maintain consistency."
    )
}
