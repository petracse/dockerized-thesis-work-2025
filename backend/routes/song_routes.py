from flask import jsonify, request, Blueprint, current_app, send_from_directory
from services.song_service import SongService
from utils.song_utils import allowed_file
from utils.music_processing_utils import process_music_file_for_chords_deepchroma, process_music_file_for_chords_cqt
from models.song_model import Song
import os
import numpy as np

song_routes = Blueprint('song_routes', __name__)
song_service = SongService()

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}

@song_routes.route('/songs', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        file = request.files.get('file')
        yt_url = request.form.get('yt_url')

        # Ha se file, se yt_url nincs, hiba
        if (not file or file.filename == '') and not yt_url:
            return jsonify({'status': 'error', 'message': 'No file or yt_url provided!'}), 400

        # Ha van file, de üres nevű, úgy kezeljük, mintha nem lenne
        if file and file.filename == '':
            file = None

        if Song.query.count() >= 20:
            return jsonify({'status': 'error', 'message': '20 songs limit exceeded!'}), 400

        # Ha van file, de nem engedélyezett típus
        if file and not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'status': 'error', 'message': 'Invalid file type'})

        try:
            new_song = song_service.add_song(
                request.form.get('title'),
                request.form.get('author'),
                file,
                current_app.config['UPLOAD_FOLDER'],
                yt_url
            )
            return jsonify({'status': 'success', 'message': 'Song added!', 'filename': getattr(new_song, "filename", None)})
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    else:
        return jsonify({'status': 'success', 'songs': [song.to_dict() for song in song_service.get_all_songs()]})

@song_routes.route('/songs/<song_id>', methods=['PUT', 'DELETE'])
def update_song(song_id):
    if request.method == 'PUT':
        file = request.files.get('file')
        yt_url = request.form.get('yt_url')

        # Ha van file, de nem engedélyezett típus
        if file and not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'status': 'error', 'message': 'Invalid file type'})

        # Ha se file, se yt_url nincs, hiba
        if (not file or file.filename == '') and yt_url is None:
            return jsonify({'status': 'error', 'message': 'No file or yt_url provided!'}), 400

        # Ha van file, de üres nevű, úgy kezeljük, mintha nem lenne
        if file and file.filename == '':
            file = None

        try:
            updated_song = song_service.update_song(
                song_id,
                request.form.get('title'),
                request.form.get('author'),
                file,
                current_app.config['UPLOAD_FOLDER'],
                yt_url
            )

            if updated_song:
                return jsonify({'status': 'success', 'message': 'Song updated!'})
            else:
                return jsonify({'status': 'error', 'message': 'Song not found!'}), 404
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    elif request.method == 'DELETE':
        if song_service.delete_song(song_id, current_app.config['UPLOAD_FOLDER']):
            return jsonify({'status': 'success', 'message': 'Song removed!'})
        else:
            return jsonify({'status': 'error', 'message': 'Song not found!'}), 404

@song_routes.route('/songs/<song_id>/file', methods=['DELETE'])
def delete_song_file(song_id):
    song = next((song for song in song_service.get_all_songs() if song.id == song_id), None)
    if not song:
        return jsonify({'status': 'error', 'message': 'Song not found!'}), 404

    song_service.delete_song_file(song, current_app.config['UPLOAD_FOLDER'])
    return jsonify({'status': 'success', 'message': 'File removed successfully!'}), 200

def get_uploaded_file_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

import logging

@song_routes.route('/songs/<song_id>/analyze-song', methods=['GET'])
def analyze_song(song_id):
    filename = request.args.get('filename')
    yt_url = request.args.get('ytUrl')
    is_youtube = request.args.get('isYoutube', 'false').lower() == 'true'
    calc_accuracy = request.args.get('calc_accuracy', 'false').lower() == 'true'


    current_app.logger.info(f"analyze_song hívás: song_id={song_id}, filename={filename}, yt_url={yt_url}, is_youtube={is_youtube}")

    if not filename and not yt_url:
        current_app.logger.warning("Hiányzó filename és yt_url paraméter!")
        return jsonify({"error": "Filename is missing"}), 400

    fn_audio = ""
    if not is_youtube:
        fn_audio = get_uploaded_file_path(filename)
        if not os.path.exists(fn_audio):
            current_app.logger.error(f"Audio file nem található: {fn_audio}")
            return jsonify({"error": "Audio file not found"}), 404

    hmm_folder = os.path.join(current_app.root_path, 'utils', 'data', 'hmm_deepchroma')
    try:
        current_app.logger.info("process_music_file_for_chords_deepchroma meghívása...")
        chords_by_time, bpm = process_music_file_for_chords_deepchroma(hmm_folder, yt_url, is_youtube, fn_audio)
        current_app.logger.info(f"process_music_file_for_chords_deepchroma visszatért, bpm={bpm}, akkordok: {len(chords_by_time)} db")
    except Exception as e:
        current_app.logger.error(f"Error in analyze_song: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    response = {
        "chords_by_time": chords_by_time,
        "bpm": bpm
    }

    if calc_accuracy and filename:
        lab_name = "06_-_Let_It_Be_v3.lab"
        lab_path = os.path.join(current_app.root_path, 'utils', 'data', lab_name)
        if not os.path.exists(lab_path):
            current_app.logger.warning(f".lab fájl nem található: {lab_path}")
            response["accuracy"] = None
        else:
            lab_intervals = load_lab_file(lab_path)
            annotated_times = [start for start, chords in lab_intervals if "N" not in chords]
            snapped_chords_by_time = snap_predicted_times_to_annotations(
                chords_by_time,
                annotated_times,
                bpm
            )
            accuracy = calculate_weighted_accuracy(snapped_chords_by_time, lab_intervals)
            response["accuracy"] = accuracy

    return jsonify(response)

@song_routes.route('/songs/<song_id>/analyze-song-with-cqt', methods=['GET'])
def analyze_song_with_cqt(song_id):
    filename = request.args.get('filename')
    yt_url = request.args.get('ytUrl')
    is_youtube = request.args.get('isYoutube', 'false').lower() == 'true'
    calc_accuracy = request.args.get('calc_accuracy', 'false').lower() == 'true'

    current_app.logger.info(f"analyze_song hívás: song_id={song_id}, filename={filename}, yt_url={yt_url}, is_youtube={is_youtube}")

    if not filename and not yt_url:
        current_app.logger.warning("Hiányzó filename és yt_url paraméter!")
        return jsonify({"error": "Filename is missing"}), 400

    fn_audio = ""
    if not is_youtube:
        fn_audio = get_uploaded_file_path(filename)
        if not os.path.exists(fn_audio):
            current_app.logger.error(f"Audio file nem található: {fn_audio}")
            return jsonify({"error": "Audio file not found"}), 404

    hmm_folder = os.path.join(current_app.root_path, 'utils', 'data', 'hmm_cqt')
    try:
        current_app.logger.info("process_music_file_for_chords_deepchroma meghívása...")
        chords_by_time, bpm = process_music_file_for_chords_cqt(hmm_folder, yt_url, is_youtube, fn_audio)
        current_app.logger.info(f"process_music_file_for_chords_deepchroma visszatért, bpm={bpm}, akkordok: {len(chords_by_time)} db")
    except Exception as e:
        current_app.logger.error(f"Error in analyze_song: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    response = {
        "chords_by_time": chords_by_time,
        "bpm": bpm
    }

    if calc_accuracy and filename:
        lab_name = "06_-_Let_It_Be_v3.lab"
        lab_path = os.path.join(current_app.root_path, 'utils', 'data', lab_name)
        if not os.path.exists(lab_path):
            current_app.logger.warning(f".lab fájl nem található: {lab_path}")
            response["accuracy"] = None
        else:
            lab_intervals = load_lab_file(lab_path)
            annotated_times = [start for start, chords in lab_intervals if "N" not in chords]
            snapped_chords_by_time = snap_predicted_times_to_annotations(
                chords_by_time,
                annotated_times,
                bpm
            )
            accuracy = calculate_weighted_accuracy(snapped_chords_by_time, lab_intervals)
            response["accuracy"] = accuracy

    return jsonify(response)

def load_lab_file(lab_path):
    """
    Beolvassa a .lab fájlt és visszaad egy listát: [(start_time, [alternatív akkordok]), ...]
    """
    intervals = []
    with open(lab_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            time = float(parts[0])
            chords = parts[1].split('|')
            intervals.append((time, chords))
    return intervals

def calculate_weighted_accuracy(chords_by_time, lab_intervals):
    """
    chords_by_time: dict {time_str: chord}
    lab_intervals: list of (start_time, [alternatív akkordok])
    """
    ai_times = sorted((float(t), ch) for t, ch in chords_by_time.items())

    # .lab feldolgozás (start, end, [alternatív akkordok])
    intervals = []
    for i, (start, chords) in enumerate(lab_intervals):
        if "N" in chords:
            continue  # Csend, nem számítjuk
        end = lab_intervals[i+1][0] if i+1 < len(lab_intervals) else None
        intervals.append((start, end, chords))

    # Utolsó intervallum végének kezelése
    if intervals and intervals[-1][1] is None:
        intervals[-1] = (intervals[-1][0], ai_times[-1][0] if ai_times else intervals[-1][0]+1.0, intervals[-1][2])

    total_duration = 0.0
    correct_duration = 0.0

    ai_idx = 0
    for start, end, gt_chords in intervals:
        if end is None:
            continue
        duration = end - start
        total_duration += duration

        # Megkeressük, hogy ebben az intervallumban mi az AI akkordja
        ai_chord = None
        for i in range(ai_idx, len(ai_times)):
            ai_time, ai_ch = ai_times[i]
            if ai_time >= end:
                break
            if ai_time >= start:
                ai_chord = ai_ch
                ai_idx = i
                break

        # Akkord egyezés: bármelyik alternatíva elfogadható
        if ai_chord is not None and ai_chord in gt_chords:
            correct_duration += duration

    if total_duration == 0:
        return None
    return correct_duration / total_duration

def snap_predicted_times_to_annotations(chords_by_time, ref_times, bpm):
    """
    chords_by_time: dict {pred_time: chord}
    ref_times: list of annotált akkordváltás időpontok (float)
    bpm: float
    Visszaad: dict {új_időpont: akkord}
    """
    import numpy as np
    dt = 60.0 / bpm
    ref_times_arr = np.array(ref_times)
    snapped = {}
    for t_str, chord in chords_by_time.items():
        t = float(t_str)
        if len(ref_times_arr) == 0:
            snapped[t] = chord
            continue
        diffs = np.abs(ref_times_arr - t)
        min_idx = np.argmin(diffs)
        closest = ref_times_arr[min_idx]
        if diffs[min_idx] < dt:
            snapped[closest] = chord
        else:
            snapped[t] = chord
    return snapped

@song_routes.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
