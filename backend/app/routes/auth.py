from flask import Blueprint, request, jsonify
from app.services.auth_service import login_service, register_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """
    處理使用者登入請求。
    
    接收 JSON 格式的 email 和 password，
    驗證成功後回傳 JWT Token。
    """

    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    login_as = data.get("login_as", "member")  # "member" 或 "staff"

    ok, result = login_service(email, password, login_as)
    if not ok:
        # result 放錯誤訊息
        return jsonify({"error": result}), 401

    # result 放 token & role
    return jsonify(result)


@auth_bp.post("/register")
def register():
    """
    處理使用者註冊請求。
    
    接收 JSON 格式的 name、email 和 password，
    註冊成功後回傳使用者 ID。
    """

    data = request.get_json() or {}
    username = data.get("name")
    email = data.get("email")
    password = data.get("password")

    ok, result = register_service(username, email, password)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)
