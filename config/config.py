import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'doc', 'docx', 'pptx', 'pdf'}
    SECRET_KEY = os.urandom(24)
