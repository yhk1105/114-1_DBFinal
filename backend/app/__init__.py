from flask import Flask
from flask_cors import CORS
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from .config import Config
from .extensions import db, init_mongo_client
from .routes.auth import auth_bp
from .routes.item import item_bp
from .routes.me import me_bp
from .routes.owner import owner_bp
from .routes.reservation import reservation_bp
from .routes.staff import staff_bp
from .mongodb import init_mongodb


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 啟用 CORS (允許前端請求)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 初始化 SQLAlchemy
    db.init_app(app)

    # 在每個資料庫連線建立時設定 search_path（最可靠的方法）
    with app.app_context():
        @event.listens_for(db.engine, "connect", insert=True)
        def set_search_path(dbapi_conn, connection_record):
            """在每個資料庫連線建立時設定 search_path"""
            with dbapi_conn.cursor() as cursor:
                cursor.execute("SET search_path TO our_things")

    # 初始化 MongoDB（類似 db 的處理方式）
    init_mongo_client(app.config["MONGODB_URI"])

    with app.app_context():
        # 初始化 MongoDB（建立索引、驗證連線）
        init_mongodb(app)

    # 註冊 Blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(me_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(staff_bp)

    return app
