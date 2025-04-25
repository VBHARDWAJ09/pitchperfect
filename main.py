from flask import Flask, jsonify, request
from datetime import datetime
from openai import AzureOpenAI
import pandas as pd
import os
import json
from flask_cors import CORS
from dotenv import load_dotenv
import ast
# from utils.faiss import build_faiss_index, search_faiss_index
from utils.gpt_prompt import build_system_prompt, build_user_prompt
from utils.database import *
from utils.email import *
import re
import pytz
from datetime import datetime, time

load_dotenv()
app = Flask(__name__)
CORS(app)

open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_api_endpoints = os.getenv("OPEN_AI_API_ENDPOINT")
deployment = os.getenv("DEPLOYMENT")
client = AzureOpenAI(api_key=open_ai_key,api_version="2024-10-21",azure_endpoint=open_ai_api_endpoints)

subject = "Feedback Report on Your Recent Customer Interaction"
sender = "sagar24263@gmail.com"
recipients = ["sagar242083@gmail.com"]
password = os.getenv("EMAIL_PASSWORD")


# def generate_embeddings(text):
#     # response = openai.Embedding.create(
#     #     model="text-embedding-3-small",
#     #     input=text
#     # )
#     return "response['data'][0]['embedding']"

def get_agent_transcript(agentId):
    transcripts_df = pd.read_csv(f"data/{agentId}.csv")
    transcripts_df.columns = transcripts_df.columns.str.strip()

    transcripts_df['speaker'] = transcripts_df['speaker'].astype(str)
    transcripts_df['time'] = transcripts_df['time'].astype(str)
    transcripts_df['text'] = transcripts_df['text'].astype(str)

    formatted_data = transcripts_df.to_dict(orient='records')

    json_output = json.dumps(formatted_data, indent=2).replace("\n", "\\r\\n")

    return json_output

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


def call_gpt_api(json_output):
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(json_output)
    messages = [system_prompt, user_prompt]

    completion = client.chat.completions.create( model=deployment, messages=messages,temperature=0.3,max_tokens=500 )
    
    content = completion.choices[0].message.content
    return content

def get_score_from_review(review):
    match = re.search(r"Total Score:\s*(\d+/\d+)", review)
    score = 0
    if match:
        score = match.group(1)
    return score
    
def get_agent_data(agentId):
    query = {"agentID":agentId}
    agentsData = get_data_by_query("agents",query)
    return agentsData[0] if agentsData else None

def update_agent_data(agentId,score):
    agentData = get_agent_data(agentId)
    previousScore = agentData['averageScore']
    callsAnalyzed = agentData['analyzedCalls']
    newScore = (previousScore*callsAnalyzed + score)/(callsAnalyzed+1)
    agentData['analyzedCalls'] =agentData['analyzedCalls']+1  
    agentData['averageScore'] = newScore
    objId = agentData['_id']
    replace_data_by_id("agents",objId,agentData)
    return agentData

def get_calls_data():

    # Get current date in IST
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # Get start of the day (00:00:00) in IST
    start_of_today = datetime.combine(now.date(), time.min).astimezone(ist)
    start_of_today_str = start_of_today.isoformat()
    query = {
        "time": {
        "$gte": start_of_today_str
    }}

    calls_data = get_data_by_query("call_history",query)
    return calls_data

def save_pitch_data(transcript_agent,review,pitch_score,callID):
    data = {"pitch" : f"{transcript_agent}","review" : f"{review}",
                "agentId" : review,
                "score" : pitch_score,
                "callID" : callID,
            "sentAt": datetime.now().isoformat()}
    save_data("pitch_data",data)

def update_call_analysis_status(call):
    call['isAnalysed'] = True
    objId = call['_id']
    replace_data_by_id("call_history",objId,call)

app = Flask(__name__)

@app.route('/getagentdata', methods=['GET'])
def getagentdata():
    agent_data = update_agent_data("PW52331",10)
    return jsonify({"data": agent_data,"isSuccess":True})

@app.route('/getagenttranscript', methods=['GET'])
def getagenttranscript():
    agentId = request.args.get('agentId')

    if not agentId:
        return jsonify({"data": None, "isSuccess": False, "message": "agentId is required"}), 400
    transcript = get_agent_transcript(agentId)
    return jsonify({"data": transcript,"isSuccess":True})

@app.route('/getallagentsPerformance', methods=['GET'])
def get_all_agents_data():
    data = get_data_by_query('agents',{})
    return jsonify({"data": data,"isSuccess":True})

@app.route('/analysescripts', methods=['GET'])
def analysescripts():
    calls_data = get_calls_data()
    read_transcripts =[]

    #agents = ast.literal_eval(agent_ids_str)
    
    for call in calls_data:
        agent = call["agentID"]
        callID = call["callID"]

        transcript_agent = get_call_transcript(callID)

        # if transcript_agent in None:
        #     continue

        review = call_gpt_api(transcript_agent)
        pitch_score = get_score_from_review(review)
        save_pitch_data(transcript_agent,review,pitch_score,callID)
        send_email_agent(subject, review, sender, recipients, password)
        score = int(pitch_score.split('/')[0])  
        update_agent_data(agent,score)
        update_call_analysis_status(call)
        read_transcripts.append({
            f"{agent}": transcript_agent,
            "review": review,
            "score" : pitch_score,
            "sentAt": datetime.now().isoformat()
        })

    return jsonify({"agents":agents,"data": read_transcripts, "isSuccess": True}), 200

@app.route('/', methods=['GET'])
def server_running():
    data = get_data_by_query('users',{'age': {'$eq': 25}})
    # data = get_data_by_id('users','680b62b98f3a484cf1bdc0e7')
    return jsonify({"message": "Welcome","isSuccess":True,"Data": data})

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided", "isSuccess": False}), 400


    # Do something with the data (this is just an example)
    save_user_data = save_data('agents',data)
    response = {
            "message": "Data Updated",
            "timestamp": datetime.now().isoformat(),
            "isSuccess": False,
        }
    if save_user_data:
        response['isSuccess'] = True
        response['res'] = str(save_user_data)
    return jsonify(response), 200

@app.route('/sendemail', methods=['GET'])
def send_email():
    send_email_agent(subject, body, sender, recipients, password)
    response = {
        "message": f"Email sent successfully",
        "timestamp": datetime.now().isoformat(),
        "isSuccess": True
    }
    return jsonify(response), 200

if __name__ == '__main__':
    databaseRes = connectDB()
    if databaseRes['connected']:
        print({"connected":databaseRes['connected']})
        set_db_connection(databaseRes['database'])
        
    else:
        print({"connected":"not"})
    app.run(debug=True)