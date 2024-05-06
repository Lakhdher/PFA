import asyncio

from flask import request 

from app import app, socketio
from app.RAG.generation.q_a import get_response, get_stream_response
from app.config.mongoConfig import  get_db, get_collection_name

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    def listen_for_question():
        @socketio.on('question')
        def handle_question(question, session_id=1):
            print('Question received:', question)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                 loop.run_until_complete(get_stream_response(question,user_id = 1,conversation_id=1))
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
    query = {'SessionId':  [int(user_id),int(conversation_id)]}
    documents = collection.find(query)
    return [doc['History'] for doc in documents]