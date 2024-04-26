from flask import Flask
from flask_socketio import SocketIO
from .config.mongoConfig import get_db


def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app)
    socketio.init_app(app)
    db = get_db()
    return app
