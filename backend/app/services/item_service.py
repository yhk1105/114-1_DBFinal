from datetime import datetime
from sqlalchemy import text
from app.extensions import db
from app.utils.jwt_utils import get_user
from app.models.item import Item
from app.models.contribution import Contribution
from app.models.report import Report
from sqlalchemy.exc import OperationalError # 用來抓取 Serialization Failure
import time
import random
from app.models.item_verification import ItemVerification
from app.services.contribution import change_contribution
from app.models.item_pick import ItemPick

def pick_a_staff():
    """
    隨機選擇員工後回傳。
    """
    staff_row = db.session.execute(
        text("""
            SELECT s_id FROM our_things.staff
            WHERE role = 'Employee' and is_deleted = false
        """)).mappings().all()
    random_staff_id = random.choice(staff_row)
    return random_staff_id["s_id"]

def get_item_detail(i_id: int):
    """
    處理取得物品詳細資訊請求。

    接收 JWT Token 和物品 ID，
    取得物品詳細資訊後回傳。
    """

    item_row = db.session.execute(
        text("""
            SELECT i_name, status, description, out_duration, c_id
            FROM our_things.item
            WHERE i_id = :i_id
        """),
        {"i_id": i_id}).mappings().first()
    if not item_row:
        return False, "Item not found"
    return True, {"item": item_row}


def get_category_items(c_id: int):
    """
    處理取得特定類別物品請求。

    接收 JWT Token 和類別 ID，
    取得特定類別物品後回傳。
    """
    items_row = db.session.execute(
        text("""
            SELECT i_id, i_name, status, description, out_duration, c_id
            FROM our_things.item
            WHERE c_id = :c_id
        """),
        {"c_id": c_id}).mappings().all()
    if not items_row:
        return False, "Items not found"
    return True, {"items": items_row}


def get_item_borrowed_time(i_id: int):
    """
    處理取得物品借用時間請求。

    接收物品 ID，
    取得物品借用時間後回傳。
    """
    today = datetime.now().date()
    borrowed_time_row = db.session.execute(
        text("""
            SELECT est_start_at, est_due_at
            FROM our_things.reservation_detail
            WHERE i_id = :i_id and (est_start_at >= :today or est_due_at >= :today)"""
             ),
        {"i_id": i_id, "today": today}).mappings().all()
    if not borrowed_time_row:
        return False, "No borrowed time"
    return True, {"borrowed_time": borrowed_time_row}


def upload_item(token: str, data: dict):
    """
    處理上傳新物品請求。

    接收 JWT Token 和物品資訊，
    上傳新物品後回傳。
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        session = db.session
        try:
            session.connection().execution_options(
                isolation_level="SERIALIZABLE"
            )
            session.begin()
            item_row = Item( i_name=data["i_name"], status="Not verified",
                        description=data["description"], out_duration=data["out_duration"], m_id=user_id, c_id=data["c_id"])
            for p_id in data["p_id_list"]:
                item_pick_row = ItemPick(i_id=item_row.i_id, p_id=p_id)
                session.add(item_pick_row)
            session.add(item_row)
            contribution_row = Contribution(u_id=user_id, i_id=item_row.i_id, is_active=False)
            session.add(contribution_row)
            session.commit()
            return True, {"item_id": item_row.i_id, "name": data["i_name"], "status": data["status"]}
        except Exception as e:
            session.rollback()
            return False, str(e)
        return True, {"item_id": item_row.i_id, "name": data["i_name"], "status": data["status"]}


def update_item(token: str, i_id: int, data: dict):
    """
    處理更新物品請求。

    接收 JWT Token 和物品 ID 和物品資訊，
    更新物品後回傳。
    pickup 
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"

    if active_role == "member":
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 1. 設定 Serializable
                db.session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
                
                # 2. 執行你的查詢 (拿掉 FOR UPDATE，讓 Serializable 幫你管)
                # 注意：這裡不需要再鎖 contribution 了，Serializable 會監控讀取依賴
                
                check_owner = db.session.execute(
                    text("""
                        SELECT u_id FROM our_things.item
                        WHERE i_id = :i_id and m_id = :user_id
                    """), # 移除了 FOR UPDATE
                    {"i_id": i_id, "user_id": user_id}).mappings().first()
                
                if not check_owner:
                    return False, "Item not found"

                item_original = db.session.execute(
                    text("""
                            SELECT i_id, i_name, status, description, out_duration, c_id, is_active FROM our_things.item
                            join our_things.contribution on item.i_id = contribution.i_id
                            WHERE item.i_id = :i_id and item.m_id = :user_id
                        """),
                    {"i_id": i_id, "user_id": user_id}).mappings().first()
                if item_original["status"] == "Borrowed":
                    return False, "Item is borrowed, cannot be edited"
                if data.get("i_name"):  # update name
                    item_row = db.session.execute(
                        text("""
                            UPDATE our_things.item
                            SET i_name = :i_name
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "i_name": data["i_name"]}).mappings().first()
                # update status
                if data.get("status") and data["status"] != item_original["status"]:
                    if data["status"] == "Not reservable":
                        if item_original["status"] == "Borrowed":
                            return False, "Item is borrowed"
                        if item_original["is_active"] == False:
                            change_contribution(user_id, i_id)
                    elif data["status"] == "Reservable":
                        item_row = db.session.execute(
                            text("""
                                UPDATE our_things.contribution
                                SET is_active = true
                                WHERE i_id = :i_id
                            """),
                            {"i_id": i_id}).mappings().first()
                    item_row = db.session.execute(
                        text("""
                            UPDATE our_things.item
                            SET status = :status
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "status": data["status"]}).mappings().first()
                if data.get("description"):  # update description
                    item_row = db.session.execute(
                        text("""
                            UPDATE our_things.item
                            SET description = :description
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "description": data["description"]}).mappings().first()
                if data.get("out_duration"):  # update out_duration
                    item_row = db.session.execute(
                        text("""
                            UPDATE our_things.item
                            SET out_duration = :out_duration
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "out_duration": data["out_duration"]}).mappings().first()
                if data.get("c_id"):  # update c_id

                    check_category_contribution = db.session.execute(
                        text("""
                            SELECT COUNT(*) 
                            FROM our_things.contribution
                            join our_things.item on contribution.i_id = item.i_id
                            WHERE m_id = :user_id and item.c_id = :item_original_c_id and is_active = true
                        """),
                        {"user_id": user_id, "item_original_c_id": item_original["c_id"]}).mappings().first()
                    if check_category_contribution == 0:
                        return False, "Cannot change category"
                    item_row = db.session.execute(
                        text("""
                            UPDATE our_things.item
                            SET c_id = :c_id
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "c_id": data["c_id"]}).mappings().first()
                item_row = db.session.execute(
                    text("""
                        SELECT i_id, i_name, status, description, out_duration, c_id
                        FROM our_things.item
                        WHERE i_id = :i_id and m_id = :user_id
                    """),
                    {"i_id": i_id, "user_id": user_id}).mappings().first()
                db.session.commit()
                return True, {"item": item_row}

            except OperationalError as e:
                db.session.rollback()
                # 檢查是不是 Serialization Failure (PostgreSQL error code 40001)
                # 或是 Deadlock
                if "could not serialize access" in str(e) or "deadlock detected" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(0.1 * (attempt + 1)) # 等一下再重試 (Exponential Backoff)
                        continue
                    else:
                        return False, "System busy, please try again later"
                raise e # 如果是其他錯誤，直接噴錯
            except Exception as e:
                db.session.rollback()
                return False, str(e)

def report_item(token: str, i_id: int, data: dict):
    """
    處理檢舉物品請求。

    接收 JWT Token 和物品 ID 和檢舉資訊，
    檢舉物品後回傳。
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        staff_id = pick_a_staff()
        if not staff_id:
            return False, "No staff available"
        report_row = Report( m_id=user_id, i_id=i_id, comment=data["comment"], create_at=datetime.now(),s_id = staff_id)
        db.session.add(report_row)
        db.session.commit()
        return True, {"report_id": report_row.re_id}

def verify_item(token: str, i_id: int):
    """
    處理驗證物品請求。

    接收 JWT Token 和物品 ID 和驗證資訊，
    驗證物品後回傳。
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":
        check_user = db.session.execute(
            text("""
                SELECT u_id FROM our_things.item
                WHERE i_id = :i_id and m_id = :user_id
            """),
            {"i_id": i_id, "user_id": user_id}).mappings().first()
        if not check_user:
            return False, "Item not found"
        staff_id = pick_a_staff()
        if not staff_id:
            return False, "No staff available"
        item_verification_row = ItemVerification(i_id=i_id, s_id=staff_id, create_at=datetime.now(), v_conclusion="Pending")
        db.session.add(item_verification_row)
        db.session.commit()
        return True, {"item_verification_id": item_verification_row.iv_id}