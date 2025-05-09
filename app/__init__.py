from flask import Flask
from flask_cors import CORS  # ✅ Add this line

def create_app():
    app = Flask(__name__)
    CORS(app)  # ✅ Enable CORS for all domains

    from .api import api_bp
    app.register_blueprint(api_bp)
    
    return app
