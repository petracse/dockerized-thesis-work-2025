# routes/song_routes.py
from flask import Flask, jsonify, request, Blueprint
from utils.song_utils import load_songs, save_songs, remove_song
from models.song_model import Song

song_routes = Blueprint('song_routes', __name__)

SONGS = load_songs()


@song_routes.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@song_routes.route('/songs', methods=['GET', 'POST'])
def all_songs():
    global SONGS
    if request.method == 'POST':
        post_data = request.get_json()
        new_song = Song(post_data.get('title'), post_data.get('author'))
        SONGS.append(new_song)
        save_songs(SONGS)
        return jsonify({'status': 'success', 'message': 'Song added!'})
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
