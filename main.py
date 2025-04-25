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

load_dotenv()
app = Flask(__name__)
CORS(app)

open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_api_endpoints = os.getenv("OPEN_AI_API_ENDPOINT")
deployment = os.getenv("DEPLOYMENT")
client = AzureOpenAI(api_key=open_ai_key,api_version="2024-10-21",azure_endpoint=open_ai_api_endpoints)

subject = "Feedback Report on Your Recent Customer Interaction"
sender = "sagar24263@gmail.com"
recipients = ["chirag3390garg@gmail.com"]
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
    


app = Flask(__name__)

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
    agent_ids_str = os.getenv("AGENT_IDS")

    read_transcripts =[]

    agents = ast.literal_eval(agent_ids_str)
    
    for agent in agents:
        transcript_agent = get_agent_transcript(agent)
        review = call_gpt_api(transcript_agent)
        pitch_score = get_score_from_review(review)
        data = {"pitch" : f"{transcript_agent}","review" : f"{review}",
                "score" : pitch_score,
            "sentAt": datetime.now().isoformat()}
        save_data("pitch_data",data)
        send_email_agent(subject, review, sender, recipients, password)
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