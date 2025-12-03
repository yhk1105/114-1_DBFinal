from flask import Blueprint, request, jsonify
from app.services.owner_service import get_future_reservation_details, punch_in_loan


owner_bp = Blueprint("owner", __name__)

@owner_bp.get("/owner/future_reservation_details")
def get_my_future_reservation_details():
    """
    處理取得未來的預約詳細資訊請求。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]
    ok, result = get_future_reservation_details(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify({"result": result}), 200

@owner_bp.post("/owner/punch_in_loan/<int:l_id>")
def punch_in_this_loan(l_id):
    """
    處理打卡請求。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]
    data = request.get_json() or {}
    ok, result = punch_in_loan(token, l_id, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify({"result": result}), 200