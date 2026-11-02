import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'visioncraft-pcd-secret-key-2026')
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB