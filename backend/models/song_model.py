# models/song_model.py
import uuid

class Song:
    def __init__(self, title, author, id=None):
        self.id = id if id else uuid.uuid4().hex
        self.title = title
        self.author = author

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['title'], data['author'], data['id'])
