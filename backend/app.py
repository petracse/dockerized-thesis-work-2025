import uuid
import json  # Importáld a json modult
import os # Import os

from flask import Flask, jsonify, request
from flask_cors import CORS


# JSON fájl elérési útja
SONGS_FILE = 'songs.json'

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


def load_songs():
    """Betölti a dalokat a JSON fájlból."""
    try:
        with open(SONGS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('songs', [])  # Visszaadja a 'songs' listát, vagy egy üres listát, ha nincs
    except FileNotFoundError:
        return []  # Ha a fájl nem létezik, üres listát ad vissza
    except json.JSONDecodeError:
        return [] # Hibás JSON esetén is üres listát ad vissza


def save_songs(songs):
    """Mentia a dalokat a JSON fájlba."""
    data = {'songs': songs}
    with open(SONGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)  # Formázott JSON mentés


# Inicializáld a dalok listáját a fájlból
SONGS = load_songs()


def remove_song(song_id):
    """Eltávolít egy dalt az ID alapján."""
    global SONGS  # Hozzáférés a globális SONGS listához
    SONGS = [song for song in SONGS if song['id'] != song_id]
    save_songs(SONGS)  # Mentsük el a változásokat a fájlba
    return True


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/songs', methods=['GET', 'POST'])
def all_songs():
    response_object = {'status': 'success'}
    global SONGS  # Hozzáférés a globális SONGS listához

    if request.method == 'POST':
        post_data = request.get_json()
        new_song = {
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
        }
        SONGS.append(new_song)
        save_songs(SONGS)  # Mentsük el a változásokat a fájlba
        response_object['message'] = 'Song added!'
    else:
        response_object['songs'] = SONGS
    return jsonify(response_object)


@app.route('/songs/<song_id>', methods=['PUT', 'DELETE'])
def single_song(song_id):
    response_object = {'status': 'success'}
    global SONGS  # Hozzáférés a globális SONGS listához

    if request.method == 'PUT':
        post_data = request.get_json()
        #remove_song(song_id) # Nem kell eltávolítani, mert frissítjük
        for song in SONGS:
            if song['id'] == song_id:
                song['title'] = post_data.get('title')
                song['author'] = post_data.get('author')
                break
        save_songs(SONGS)
        response_object['message'] = 'Song updated!'
    if request.method == 'DELETE':
        remove_song(song_id)
        response_object['message'] = 'Song removed!'
    return jsonify(response_object)


if __name__ == '__main__':
    # Győződjünk meg róla, hogy a JSON fájl létezik, különben létrehozzuk
    if not os.path.exists(SONGS_FILE):
        save_songs([])
    app.run()
