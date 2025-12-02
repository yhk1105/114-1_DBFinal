from sqlalchemy import text


def get_root_category(session, c_id: int) -> int:
    """
    找到 category 的 root category（最上層的父類別）。
    如果 category 本身沒有父類別，則返回自己。
    """
    result = session.execute(text("""
        WITH RECURSIVE category_path AS (
            -- 起始點：從給定的 category 開始
            SELECT c_id, parent_c_id, c_id as root_c_id
            FROM category
            WHERE c_id = :c_id
            
            UNION ALL
            
            -- 遞迴向上查找父類別
            SELECT c.c_id, c.parent_c_id,
                   CASE 
                       WHEN c.parent_c_id IS NULL THEN c.c_id 
                       ELSE cp.root_c_id 
                   END as root_c_id
            FROM category c
            JOIN category_path cp ON c.c_id = cp.parent_c_id
            WHERE cp.parent_c_id IS NOT NULL
        )
        SELECT root_c_id 
        FROM category_path 
        WHERE parent_c_id IS NULL
        LIMIT 1
    """), {"c_id": c_id}).scalar()

    # 如果找不到（理論上不應該發生），返回原 c_id
    return result if result else c_id


def change_contribution(session, m_id: int, i_id: int) -> bool:
    """
    處理更改貢獻。
    使用 root category 來檢查：只要在同一個 root category 下，就可以互用。
    """
    # 1. 取得物品資訊
    item_original = session.execute(
        text("""
            SELECT i_id, i_name, status, description, out_duration, c_id, is_active 
            FROM item
            JOIN contribution ON item.i_id = contribution.i_id
            WHERE item.i_id = :i_id AND item.m_id = :user_id
        """),
        {"i_id": i_id, "user_id": m_id}
    ).mappings().first()

    if not item_original:
        return False

    # 2. 檢查當前 contribution 的狀態
    check_this_contribution = session.execute(text("""
        SELECT is_active FROM contribution
        WHERE m_id = :m_id AND i_id = :i_id
    """), {
        "m_id": m_id,
        "i_id": i_id
    }).mappings().first()

    if not check_this_contribution:
        return False

    is_active = check_this_contribution["is_active"]

    # 3. 如果當前 contribution 是 inactive，直接設為 false 並返回
    if is_active:
        return True

    # 4. 如果當前 contribution 是 active，需要檢查 root category
    # 找到物品的 root category
    root_c_id = get_root_category(session, item_original["c_id"])

    # 5. 檢查用戶在該 root category 及其所有子類別下是否有其他 active contribution
    check_root_category_contribution = session.execute(
        text("""
            SELECT contribution.i_id
            FROM contribution
            JOIN item ON contribution.i_id = item.i_id
            WHERE contribution.m_id = :m_id 
            AND contribution.is_active = true
            AND contribution.i_id != :current_i_id
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
        """),
        {
            "m_id": m_id,
            "root_c_id": root_c_id,
            "current_i_id": i_id
        }
    ).mappings().first()

    # 6. 如果沒有找到其他 active contribution，無法啟用（需要至少一個 active）
    if not check_root_category_contribution:
        return False

    # 7. 如果找到了，將舊的設為 inactive，將新的設為 active
    session.execute(text("""
        UPDATE contribution
        SET is_active = false
        WHERE i_id = :old_i_id
    """), {
        "old_i_id": check_root_category_contribution["i_id"]
    })

    session.execute(text("""
        UPDATE contribution
        SET is_active = true
        WHERE i_id = :i_id
    """), {
        "i_id": i_id
    })

    return True
