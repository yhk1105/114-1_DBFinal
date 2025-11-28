from sqlalchemy import text
from app.extensions import db
from app.utils.jwt_utils import generate_token
from werkzeug.security import generate_password_hash, check_password_hash


def login_service(username: str, password: str, login_as: str):
    # 1. 查使用者
    user_row = db.session.execute(
        text("""
            SELECT u_id, u_password, is_staff
            FROM our_things.user    -- 如果你在 public schema 就改成 public.user 或直接 user
            WHERE u_mail = :mail
        """),
        {"mail": username},
    ).mappings().first()

    if not user_row:
        return False, "user not found"

    # 2. 比對密碼（這裡先簡單比對字串，之後你可以改成 hash）
    if password != user_row["u_password"]:
        return False, "wrong password"

    # 3. 檢查角色（假設 is_staff boolean）
    roles = ["member"]
    if user_row["is_staff"]:
        roles.append("staff")

    if login_as not in roles:
        return False, "you cannot login as this role"

    # 4. 產生 token
    token = generate_token(user_row["u_id"], login_as, roles)
    return True, {"token": token, "role": login_as}

def register_service(username: str, email: str, password: str):
    # 1. 檢查使用者是否存在
    user_row = db.session.execute(
        text("""
            SELECT u_id
            FROM our_things.user
            WHERE u_mail = :mail
        """),
        {"mail": username},
    ).mappings().first()
    if user_row:
        return False, "user already exists"
    
    # 2. 新增使用者
    new_user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    return True, "user created successfully"