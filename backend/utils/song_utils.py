# utils/song_utils.py
import json
from models.song_model import Song

SONGS_FILE = 'songs.json'

def load_songs():
    try:
        with open(SONGS_FILE, 'r') as f:
            data = json.load(f)
            return [Song.from_dict(song) for song in data.get('songs', [])]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_songs(songs):
    data = {'songs': [song.to_dict() for song in songs]}
    with open(SONGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def remove_song(songs, song_id):
    return [song for song in songs if song.id != song_id]
