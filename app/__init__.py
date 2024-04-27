from flask import Flask
from flask_socketio import SocketIO
from app.models import gemini

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app)

def init_routes():
    from app import routes
