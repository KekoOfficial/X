from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os, subprocess, datetime

app = Flask(__name__)
UPLOAD_FOLDER = "VideosServer"
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, "Cortados")
HISTORIAL_FILE = os.path.join(OUTPUT_FOLDER, "historial_cortes.txt")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Función para leer historial
def leer_historial():
    historial = []
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE,"r") as f:
            for line in f.readlines():
                parts = line.strip().split("|")
                if len(parts)==4:
                    historial.append({
                        "video": parts[0],
                        "duracion": parts[1],
                        "clips": parts[2],
                        "fecha": parts[3]
                    })
    return historial

@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST":
        files = request.files.getlist("files")
        folder_name = request.form.get("folder_name","Videos")
        cap_duration = int(request.form.get("cap_duration",15))
        auto_caps = int(request.form.get("auto_caps",0))

        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for f in files:
            if f.filename.endswith(".mp4"):
                filepath = os.path.join(folder_path,f.filename)
                f.save(filepath)

                # Obtener duración total con ffmpeg
                result = subprocess.run(["ffprobe","-v","error","-show_entries",
                                         "format=duration","-of",
                                         "default=noprint_wrappers=1:nokey=1", filepath],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                total_duration = float(result.stdout)
                # Calcular capítulos automáticos
                if auto_caps>0:
                    cap_duration = max(1, total_duration/auto_caps)

                # Cortar video por capítulos
                count=0
                start=0
                while start<total_duration:
                    end=min(start+cap_duration,total_duration)
                    count+=1
                    outname=f"{os.path.splitext(f.filename)[0]}_cap{count}.mp4"
                    outpath=os.path.join(OUTPUT_FOLDER,outname)
                    subprocess.run(["ffmpeg","-y","-i",filepath,"-ss",str(start),"-to",str(end),"-c","copy",outpath])
                    start=end

                # Guardar historial
                with open(HISTORIAL_FILE,"a") as hist:
                    fecha=str(datetime.datetime.now())
                    hist.write(f"{f.filename}|{int(total_duration)}|{count}|{fecha}\n")

    historial = leer_historial()
    return render_template("index.html", historial=historial)

@app.route("/borrar_historial")
def borrar_historial():
    if os.path.exists(HISTORIAL_FILE):
        os.remove(HISTORIAL_FILE)
    return redirect("/")

@app.route("/borrar_carpeta")
def borrar_carpeta():
    for f in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER,f))
    return redirect("/")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)