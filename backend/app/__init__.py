from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db
from .routes.auth import auth_bp
from .routes.item import item_bp
from .routes.me import me_bp
from .routes.owner import owner_bp
from .routes.reservation import reservation_bp
from .routes.staff import staff_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 啟用 CORS (允許前端請求)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 初始化 SQLAlchemy
    db.init_app(app)

    # 註冊 Blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(me_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(staff_bp)

    return app
