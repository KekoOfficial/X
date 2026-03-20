from flask import Flask, render_template, request, redirect, send_from_directory
import os
from utils import generate_unique_name, cut_video_by_chapters
from config import UPLOAD_FOLDER, DOWNLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Asegurar carpetas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    chapters = int(request.form.get("chapters", 0))
    if file.filename == '':
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = generate_unique_name()
        file_path = os.path.join(UPLOAD_FOLDER, filename + ".mp4")
        file.save(file_path)
        output_files = cut_video_by_chapters(file_path, chapters)
        return render_template("history.html", files=output_files)
    return "Invalid file"

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)