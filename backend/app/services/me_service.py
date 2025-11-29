from sqlalchemy import text
from app.extensions import db
from app.utils.jwt_utils import get_user


def get_profile_service(token: str):
    """
    處理取得使用者 profile 請求。
    
    接收 JWT Token，
    取得使用者 profile 後回傳。
    """

    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        member_row = db.session.execute(
            text("""
                SELECT m_name, m_mail
                FROM our_things.member
                WHERE m_id = :m_id
            """),
            {"m_id": user_id}).mappings().first()
        return True, {"name": member_row["m_name"], "email": member_row["m_mail"]}
    elif active_role == "staff":
        staff_row = db.session.execute(
            text("""
                SELECT s_name, s_mail
                FROM our_things.staff
                WHERE s_id = :s_id
            """),
            {"s_id": user_id}).mappings().first()
        return True, {"name": staff_row["s_name"], "email": staff_row["s_mail"]}

def get_my_items(token: str):
    """
    處理取得使用者物品請求。
    
    接收 JWT Token，
    取得使用者物品後回傳。
    """

    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        items_row = db.session.execute(
            text("""
                SELECT i_id, i_name, status, description, out_duration, c_id
                FROM our_things.item
                WHERE m_id = :m_id
            """),
            {"m_id": user_id}).mappings().all()
        return True, {"items": items_row}
    else:
        return False, "Only members can get items"

def get_my_reservations(token: str):
    """
    處理取得使用者預約請求。
    
    接收 JWT Token，
    取得使用者預約後回傳。
    """

    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        reservations_row = db.session.execute(
            text("""
                SELECT r_id, r_status, r_created_at
                FROM our_things.reservation
                WHERE m_id = :m_id
                and is_deleted = false
                order by r_created_at desc
            """),
            {"m_id": user_id}).mappings().all()
        return True, {"reservations": reservations_row}
    else:
        return False, "Only members can get reservations"

def get_reservation_detail(token: str, r_id: int):
    """
    處理取得使用者預約詳細資訊請求。
    
    接收 JWT Token 和預約 ID，
    取得使用者預約詳細資訊後回傳。
    """

    member_id, active_role = get_user(token)
    if not member_id:
        return False, "Unauthorized"
    if active_role == "member":
        reservation_detail_row = db.session.execute(
            text("""
                SELECT est_start_at, est_due_at, i_name, p_name
                FROM our_things.reservation_detail
                join our_things.item on reservation_detail.i_id = item.i_id
                join our_things.reservation on reservation_detail.r_id = reservation.r_id
                join our_things.pick_up_place on reservation_detail.p_id = pick_up_place.p_id
                WHERE r_id = :r_id and reservation.m_id = :m_id
                and reservation.is_deleted = false
                order by est_start_at asc
            """),
            {"r_id": r_id, "m_id": member_id}).mappings().first()
        return True, {"reservation_detail": reservation_detail_row}
    else:
        return False, "Only members can get reservation detail"

