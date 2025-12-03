from app.extensions import db
from app.models.reservation import Reservation
from app.models.reservation_detail import ReservationDetail
from datetime import datetime, timedelta
from app.utils.jwt_utils import get_user
from sqlalchemy import text
from app.services.contribution import get_root_category


def check_item_available(session, i_id: int, p_id: int, est_start_at: datetime, est_due_at: datetime):
    """
    檢查物品是否可用。
    使用 SQL OVERLAPS operator 檢查時間是否重疊。
    需排除被刪除的預約。
    """

    conflict_count = session.execute(text("""
        SELECT rd.rd_id
        FROM reservation_detail rd
        JOIN reservation r ON rd.r_id = r.r_id
        WHERE rd.i_id = :i_id
        AND r.is_deleted = false
        AND ((rd.est_start_at, rd.est_due_at) OVERLAPS (:est_start_at, :est_due_at))
        FOR UPDATE OF rd
    """), {
        "i_id": i_id,
        "est_start_at": est_start_at,
        "est_due_at": est_due_at
    }).scalar()

    if conflict_count > 0:
        return False
    pid_check = db.session.execute(text("""
        SELECT COUNT(*)
        FROM item i
        join item_pick ip on i.i_id = ip.i_id
        WHERE ip.p_id = :p_id and ip.is_deleted = false
        AND i.i_id = :i_id
    """), {
        "p_id": p_id,
        "i_id": i_id,
    }).scalar()

    return pid_check > 0

def get_pickup_places(i_id: int):
    """
    處理取得物品可取貨地點請求。
    """
    pickup_places = db.session.execute(text("""
        SELECT p_id, p_name
        FROM item_pick
        join pick_up_place on item_pick.p_id = pick_up_place.p_id
        WHERE item_pick.i_id = :i_id and item_pick.is_deleted = false and pick_up_place.is_deleted = false
    """), {
        "i_id": i_id,
    }).mappings().all()
    return pickup_places

def create_reservation(token: str, data: dict):
    """
    處理建立預約請求。
    """
    m_id, active_role = get_user(token)
    if not m_id:
        return False, "Unauthorized"
    if active_role == "member":

        try:
            db.session.execute(
                text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
            new_reservation = Reservation(
                m_id=m_id,
                create_at=datetime.now(),
                is_deleted=False
            )
            db.session.add(new_reservation)
            for rd in data["rd_list"]:
                # 將字串轉為 datetime 物件 (如果傳入是字串)
                # 假設 data["rd_list"] 裡的日期是 ISO 格式字串，需要先 parse
                start_at = rd["est_start_at"]
                if isinstance(start_at, str):
                    start_at = datetime.fromisoformat(start_at)
                due_at = rd["est_due_at"]
                if isinstance(due_at, str):
                    due_at = datetime.fromisoformat(due_at)

                if not check_item_available(db.session, rd["i_id"], rd["p_id"], start_at, due_at):
                    db.session.rollback()  # 確保 rollback
                    return False, f"Item {rd['i_id']} is not available during selected time"
                cat = db.session.execute(text("""
                    SELECT item.c_id, category.c_name
                    FROM item
                    join category on item.c_id = category.c_id
                    WHERE i_id = :i_id
                """), {
                    "i_id": rd["i_id"]
                }).mappings().first()
                check_ban = db.session.execute(text("""
                    SELECT COUNT(*)
                    FROM category_ban
                    WHERE c_id = :c_id and m_id = :m_id and is_deleted = false
                """), {
                    "c_id": cat["c_id"],
                    "m_id": m_id,
                }).scalar()
                if check_ban > 0:
                    db.session.rollback()
                    return False, f"You are banned from {cat['c_name']} category"

                # 取得物品的 root category
                root_c_id = get_root_category(db.session, cat["c_id"])

                # 檢查用戶在該 root category 及其所有子類別下是否有 active contribution
                check_contribution = db.session.execute(text("""
                    SELECT contribution.i_id
                    FROM contribution
                    JOIN item ON contribution.i_id = item.i_id
                    WHERE contribution.m_id = :m_id 
                    AND contribution.is_active = true
                    AND item.c_id IN (
                        -- 找到 root category 下的所有子類別（包括 root 自己）
                        WITH RECURSIVE category_tree AS (
                            -- 起始點：root category
                            SELECT c_id FROM category WHERE c_id = :root_c_id
                            
                            UNION ALL
                            
                            -- 遞迴向下查找所有子類別
                            SELECT c.c_id 
                            FROM category c
                            JOIN category_tree ct ON c.parent_c_id = ct.c_id
                        )
                        SELECT c_id FROM category_tree
                    )
                    LIMIT 1
                    FOR UPDATE OF contribution
                """), {
                    "root_c_id": root_c_id,
                    "m_id": m_id,
                }).mappings().all()

                if len(check_contribution) > 0:
                    # 如果找到 contribution，確保它是 active 的
                    db.session.execute(text("""
                        UPDATE contribution
                        SET is_active = true
                        WHERE i_id = :i_id AND m_id = :m_id
                    """), {
                        "i_id": check_contribution[0]["i_id"],
                        "m_id": m_id,
                    })
                else:
                    db.session.rollback()
                    return False, f"Your contribution to {cat['c_name']} category (root category) is not active"
                new_reservation_detail = ReservationDetail(
                    r_id=new_reservation.r_id,
                    i_id=rd["i_id"],
                    p_id=rd["p_id"],
                    est_start_at=start_at,
                    est_due_at=due_at,
                )

                db.session.add(new_reservation_detail)
            db.session.commit()
            return True, {"reservation_id": new_reservation.r_id}
        except Exception as e:
            db.session.rollback()
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
        try:
            db.session.execute(
                text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
            check_time = db.session.execute(text("""
                SELECT est_start_at, est_due_at
                FROM reservation_detail
                WHERE r_id = :r_id
            """), {
                "r_id": r_id,
            }).mappings().all()
            for rd in check_time:
                if rd["est_start_at"] < datetime.now() + timedelta(hours=24):
                    db.session.rollback()
                    return False, "You can only cancel the reservation within 24 hours before the start time"
            rds = db.session.execute(text("""
                SELECT rd_id, i_id, c_id
                FROM reservation_detail
                join item on reservation_detail.i_id = item.i_id
                WHERE r_id = :r_id
            """), {
                "r_id": r_id,
            }).mappings().all()
            for rd in rds:
                # 取得該物品的 root category
                root_c_id = get_root_category(db.session, rd["c_id"])

                # 在該 root category 及其所有子類別下找一個 inactive 的 contribution
                inactive_contribution = db.session.execute(text("""
                    SELECT contribution.i_id
                    FROM contribution
                    JOIN item ON contribution.i_id = item.i_id
                    WHERE contribution.m_id = :m_id
                    AND contribution.is_active = false
                    AND item.c_id IN (
                        -- 找到 root category 下的所有子類別（包括 root 自己）
                        WITH RECURSIVE category_tree AS (
                            -- 起始點：root category
                            SELECT c_id FROM category WHERE c_id = :root_c_id
                            
                            UNION ALL
                            
                            -- 遞迴向下查找所有子類別
                            SELECT c.c_id 
                            FROM category c
                            JOIN category_tree ct ON c.parent_c_id = ct.c_id
                        )
                        SELECT c_id FROM category_tree
                    )
                    LIMIT 1
                """), {
                    "root_c_id": root_c_id,
                    "m_id": m_id,
                }).mappings().first()

                # 如果找到 inactive 的 contribution，將它設為 active
                if inactive_contribution:
                    db.session.execute(text("""
                        UPDATE contribution
                        SET is_active = true
                        WHERE i_id = :i_id AND m_id = :m_id
                    """), {
                        "i_id": inactive_contribution["i_id"],
                        "m_id": m_id,
                    })
            db.session.execute(text("""
                UPDATE reservation_detail
                SET is_deleted = true
                WHERE r_id = :r_id
            """), {
                "r_id": r_id,
            })
            db.session.execute(text("""
                UPDATE reservation
                SET is_deleted = true
                WHERE r_id = :r_id
            """), {
                "r_id": r_id,
            })
            db.session.commit()
            return True, "OK"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    return False, "Unauthorized"
