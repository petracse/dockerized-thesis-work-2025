import os
import uuid
from flask import Flask, jsonify, request, Blueprint, send_from_directory, current_app
from utils.song_utils import load_songs, save_songs, remove_song
from models.song_model import Song
from werkzeug.utils import secure_filename

song_routes = Blueprint('song_routes', __name__)

SONGS = load_songs()

ALLOWED_EXTENSIONS = {'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@song_routes.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@song_routes.route('/songs', methods=['GET', 'POST'])
def all_songs():
    global SONGS
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'})

        file = request.files['file']

        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            post_data = request.form  # Use request.form to get other form data
            new_song = Song(post_data.get('title'), post_data.get('author'), filename=filename)  # Pass filename to Song
            SONGS.append(new_song)
            save_songs(SONGS)

            return jsonify({'status': 'success', 'message': 'Song added!', 'filename': filename})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file type'})
    else:
        return jsonify({'status': 'success', 'songs': [song.to_dict() for song in SONGS]})

@song_routes.route('/songs/<song_id>', methods=['PUT', 'DELETE'])
def single_song(song_id):
    global SONGS
    if request.method == 'PUT':
        post_data = request.get_json()
        for song in SONGS:
            if song.id == song_id:
                song.title = post_data.get('title')
                song.author = post_data.get('author')
                break
        save_songs(SONGS)
        return jsonify({'status': 'success', 'message': 'Song updated!'})
    if request.method == 'DELETE':
        SONGS = remove_song(SONGS, song_id)
        save_songs(SONGS)
        return jsonify({'status': 'success', 'message': 'Song removed!'})
