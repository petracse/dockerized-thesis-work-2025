# utils/song_utils.py
import json
import os
from models.song_model import Song

SONGS_FILE = 'songs.json'

def load_songs():
    """Betölti a dalokat a JSON fájlból."""
    try:
        with open(SONGS_FILE, 'r') as f:
            data = json.load(f)
            return [Song.from_dict(song) for song in data.get('songs', [])]  # Song objektumokat ad vissza
    except FileNotFoundError:
        return []  # Ha a fájl nem létezik, üres listát ad vissza
    except json.JSONDecodeError:
        return []  # Hibás JSON esetén is üres listát ad vissza


def save_songs(songs):
    """Mentia a dalokat a JSON fájlba."""
    data = {'songs': [song.to_dict() for song in songs]}
    with open(SONGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)  # Formázott JSON mentés

def remove_song(songs, song_id):
    """Eltávolít egy dalt az ID alapján."""
    return [song for song in songs if song.id != song_id]
