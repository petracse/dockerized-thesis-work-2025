from flask import jsonify, request, Blueprint, current_app, send_from_directory
from services.song_service import SongService
from utils.song_utils import allowed_file
from utils.music_processing_utils import process_music_file_for_chords_deepchroma
from models.song_model import Song
import os

song_routes = Blueprint('song_routes', __name__)
song_service = SongService()

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}

@song_routes.route('/songs', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        file = request.files.get('file')
        yt_url = request.form.get('yt_url')

        # Ha se file, se yt_url nincs, hiba
        if (not file or file.filename == '') and not yt_url:
            return jsonify({'status': 'error', 'message': 'No file or yt_url provided!'}), 400

        # Ha van file, de üres nevű, úgy kezeljük, mintha nem lenne
        if file and file.filename == '':
            file = None

        if Song.query.count() >= 20:
            return jsonify({'status': 'error', 'message': '20 songs limit exceeded!'}), 400

        # Ha van file, de nem engedélyezett típus
        if file and not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'status': 'error', 'message': 'Invalid file type'})

        try:
            new_song = song_service.add_song(
                request.form.get('title'),
                request.form.get('author'),
                file,
                current_app.config['UPLOAD_FOLDER'],
                yt_url
            )
            return jsonify({'status': 'success', 'message': 'Song added!', 'filename': getattr(new_song, "filename", None)})
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    else:
        return jsonify({'status': 'success', 'songs': [song.to_dict() for song in song_service.get_all_songs()]})

@song_routes.route('/songs/<song_id>', methods=['PUT', 'DELETE'])
def update_song(song_id):
    if request.method == 'PUT':
        file = request.files.get('file')
        yt_url = request.form.get('yt_url')

        # Ha van file, de nem engedélyezett típus
        if file and not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'status': 'error', 'message': 'Invalid file type'})

        # Ha se file, se yt_url nincs, hiba
        if (not file or file.filename == '') and yt_url is None:
            return jsonify({'status': 'error', 'message': 'No file or yt_url provided!'}), 400

        # Ha van file, de üres nevű, úgy kezeljük, mintha nem lenne
        if file and file.filename == '':
            file = None

        try:
            updated_song = song_service.update_song(
                song_id,
                request.form.get('title'),
                request.form.get('author'),
                file,
                current_app.config['UPLOAD_FOLDER'],
                yt_url
            )

            if updated_song:
                return jsonify({'status': 'success', 'message': 'Song updated!'})
            else:
                return jsonify({'status': 'error', 'message': 'Song not found!'}), 404
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

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

def get_uploaded_file_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

import logging

@song_routes.route('/songs/<song_id>/analyze-song', methods=['GET'])
def analyze_song(song_id):
    filename = request.args.get('filename')
    yt_url = request.args.get('ytUrl')
    is_youtube = request.args.get('isYoutube', 'false').lower() == 'true'

    current_app.logger.info(f"analyze_song hívás: song_id={song_id}, filename={filename}, yt_url={yt_url}, is_youtube={is_youtube}")

    if not filename and not yt_url:
        current_app.logger.warning("Hiányzó filename és yt_url paraméter!")
        return jsonify({"error": "Filename is missing"}), 400

    fn_audio = ""
    if not is_youtube:
        fn_audio = get_uploaded_file_path(filename)
        if not os.path.exists(fn_audio):
            current_app.logger.error(f"Audio file nem található: {fn_audio}")
            return jsonify({"error": "Audio file not found"}), 404

    hmm_folder = os.path.join(current_app.root_path, 'utils', 'data', 'hmm_deepchroma')
    try:
        current_app.logger.info("process_music_file_for_chords_deepchroma meghívása...")
        chords_by_time, bpm = process_music_file_for_chords_deepchroma(hmm_folder, yt_url, is_youtube, fn_audio)
        current_app.logger.info(f"process_music_file_for_chords_deepchroma visszatért, bpm={bpm}, akkordok: {len(chords_by_time)} db")
    except Exception as e:
        current_app.logger.error(f"Error in analyze_song: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "chords_by_time": chords_by_time,
        "bpm": bpm
    })


@song_routes.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
