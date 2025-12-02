from app.extensions import db
from app.models.reservation import Reservation
from app.models.reservation_detail import ReservationDetail
from datetime import datetime, timedelta
from app.utils.jwt_utils import get_user
from sqlalchemy import text


def check_item_available(i_id: int, p_id: int, est_start_at: datetime, est_due_at: datetime):
    """
    檢查物品是否可用。
    使用 SQL OVERLAPS operator 檢查時間是否重疊。
    需排除被刪除的預約。
    """

    conflict_count = db.session.execute(text("""
        SELECT COUNT(*)
        FROM our_things.reservation_detail rd
        JOIN our_things.reservation r ON rd.r_id = r.r_id
        WHERE rd.i_id = :i_id
        AND r.is_deleted = false
        AND (
            (rd.est_start_at < :est_due_at) AND (rd.est_due_at > :est_start_at)
        )
    """), {
        "i_id": i_id,
        "est_start_at": est_start_at,
        "est_due_at": est_due_at
    }).scalar()

    if conflict_count > 0:
        return False
    pid_check = db.session.execute(text("""
        SELECT COUNT(*)
        FROM our_things.item i
        join item_pick ip on i.i_id = ip.i_id
        WHERE ip.p_id = :p_id
        AND i.i_id = :i_id
    """), {
        "p_id": p_id,
        "i_id": i_id,
    }).scalar()
    if pid_check > 0:
        return True
    return False


def create_reservation(token: str, data: dict):
    """
    處理建立預約請求。
    """
    m_id, active_role = get_user(token)
    if not m_id:
        return False, "Unauthorized"
    if active_role == "member":
        session = db.session
        try:
            session.connection().execution_options(
                isolation_level="SERIALIZABLE"
            )
            session.begin()
            new_reservation = Reservation(
                m_id=m_id,
                create_at=datetime.now(),
                is_deleted=False
            )
            for rd in data["rd_list"]:
                # 將字串轉為 datetime 物件 (如果傳入是字串)
                # 假設 data["rd_list"] 裡的日期是 ISO 格式字串，需要先 parse
                start_at = rd["est_start_at"]
                if isinstance(start_at, str):
                    start_at = datetime.fromisoformat(start_at)
                due_at = rd["est_due_at"]
                if isinstance(due_at, str):
                    due_at = datetime.fromisoformat(due_at)

                if not check_item_available(rd["i_id"], rd["p_id"], start_at, due_at):
                    session.rollback()  # 確保 rollback
                    return False, f"Item {rd['i_id']} is not available during selected time"
                cat = session.execute(text("""
                    SELECT item.c_id, category.c_name
                    FROM our_things.item
                    join our_things.category on item.c_id = category.c_id
                    WHERE i_id = :i_id
                """), {
                    "i_id": rd["i_id"]
                }).mappings().first()
                check_ban = db.session.execute(text("""
                    SELECT COUNT(*)
                    FROM our_things.category_ban
                    WHERE c_id = :c_id and m_id = :m_id and is_deleted = false
                """), {
                    "c_id": cat["c_id"],
                    "m_id": m_id,
                }).scalar()
                if check_ban > 0:
                    session.rollback()
                    return False, f"You are banned from {cat['c_name']} category"

                check_contribution = db.session.execute(text("""
                    SELECT i_id
                    FROM our_things.contribution
                    join our_things.item on contribution.i_id = item.i_id
                    WHERE item.c_id = :c_id and contribution.m_id = :m_id and contribution.is_active = active
                """), {
                    "c_id": cat["c_id"],
                    "m_id": m_id,
                }).mappings().all()
                if len(check_contribution) > 0:
                    session.execute(text("""
                    UPDATE our_things.contribution
                    SET is_active = true
                    WHERE i_id = :i_id and m_id = :m_id
                    """), {
                        "i_id": check_contribution[0]["i_id"],
                        "m_id": m_id,
                    })
                else:
                    session.rollback()
                    return False, f"Your contribution to {cat['c_name']} category is not active"
                new_reservation_detail = ReservationDetail(
                    r_id=new_reservation.r_id,
                    i_id=rd["i_id"],
                    p_id=rd["p_id"],
                    est_start_at=start_at,
                    est_due_at=due_at,
                )

                session.add(new_reservation_detail)
            session.add(new_reservation)
            session.commit()
            return True, {"reservation_id": new_reservation.r_id}
        except Exception as e:
            session.rollback()
            return False, str(e)
    return False, "Unauthorized"

def delete_reservation(token: str, r_id: int):
    """
    處理刪除預約請求。
    """
    m_id, active_role = get_user(token)
    if not m_id:
        return False, "Unauthorized"
    if active_role == "member":
        session = db.session
        try:
            session.connection().execution_options(
                isolation_level="SERIALIZABLE"
            )
            session.begin()
            check_time = session.execute(text("""
                SELECT est_start_at, est_due_at
                FROM our_things.reservation_detail
                WHERE r_id = :r_id
            """), {
                "r_id": r_id,
            }).mappings().all()
            for rd in check_time:
                if rd["est_start_at"] < datetime.now() + timedelta(hours=24):
                    session.rollback()
                    return False, "You can only cancel the reservation within 24 hours before the start time"
            session.execute(text("""
                UPDATE our_things.reservation_detail
                SET is_deleted = true
                WHERE r_id = :r_id
            """), {
                "r_id": r_id,
            })
            session.execute(text("""
                UPDATE our_things.reservation
                SET is_deleted = true
                WHERE r_id = :r_id
            """), {
                "r_id": r_id,
            })
            session.commit()
            return True, "OK"
        except Exception as e:
            session.rollback()
            return False, str(e)
    return False, "Unauthorized"