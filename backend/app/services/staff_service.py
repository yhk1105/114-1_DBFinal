from app.extensions import db
from sqlalchemy import text
from app.utils.jwt_utils import get_user
from app.models.staff import Staff
from datetime import datetime

def get_this_staff(token: str):
    """
    處理取得員工資訊請求。

    接收 JWT Token，
    取得員工資訊後回傳。
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "staff":
        staff_row = db.session.execute(
            text("""
                SELECT s_id, s_name, s_mail, role, is_deleted
                FROM our_things.staff
                WHERE s_id = :user_id
            """),
            {"user_id": user_id}
        ).mappings().first()
        if not staff_row:
            return False, "Staff not found"
        return True, {"staff": staff_row}

def get_not_deal_reports(token: str):
    """
    處理取得未處理的檢舉資訊請求。

    接收 JWT Token，
    取得未處理的檢舉資訊後回傳。
    """
    s_id, active_role = get_user(token)
    if not s_id:
        return False, "Unauthorized"
    if active_role == "staff":
        report_row = db.session.execute(
            text("""
                SELECT re_id, comment, create_at, conclude_at, m_id, i_id
                FROM our_things.report
                WHERE s_id = :user_id and r_conclusion is null
            """),
            {"user_id": s_id}
        ).mappings().all()
        return True, {"reports": report_row}

def conclude_report(token: str, re_id: int, data: dict):
    """
    處理結案檢舉請求。

    接收 JWT Token 和檢舉 ID 和結案資訊，
    結案檢舉後回傳。
    """
    s_id, active_role = get_user(token)
    if not s_id:
        return False, {"message": "Unauthorized"}
    if active_role == "staff":
        db.session.execute(text("""
            UPDATE our_things.report
            SET r_conclusion = :r_conclusion, conclude_at = :conclude_at
            WHERE re_id = :re_id
        """),
        {"r_conclusion": data["r_conclusion"], "conclude_at": datetime.now(), "re_id": re_id}
        ).mappings().first()
        return True, {"message": "success"}