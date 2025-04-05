import os
import re
import mimetypes
from flask import (
    Blueprint, flash, g, redirect, render_template, request,
    url_for, current_app, send_from_directory, jsonify, abort, Response
)
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.database.models import Video, VideoProgress
from app.utils.video_converter import create_hls_segments

video_bp = Blueprint('video', __name__)


def allowed_file(filename):
    allowed_extensions = {'mp4', 'avi', 'mkv', 'mov', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@video_bp.route('/')
def index():
    videos = Video.get_all(limit=12)

    if current_user.is_authenticated:
        recent_videos = VideoProgress.get_recently_watched(current_user.id, limit=4)
    else:
        recent_videos = []

    return render_template('index.html', videos=videos, recent_videos=recent_videos)


@video_bp.route('/dashboard')
@login_required
def dashboard():
    recent_videos = VideoProgress.get_recently_watched(current_user.id)
    return render_template('dashboard.html', recent_videos=recent_videos)


@video_bp.route('/watch/<int:video_id>')
@login_required
def watch(video_id):
    video = Video.get_by_id(video_id)

    if video is None:
        flash('El video solicitado no existe.', 'danger')
        return redirect(url_for('video.index'))

    progress = VideoProgress.get_progress(current_user.id, video_id)

    # Generar segmentos HLS para este video
    video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video.filename)
    hls_dir = os.path.join(current_app.static_folder, 'hls', str(video_id))
    playlist_path = create_hls_segments(video_path, hls_dir)

    # Comprobar si la conversión fue exitosa
    if not playlist_path:
        flash('Error al preparar el video para streaming.', 'danger')
        return redirect(url_for('video.index'))

    # Obtener la ruta relativa del playlist
    playlist_url = f'/static/hls/{video_id}/{os.path.basename(playlist_path)}'

    return render_template('player.html', video=video, progress=progress, playlist_url=playlist_url)


@video_bp.route('/video-segment/<path:filename>')
@login_required
def serve_video_segment(filename):
    """Sirve segmentos de video HLS"""
    segments_dir = os.path.join(current_app.static_folder, 'hls')
    return send_from_directory(segments_dir, filename)


@video_bp.route('/api/update-progress', methods=['POST'])
@login_required
def update_progress():
    if not request.json:
        abort(400)

    video_id = request.json.get('video_id')
    current_time = request.json.get('current_time')
    watched = request.json.get('watched', False)

    if not video_id or current_time is None:
        return jsonify({'error': 'Datos incompletos'}), 400

    VideoProgress.update_progress(current_user.id, video_id, current_time, watched)

    return jsonify({'status': 'success'})


@video_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            # Guardar el archivo
            file.save(file_path)

            title = request.form.get('title', filename)
            description = request.form.get('description', '')
            category = request.form.get('category', 'General')

            # Crear entrada en la base de datos
            video = Video.create(
                title=title,
                description=description,
                filename=filename,
                thumbnail=None,
                duration=0,
                category=category,
                uploader_id=current_user.id
            )

            flash('Video subido correctamente', 'success')
            return redirect(url_for('video.watch', video_id=video.id))
        else:
            flash('Tipo de archivo no permitido', 'danger')

    return render_template('upload.html')