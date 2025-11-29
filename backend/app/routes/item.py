Item

from flask import Blueprint, request, jsonify
from app.services.item_service import get_item_detail, get_category_items, get_item_borrowed_time, upload_item, update_item

item_bp = Blueprint("item", __name__)

@item_bp.get("/item/<int:i_id>")
def get_this_item_detail(i_id):
    """
    處理取得物品詳細資訊請求。
    
    接收物品 ID，
    取得物品詳細資訊後回傳。
    """

    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_item_detail(i_id)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@item_bp.get("/item/category/<int:c_id>")
def get_this_category_items(c_id):
    """
    處理取得特定類別物品請求。
    
    接收類別 ID，
    取得特定類別物品後回傳。
    """

    data = request.get_json() or {}
    c_id = data.get("c_id")
    if not c_id:
        return jsonify({"error": "Category ID is required"}), 400
    ok, result = get_category_items(c_id)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@item_bp.get("/item/<int:i_id>/borrowed_time")
def get_this_item_borrowed_time(i_id):
    """
    處理取得物品借用時間請求。
    
    接收物品 ID，
    取得物品借用時間後回傳。
    """

    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_item_borrowed_time(i_id)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@item_bp.post("/item/upload")
def upload_new_item():
    """
    處理上傳新物品請求。
    
    接收物品資訊，
    上傳新物品後回傳。
    """

    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = upload_item(token, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@item_bp.put("/item/<int:i_id>")
def update_this_item(i_id):
    """
    處理更新物品請求。
    
    接收物品 ID 和物品資訊，
    更新物品後回傳。
    """

    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = update_item(token, i_id, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)


