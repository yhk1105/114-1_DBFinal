from datetime import datetime
from sqlalchemy import text
from app.extensions import db
from app.utils.jwt_utils import get_user
from app.models.item import Item
from app.models.contribution import Contribution
from app.models.report import Report
from sqlalchemy.exc import OperationalError  # 用來抓取 Serialization Failure
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
            SELECT s_id FROM staff
            WHERE role = 'Employee' and is_deleted = false
        """)).mappings().all()
    random_staff = random.choice(staff_row)
    return random_staff["s_id"]


def get_item_detail(i_id: int):
    """
    處理取得物品詳細資訊請求。

    接收 JWT Token 和物品 ID，
    取得物品詳細資訊後回傳。
    """

    item_row = db.session.execute(
        text("""
            SELECT i_name, status, description, out_duration, c_id
            FROM item
            WHERE i_id = :i_id
        """),
        {"i_id": i_id}).mappings().first()
    if not item_row:
        return False, "Item not found"
    return True, {"item": dict(item_row)}


def get_category_items(c_id: int):
    """
    處理取得特定類別物品請求。
    使用 DFS（深度優先搜尋）遞迴取得該類別及其所有子類別下的物品。

    接收類別 ID，
    取得該類別及其所有子類別下的物品後回傳。
    """
    # 使用 WITH RECURSIVE 遞迴查詢所有子類別（包括自己）
    items_row = db.session.execute(
        text("""
            WITH RECURSIVE category_tree AS (
                -- 起始點：給定的類別
                SELECT c_id
                FROM category
                WHERE c_id = :c_id
                
                UNION ALL
                
                -- 遞迴向下查找所有子類別
                SELECT c.c_id
                FROM category c
                INNER JOIN category_tree ct ON c.parent_c_id = ct.c_id
            )
            SELECT i.i_id, i.i_name, i.status, i.description, i.out_duration, i.c_id
            FROM item i
            INNER JOIN category_tree ct ON i.c_id = ct.c_id
        """),
        {"c_id": c_id}).mappings().all()

    items_list = [dict(row) for row in items_row]
    return True, {"items": items_list}


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
            FROM reservation_detail
            WHERE i_id = :i_id and (est_start_at >= :today or est_due_at >= :today)"""
             ),
        {"i_id": i_id, "today": today}).mappings().all()
    if not borrowed_time_row:
        return False, "No borrowed time"
    borrowed_time_list = [dict(row) for row in borrowed_time_row]
    return True, {"borrowed_time": borrowed_time_list}


def upload_item(token: str, data: dict):
    """
    處理上傳新物品請求。

    接收 JWT Token 和物品資訊，
    上傳新物品後回傳。
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role != "member":
        return False, "Only members can upload items"

    try:
        # 驗證必要欄位
        if not data.get("i_name") or not data.get("description") or not data.get("out_duration") or not data.get("c_id"):
            return False, "Missing required fields"

        if not data.get("p_id_list") or len(data["p_id_list"]) == 0:
            return False, "At least one pickup place is required"

        item_row = Item(i_name=data["i_name"], status="Not verified",
                        description=data["description"], out_duration=data["out_duration"], m_id=user_id, c_id=data["c_id"])
        db.session.add(item_row)
        db.session.flush()

        for p_id in data["p_id_list"]:
            item_pick_row = ItemPick(i_id=item_row.i_id, p_id=p_id)
            db.session.add(item_pick_row)

        contribution_row = Contribution(
            m_id=user_id, i_id=item_row.i_id, is_active=False)
        db.session.add(contribution_row)
        db.session.commit()
        return True, {"item_id": item_row.i_id, "name": data["i_name"], "status": item_row.status}
    except Exception as e:
        db.session.rollback()
        print(e)
        return False, str(e)


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
                db.session.execute(
                    text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
                # 2. 執行你的查詢 (拿掉 FOR UPDATE，讓 Serializable 幫你管)
                # 注意：這裡不需要再鎖 contribution 了，Serializable 會監控讀取依賴

                check_owner = db.session.execute(
                    text("""
                        SELECT m_id FROM item
                        WHERE i_id = :i_id and m_id = :user_id
                    """),  # 移除了 FOR UPDATE
                    {"i_id": i_id, "user_id": user_id}).mappings().first()

                if not check_owner:
                    db.session.rollback()
                    return False, "Item not found"

                item_original = db.session.execute(
                    text("""
                            SELECT item.i_id, item.i_name, item.status, item.description, item.out_duration, item.c_id, contribution.is_active FROM item
                            join contribution on item.i_id = contribution.i_id
                            WHERE item.i_id = :i_id and item.m_id = :user_id
                            FOR UPDATE
                        """),
                    {"i_id": i_id, "user_id": user_id}).mappings().first()
                if item_original["status"] == "Borrowed":
                    db.session.rollback()
                    return False, "Item is borrowed, cannot be edited"

                # 追蹤是否有任何更新（用於判斷是否需要重新審核）
                has_updates = False

                if data.get("i_name"):  # update name
                    has_updates = True
                    db.session.execute(
                        text("""
                            UPDATE item
                            SET i_name = :i_name
                            WHERE i_id = :i_id and m_id = :user_id
                            
                        """),
                        {"i_id": i_id, "user_id": user_id, "i_name": data["i_name"]})
                # update status
                if item_original.get("status") != "Not verified" and data.get("status") and data["status"] != item_original["status"]:
                    if data["status"] == "Not reservable":
                        if item_original["status"] == "Borrowed":
                            db.session.rollback()
                            return False, "Item is borrowed"
                        if item_original["is_active"] is False:
                            ok = change_contribution(db.session, user_id, i_id)
                            if not ok:
                                db.session.rollback()
                                return False, "Cannot change contribution"
                        db.session.execute(
                            text("""
                                UPDATE item
                                SET status = :status
                                WHERE i_id = :i_id and m_id = :user_id
                            """),
                            {"i_id": i_id, "user_id": user_id, "status": "Not reservable"})

                    elif data["status"] == "Reservable":  # 他要重新上架的話需要重新認證
                        db.session.execute(
                            text("""
                                UPDATE contribution
                                SET is_active = False
                                WHERE i_id = :i_id
                            """),
                            {"i_id": i_id})
                        db.session.execute(
                            text("""
                                UPDATE item
                                SET status = :status
                                WHERE i_id = :i_id and m_id = :user_id
                            """),
                            {"i_id": i_id, "user_id": user_id, "status": "Not verified"})
                        check_ban = db.session.execute(
                            text("""
                                SELECT is_banned FROM member
                                WHERE m_id = :user_id
                            """),
                            {"user_id": user_id}).mappings().first()
                        if check_ban["is_banned"]:
                            db.session.rollback()
                            return False, "Member is banned"
                if data.get("description"):  # update description
                    has_updates = True
                    db.session.execute(
                        text("""
                            UPDATE item
                            SET description = :description
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "description": data["description"]})
                if data.get("out_duration"):  # update out_duration
                    has_updates = True
                    db.session.execute(
                        text("""
                            UPDATE item
                            SET out_duration = :out_duration
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "out_duration": data["out_duration"]})
                if data.get("c_id"):  # update c_id
                    has_updates = True
                    if item_original['status'] =="reservable":
                        ok = change_contribution(db.session, user_id, i_id)
                        if not ok:
                            db.session.rollback()
                            return False, "Cannot change contribution"
                    db.session.execute(
                        text("""
                            UPDATE item
                            SET c_id = :c_id
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id, "c_id": data["c_id"]})
                if data.get("p_id_list"):
                    has_updates = True
                    # 取得目前資料庫中該 item 的所有 pick records
                    existing_picks = db.session.execute(
                        text("""
                            SELECT p_id, is_deleted FROM item_pick
                            WHERE i_id = :i_id
                        """),
                        {"i_id": i_id}).mappings().all()
                    existing_p_ids = {
                        pick["p_id"]: pick for pick in existing_picks}
                    new_p_id_list = data["p_id_list"]

                    # 檢查每個新的 p_id
                    for p_id in new_p_id_list:
                        if p_id in existing_p_ids:
                            # 如果本來就有，且目前是不活躍 (is_active=False)，則設為 True
                            if not existing_p_ids[p_id]["is_deleted"]:
                                db.session.execute(
                                    text("""
                                        UPDATE item_pick
                                        SET is_deleted = False
                                        WHERE i_id = :i_id and p_id = :p_id
                                    """),
                                    {"i_id": i_id, "p_id": p_id})
                        else:
                            # 如果本來沒有，則新增
                            new_pick = ItemPick(
                                i_id=i_id, p_id=p_id)
                            db.session.add(new_pick)

                    # 檢查是否有被移除的 p_id (在資料庫中有，但在新清單中沒有)
                    for p_id, pick in existing_p_ids.items():
                        if p_id not in new_p_id_list:
                            db.session.execute(
                                text("""
                                    UPDATE item_pick
                                    SET is_deleted = True
                                    WHERE i_id = :i_id and p_id = :p_id
                                """),
                                {"i_id": i_id, "p_id": p_id})

                # 如果物品狀態是 "Not reservable" 且用戶進行了任何更新，則改回 "Not verified" 並重置審核狀態
                if item_original["status"] == "Not reservable" and has_updates:
                    # 將 contribution 的 is_active 設為 False（需要重新審核）
                    db.session.execute(
                        text("""
                            UPDATE contribution
                            SET is_active = False
                            WHERE i_id = :i_id
                        """),
                        {"i_id": i_id})
                    # 將狀態改回 "Not verified"
                    db.session.execute(
                        text("""
                            UPDATE item
                            SET status = 'Not verified'
                            WHERE i_id = :i_id and m_id = :user_id
                        """),
                        {"i_id": i_id, "user_id": user_id})

                item_row = db.session.execute(
                    text("""
                        SELECT i_id, i_name, status, description, out_duration, c_id
                        FROM item
                        WHERE i_id = :i_id and m_id = :user_id
                    """),
                    {"i_id": i_id, "user_id": user_id}).mappings().first()
                db.session.commit()
                item_row = dict(item_row)
                return True, {"item": item_row}

            except OperationalError as e:
                db.session.rollback()
                # 檢查是不是 Serialization Failure (PostgreSQL error code 40001)
                # 或是 Deadlock
                if "could not serialize access" in str(e) or "deadlock detected" in str(e):
                    if attempt < max_retries - 1:
                        # 等一下再重試 (Exponential Backoff)
                        time.sleep(0.1 * (attempt + 1))
                        continue
                    else:
                        return False, "System busy, please try again later"
                raise e  # 如果是其他錯誤，直接噴錯
            except Exception as e:
                print(e)
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
        try:
            report_row = Report(m_id=user_id, i_id=i_id, r_conclusion="Pending",
                                comment=data["comment"], create_at=datetime.now(), s_id=staff_id)
            db.session.add(report_row)
            db.session.commit()
            return True, {"report_id": report_row.re_id}
        except Exception as e:
            db.session.rollback()
            return False, str(e)


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
                SELECT m_id FROM item
                WHERE i_id = :i_id and m_id = :user_id
            """),
            {"i_id": i_id, "user_id": user_id}).mappings().first()
        if not check_user:
            return False, "Item not found"
        staff_id = pick_a_staff()
        if not staff_id:
            return False, "No staff available"
        try:
            item_verification_row = ItemVerification(
                i_id=i_id, s_id=staff_id, create_at=datetime.now(), v_conclusion="Pending")
            db.session.add(item_verification_row)
            db.session.commit()
            return True, {"item_verification_id": item_verification_row.iv_id}
        except Exception as e:
            db.session.rollback()
            return False, str(e)


def get_subcategory(c_id: int):
    """
    處理取得特定子類別物品請求。
    """
    if c_id == 0:
        items_row = db.session.execute(
            text("""
                SELECT c_id, c_name
                FROM category
                WHERE parent_c_id is NULL
            """),
            {"c_id": c_id}).mappings().all()
        # 轉換為字典列表
        return [dict(row) for row in items_row]
    else:
        items_row = db.session.execute(
            text("""
                SELECT c_id, c_name
                FROM category
                WHERE parent_c_id = :c_id
            """),
            {"c_id": c_id}).mappings().all()
        # 轉換為字典列表
        return [dict(row) for row in items_row]
