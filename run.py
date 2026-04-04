import os
from dotenv import load_dotenv
from app.main import create_app

# 1. CARGA DE MATRIZ (.env)
load_dotenv()

# 2. INICIALIZACIÓN DEL NODO V2000
app = create_app()

if __name__ == "__main__":
    # Extraemos configuración del .env o usamos valores por defecto
    port = int(os.getenv("FLASK_PORT", 8000))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    print("\n" + "="*40)
    print("🚀 SISTEMA MALLY CUTS V2000 ACTIVADO")
    print(f"📡 PUERTO: {port}")
    print(f"🔗 URL: http://127.0.0.1:{port}")
    print("="*40 + "\n")

    try:
        # Ejecución Nitro: 
        # threaded=True permite procesar múltiples peticiones a la vez
        # host='0.0.0.0' permite acceder desde otros dispositivos en la misma WiFi
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=debug_mode, 
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 V2000: Apagado de emergencia detectado. Cerrando hilos...")
    except Exception as e:
        print(f"\n❌ CRITICAL_ERROR en el arranque: {e}")
