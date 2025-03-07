from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=True)
    userid = db.Column(db.String(255), default="default_user_id")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'filename': self.filename,
            'userid': self.userid,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
