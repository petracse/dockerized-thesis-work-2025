import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS


SONGS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'Praise The Lord (Da Shine)',
        'author': 'A$AP Rocky',
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Black Star',
        'author': 'Yngwie Malmsteen',
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Here I Go Again',
        'author': 'Whitesnake',
    }
]


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


def remove_song(song_id):
    for song in SONGS:
        if song['id'] == song_id:
            SONGS.remove(song)
            return True
    return False


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/songs', methods=['GET', 'POST'])
def all_songs():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        SONGS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
        })
        response_object['message'] = 'Song added!'
    else:
        response_object['songs'] = SONGS
    return jsonify(response_object)


@app.route('/songs/<song_id>', methods=['PUT', 'DELETE'])
def single_song(song_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_song(song_id)
        SONGS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
        })
        response_object['message'] = 'Song updated!'
    if request.method == 'DELETE':
        remove_song(song_id)
        response_object['message'] = 'Song removed!'
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()