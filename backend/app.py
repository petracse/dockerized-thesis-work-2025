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
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
CORS(app, resources={r'/*': {'origins': '*'}})
db.init_app(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Importáld a route-okat az adatbázis inicializálása után
from routes.song_routes import song_routes
from routes.music_processing_routes import music_processing

app.register_blueprint(song_routes)
app.register_blueprint(music_processing)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()

