import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.song_routes import song_routes
from routes.music_processing_routes import music_processing
from utils.song_utils import SONGS_FILE, save_songs
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['S3_BUCKET'] = os.getenv('S3_BUCKET')
app.config['S3_REGION'] = os.getenv('S3_REGION')
app.config['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# Regisztráljuk a song_routes blueprint-et
app.register_blueprint(song_routes)
app.register_blueprint(music_processing)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(SONGS_FILE):
        save_songs([])
    app.run()
