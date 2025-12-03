from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.utils.jwt_utils import get_user
from app.models.review import Review


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
                with owner_rate as(
                    SELECT owner.m_id, AVG(review.score) as owner_rate
                    FROM member as owner
                    join review on owner.m_id = review.reviewee_id
                    join loan on review.l_id = loan.l_id
                    join reservation on loan.rd_id = reservation.rd_id
                    join reservation_detail on reservation.r_id = reservation_detail.r_id
                    join item on reservation_detail.i_id = item.i_id
                    join category on item.c_id = category.c_id
                    WHERE owner.m_id = :m_id
                    group by owner.m_id
                ),
                borrower_rate as(
                    SELECT borrower.m_id, AVG(review.score) as borrower_rate
                    FROM member as borrower
                    join review on borrower.m_id = review.reviewee_id
                    join loan on review.l_id = loan.l_id
                    join reservation on loan.rd_id = reservation.rd_id and reservation.m_id = :m_id
                    where borrower.m_id = :m_id
                    group by borrower.m_id
                )
                SELECT m_name, m_mail, owner_rate, borrower_rate
                FROM member
                join owner_rate on member.m_id = owner_rate.m_id
                join borrower_rate on member.m_id = borrower_rate.m_id
                WHERE m_id = :m_id
            """),
            {"m_id": user_id}).mappings().first()
        return True, {"name": member_row["m_name"], "email": member_row["m_mail"], "owner_rate": member_row["owner_rate"], "borrower_rate": member_row["borrower_rate"]}
    elif active_role == "staff":
        staff_row = db.session.execute(
            text("""
                SELECT s_name, s_mail
                FROM staff
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
                FROM item
                WHERE m_id = :m_id
            """),
            {"m_id": user_id}).mappings().all()
        return True, {"items": items_row}
    else:
        return False, "Only members can get items"

def find_items(r_id: int):
    """
    處理取得預約物品請求。

    接收預約 ID，
    取得預約物品後回傳。
    """
    items_row = db.session.execute(
        text("""
            SELECT i_name
            FROM reservation_detail
            join item on reservation_detail.i_id = item.i_id
            WHERE reservation_detail.r_id = :r_id
        """),
        {"r_id": r_id}).mappings().all()
    item_list = []
    for item in items_row:
        item_list.append(item["i_name"])
    return item_list
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
                SELECT r_id, create_at
                FROM reservation
                WHERE m_id = :m_id
                and is_deleted = false
                order by create_at desc
            """),
            {"m_id": user_id}).mappings().all()
        for reservation in reservations_row:
            reservation["items"] = find_items(reservation["r_id"])
            
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
                FROM reservation_detail
                join item on reservation_detail.i_id = item.i_id
                join reservation on reservation_detail.r_id = reservation.r_id
                join pick_up_place on reservation_detail.p_id = pick_up_place.p_id
                WHERE r_id = :r_id and reservation.m_id = :m_id
                and reservation.is_deleted = false
                order by est_start_at asc
            """),
            {"r_id": r_id, "m_id": member_id}).mappings().all()
        return True, {"reservation_details": reservation_detail_row}
    else:
        return False, "Only members can get reservation detail"


def get_reviewable_items(token: str):
    """
    處理取得使用者可評論的物品請求。

    接收 JWT Token，
    取得使用者可評論的物品後回傳。
    """

    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        reviewable_items_row = db.session.execute(
            text("""
                SELECT 
                CASE 
                        WHEN r.m_id = :m_id THEN "owner" 
                        ELSE "borrower" 
                    END AS review_target,
                    l.l_id,
                    i.i_id,
                    i.i_name,
                    CASE 
                        WHEN r.m_id = :m_id THEN owner.m_name 
                        ELSE borrower.m_name 
                    END AS object_name,
                    l.actual_return_at
                FROM loan l
                JOIN reservation_detail rd ON l.rd_id = rd.rd_id
                JOIN reservation r ON rd.r_id = r.r_id
                JOIN item i ON rd.i_id = i.i_id
                JOIN member borrower ON r.m_id = borrower.m_id
                JOIN member owner ON i.m_id = owner.m_id
                WHERE 
                    l.actual_return_at IS NOT NULL
                    AND (r.m_id = :m_id OR i.m_id = :m_id)
                    AND NOT EXISTS (
                        SELECT 1 
                        FROM review rv 
                        WHERE rv.l_id = l.l_id 
                        AND rv.reviewer_id = :m_id
                    )
            """),
            {"m_id": user_id}).mappings().all()
        return True, {"reviewable_items": reviewable_items_row}
    else:
        return False, "Only members can get reviewable items"


def review_item(token: str, l_id: int, data: dict):
    """
    處理評論物品請求。

    接收 JWT Token 和預約 ID，
    評論物品後回傳。
    """

    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"

    if active_role != "member":
        return False, "Only members can review items"
    try:
        # 1. 查詢 Loan 資訊，確認使用者是否有權評論，並找出 reviewee_id
        loan_info = db.session.execute(
        text("""
            SELECT 
                r.m_id AS borrower_id,
                i.m_id AS owner_id,
                l.actual_return_at
            FROM loan l
            JOIN reservation_detail rd ON l.rd_id = rd.rd_id
            JOIN reservation r ON rd.r_id = r.r_id
            JOIN item i ON rd.i_id = i.i_id
            WHERE l.l_id = :l_id
        """),
        {"l_id": l_id}
        ).mappings().first()
        if not loan_info:
            return False, "Loan not found"

        if not loan_info["actual_return_at"]:
            return False, "Item has not been returned yet"

        borrower_id = loan_info["borrower_id"]
        owner_id = loan_info["owner_id"]

        # 2. 判斷使用者身份並決定評論對象
        if user_id == borrower_id:
            reviewee_id = owner_id
        elif user_id == owner_id:
            reviewee_id = borrower_id
        else:
            return False, "You are not related to this loan"

        # 3. 檢查是否已經評論過 (防止重複評論)
        existing_review = db.session.execute(
            text("""
                SELECT 1 FROM review r
                WHERE l_id = :l_id AND reviewer_id = :reviewer_id
            """),
            {"l_id": l_id, "reviewer_id": user_id}
        ).first()

        if existing_review:
            return False, "You have already reviewed this loan"
        # 4. 新增評論
        new_review = Review(
            score=data["score"],
            comment=data["comment"],
            reviewer_id=user_id,
            reviewee_id=reviewee_id,
            l_id=l_id
        )
        db.session.add(new_review)

        db.session.commit()
        return True, {"review_id": new_review.review_id}
    except IntegrityError:
        db.session.rollback()
        # 這裡就代表 UNIQUE(l_id, reviewer_id) 被觸發 → 使用者之前已經評過
        return False, "You have already reviewed this loan"
    except Exception as e:
        db. session.rollback()
        return False, str(e)


def get_contributions_and_bans(token: str):
    """
    處理取得使用者貢獻請求。

    接收 JWT Token，
    取得使用者貢獻後回傳。
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        contributions_row = db.session.execute(
            text("""
                SELECT item.i_id, item.i_name, contribution.is_active, category.c_id, category.c_name
                FROM contribution
                join item on contribution.i_id = item.i_id
                join category on item.c_id = category.c_id
                WHERE contribution.m_id = :m_id
            """),
            {"m_id": user_id}).mappings().all()
        bans_row = db.session.execute(
            text("""
                SELECT category_ban.c_id, category.c_name
                FROM category_ban
                join category on category_ban.c_id = category.c_id
                WHERE m_id = :m_id
            """),
            {"m_id": user_id}).mappings().all()
        return True, {"contributions": contributions_row, "bans": bans_row}
    else:
        return False, "Only members can get contributions and bans"