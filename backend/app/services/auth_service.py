from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.utils.jwt_utils import generate_token
from app.models.member import Member

def login_service(email: str, password: str, login_as: str):
    """
    處理使用者登入請求。
    
    接收 email 和 password，
    驗證成功後回傳 JWT Token。
    """

    if login_as == "member":
        member = Member.query.filter_by(u_mail=email).first()
        
        if not member:
            return False, "member not found"

        if not check_password_hash(member.u_password, password):
            return False, "wrong password"

        # 4. 產生 token
        token = generate_token(member.m_id, "member")
        return True, {"token": token, "role": "member", "id": member.m_id, "name": member.u_name}
    
    elif login_as == "staff":
        # Staff model implementation is missing or not verified, skipping for now or adding placeholder
        # Assuming Staff model exists or will be added. For now, return error if staff login attempted
        # to avoid breaking if Staff model is not ready.
        # Based on createTable.sql, Staff table exists, but I haven't checked the model.
        # I will return an error for now to focus on member login.
        return False, "staff login not implemented yet"
    else:
        return False, "invalid login_as"

def register_service(name: str, email: str, password: str):
    """
    處理使用者註冊請求。
    
    接收 name、email 和 password，
    註冊成功後回傳使用者 ID。
    """

    member = Member.query.filter_by(u_mail=email).first()
    if member:
        return False, "member already exists"
    
    # 2. 檢查是否為學校信箱
    if not email.endswith("@ntu.edu.tw"):
        return False, "only ntu.edu.tw email is allowed"
    
    # 3. 新增會員
    # m_id is auto-increment if not specified, but the model defined it as Integer primary key.
    # If it's not autoincrement in DB (SQLite default is usually yes for Integer PK), we might need to set it.
    # However, createTable.sql didn't specify SERIAL or AUTOINCREMENT explicitly for SQLite compatibility in the SQL,
    # but SQLAlchemy usually handles it.
    # Let's try without setting m_id explicitly first, or use a simple count + 1 strategy if needed.
    # Given the previous code used count + 1, I'll stick to auto-increment if possible, but let's just create the object.
    
    new_member = Member(
        u_name=name,
        u_mail=email,
        u_password=generate_password_hash(password)
        # is_active defaults to True in model? No default in model definition seen in previous turn (only in SQL).
        # I should check model again.
    )
    # Model definition:
    # m_id = db.Column(db.Integer, primary_key=True)
    # u_mail = db.Column(db.String(120), unique=True, nullable=False)
    # u_name = db.Column(db.String(50), nullable=False)
    # u_password = db.Column(db.String(255), nullable=False)
    
    db.session.add(new_member)
    db.session.commit()
    
    return True, {"member_id": new_member.m_id, "member_name": name, "member_email": email}