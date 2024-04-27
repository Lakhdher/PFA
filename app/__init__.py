from flask import Flask
from flask_socketio import SocketIO
from app.models import gemini

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


def init_routes():
    from app import routes
