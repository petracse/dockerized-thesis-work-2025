from flask import Blueprint, jsonify

# Külön route fájl létrehozása (Blueprint)
music_processing = Blueprint('music_processing_routes', __name__)


@music_processing.route('/process-audio', methods=['POST'])
def process_audio():
    # Ez itt egy egyszerű válasz a teszthez, amit JSON formátumban küldünk vissza
    response = {"chromagram": "valami"}  # A válasz JSON formátumban

    return jsonify(response)  # Flask biztosítja a JSON válasz formázását

