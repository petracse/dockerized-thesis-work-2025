from flask import Blueprint, jsonify, current_app, request
from utils.music_processing_utils import compute_chromagram_from_filename
import os

music_processing = Blueprint('music_processing_routes', __name__)
@music_processing.route('/songs/<song_id>/analyze-song', methods=['GET'])
def analyze_song(song_id):
    uploads_folder = os.path.join(current_app.root_path, 'uploads')
    filename = request.args.get('filename')  # Kinyerjük a filename-et a query paraméterekből

    if not filename:
        return jsonify({"error": "Filename is missing"}), 400

    # Összerakjuk a fájl teljes elérési útvonalát
    fn_wav = os.path.join(uploads_folder, filename)

    if not os.path.exists(fn_wav):
        return jsonify({"error": "Audio file not found"}), 404

    N = 4096
    H = 2048
    try:
        X_STFT, Fs_X, x, Fs, x_dur = compute_chromagram_from_filename(fn_wav, N=N, H=H, gamma=0.1, version='STFT')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    chromagram_list = X_STFT.tolist()

    response = {
        "chromagram": chromagram_list,
        "Fs_X": Fs_X,
        "x_dur": x_dur
    }

    return jsonify(response)

@music_processing.route('/process-audio', methods=['POST'])
def process_audio():

    uploads_folder = os.path.join(current_app.root_path, 'uploads')

    wav_filename = 'FMP_C5_F01_Beatles_LetItBe-mm1-4_Original.wav'
    fn_wav = os.path.join(uploads_folder, wav_filename)

    if not os.path.exists(fn_wav):
        return jsonify({"error": "Audio file not found"}), 404

    N = 4096
    H = 2048
    X_STFT, Fs_X, x, Fs, x_dur = compute_chromagram_from_filename(fn_wav, N=N, H=H, gamma=0.1, version='STFT')

    chromagram_list = X_STFT.tolist()

    response = {
        "chromagram": chromagram_list,
        "Fs_X": Fs_X,
        "x_dur": x_dur
    }

    return jsonify(response)

