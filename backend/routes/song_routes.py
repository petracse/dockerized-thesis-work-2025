from flask import jsonify, request, Blueprint, current_app
from services.song_service import SongService
from utils.song_utils import allowed_file

from models.song_model import Song

song_routes = Blueprint('song_routes', __name__)
song_service = SongService()

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}

@song_routes.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@song_routes.route('/songs', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'})

        file = request.files['file']

        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'})
        if Song.query.count() >= 20:
            return jsonify({'status': 'error', 'message': '20 songs limit exceeded!'}), 400
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            try:
                new_song = song_service.add_song(
                    request.form.get('title'),
                    request.form.get('author'),
                    file,
                    current_app.config['UPLOAD_FOLDER'],
                    request.form.get('yt_url')
                )
                return jsonify({'status': 'success', 'message': 'Song added!', 'filename': new_song.filename})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file type'})
    else:
        return jsonify({'status': 'success', 'songs': [song.to_dict() for song in song_service.get_all_songs()]})

@song_routes.route('/songs/<song_id>', methods=['PUT', 'DELETE'])
def update_song(song_id):
    if request.method == 'PUT':
        file = request.files.get('file')
        if file and not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'status': 'error', 'message': 'Invalid file type'})

        updated_song = song_service.update_song(
            song_id,
            request.form.get('title'),
            request.form.get('author'),
            file,
            current_app.config['UPLOAD_FOLDER'],
            request.form.get('yt_url')
        )

        if updated_song:
            return jsonify({'status': 'success', 'message': 'Song updated!'})
        else:
            return jsonify({'status': 'error', 'message': 'Song not found!'}), 404

    elif request.method == 'DELETE':
        if song_service.delete_song(song_id, current_app.config['UPLOAD_FOLDER']):
            return jsonify({'status': 'success', 'message': 'Song removed!'})
        else:
            return jsonify({'status': 'error', 'message': 'Song not found!'}), 404

@song_routes.route('/songs/<song_id>/file', methods=['DELETE'])
def delete_song_file(song_id):
    song = next((song for song in song_service.get_all_songs() if song.id == song_id), None)
    if not song:
        return jsonify({'status': 'error', 'message': 'Song not found!'}), 404

    song_service.delete_song_file(song, current_app.config['UPLOAD_FOLDER'])
    return jsonify({'status': 'success', 'message': 'File removed successfully!'}), 200
