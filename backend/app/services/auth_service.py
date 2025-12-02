from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.utils.jwt_utils import generate_token
from app.models.member import Member
from sqlalchemy.exc import IntegrityError


def login_service(email: str, password: str, login_as: str):
    """
    處理使用者登入請求。

    接收 email 和 password，
    驗證成功後回傳 JWT Token。
    """

    if login_as == "member":
        member_row = db.session.execute(
            text("""
                SELECT m_id, m_password, m_name
                FROM our_things.member    -- 如果你在 public schema 就改成 public.user 或直接 user
                WHERE m_mail = :mail and is_active = true
            """),
            {"mail": email},
        ).mappings().first()
        if not member_row:
            return False, "member not found"

        if not check_password_hash(member_row["m_password"], password):
            return False, "wrong password"

        # 4. 產生 token
        token = generate_token(member_row["m_id"], "member")
        return True, {"token": token, "role": "member", "m_id": member_row["m_id"], "m_name": member_row["m_name"]}
    elif login_as == "staff":
        staff_row = db.session.execute(
            text("""
                SELECT s_id, s_password, s_name
                FROM our_things.staff
                WHERE s_mail = :mail and is_deleted = false
            """),
            {"mail": email},
        ).mappings().first()
        if not staff_row:
            return False, "staff not found"
        if not check_password_hash(staff_row["s_password"], password):
            return False, "wrong password"
        token = generate_token(staff_row["s_id"], "staff")
        return True, {"token": token, "role": "staff", "s_id": staff_row["s_id"], "s_name": staff_row["s_name"]}
    else:
        return False, "invalid login_as"


def register_service(name: str, email: str, password: str):
    """
    處理使用者註冊請求。

    接收 name、email 和 password，
    註冊成功後回傳使用者 ID。
    """
    if not email.endswith("@ntu.edu.tw"):
        return False, "only ntu.edu.tw email is allowed"
    # 3. 新增會員
    new_member = Member(m_name=name, m_mail=email,
                        m_password=generate_password_hash(password), is_active=True)
    db.session.add(new_member)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False, "member already exists"
    return True, {"m_id": new_member.m_id, "m_name": name, "m_email": email}
