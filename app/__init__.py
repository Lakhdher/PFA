from flask import Flask
from flask_socketio import SocketIO


def create_app():
    app = Flask(__name__)
    socketio.init_app(app)

    return app
