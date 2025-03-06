import uuid

from models.song_model import Song
from utils.song_utils import load_songs, save_songs, remove_song
from services.s3_service import upload_file_to_s3, delete_file_from_s3
import os

class SongService:
    def __init__(self):
        self.songs = load_songs()

    def get_all_songs(self):
        return self.songs

    def add_song(self, title, author, file, upload_folder):
        new_song_id = uuid.uuid4().hex
        filename = f"{new_song_id}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        upload_file_to_s3(file, filename)

        new_song = Song(title, author, id=new_song_id, filename=filename)
        self.songs.append(new_song)
        save_songs(self.songs)
        return new_song

    def update_song(self, song_id, title, author, file, upload_folder):
        song_to_update = next((song for song in self.songs if song.id == song_id), None)
        if not song_to_update:
            return None

        if file:
            self.delete_song_file(song_to_update, upload_folder)
            filename = f"{song_id}.{file.filename.rsplit('.', 1)[1].lower()}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            upload_file_to_s3(file, filename)
            song_to_update.filename = filename

        song_to_update.title = title if title else song_to_update.title
        song_to_update.author = author if author else song_to_update.author

        save_songs(self.songs)
        return song_to_update

    def delete_song(self, song_id, upload_folder):
        song_to_delete = next((song for song in self.songs if song.id == song_id), None)
        if song_to_delete:
            self.delete_song_file(song_to_delete, upload_folder)
            self.songs = remove_song(self.songs, song_id)
            save_songs(self.songs)
            return True
        return False

    def delete_song_file(self, song, upload_folder):
        if song.filename:
            file_path = os.path.join(upload_folder, song.filename)
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            delete_file_from_s3(song.filename)
            song.filename = None

