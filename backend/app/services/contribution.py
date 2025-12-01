from app.extensions import db
from sqlalchemy import text

def change_contribution(m_id: int, i_id: int):
    """
    處理更改貢獻。
    """
    item_original = db.session.execute(
                    text("""
                            SELECT i_id, i_name, status, description, out_duration, c_id, is_active FROM our_things.item
                            join our_things.contribution on item.i_id = contribution.i_id
                            WHERE item.i_id = :i_id and item.m_id = :user_id
                        """),
                    {"i_id": i_id, "user_id": m_id}).mappings().first()
    check_this_contribution = db.session.execute(text("""
        SELECT is_active FROM our_things.contribution
        WHERE m_id = :m_id and i_id = :i_id
    """),
    {"m_id": m_id, "i_id": i_id}
    ).mappings().first()["is_active"]
    if not check_this_contribution:
        db.session.execute(text("""
            UPDATE our_things.contribution
            SET is_active = false
            WHERE m_id = :m_id and i_id = :i_id
        """),
        {"m_id": m_id, "i_id": i_id}
        ).mappings().first()
    else:
        check_category_contribution = db.session.execute(
            text("""
                SELECT i_id
                FROM our_things.contribution
                join our_things.item on contribution.i_id = item.i_id
                WHERE m_id = :m_id and item.c_id = :c_id and is_active = true
            """),
            {"m_id": m_id, "c_id": item_original["c_id"]}).mappings().first()
        if not check_category_contribution:
            return False
        else:
            db.session.execute(
                text("""
                    UPDATE our_things.contribution
                    SET is_active = false
                    WHERE i_id = :i_id
                """),
                {"i_id": check_category_contribution["i_id"]})
            db.session.execute(
                text("""
                UPDATE our_things.contribution
                SET is_active = true
                WHERE i_id = :i_id
            """),
                {"i_id": i_id})
            return True