from app.extensions import db
from sqlalchemy import text


def get_all_pickup_places():
    """
    處理取得所有取貨地點請求。
    """
    pickup_places = db.session.execute(text("""
        SELECT p_id, p_name
        FROM pick_up_place
        WHERE is_deleted = false
    """)).mappings().all()
    # 轉換為字典列表
    return [dict(row) for row in pickup_places]
