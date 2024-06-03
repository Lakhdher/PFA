import asyncio

from flask import request ,abort

from app import app, socketio
from app.RAG.generation.q_a import get_response, get_stream_response
from app.config.mongoConfig import  get_db, get_collection_name

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    def listen_for_question():
        @socketio.on('question')
        def handle_question(data):
            question = data.get('question')
            conversation_id = data.get('conversation_id')
            user_id = data.get('user_id')
            print('Question received:', data)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                 loop.run_until_complete(get_stream_response(question,user_id =user_id,conversation_id=conversation_id))
            finally:
                loop.close()
                print('Question processed')

    socketio.start_background_task(listen_for_question)
    

@app.route('/full_qa', methods=['POST'])
def full_qa():
    question = request.json['question']
    print('Question received:', question)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response, docs = loop.run_until_complete(get_response(question, user_id=1,conversation_id=1))
    finally:
        loop.close()
    return {'answer': response['answer'].content, 'metadata': response['answer'].response_metadata, 'docs': docs}


@app.route('/get_history', methods=['GET'])
def get_history():
    conversation_id = request.args.get('conversation_id')
    user_id = request.args.get('user_id')
    db = get_db()
    collection = db[get_collection_name()]
    query = {'SessionId':  [user_id,conversation_id]}
    documents = collection.find(query)
    return [doc['History'] for doc in documents]

@app.route('/get_user_history', methods=['GET'])
def get_user_history():
    user_id = request.args.get('user_id')
    db = get_db()
    collection = db[get_collection_name()]
    pipeline = [
        {"$match": {"$expr": {"$eq": [{"$arrayElemAt": ["$SessionId", 0]}, user_id]}}},
        {"$group": {"_id": {"$arrayElemAt": ["$SessionId", 1]}, "history": {"$push": "$History"}}}
    ]
    documents = collection.aggregate(pipeline)
    return [{"conversation_id": doc["_id"], "history": doc["history"]} for doc in documents]

@app.route('/delete_history', methods=['DELETE'])
def delete_history():
    auth_token = request.headers.get('authorization')
    if not auth_token:
        abort(403)  # Forbidden

    data = request.get_json()
    conversation_id = data['conversation_id']
    user_id = data['user_id']

    # Check if the user_id associated with the auth_token matches the user_id in the request
    if not user_id == auth_token:
        abort(403)  # Forbidden

    db = get_db()
    collection = db[get_collection_name()]
    query = {'SessionId':  [user_id, conversation_id]}
    collection.delete_many(query)
    return {'message': 'History with id deleted'}