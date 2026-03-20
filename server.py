import os
import subprocess
from yt_dlp import YoutubeDL
from tqdm import tqdm

# Carpeta base para vídeos
BASE_FOLDER = "/storage/emulated/0/Download/VideosServer"
CORTADOS_FOLDER = os.path.join(BASE_FOLDER, "Cortados")
HISTORIAL_FILE = os.path.join(CORTADOS_FOLDER, "historial_cortes.txt")

os.makedirs(CORTADOS_FOLDER, exist_ok=True)

def limpiar_historial():
    if os.path.exists(HISTORIAL_FILE):
        os.remove(HISTORIAL_FILE)
        print("✅ Historial borrado.")

def limpiar_carpeta():
    for f in os.listdir(CORTADOS_FOLDER):
        file_path = os.path.join(CORTADOS_FOLDER, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("✅ Carpeta de cortes limpia.")

def descargar_video(url, carpeta):
    ydl_opts = {
        "outtmpl": os.path.join(carpeta, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "progress_hooks": [progreso_descarga],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename, info

def progreso_descarga(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            pct = downloaded / total * 100
            print(f"\r📥 Descargando... {pct:.2f}% ", end='')

def cortar_video(video_path, duracion_capitulo):
    import math
    import re

    # Obtener duración del vídeo en segundos
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    duracion_total = float(result.stdout.strip())
    num_capitulos = math.ceil(duracion_total / duracion_capitulo)

    print(f"\n🎬 Duración total: {duracion_total:.2f}s, Capítulos: {num_capitulos}")

    base_name = os.path.splitext(os.path.basename(video_path))[0]

    for i in range(num_capitulos):
        start = i * duracion_capitulo
        end = min((i + 1) * duracion_capitulo, duracion_total)
        cap_name = f"{base_name}_cap{i+1}.mp4"
        cap_path = os.path.join(CORTADOS_FOLDER, cap_name)

        cmd_ffmpeg = [
            "ffmpeg", "-y", "-i", video_path,
            "-ss", str(start), "-to", str(end),
            "-c", "copy", cap_path
        ]
        subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Capítulo {i+1} guardado: {cap_name}")

        with open(HISTORIAL_FILE, "a") as f:
            f.write(f"{video_path} -> {cap_name}\n")

def main():
    print("🚀 Cortador de vídeos Khasam")
    while True:
        print("\nOpciones:")
        print("1️⃣ Descargar y cortar vídeo")
        print("2️⃣ Limpiar carpeta de cortes")
        print("3️⃣ Borrar historial")
        print("4️⃣ Salir")

        opcion = input("Selecciona opción: ")

        if opcion == "1":
            url = input("🔗 Ingresa la URL del vídeo: ")
            duracion_cap = input("⏱ Duración de capítulo en segundos (15/30/60): ")
            try:
                duracion_cap = int(duracion_cap)
                video_file, info = descargar_video(url, BASE_FOLDER)
                print(f"\n✅ Vídeo descargado: {video_file}")
                cortar_video(video_file, duracion_cap)
            except Exception as e:
                print(f"❌ Error: {e}")

        elif opcion == "2":
            limpiar_carpeta()

        elif opcion == "3":
            limpiar_historial()

        elif opcion == "4":
            print("👋 Saliendo...")
            break

        else:
            print("⚠️ Opción inválida.")

if __name__ == "__main__":
    main()