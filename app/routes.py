import asyncio

from flask import request  # Import session

from app import app, socketio
from app.RAG.generation.q_a import get_response, get_stream_response


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
                loop.run_until_complete(get_stream_response(question, session_id=1))
            finally:
                loop.close()

    socketio.start_background_task(listen_for_question)


@app.route('/full_qa', methods=['POST'])
def full_qa():
    question = request.json['question']
    print('Question received:', question)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response, docs = loop.run_until_complete(get_response(question, session_id=1))
    finally:
        loop.close()
    return {'answer': response['answer'].content, 'metadata': response['answer'].response_metadata, 'docs': docs}


@app.route('/')
def hello_world():
    return "<h1>Hello, World!</h1>"  # Return a simple HTML string
