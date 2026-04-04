from flask import Flask
from app.routes import main_bp
import os

app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

app.register_blueprint(main_bp)

if __name__ == '__main__':
    # Asegurar que las carpetas de media existan al arrancar
    os.makedirs('media/cuts', exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=True)
