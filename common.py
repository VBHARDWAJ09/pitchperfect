from datetime import datetime, time
import json
import os
import re

# Third-party imports
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import AzureOpenAI
import pandas as pd
import pytz
from dotenv import load_dotenv

# Local imports
from utils.gpt_prompt import build_system_prompt, build_user_prompt, build_previous_context_prompt
from utils.database import *
from utils.email import *


load_dotenv()

# Azure OpenAI Configuration
open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_api_endpoints = os.getenv("OPEN_AI_API_ENDPOINT")
deployment = os.getenv("DEPLOYMENT")
client = AzureOpenAI(
    api_key=open_ai_key,
    api_version="2024-10-21",
    azure_endpoint=open_ai_api_endpoints
)

# Email Configuration
subject = "Feedback Report on Your Recent Customer Interaction"
sender = "sagar24263@gmail.com"
recipients = ["sagar242083@gmail.com"]
password = os.getenv("EMAIL_PASSWORD")


# Database Functions
def get_agent_data(agentId):
    query = {"agentID": agentId}
    agentsData = get_data_by_query("agents", query)
    return agentsData[0] if agentsData else None

def update_agent_data(agentId, score):
    agentData = get_agent_data(agentId)
    previousScore = agentData['averageScore']
    callsAnalyzed = agentData['analyzedCalls']
    newScore = (previousScore * callsAnalyzed + score) / (callsAnalyzed + 1)
    agentData['analyzedCalls'] = agentData['analyzedCalls'] + 1
    agentData['averageScore'] = newScore
    objId = agentData['_id']
    replace_data_by_id("agents", objId, agentData)
    return agentData

def get_calls_data():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    start_of_today = datetime.combine(now.date(), time.min).astimezone(ist)
    start_of_today_str = start_of_today.isoformat()
    # query = {"time": {"$gte": start_of_today_str}}
    query = {}
    return get_data_by_query("call_history", query)

# Transcript Processing Functions
def get_agent_transcript(agentId):
    transcripts_df = pd.read_csv(f"data/{agentId}.csv")
    transcripts_df.columns = transcripts_df.columns.str.strip()
    transcripts_df['speaker'] = transcripts_df['speaker'].astype(str)
    transcripts_df['time'] = transcripts_df['time'].astype(str)
    transcripts_df['text'] = transcripts_df['text'].astype(str)
    formatted_data = transcripts_df.to_dict(orient='records')
    return json.dumps(formatted_data, indent=2).replace("\n", "\\r\\n")

def get_call_transcript(callID):
    try:
        transcripts_df = pd.read_csv(f"data/{callID}.csv")
        transcripts_df.columns = transcripts_df.columns.str.strip()
        transcripts_df['speaker'] = transcripts_df['speaker'].astype(str)
        transcripts_df['time'] = transcripts_df['time'].astype(str)
        transcripts_df['text'] = transcripts_df['text'].astype(str)
        formatted_data = transcripts_df.to_dict(orient='records')
        return json.dumps(formatted_data, indent=2).replace("\n", "\\r\\n")
    except FileNotFoundError:
        return None

# GPT and Analysis Functions
def call_gpt_api(json_output):
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(json_output)
    messages = [system_prompt, user_prompt]
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )
    return completion.choices[0].message.content
    
def call_gpt_api_with_context(json_output,context):
    system_prompt = build_system_prompt()
    context_prompt = build_previous_context_prompt(context)
    user_prompt = build_user_prompt(json_output)
    messages = [system_prompt, context_prompt,user_prompt]
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )
    return completion.choices[0].message.content

def get_score_from_review(review):
    match = re.search(r"Total Score:\s*(\d+/\d+)", review)
    return match.group(1) if match else 0

def save_pitch_data(transcript_agent, review, pitch_score, callID,agentID):
    data = {
        "pitch": f"{transcript_agent}",
        "review": f"{review}",
        "agentId": agentID,
        "score": pitch_score,
        "callID": callID,
        "sentAt": datetime.now().isoformat()
    }
    save_data("pitch_data", data)

def update_call_analysis_status(call):
    call['isAnalysed'] = True
    objId = call['_id']
    replace_data_by_id("call_history", objId, call)