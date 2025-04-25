from flask import Flask, jsonify, request
from datetime import datetime
from openai import AzureOpenAI
import pandas as pd
import os
import json
from dotenv import load_dotenv
import ast
# from utils.faiss import build_faiss_index, search_faiss_index
from utils.gpt_prompt import build_system_prompt, build_user_prompt
from utils.database import *

load_dotenv()

open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_api_endpoints = os.getenv("OPEN_AI_API_ENDPOINT")
deployment = os.getenv("DEPLOYMENT")

# openai.api_type = "azure"
# openai.api_key = open_ai_key
# openai.api_base = open_ai_api_endpoints
# openai.api_version = "2023-05-15"

client = AzureOpenAI(api_key=open_ai_key,api_version="2024-10-21",azure_endpoint=open_ai_api_endpoints)



# def generate_embeddings(text):
#     # response = openai.Embedding.create(
#     #     model="text-embedding-3-small",
#     #     input=text
#     # )
#     return "response['data'][0]['embedding']"

def get_agent_transcript(agentId):
    #return agentId
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

# if __name__ == "__main__":
#     query_text = "Provide feedback for the agent's sales pitch throughout the day."
#     #res = call_gpt_api(json_output)
#     #print(get_agent_transcript("PW47633"))

app = Flask(__name__)

@app.route('/getagenttranscript', methods=['GET'])
def getagenttranscript():
    agentId = request.args.get('agentId')

    if not agentId:
        return jsonify({"data": None, "isSuccess": False, "message": "agentId is required"}), 400
    transcript = get_agent_transcript(agentId)
    return jsonify({"data": transcript,"isSuccess":True})


@app.route('/analysescripts', methods=['GET'])
def analysescripts():
    agent_ids_str = os.getenv("AGENT_IDS")

    read_transcripts =[]

    agents = ast.literal_eval(agent_ids_str)
    
    for agent in agents:
        transcript_agent = get_agent_transcript(agent)
        review = call_gpt_api(transcript_agent)
        read_transcripts.append({ f"{agent}": transcript_agent, "review" : review})

    return jsonify({"agents":agents,"data": read_transcripts, "isSuccess": False, "message": "agentId is required"}), 400

@app.route('/', methods=['GET'])
def server_running():
    return jsonify({"message": "Welcome","isSuccess":True})

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided", "isSuccess": False}), 400
    
    name = data.get('name')
    age = data.get('age')

    # Do something with the data (this is just an example)
    response = {
        "message": f"Received data for {name}, age {age}",
        "timestamp": datetime.now().isoformat(),
        "isSuccess": True
    }
    return jsonify(response), 200

if __name__ == '__main__':
    databaseRes = connectDB()
    if databaseRes['connected']:
        print({"connected":databaseRes['connected'],"database":databaseRes['database']})
    else:
        print({"connected":"not"})
    app.run(debug=True)