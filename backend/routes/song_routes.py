import os
import uuid
import boto3
from flask import jsonify, request, Blueprint, current_app
from utils.song_utils import load_songs, save_songs, remove_song
from models.song_model import Song
from dotenv import load_dotenv

song_routes = Blueprint('song_routes', __name__)

SONGS = load_songs()

ALLOWED_EXTENSIONS = {'mp3', 'wav'}

load_dotenv()

S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

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
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            new_song_id = uuid.uuid4().hex
            filename = f"{new_song_id}.{file_extension}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                s3_client.upload_fileobj(file, S3_BUCKET, filename) # feltöltjük az S3-ba
                #os.remove(file_path)
            except Exception as e:
                print(f"S3 feltöltési hiba: {e}")
                return jsonify({'message': f'Hiba a fájl S3-ba való feltöltése közben: {str(e)}'}), 500

            post_data = request.form
            new_song = Song(post_data.get('title'), post_data.get('author'), id=new_song_id, filename=filename)
            SONGS.append(new_song)
            save_songs(SONGS)

            return jsonify({'status': 'success', 'message': 'Song added!', 'filename': filename})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file type'})
    else:
        return jsonify({'status': 'success', 'songs': [song.to_dict() for song in SONGS]})


@song_routes.route('/songs/<song_id>', methods=['PUT'])
def single_song(song_id):
    global SONGS
    song_to_update = next((song for song in SONGS if song.id == song_id), None)

    if not song_to_update:
        return jsonify({'status': 'error', 'message': 'Song not found!'}), 404

    if request.method == 'PUT':
        title = request.form.get('title')
        author = request.form.get('author')

        file = request.files.get('file')

        if file:
            if allowed_file(file.filename):
                file_extension = file.filename.rsplit('.', 1)[1].lower()

                filename = f"{song_id}.{file_extension}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                if song_to_update.filename:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], song_to_update.filename)
                    try:
                        os.remove(old_file_path)
                        s3_client.delete_object(Bucket=S3_BUCKET, Key=song_to_update.filename)
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        print(f"Error deleting old file: {e}")

                file.save(file_path)
                s3_client.upload_fileobj(file, S3_BUCKET, filename)

                song_to_update.filename = filename
            else:
                return jsonify({'status': 'error', 'message': 'Invalid file type'})

        song_to_update.title = title if title else song_to_update.title
        song_to_update.author = author if author else song_to_update.author

        save_songs(SONGS)
        return jsonify({'status': 'success', 'message': 'Song updated!'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request method!'}), 405


@song_routes.route('/songs/<song_id>/file', methods=['DELETE'])
def delete_song_file(song_id):
    global SONGS
    song_to_update = next((song for song in SONGS if song.id == song_id), None)

    if not song_to_update:
        return jsonify({'status': 'error', 'message': 'Song not found!'}), 404

    filename = request.get_json().get('filename')

    if not filename:
        return jsonify({'status': 'error', 'message': 'Filename not provided!'}), 400

    if song_to_update.filename:
        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], song_to_update.filename)
        try:
            os.remove(old_file_path)
            s3_client.delete_object(Bucket=S3_BUCKET, Key=song_to_update.filename)
            song_to_update.filename = None  # Töröljük a fájlnevet a song objektumból
            save_songs(SONGS)  # Mentsük a változásokat
        except FileNotFoundError:
            return jsonify({'status': 'error', 'message': 'File not found!'}), 404
        except Exception as e:
            print(f"Error deleting old file: {e}")
            return jsonify({'status': 'error', 'message': 'Error deleting file!'}), 500

    return jsonify({'status': 'success', 'message': 'File removed successfully!'}), 200


@song_routes.route('/songs/<song_id>', methods=['DELETE'])
def single_song_delete(song_id):
    global SONGS
    song_to_delete = next((song for song in SONGS if song.id == song_id), None)

    if song_to_delete:
        filename = song_to_delete.filename
        if filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            try:
                os.remove(file_path)
                s3_client.delete_object(Bucket=S3_BUCKET, Key=song_to_delete.filename)
                print(f"File '{filename}' deleted from S3 bucket '{S3_BUCKET}'")
            except FileNotFoundError:
                print(f"File '{filename}' not found in S3 bucket '{S3_BUCKET}'")
            except Exception as e:
                print(f"Error deleting file '{filename}': {e}")

        SONGS = remove_song(SONGS, song_id)
        save_songs(SONGS)
        return jsonify({'status': 'success', 'message': 'Song removed!'})
    else:
        return jsonify({'status': 'error', 'message': 'Song not found!'})
