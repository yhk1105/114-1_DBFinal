"""
漏斗追蹤服務
用於記錄用戶從查詢到預約的完整流程
"""
import uuid
from datetime import datetime
from flask import request
from app.mongodb.connection import get_mongo_db
from app.utils.jwt_utils import get_user


def get_session_id():
    """
    從 request header 取得 session_id，如果沒有則生成新的

    Returns:
        str: session_id
    """
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        # 如果沒有 session_id，生成一個新的
        session_id = str(uuid.uuid4())
    return session_id


def get_or_create_session(session_id, user_token=None, m_id=None):
    """
    取得或建立用戶 session

    Args:
        session_id: Session ID
        user_token: JWT Token（如果有）
        m_id: 會員 ID（如果有 token 且解析成功）

    Returns:
        dict: Session 文件
    """
    db = get_mongo_db()
    user_sessions = db["user_sessions"]

    # 查找現有 session
    session = user_sessions.find_one({"session_id": session_id})

    if not session:
        # 建立新 session
        session = {
            "session_id": session_id,
            "user_token": user_token,
            "m_id": m_id,
            "events": [],
            "funnel_stage": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        user_sessions.insert_one(session)
    else:
        # 更新現有 session（如果有新的 token 或 m_id）
        update_data = {"updated_at": datetime.utcnow()}
        if user_token and not session.get("user_token"):
            update_data["user_token"] = user_token
        if m_id and not session.get("m_id"):
            update_data["m_id"] = m_id

        if len(update_data) > 1:  # 除了 updated_at 還有其他更新
            user_sessions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )

    return session


def log_event(event_type, endpoint, success=True, error_reason=None, **kwargs):
    """
    記錄用戶行為事件

    Args:
        event_type: 事件類型（例如：'browse_category', 'view_item', 'create_reservation'）
        endpoint: API endpoint
        success: 是否成功
        error_reason: 失敗原因（如果有）
        **kwargs: 其他相關資訊（例如：item_id, category_id 等）

    範例：
        log_event('browse_category', '/item/category/1', category_id=1)
        log_event('view_item', '/item/5', item_id=5)
        log_event('create_reservation', '/reservation/create', success=False, error_reason='Item not available')
    """
    try:
        # 取得 session_id
        session_id = get_session_id()

        # 嘗試從 token 取得 m_id
        user_token = None
        m_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            user_token = auth_header.split(" ")[1]
            try:
                m_id, _ = get_user(user_token)
            except Exception:
                pass  # token 無效或過期，忽略

        # 取得或建立 session
        session = get_or_create_session(session_id, user_token, m_id)

        # 建立事件
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "endpoint": endpoint,
            "success": success,
            "error_reason": error_reason,
            **kwargs  # 其他相關資訊（item_id, category_id 等）
        }

        # 更新 session：加入事件並更新漏斗階段
        db = get_mongo_db()
        user_sessions = db["user_sessions"]

        # 更新漏斗階段
        funnel_stage = determine_funnel_stage(event_type)

        user_sessions.update_one(
            {"session_id": session_id},
            {
                "$push": {"events": event},
                "$set": {
                    "funnel_stage": funnel_stage,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    except Exception as e:
        # 記錄錯誤但不影響主要業務邏輯
        # 可以選擇記錄到 log 或忽略
        pass


def determine_funnel_stage(event_type):
    """
    根據事件類型決定當前漏斗階段

    Args:
        event_type: 事件類型

    Returns:
        str: 漏斗階段
    """
    stage_mapping = {
        'browse_category': 'browse_category',
        'view_subcategory': 'browse_category',
        'view_item': 'view_item',
        'check_availability': 'check_availability',
        'view_pickup_places': 'view_pickup_places',
        'attempt_reservation': 'attempt_reservation',
        'reservation_success': 'reservation_success',
        'reservation_failed': 'reservation_failed',
    }
    return stage_mapping.get(event_type, 'unknown')
