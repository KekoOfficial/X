from flask import Blueprint, render_template, request, jsonify
from app.services import VideoEngine

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/editor')
def editor():
    video_path = request.args.get('path', '')
    return render_template('editor.html', video_path=video_path)

@bp.route('/api/cut', methods=['POST'])
def process_cut():
    data = request.json
    result = VideoEngine.execute_fast_cut(data['path'], data['seconds'])
    if result:
        return jsonify({"status": "success", "folder": result})
    return jsonify({"status": "error"}), 500
