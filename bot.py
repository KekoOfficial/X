@app.route("/api/upload_pro", methods=["POST"])
def upload_pro():
    file = request.files.get("video")
    # Recibimos las preferencias del usuario desde la web
    sec = int(request.form.get("seconds", 60)) 
    silent = request.form.get("silent") == "true"

    if not file: return jsonify({"status": "error"}), 400

    f_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, f"{f_id}_{file.filename}")
    file.save(path)

    # Enviamos los ajustes al motor turbo
    executor.submit(synchronized_engine, path, file.filename, sec, silent)
    
    return jsonify({"status": "success"})

def synchronized_engine(input_path, filename, segment_time, silent_mode):
    """Motor Pro con ajustes dinámicos de tiempo y notificaciones."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        # Corte instantáneo con el tiempo elegido (60, 300 o 600)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", str(segment_time),
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)

        # Subida secuencial respetando el modo silencio
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            # Payload para Telegram con opción disable_notification
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                'chat_id': CHAT_ID,
                'caption': f"📦 PARTE {i}/{total}\n🎬 {filename}",
                'supports_streaming': True,
                'disable_notification': silent_mode # Si es True, no suena el móvil
            }, files={'video': open(p_path, 'rb')})
            
            os.remove(p_path)
            time.sleep(1.2) # Mantener el orden perfecto

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"✅ Finalizado con {segment_time}s por clip.")

    except Exception as e:
        log.error(f"🔥 Error: {e}")
