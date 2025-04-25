from flask import Blueprint
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import *

agent_bp = Blueprint('agent_bp', __name__)

@agent_bp.route('/getagentdata', methods=['GET'])
def getagentdata():
    agent_data = get_agent_data("PW52331")
    return jsonify({"data": agent_data, "isSuccess": True})

@agent_bp.route('/getagenttranscript', methods=['GET'])
def getagenttranscript():
    agentId = request.args.get('agentId')
    if not agentId:
        return jsonify({"data": None, "isSuccess": False, "message": "agentId is required"}), 400
    transcript = get_agent_transcript(agentId)
    return jsonify({"data": transcript, "isSuccess": True})

@agent_bp.route('/getallagentsPerformance', methods=['GET'])
def get_all_agents_data():
    data = get_data_by_query('agents', {})
    for agent in data:
        agent['calls'] = get_data_by_query('call_history', {'agentID': agent['agentID']})
    return jsonify({"data": data, "isSuccess": True})


@agent_bp.route('/sendemail', methods=['GET'])
def send_email():
    send_email_agent(subject, "body", sender, recipients, password)
    return jsonify({
        "message": "Email sent successfully",
        "timestamp": datetime.now().isoformat(),
        "isSuccess": True
    }), 200
