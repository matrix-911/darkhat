from flask import Flask
from flask_cors import CORS  # ✅ import CORS

def create_app():
    app = Flask(__name__)

    CORS(app)  # ✅ ENABLE CORS for external calls like from Wix

    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
