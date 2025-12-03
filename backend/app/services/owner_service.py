from app.extensions import db
from sqlalchemy import text
from app.utils.jwt_utils import get_user
from app.models.loan_event import LoanEvent
from datetime import datetime
from app.services.loan_service import create_loan_for_upcoming_reservations


def get_future_reservation_details(token: str):
    """
    處理取得未來的預約詳細資訊請求。
    同時觸發自動建立 Loan 的機制 (Lazy Trigger)。
    """
    m_id, active_role = get_user(token)
    if not m_id:
        return False, "Unauthorized"
    if active_role == "member":
        # Lazy Trigger: 在查詢前先嘗試建立即將到期的 Loan
        create_loan_for_upcoming_reservations(hours_ahead=24)

        result = db.session.execute(text("""
            SELECT l_id, i_id, m_name, est_start_at, est_return_at
            FROM reservation_detail
            join loan on reservation_detail.rd_id = loan.rd_id
            join item on reservation_detail.i_id = item.i_id
            join member on item.m_id = member.m_id
            WHERE m_id = :m_id and (actual_return_at is null or actual_return_at is null)
            order by est_start_at asc
        """), {"m_id": m_id}).mappings().all()
        return True, result
    return False, "Unauthorized"


def punch_in_loan(token: str, l_id: int, data: dict):
    """
    處理打卡請求。
    """
    m_id, active_role = get_user(token)
    if not m_id:
        return False, "Unauthorized"
    if active_role == "member":
        try:
            db.session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))

            # 使用更高精度的 timestamp (毫秒級) 避免衝突
            timestamp_ms = int(datetime.now().timestamp() * 1000)

            loan_event = LoanEvent(
                timestamp=timestamp_ms,
                event_type=data["event_type"],
                l_id=l_id
            )
            db.session.add(loan_event)
            if data["event_type"] == "Handover":
                db.session.execute(text("""
                        UPDATE loan
                        SET actual_start_at = :actual_start_at
                        WHERE l_id = :l_id
                    """), {"actual_start_at": datetime.now(), "l_id": l_id})
            elif data["event_type"] == "Return":
                db.session.execute(text("""
                        UPDATE loan
                        SET actual_return_at = :actual_return_at
                        WHERE l_id = :l_id
                    """), {"actual_return_at": datetime.now(), "l_id": l_id})

            db.session.commit()
            return True, "OK"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    return False, "Unauthorized"
