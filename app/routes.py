import asyncio

from flask import render_template, request, abort  # Import necessary modules
from app import app
from app.RAG.generation.q_a import stream_response, get_response
from app.RAG.utils.utils import to_markdown, markdown_to_html


@app.route('/stream_qa', methods=['POST'])
def multiquery():
    question = request.json['question']
    token = request.json['token']


@app.route('/full_qa',methods=['POST'])
def full_qa():
    final_answer = []
    question = request.json['question']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        answer, metadata = loop.run_until_complete(get_response(question))
        final_answer = ' '.join(answer)
    finally:
        loop.close()
    return final_answer


@app.route('/')
def hello_world():
    return "<h1>Hello, World!</h1>"  # Return a simple HTML string
