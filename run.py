from app import create_app
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
