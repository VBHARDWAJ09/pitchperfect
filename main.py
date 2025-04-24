from flask import Flask, jsonify, request
from datetime import datetime
from openai import AzureOpenAI
import pandas as pd
import os
import json
from dotenv import load_dotenv
# from utils.faiss import build_faiss_index, search_faiss_index
from utils.gpt_prompt import build_system_prompt, build_user_prompt

load_dotenv()

open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_api_endpoints = os.getenv("OPEN_AI_API_ENDPOINT")
deployment = os.getenv("DEPLOYMENT")

client = AzureOpenAI(api_key=open_ai_key,api_version="2024-10-21",azure_endpoint=open_ai_api_endpoints)


# def generate_embeddings(text):
#     # response = openai.Embedding.create(
#     #     model="text-embedding-3-small",
#     #     input=text
#     # )
#     return "response['data'][0]['embedding']"

# def call_gpt_api(json_output):
#     system_prompt = build_system_prompt()
#     user_prompt = build_user_prompt(json_output)
#     messages = [system_prompt, user_prompt]

#     completion = client.chat.completions.create( model=deployment, messages=messages,temperature=0.3,max_tokens=100 )
    
#     content = completion.choices[0].message.content
#     return content

    

app = Flask(__name__)


@app.route('/', methods=['GET'])
def server_running():
    return jsonify({"message": "Welcome","isSuccess":True}), 200

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
    app.run(debug=True)