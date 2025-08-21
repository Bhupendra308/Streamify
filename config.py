import os

class Config:
    SECRET_KEY = 'your-secret-key'
    # SQLAlchemy config for MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Bhupendra.2004@localhost/videoplatform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join('static', 'videos')
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}