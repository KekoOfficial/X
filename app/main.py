import os
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # CONFIGURACIÓN DE PODER: Permite subir videos de hasta 100GB (Ajustable)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 1024 
    
    # Registrar las rutas simplificadas
    from app.routes import bp
    app.register_blueprint(bp)
    
    # Asegurar que las carpetas existan al arrancar
    os.makedirs('media/raw', exist_ok=True)
    os.makedirs('media/exports', exist_ok=True)
    
    return app
