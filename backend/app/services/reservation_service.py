from app.extensions import db
from app.models.reservation import Reservation
from app.models.reservation_detail import ReservationDetail
from datetime import datetime
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
        return False
    return True


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
                isolation_level="REPEATABLE READ"
            )
            session.begin()
            r_id = session.execute(text("""
                SELECT max(r_id) as max
                FROM our_things.reservation
            """)).mappings().first()["max"]
            if not r_id:
                r_id = 1
            else:
                r_id = r_id + 1
            reservation = Reservation(
                r_id=r_id,
                m_id=m_id,
                create_at=datetime.now(),
                is_deleted=False
            )
            rd_id = session.execute(text("""
                SELECT max(rd_id) as max
                FROM our_things.reservation_detail
            """)).mappings().first()["max"]
            if not rd_id:
                rd_id = 1
            else:
                rd_id = rd_id + 1
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

                reservation_detail = ReservationDetail(
                    rd_id=rd_id,
                    r_id=r_id,
                    i_id=rd["i_id"],
                    p_id=rd["p_id"],
                    est_start_at=start_at,
                    est_due_at=due_at,
                    is_deleted=False  # 注意：ReservationDetail model 沒有 is_deleted，是跟著 Reservation 走的，這邊可能多餘或 schema 不符，先依 ReservationDetail 定義移除
                )
                # 檢查 ReservationDetail 是否真的有 is_deleted 欄位，剛才 read_file 顯示只有 r_id, i_id, p_id, est_start, est_due
                # 所以不需要 is_deleted

                # 修正：重新建立物件，不含 is_deleted
                reservation_detail = ReservationDetail(
                    rd_id=rd_id,
                    r_id=r_id,
                    i_id=rd["i_id"],
                    p_id=rd["p_id"],
                    est_start_at=start_at,
                    est_due_at=due_at
                )

                session.add(reservation_detail)
                rd_id = rd_id + 1
            session.add(reservation)
            session.commit()
            return True, "OK"
        except Exception as e:
            session.rollback()
            return False, str(e)
    return False, "Unauthorized"
