import uuid

class Song:
    def __init__(self, title, author, id=None, filename=None):
        self.id = id if id else uuid.uuid4().hex
        self.title = title
        self.author = author
        self.filename = filename  # Store the filename

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'filename': self.filename  # Include filename in dictionary representation
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['title'], data['author'], data['id'], data.get('filename'))
