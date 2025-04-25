from datetime import datetime, time
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import AzureOpenAI
import pandas as pd
import pytz
from dotenv import load_dotenv
from utils.gpt_prompt import build_system_prompt, build_user_prompt
from utils.database import *
from utils.email import *
from routes.agent import agent_bp
from routes.call import call_bp


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.register_blueprint(agent_bp)
app.register_blueprint(call_bp)


#routes
@app.route('/', methods=['GET'])
def server_running():
    data = get_data_by_query('users', {'age': {'$eq': 25}})
    return jsonify({"message": "Welcome", "isSuccess": True, "Data": data})

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided", "isSuccess": False}), 400

    save_user_data = save_data('agents', data)
    response = {
        "message": "Data Updated",
        "timestamp": datetime.now().isoformat(),
        "isSuccess": False,
    }
    if save_user_data:
        response['isSuccess'] = True
        response['res'] = str(save_user_data)
    return jsonify(response), 200



# Main execution
if __name__ == '__main__':
    databaseRes = connectDB()
    if databaseRes['connected']:
        print({"connected": databaseRes['connected']})
        set_db_connection(databaseRes['database'])
    else:
        print({"connected": "not"})
    app.run(debug=True)