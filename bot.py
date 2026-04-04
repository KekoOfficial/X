import subprocess
import requests
import os
import time
from config import get_nexus_settings, DOWNLOAD_FOLDER

def start_mally_engine(path, filename, s_queue):
    """
    Motor Mally v14.1 - Khassamx Dev
    Procesa, corta y envía con monitoreo y branding imperial.
    """
    # 1. Cargar Configuración de la Base de Datos
    settings = get_nexus_settings()
    token = settings.get("bot_token")
    cid = settings.get("chat_id")
    
    if not token or not cid:
        s_queue.put("❌ ERROR: Configura los Tokens en /settings")
        return

    # Limpiar nombre de archivo para el título
    base_name = os.path.splitext(filename)[0].replace("_", " ").upper()
    out_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base_name}_%03d.mp4")

    # 2. Notificar Inicio a la Web y Telegram
    s_queue.put(f"🎬 Analizando: {base_name}")
    
    # Mensaje Maestro que se editará (Control de Consola)
    master_msg = (
        f"⏳ **MALLY MONITOR v14.1**\n"
        f"────────────────────\n"
        f"🛰️ **Estado:** Fragmentando Video...\n"
        f"🎥 **Serie:** {base_name}\n"
        f"👑 **Admin:** Khassamx Dev"
    )
    
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage", 
            data={'chat_id': cid, 'text': master_msg, 'parse_mode': 'Markdown'}
        )
        msg_id = res.json()['result']['message_id']
    except Exception as e:
        s_queue.put(f"❌ Error Telegram: {e}")
        return

    # 3. Proceso de Corte Flash (FFmpeg)
    s_queue.put("⚡ Fragmentando en partes de 1 min...")
    subprocess.run([
        "ffmpeg", "-y", "-i", path, 
        "-c", "copy", "-map", "0", 
        "-f", "segment", "-segment_time", "60", 
        "-reset_timestamps", "1", 
        out_pattern
    ], capture_output=True)

    # Listar y ordenar las partes creadas
    parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base_name)])
    total = len(parts)

    # 4. Envío con Diseño Imperial de Redes Sociales
    for i, p in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOAD_FOLDER, p)
        s_queue.put(f"📤 Enviando Parte {i} de {total}...")

        # Actualizar Mensaje Maestro en Telegram
        edit_text = (
            f"⚡ **MALLY MONITOR v14.1**\n"
            f"────────────────────\n"
            f"📤 **Enviando:** {base_name}\n"
            f"📦 **Progreso:** Parte {i} de {total}\n"
            f"🔥 @MallySeries"
        )
        requests.post(
            f"https://api.telegram.org/bot{token}/editMessageText", 
            data={'chat_id': cid, 'message_id': msg_id, 'text': edit_text, 'parse_mode': 'Markdown'}
        )

        # DISEÑO DE LEYENDA (CAPTION) PARA CADA PARTE
        caption_text = (
            f"🎬 **PELÍCULA:** {base_name}\n"
            f"📦 **PARTE:** {i} de {total}\n"
            f"⏳ **DURACIÓN:** 01:00 min\n"
            f"👤 **CREADOR:** Khassamx Dev\n"
            f"────────────────────\n"
            f"📸 **Instagram:** @MallySeries\n"
            f"🎵 **TikTok:** @Esenaen15\n"
            f"📢 **Telegram:** @MallySeries\n"
            f"────────────────────\n"
            f"👑 **IMPERIO MALLY v14.1**"
        )

        # Enviar Video con la nueva leyenda
        with open(p_path, 'rb') as video_file:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendVideo", 
                data={
                    'chat_id': cid, 
                    'caption': caption_text, 
                    'parse_mode': 'Markdown',
                    'supports_streaming': True
                }, 
                files={'video': video_file}
            )
        
        # Limpieza inmediata para ahorrar espacio
        os.remove(p_path)
        time.sleep(1) # Pausa de seguridad anti-flood

    # 5. Finalización
    s_queue.put("✅ PROCESO COMPLETADO")
    
    final_msg = (
        f"✅ **FRAGMENTACIÓN EXITOSA**\n"
        f"────────────────────\n"
        f"🎥 **Serie:** {base_name}\n"
        f"📦 **Total:** {total} partes enviadas\n"
        f"🌟 **Destino:** @MallySeries\n\n"
        f"👑 Sistema desarrollado por Khassamx Dev"
    )
    
    requests.post(
        f"https://api.telegram.org/bot{token}/editMessageText", 
        data={'chat_id': cid, 'message_id': msg_id, 'text': final_msg, 'parse_mode': 'Markdown'}
    )

    # Eliminar video maestro de uploads
    if os.path.exists(path):
        os.remove(path)
