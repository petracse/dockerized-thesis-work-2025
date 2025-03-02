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
            # Eredeti fájlnév kiterjesztése
            file_extension = file.filename.rsplit('.', 1)[1].lower()

            # Új ID generálása
            new_song_id = uuid.uuid4().hex

            # Új fájlnév létrehozása az ID és a kiterjesztés alapján
            filename = f"{new_song_id}.{file_extension}"

            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            post_data = request.form  # Használd a request.form-ot az egyéb adatokhoz
            new_song = Song(post_data.get('title'), post_data.get('author'), id=new_song_id, filename=filename)
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
        # Megkeressük a törlendő dalt
        song_to_delete = next((song for song in SONGS if song.id == song_id), None)

        if song_to_delete:
            # Eltávolítjuk a fájlt az uploads mappából, ha létezik
            filename = song_to_delete.filename
            if filename:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(file_path)
                    print(f"File '{filename}' deleted from '{current_app.config['UPLOAD_FOLDER']}'")
                except FileNotFoundError:
                    print(f"File '{filename}' not found in '{current_app.config['UPLOAD_FOLDER']}'")
                except Exception as e:
                    print(f"Error deleting file '{filename}': {e}")

            # Eltávolítjuk a dalt a listából
            SONGS = remove_song(SONGS, song_id)
            save_songs(SONGS)
            return jsonify({'status': 'success', 'message': 'Song removed!'})
        else:
            return jsonify({'status': 'error', 'message': 'Song not found!'})
