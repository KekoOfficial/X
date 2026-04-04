import os
from flask import Flask
from app.routes import bp

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = "mally_secret_v18"
    
    # Asegurar carpetas de media
    os.makedirs('media/raw', exist_ok=True)
    os.makedirs('media/exports', exist_ok=True)
    
    app.register_blueprint(bp)
    return app
