from flask import Blueprint, request, jsonify
from app.services.reservation_service import create_reservation


reservation_bp = Blueprint("reservation", __name__)

@reservation_bp.post("/reservation/create")
def create_this_reservation():
    """
    處理建立預約請求。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]
    data = request.get_json() or {}
    ok, result = create_reservation(token, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify({"result": result}), 200