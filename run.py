import os
import sys
from app.main import create_app

# CONFIGURACIÓN DE ENTORNO IMPERIAL
app = create_app()

def setup_system():
    """
    Asegura que la estructura de carpetas optimizada esté intacta 
    antes de iniciar el motor V10.
    """
    directories = [
        'media/raw', 
        'media/exports', 
        'static/css', 
        'static/js',
        'templates',
        'logs'
    ]
    
    print("--- [ MALLY CUTS v18.5 | SYSTEM CHECK ] ---")
    for folder in directories:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"> CREATED: {folder}")
        else:
            print(f"> OK: {folder}")
    print("--- [ CHECK COMPLETADO | MOTOR LISTO ] ---\n")

if __name__ == '__main__':
    # 1. Preparar el terreno
    setup_system()
    
    # 2. Parámetros de red para acceso desde móvil o PC
    # Host '0.0.0.0' permite que entres desde tu IP local
    PORT = 8000
    
    print(f"🚀 MALLY CUTS v18 ONLINE")
    print(f"📡 ACCESO LOCAL: http://localhost:{PORT}")
    print(f"🔗 ACCESO RED: http://tu-ip-local:{PORT}")
    print("⚡ MODO: PARALLEL MULTI-CORE PROCESSING ACTIVE")
    
    try:
        # Ejecución del servidor Flask
        app.run(host='0.0.0.0', port=PORT, debug=True)
    except KeyboardInterrupt:
        print("\n[!] Motor detenido por el usuario. Cerrando protocolos...")
        sys.exit(0)
