from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

db = SQLAlchemy()  # 拿來做 engine + session，用不用 ORM 你自己決定

# MongoDB client（類似 db 的處理方式）
_mongo_client = None  # 會在 create_app 中初始化


def init_mongo_client(mongodb_uri):
    """
    初始化 MongoDB client

    Args:
        mongodb_uri: MongoDB 連線字串
    """
    global _mongo_client
    _mongo_client = MongoClient(mongodb_uri)


def get_mongo_client():
    """
    取得 MongoDB client

    Returns:
        MongoClient 物件
    """
    if _mongo_client is None:
        raise RuntimeError("MongoDB client 尚未初始化，請先調用 init_mongo_client()")
    return _mongo_client
