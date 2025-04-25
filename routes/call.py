from flask import Blueprint
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import *

call_bp = Blueprint('call_bp', __name__)

@call_bp.route('/getCallIdData', methods=['GET'])
def get_call_id_data():
    call_id = request.args.get('callid')
    data = get_data_by_query('pitch_data', {'callID': int(call_id)})
    return jsonify({"data": data, "isSuccess": True})

@call_bp.route('/analysescripts', methods=['GET'])
def analysescripts():
    calls_data = get_calls_data()
    read_transcripts = []
    agents = []
    
    for call in calls_data:
        agent = call["agentID"]
        callID = call["callID"]
        agents.append(agent)
        transcript_agent = get_call_transcript(callID)

        if transcript_agent:
            review = call_gpt_api(transcript_agent)
            pitch_score = get_score_from_review(review)
            save_pitch_data(transcript_agent, review, pitch_score, callID)
            send_email_agent(subject, review, sender, recipients, password)
            score = int(pitch_score.split('/')[0])
            update_agent_data(agent, score)
            update_call_analysis_status(call)
            read_transcripts.append({
                f"{agent}": transcript_agent,
                "review": review,
                "score": pitch_score,
                "sentAt": datetime.now().isoformat()
            })

    return jsonify({"agents": agents, "data": read_transcripts, "isSuccess": True}), 200


@call_bp.route('/analysescriptbycallid', methods=['GET'])
def analysescriptbycallid():
    callID = request.args.get('callid')
    query = {"callID": int(callID)}

    calls = get_data_by_query("call_history",query)
    call = calls[0]

    agent = call["agentID"]
    callID = call["callID"]

    transcript_agent = get_call_transcript(callID)

    if transcript_agent:
        review = call_gpt_api(transcript_agent)
        pitch_score = get_score_from_review(review)
        save_pitch_data(transcript_agent, review, pitch_score, callID)
        send_email_agent(subject, review, sender, recipients, password)
        score = int(pitch_score.split('/')[0])
        update_agent_data(agent, score)
        update_call_analysis_status(call)

    return jsonify({"agents": "", "data":"" , "isSuccess": True}), 200

