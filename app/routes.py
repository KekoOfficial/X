from flask import Blueprint, request, render_template, redirect
from app.services.video_service import fast_segment_video
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/process', methods=['POST'])
def process_video():
    video_path = request.form.get('video_path')
    t_segmento = request.form.get('time', 60)
    
    # Destino ordenado según tu estructura: media/cuts/
    output_folder = os.path.join('media', 'cuts', 'PROYECTO_RECIENTE')
    
    success = fast_segment_video(video_path, output_folder, t_segmento)
    
    if success:
        return f"⚡ FRAGMENTACIÓN COMPLETADA. Revisa: {output_folder}"
    return "❌ Error en el proceso."
