from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Use 255 to fit werkzeug's scrypt/argon hashes comfortably
    password = db.Column(db.String(255), nullable=False)

    videos = db.relationship("Video", backref="user", lazy=True, cascade="all, delete-orphan")


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True)

    # Stored/transcoded filename (e.g., abc123.mp4) inside UPLOAD_FOLDER
    filename = db.Column(db.String(200), nullable=False)

    # Original uploaded filename (e.g., holiday.mov)
    original_filename = db.Column(db.String(200), nullable=False)

    # Editable metadata (this is what “manage” enables)
    title = db.Column(db.String(200), nullable=False, default="Untitled")
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
