import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from models.song_model import db
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# instantiate the app
app = Flask(__name__)

# Konfiguráció SQLite adatbázishoz
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024  # 40 MB
CORS(app, resources={r'/*': {'origins': '*'}})
db.init_app(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Importáld a route-okat az adatbázis inicializálása után
from routes.song_routes import song_routes

app.register_blueprint(song_routes, url_prefix='/api')

warmup_done = False

def warmup_jit():
    global warmup_done
    try:
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], 'FMP_C5_F01_Beatles_LetItBe-mm1-4_Original.wav')
        hmm_folder = os.path.join(app.root_path, 'utils', 'data', 'hmm_deepchroma')
        from utils.music_processing_utils import process_music_file_for_chords_deepchroma
        process_music_file_for_chords_deepchroma(
            hmm_folder=hmm_folder,
            yt_url="",
            is_youtube=False,
            song_path=wav_path
        )
        warmup_done = True
        print("Warm-up JIT: sikeres.")
    except Exception as e:
        print(f"Warm-up JIT hiba: {e}")
        warmup_done = False

warmup_jit()

@app.route('/api/warmup-status')
def warmup_status():
    return {'done': warmup_done}

if __name__ == '__main__':
    app.run()

