from sqlalchemy import text
from datetime import datetime
from app.extensions import db
from app.utils.jwt_utils import get_user
from app.models.item import Item

def get_item_detail( i_id: int):
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
        item_id = db.session.execute(
            text("""
                SELECT MAX(i_id) + 1 FROM our_things.item
            """)).scalar()
        if not item_id:
            item_id = 1
        item_row = Item(i_id=item_id, i_name=data["i_name"], status="Not verified", description=data["description"], out_duration=data["out_duration"], m_id=user_id, c_id=data["c_id"])
        db.session.add(item_row)
        db.session.commit()
        return True, {"item_id": item_id, "name": data["i_name"], "status": data["status"]}

def update_item(token: str, i_id: int, data: dict):
    """
    處理更新物品請求。
    
    接收 JWT Token 和物品 ID 和物品資訊，
    更新物品後回傳。
    """
    user_id, active_role = get_user(token)
    if not user_id:
        return False, "Unauthorized"
    if active_role == "member":

        check_owner = db.session.execute(
            text("""
                SELECT u_id FROM our_things.item
                WHERE i_id = :i_id and m_id = :user_id
            """),
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
        if data.get("i_name"): # update name
            item_row = db.session.execute(
                text("""
                    UPDATE our_things.item
                    SET i_name = :i_name
                    WHERE i_id = :i_id and m_id = :user_id
                """),
                {"i_id": i_id, "user_id": user_id, "i_name": data["i_name"]}).mappings().first()
        if data.get("status") and data["status"] != item_original["status"]: # update status
            if data["status"] == "Not reservable":
                if item_original["status"] == "Borrowed":
                    return False, "Item is borrowed"
                if item_original["is_active"] == False:
                    check_category_contribution = db.session.execute(
                    text("""
                        SELECT i_id
                        FROM our_things.contribution
                        join our_things.item on contribution.i_id = item.i_id
                        WHERE m_id = :user_id and item.c_id = :item_original_c_id and is_active = true
                    """),
                    {"user_id": user_id, "item_original_c_id": item_original["c_id"]}).mappings().first()
                    if not check_category_contribution:
                        return False, "Cannot change status"
                    else:
                        item_row = db.session.execute(
                            text("""
                                UPDATE our_things.contribution
                                SET is_active = false
                                WHERE i_id = :i_id
                            """),
                            {"i_id": check_category_contribution["i_id"]}).mappings().first()
                        item_row = db.session.execute(
                        text("""
                            UPDATE our_things.contribution
                            SET is_active = 
                            WHERE i_id = :i_id
                        """),
                        {"i_id": i_id}).mappings().first()
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
        if data.get("description"): # update description
            item_row = db.session.execute(
                text("""
                    UPDATE our_things.item
                    SET description = :description
                    WHERE i_id = :i_id and m_id = :user_id
                """),
                {"i_id": i_id, "user_id": user_id, "description": data["description"]}).mappings().first()
        if data.get("out_duration"): # update out_duration
            item_row = db.session.execute(
                text("""
                    UPDATE our_things.item
                    SET out_duration = :out_duration
                    WHERE i_id = :i_id and m_id = :user_id
                """),
                {"i_id": i_id, "user_id": user_id, "out_duration": data["out_duration"]}).mappings().first()
        if data.get("c_id"): # update c_id
            
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