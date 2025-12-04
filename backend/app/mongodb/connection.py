from pymongo.errors import ConnectionFailure
from app.extensions import get_mongo_client


def get_mongo_db(database_name="our_things_funnel_tracking"):
    """
    取得 MongoDB 資料庫物件

    Args:
        database_name: 資料庫名稱，預設為 "our_things_funnel_tracking"

    Returns:
        Database 物件
    """
    mongo_client = get_mongo_client()
    return mongo_client.get_database(database_name)


def init_mongodb(app):
    """
    初始化 MongoDB：驗證連線、建立索引

    Args:
        app: Flask 應用程式實例
    """
    try:
        mongo_client = get_mongo_client()
    except RuntimeError:
        app.logger.error("❌ MongoDB client 尚未初始化")
        app.logger.warning("應用程式將繼續運行，但 MongoDB 功能將無法使用")
        return

    try:
        # 測試連線
        mongo_client.admin.command('ping')
        app.logger.info("✅ MongoDB 連線成功")

        # 取得資料庫
        db = get_mongo_db()

        # 建立索引（提升查詢效能）
        user_sessions = db["user_sessions"]

        # 建立索引（如果已存在會忽略，不會報錯）
        indexes_to_create = [
            ("session_id", {"unique": True}),
            ("user_token", {}),
            ("m_id", {}),
            ("created_at", {}),
            ("funnel_stage", {}),
            ([("events.timestamp", 1)], {}),
        ]

        for index_def in indexes_to_create:
            try:
                if isinstance(index_def[0], list):
                    user_sessions.create_index(index_def[0], **index_def[1])
                else:
                    user_sessions.create_index(index_def[0], **index_def[1])
            except Exception:
                pass  # 索引已存在，忽略

        app.logger.info("✅ MongoDB 索引建立完成")

        # 顯示資料庫資訊
        db_names = mongo_client.list_database_names()
        app.logger.info(f"MongoDB 資料庫列表: {db_names}")

    except ConnectionFailure as e:
        app.logger.error(f"❌ MongoDB 連線失敗: {e}")
        app.logger.warning("應用程式將繼續運行，但 MongoDB 功能將無法使用")
    except Exception as e:
        app.logger.error(f"❌ MongoDB 初始化錯誤: {e}")
        app.logger.warning("應用程式將繼續運行，但 MongoDB 功能將無法使用")
