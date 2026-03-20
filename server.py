from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from config import UPLOAD_FOLDER, DOWNLOAD_FOLDER
from utils import generate_unique_name, cut_video_by_chapters

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    videos = os.listdir(DOWNLOAD_FOLDER)
    if request.method == "POST":
        uploaded_files = request.files.getlist("files")
        chapters = request.form.get("chapters")
        chapters = int(chapters) if chapters else None

        for file in uploaded_files:
            filename = generate_unique_name(file.filename)
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(upload_path)

            cut_video_by_chapters(upload_path, chapters=chapters)

        return redirect(url_for("index"))

    return render_template("index.html", videos=videos)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)