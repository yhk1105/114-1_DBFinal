from flask import Flask
from .config import Config
from .extensions import db
from dotenv import load_dotenv

load_dotenv()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化 SQLAlchemy
    db.init_app(app)

    

    return app