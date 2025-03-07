import uuid
from datetime import datetime

class Song:
    def __init__(self, title, author, id=None, filename=None, userid="default_user_id", created_at=None, updated_at=None):
        self.id = id if id else uuid.uuid4().hex
        self.title = title
        self.author = author
        self.filename = filename
        self.userid = userid
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'filename': self.filename,
            'userid': self.userid,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['title'],
            data['author'],
            data['id'],
            data.get('filename'),
            data.get('userid', "default_user_id"),
            data.get('created_at'),
            data.get('updated_at')
        )
