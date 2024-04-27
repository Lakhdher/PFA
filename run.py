from flask_socketio import SocketIO
from app import app, init_routes, socketio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
init_routes()

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
