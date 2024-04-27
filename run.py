from flask_socketio import SocketIO

from app import app, init_routes
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

if __name__ == "__main__":
    init_routes()
    socketio = SocketIO(app)
    socketio.run(app, debug=True,  allow_unsafe_werkzeug=True)
