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
app.config['S3_BUCKET'] = os.getenv('S3_BUCKET')
app.config['S3_REGION'] = os.getenv('S3_REGION')
app.config['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
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

