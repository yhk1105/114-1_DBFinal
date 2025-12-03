from app.extensions import db
from sqlalchemy import text
from app.utils.jwt_utils import get_user
from app.models.staff import Staff
from datetime import datetime
from app.models.contribution import Contribution
from app.services.contribution import change_contribution


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
                FROM staff
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
                FROM report
                WHERE s_id = :user_id and r_conclusion is null
            """),
            {"user_id": s_id}
        ).mappings().all()
        return True, {"reports": report_row}


def conclude_report(token: str, re_id: int, data: dict):
    """
    處理結案檢舉請求。
    """
    s_id, active_role = get_user(token)
    if not s_id:
        return False, {"message": "Unauthorized"}

    if active_role == "staff":
        if data["r_conclusion"] not in ["Withdraw", "Ban Category", "Delist"]:
            return False, {"message": "Invalid conclusion"}

        try:
            db.session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))

            # 1. 取得檢舉相關資訊 (增加抓取 m_id, c_id 以便後續檢查)
            # 使用 FOR UPDATE 鎖定 report、item 和 contribution，避免並發問題
            report_row = db.session.execute(text("""
                SELECT r.i_id, i.c_id, r.m_id, i.i_name
                FROM report r
                JOIN item i ON r.i_id = i.i_id
                LEFT JOIN contribution c ON c.m_id = r.m_id AND c.i_id = i.i_id
                WHERE re_id = :re_id
                FOR UPDATE OF r, i, c
            """), {"re_id": re_id}).mappings().first()

            if not report_row:
                db.session.rollback()
                return False, {"message": "Report not found"}

            # 2. 更新檢舉結案狀態
            db.session.execute(text("""
                UPDATE report
                SET r_conclusion = :r_conclusion, conclude_at = :conclude_at
                WHERE re_id = :re_id
            """),
                               {"r_conclusion": data["r_conclusion"], "conclude_at": datetime.now(), "re_id": re_id})

            target_m_id = report_row["m_id"]
            target_c_id = report_row["c_id"]
            target_i_id = report_row["i_id"]

            # 3. 處理 Ban Category
            if data["r_conclusion"] == "Ban Category":
                # 使用 ON CONFLICT 處理並發，不需要 table lock
                db.session.execute(text("""
                    INSERT INTO category_ban (s_id, c_id, m_id, ban_at, is_deleted)
                    VALUES (:s_id, :c_id, :m_id, :ban_at, false)
                    ON CONFLICT (c_id, m_id) DO UPDATE
                    SET is_deleted = false, ban_at = EXCLUDED.ban_at, s_id = EXCLUDED.s_id
                """),
                {"s_id": s_id, "c_id": target_c_id, "m_id": target_m_id, "ban_at": datetime.now()})
            deleted_reservations = []
            # 4. 處理 Delist 或 Ban Category (都需要下架商品)
            if data["r_conclusion"] in ["Delist", "Ban Category"]:
                # A. 更新商品狀態
                db.session.execute(text("""
                    UPDATE item
                    SET status = 'Not reservable'
                    WHERE i_id = :i_id
                """), {"i_id": target_i_id})

                # B. 【新增】同步將 Contribution 設為無效
                # 如果物品被下架，它就不該再算作有效的 Contribution
                change_contribution(db.session, target_m_id, target_i_id)

                # C. 【新增】清理尚未取貨的預約 (Pending Reservations)
                # 找出該使用者在該類別下，且尚未產生 Loan (未取貨) 的預約
                deleted_reservations = db.session.execute(text("""
                    UPDATE reservation
                    SET is_deleted = true
                    WHERE m_id = :m_id
                    AND r_id IN (
                        SELECT r.r_id
                        FROM reservation r
                        JOIN reservation_detail rd ON r.r_id = rd.r_id
                        JOIN item i ON rd.i_id = i.i_id
                        LEFT JOIN loan l ON rd.rd_id = l.rd_id
                        WHERE r.m_id = :m_id
                        AND i.c_id = :c_id
                        AND l.l_id IS NULL -- 沒有 Loan 代表還沒取貨
                        AND r.is_deleted = false
                    )
                    RETURNING r_id
                """), {"m_id": target_m_id, "c_id": target_c_id}).mappings().all()

            # 5. 檢查是否有正在進行中的借用 (Active Loans) 以便回傳警示
            active_loans = db.session.execute(text("""
                SELECT l.l_id, i.i_name
                FROM loan l
                JOIN reservation_detail rd ON l.rd_id = rd.rd_id
                JOIN reservation r ON rd.r_id = r.r_id
                JOIN item i ON rd.i_id = i.i_id
                LEFT JOIN loan_event le_return ON l.l_id = le_return.l_id AND le_return.event_type = 'Return'
                WHERE r.m_id = :m_id
                AND i.c_id = :c_id
                AND le_return.timestamp IS NULL -- 沒有歸還紀錄
            """), {"m_id": target_m_id, "c_id": target_c_id}).mappings().all()

            db.session.commit()

            # 6. 建構回傳訊息
            msg = "Success"
            if deleted_reservations:
                msg += f", canceled {len(deleted_reservations)} pending reservations"
            if active_loans:
                msg += f", WARNING: User has {len(active_loans)} active loans (Items: {', '.join([row['i_name'] for row in active_loans])})"

            return True, {"message": msg}
        except Exception as e:
            db.session.rollback()
            return False, {"message": str(e)}

    return False, {"message": "Unauthorized role"}

def get_not_deal_verification(token: str):
    """
    處理取得未處理的驗證資訊請求。

    接收 JWT Token，
    取得未處理的驗證資訊後回傳。
    """
    s_id, active_role = get_user(token)
    if not s_id:
        return False, "Unauthorized"
    if active_role == "staff":
        verification_row = db.session.execute(text("""
            SELECT iv_id, i_id, v_conclusion, create_at
            FROM item_verification
            WHERE s_id = :s_id and v_conclusion = 'Pending'
        """),
        {"s_id": s_id}
        ).mappings().all()
        if not verification_row:
            return False, {"message": "No pending verifications"}
        return True, {"verifications": verification_row}
    return False, "Unauthorized"

def conclude_verification(token: str, iv_id: int, data: dict):
    """
    處理結案驗證請求。
    """
    s_id, active_role = get_user(token)
    if not s_id:
        return False, {"message": "Unauthorized"}
    if active_role == "staff":
        try:
            db.session.execute(text("""
                SET TRANSACTION ISOLATION LEVEL REPEATABLE READ
            """))
            db.session.execute(text("""
                UPDATE item_verification
                SET v_conclusion = :v_conclusion, conclude_at = :conclude_at
                WHERE iv_id = :iv_id
            """),
            {"v_conclusion": data["v_conclusion"], "conclude_at": datetime.now(), "iv_id": iv_id}
            )
            result = db.session.execute(text("""
                    SELECT m_id, item.i_id 
                    FROM item_verification
                    join item on item_verification.i_id = item.i_id
                    where item_verification.iv_id = :iv_id
                """),
                {"iv_id": iv_id}
                ).mappings().first()
            if not result:
                db.session.rollback()
                return False, {"message": "Item verification not found"}
            if data["v_conclusion"] == "Pass":
                db.session.execute(text("""
                    update contribution
                    set is_active = true
                    where m_id = :m_id and i_id = :i_id
                """),
                {"m_id": result["m_id"], "i_id": result["i_id"]}
                )
            elif data["v_conclusion"] == "Fail":
                check_have_contribution = db.session.execute(text("""
                    SELECT COUNT(*) FROM contribution
                    WHERE m_id = :m_id and i_id = :i_id
                """),
                {"m_id": result["m_id"], "i_id": result["i_id"]}
                ).scalar()
                if check_have_contribution != 0:
                    db.session.execute(text("""
                        UPDATE contribution
                        SET is_active = false
                        WHERE m_id = :m_id and i_id = :i_id
                    """),
                    {"m_id": result["m_id"], "i_id": result["i_id"]}
                    )
            db.session.commit()

            return True, {"message": "Success"}
        except Exception as e:
            return False, {"message": str(e)}
    return False, {"message": "Unauthorized"}