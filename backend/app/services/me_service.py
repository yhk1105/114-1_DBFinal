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
                    SELECT i.m_id, AVG(rv.score) as owner_rate
                    FROM review rv
                    join loan l on rv.l_id = l.l_id
                    join reservation_detail rd on l.rd_id = rd.rd_id
                    join item i on rd.i_id = i.i_id
                    WHERE rv.reviewee_id = :m_id AND i.m_id = :m_id AND rv.is_deleted = false
                    group by i.m_id
                ),
                borrower_rate as(
                    SELECT r.m_id, AVG(rv.score) as borrower_rate
                    FROM review rv
                    join loan l on rv.l_id = l.l_id
                    join reservation_detail rd on l.rd_id = rd.rd_id
                    join reservation r on rd.r_id = r.r_id
                    WHERE rv.reviewee_id = :m_id AND r.m_id = :m_id AND rv.is_deleted = false
                    group by r.m_id
                )
                SELECT m.m_name, m.m_mail, 
                       owner_rate.owner_rate, 
                       borrower_rate.borrower_rate
                FROM member m
                LEFT JOIN owner_rate on m.m_id = owner_rate.m_id
                LEFT JOIN borrower_rate on m.m_id = borrower_rate.m_id
                WHERE m.m_id = :m_id
            """),
            {"m_id": user_id}).mappings().first()

        if not member_row:
            return False, "Member not found"

        member_dict = dict(member_row)
        # 確保評分是 float 或 None
        owner_rate = float(
            member_dict["owner_rate"]) if member_dict["owner_rate"] is not None else None
        borrower_rate = float(
            member_dict["borrower_rate"]) if member_dict["borrower_rate"] is not None else None

        return True, {
            "name": member_dict["m_name"],
            "email": member_dict["m_mail"],
            "owner_rate": owner_rate,
            "borrower_rate": borrower_rate
        }
    elif active_role == "staff":
        staff_row = db.session.execute(
            text("""
                SELECT s_name, s_mail
                FROM staff
                WHERE s_id = :s_id
            """),
            {"s_id": user_id}).mappings().first()
        staff_dict = dict(staff_row)
        return True, {"name": staff_dict["s_name"], "email": staff_dict["s_mail"]}


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
        # 轉換為字典列表
        items_list = [dict(row) for row in items_row]
        return True, {"items": items_list}
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
                SELECT r.r_id, r.create_at
                FROM reservation r
                join reservation_detail rd on r.r_id = rd.r_id
                join loan l on rd.rd_id = l.rd_id
                WHERE r.m_id = :m_id and l.actual_return_at is null
                and r.is_deleted = false
                order by r.create_at desc
            """),
            {"m_id": user_id}).mappings().all()
        # 轉換為字典列表
        reservations_list = [dict(row) for row in reservations_row]
        for reservation in reservations_list:
            reservation["items"] = find_items(reservation["r_id"])

        return True, {"reservations": reservations_list}
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
                SELECT rd.est_start_at, rd.est_due_at, i.i_name, p.p_name
                FROM reservation_detail rd
                join item i on rd.i_id = i.i_id
                join reservation r on rd.r_id = r.r_id
                join pick_up_place p on rd.p_id = p.p_id
                WHERE rd.r_id = :r_id and r.m_id = :m_id
                and r.is_deleted = false
                order by est_start_at asc
            """),
            {"r_id": r_id, "m_id": member_id}).mappings().all()
        # 轉換為字典列表
        details_list = [dict(row) for row in reservation_detail_row]
        return True, {"reservation_details": details_list}
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
        # 轉換為字典列表
        reviewable_items_list = [dict(row) for row in reviewable_items_row]
        return True, {"reviewable_items": reviewable_items_list}
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
            l_id=l_id,
            is_deleted=False
        )
        db.session.add(new_review)

        db.session.commit()
        return True, {"review_id": new_review.review_id}

    except Exception as e:
        db.session.rollback()
        print(e)
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
        # 轉換為字典列表
        contributions_list = [dict(row) for row in contributions_row]
        bans_list = [dict(row) for row in bans_row]
        return True, {"contributions": contributions_list, "bans": bans_list}
    else:
        return False, "Only members can get contributions and bans"
