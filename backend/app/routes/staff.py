from flask import Blueprint, request, jsonify
from app.services.staff_service import get_this_staff, get_not_deal_reports

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