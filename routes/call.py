from flask import Blueprint
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import *
from rag.embeddings import *
from rag.faiss_index import *


call_bp = Blueprint('call_bp', __name__)

@call_bp.route('/getCallIdData', methods=['GET'])   
def get_call_id_data():
    call_id = request.args.get('callid')
    data = get_data_by_query('pitch_data', {'callID': int(call_id)})
    return jsonify({"data": data, "isSuccess": True})

@call_bp.route('/analysescriptswithcontext', methods=['GET'])
def analysescriptswithcontext():
    calls_data = get_calls_data()
    read_transcripts = []
    agents = []
    
    for call in calls_data:
        agent = call["agentID"]
        callID = call["callID"]
        agent_data = get_data_by_query('agents',{"agentID":agent})
        if len(agent_data) > 0:
            email = agent_data[0]['emailID']

        #check if call is already analysed
        existing_call = get_data_by_query('pitch_data', {'callID': int(callID)})

        if existing_call:
            call_feedback = existing_call[0]
            read_transcripts.append({
                    f"{agent}": call_feedback['pitch'],
                    "review": call_feedback['review'],
                    "score": call_feedback['score'],
                    "sentAt": call_feedback['sentAt']
                })
            continue
        
        agents.append(agent)
        transcript_agent = get_call_transcript(callID)

        if transcript_agent:
            embedding = get_embedding(transcript_agent)
            similar_transcripts = search_similar(embedding, top_k=2)
            context = "\n\n".join(f"Transcript: {s['transcript']}\nFeedback: {s['pitch']}" for s in similar_transcripts)

            review = call_gpt_api_with_context(transcript_agent,context)
            pitch_score = get_score_from_review(review)
            save_pitch_data(transcript_agent, review, pitch_score, callID,agent)
            add_to_index(embedding, {"call_id": callID, "transcript": transcript_agent, "pitch": review})
            if email:
                send_email_agent(subject, review, sender, email, password)
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
        save_pitch_data(transcript_agent, review, pitch_score, callID,agent)
        send_email_agent(subject, review, sender, recipients, password)
        score = int(pitch_score.split('/')[0])
        update_agent_data(agent, score)
        update_call_analysis_status(call)

    return jsonify({"agents": "", "data":"" , "isSuccess": True}), 200


@call_bp.route('/analysescripts', methods=['GET'])
def analysescripts():
    calls_data = get_calls_data()
    read_transcripts = []
    agents = []
    
    for call in calls_data:
        agent = call["agentID"]
        callID = call["callID"]
        agent_data = get_data_by_query('agents',{"agentID":agent})
        if len(agent_data) > 0:
            email = agent_data[0]['emailID']

        #check if call is already analysed
        call = get_data_by_query('pitch_data', {'callID': int(callID)})

        if call:
            call_feedback = call[0]
            read_transcripts.append({
                    f"{agent}": call_feedback['pitch'],
                    "review": call_feedback['review'],
                    "score": call_feedback['score'],
                    "sentAt": call_feedback['sentAt']
                })
            continue
        
        agents.append(agent)
        transcript_agent = get_call_transcript(callID)

        if transcript_agent:
            review = call_gpt_api(transcript_agent)
            pitch_score = get_score_from_review(review)
            save_pitch_data(transcript_agent, review, pitch_score, callID,agent)
            if email:
                send_email_agent(subject, review, sender, email, password)
            score = int(pitch_score.split('/')[0])
            update_agent_data(agent, score)
            if call:
                update_call_analysis_status(call)
            read_transcripts.append({
                f"{agent}": transcript_agent,
                "review": review,
                "score": pitch_score,
                "sentAt": datetime.now().isoformat()
            })

    return jsonify({"agents": agents, "data": read_transcripts, "isSuccess": True}), 200
