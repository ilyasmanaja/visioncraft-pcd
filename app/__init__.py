from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Blueprint halaman utama
    from app.routes.pages import pages_bp
    app.register_blueprint(pages_bp)

    # Blueprint API proses citra
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    return app