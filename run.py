import os
import sys

from app import app, init_routes
from app import socketio
from flask_cors import CORS
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
init_routes()
cors=CORS(app, resources={r"/*": {"origins": "*"}})


if __name__ == "__main__":
    socketio.run(app, debug=True,  allow_unsafe_werkzeug=True,host= '0.0.0.0', port=5000)
