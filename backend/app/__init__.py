from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from .config import Config
from .extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化 SQLAlchemy
    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.item import item_bp
    from app.routes.me import me_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(item_bp)
    app.register_blueprint(me_bp)

    return app
