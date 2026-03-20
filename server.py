from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from config import UPLOAD_FOLDER, DOWNLOAD_FOLDER, CHAPTER_OPTIONS
from utils import generate_unique_name, cut_video_by_chapters

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', chapter_options=CHAPTER_OPTIONS)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['video']
    filename = secure_filename(file.filename)
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(saved_path)
    return jsonify({'filename': filename})

@app.route('/cut', methods=['POST'])
def cut_video():
    data = request.json
    filename = data.get('filename')
    chapter_duration = int(data.get('chapter_duration', 15))
    input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_file):
        return jsonify({'error': 'File not found'}), 404

    output_files = cut_video_by_chapters(input_file, chapter_duration)
    return jsonify({'status': 'success', 'files': [os.path.basename(f) for f in output_files]})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/clear', methods=['POST'])
def clear_downloads():
    for f in os.listdir(DOWNLOAD_FOLDER):
        os.remove(os.path.join(DOWNLOAD_FOLDER, f))
    return jsonify({'status': 'Downloads cleared'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)