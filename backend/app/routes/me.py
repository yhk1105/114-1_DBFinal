from flask import Blueprint, request, jsonify
from app.services.me_service import get_profile_service, get_my_items, get_my_reservations, get_reservation_detail, get_reviewable_items, get_contributions_and_bans


me_bp = Blueprint("me", __name__)


@me_bp.get("/me/profile")
def get_profile():
    """
    處理取得使用者 profile 請求。

    接收 JSON 格式的 token，
    取得使用者 profile 後回傳。
    """

    auth_header = request.headers.get("Authorization")

    # 檢查格式是否正確 (Bearer <token>)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_profile_service(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)


@me_bp.get("/me/items")
def get_items():
    """
    處理取得使用者物品請求。

    接收 JSON 格式的 token，
    取得使用者物品後回傳。
    """

    auth_header = request.headers.get("Authorization")

    # 檢查格式是否正確 (Bearer <token>)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_my_items(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)


@me_bp.get("/me/reservations")
def get_reservations():
    """
    處理取得使用者預約請求。

    接收 JSON 格式的 token，
    取得使用者預約後回傳。
    """

    auth_header = request.headers.get("Authorization")

    # 檢查格式是否正確 (Bearer <token>)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_my_reservations(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)


@me_bp.get("/me/reservation_detail/<int:r_id>")
def get_this_reservation_detail(r_id):
    """
    處理取得使用者預約詳細資訊請求。

    接收 JSON 格式的 token，
    取得使用者預約詳細資訊後回傳。
    """

    auth_header = request.headers.get("Authorization")

    # 檢查格式是否正確 (Bearer <token>)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_reservation_detail(token, r_id)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)


@me_bp.get("/me/reviewable_items")
def get_my_reviewable_items():
    """
    處理取得使用者可評論的物品請求。

    接收 JSON 格式的 token，
    取得使用者可評論的物品後回傳。
    """

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_reviewable_items(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@me_bp.get("/me/contributions")
def get_my_contributions():
    """
    處理取得使用者貢獻請求。

    接收 JSON 格式的 token，
    取得使用者貢獻後回傳。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_contributions_and_bans(token)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)