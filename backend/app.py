# backend/app.py
import os
from flask import Flask
from flask_cors import CORS
from routes.song_routes import song_routes
from utils.song_utils import SONGS_FILE, save_songs

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# Regisztráljuk a song_routes blueprint-et
app.register_blueprint(song_routes)


if __name__ == '__main__':
    # Győződjünk meg róla, hogy a JSON fájl létezik, különben létrehozzuk
    if not os.path.exists(SONGS_FILE):
        save_songs([])
    app.run()
