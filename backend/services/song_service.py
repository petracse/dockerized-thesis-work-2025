import uuid

from models.song_model import Song, db
from datetime import datetime, timezone
import os
import re

class SongService:
    YOUTUBE_REGEX = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/)?[A-Za-z0-9_-]{11}'
    )

    @staticmethod
    def is_youtube_url(url):
        if not url:
            return True
        return bool(SongService.YOUTUBE_REGEX.match(url))

    @staticmethod
    def get_all_songs():
        return Song.query.all()

    @staticmethod
    def add_song(title, author, file, upload_folder, yt_url=None):
        if yt_url and not SongService.is_youtube_url(yt_url):
            yt_url = ""
        filename = None
        if file:
            song_id = uuid.uuid4().hex
            filename = f"{song_id}.{file.filename.rsplit('.', 1)[1].lower()}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

        new_song = Song(
            title=title,
            author=author,
            filename=filename,
            yt_url=yt_url if yt_url is not None else ""
        )
        db.session.add(new_song)
        db.session.commit()
        return new_song

    @staticmethod
    def update_song(song_id, title, author, file, upload_folder, yt_url=None):
        song = Song.query.get(song_id)
        if not song:
            return None

        if yt_url is not None:
            if yt_url and not SongService.is_youtube_url(yt_url):
                yt_url = ""
            song.yt_url = yt_url

        if file:
            SongService.delete_song_file(song, upload_folder)
            filename = f"{song_id}.{file.filename.rsplit('.', 1)[1].lower()}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            song.filename = filename

        song.title = title if title else song.title
        song.author = author if author else song.author
        song.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        return song

    @staticmethod
    def delete_song(song_id, upload_folder):
        song = Song.query.get(song_id)
        if song:
            SongService.delete_song_file(song, upload_folder)
            db.session.delete(song)
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_song_file(song, upload_folder):
        if song.filename:
            file_path = os.path.join(upload_folder, song.filename)
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            song.filename = None
            db.session.commit()
