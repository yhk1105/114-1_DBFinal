from flask import Blueprint, request, jsonify
from app.services.staff_service import get_this_staff, get_not_deal_reports, conclude_report, get_not_deal_verification, conclude_verification

staff_bp = Blueprint("staff", __name__)

@staff_bp.get("/staff")
def get_staff():
    """
    處理取得員工資訊請求。

    接收員工 ID，
    取得員工資訊後回傳。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_this_staff(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@staff_bp.get("/staff/report")
def get_not_deal_reports_route():
    """
    處理取得未處理的檢舉資訊請求。

    接收員工 ID，
    取得未處理的檢舉資訊後回傳。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_not_deal_reports(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@staff_bp.post("/staff/report/<int:re_id>")
def conclude_this_report(re_id):
    """
    處理結案檢舉請求。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    ok, result = conclude_report(token, re_id, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@staff_bp.get("/staff/verification")
def get_not_deal_verification_route():
    """
    處理取得未處理的驗證資訊請求。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_not_deal_verification(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@staff_bp.post("/staff/verification/<int:iv_id>")
def conclude_this_verification(iv_id):
    """
    處理結案驗證請求。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    ok, result = conclude_verification(token, iv_id, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)