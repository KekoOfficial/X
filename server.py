from flask import Flask, request, render_template, send_from_directory
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = "/storage/emulated/0/Download/VideosServer"
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, "Cortados")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("files")
        chapters = int(request.form.get("chapters", 1))

        count = len([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")])

        for file in files:
            try:
                filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                for i in range(chapters):
                    start = i * 15

                    count += 1
                    output_name = f"video_{count}_cap{i+1}.mp4"
                    output_path = os.path.join(OUTPUT_FOLDER, output_name)

                    subprocess.run([
                        "ffmpeg",
                        "-ss", str(start),
                        "-i", filepath,
                        "-t", "15",
                        "-c", "copy",
                        output_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            except Exception as e:
                print("Error:", e)
                continue

    videos = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")]
    return render_template("index.html", videos=videos)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    print("Servidor activo en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)