from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Registrasi blueprint routing halaman
    from app.routes.pages import pages_bp
    app.register_blueprint(pages_bp)

    return app