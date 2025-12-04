from flask import Blueprint, request, jsonify
from app.services.item_service import get_item_detail, get_category_items, get_item_borrowed_time, upload_item, update_item, report_item, verify_item, get_subcategory_items
from app.mongodb.funnel_tracker import log_event
item_bp = Blueprint("item", __name__)

@item_bp.get("/item/<int:i_id>")
def get_this_item_detail(i_id):
    """
    處理取得物品詳細資訊請求。

    接收物品 ID，
    取得物品詳細資訊後回傳。
    """

    auth_header = request.headers.get("Authorization")

    # 檢查格式是否正確 (Bearer <token>)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串

    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = get_item_detail(i_id)
    log_event(
        event_type='get_item_detail',
        endpoint=f'/item/{i_id}',
        success=ok,
        item_id=i_id,
        error_reason=result if not ok else None
    )
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

    if not c_id:
        return jsonify({"error": "Category ID is required"}), 400
    ok, result = get_category_items(c_id)
    log_event(
        event_type='browse_category',
        endpoint=f'/item/category/{c_id}',
        success=ok,
        category_id=c_id,
        error_reason=result if not ok else None
    )
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)


@item_bp.get("/item/category/<int:c_id>/subcategories")
def get_this_subcategory_items(c_id):
    """
    處理取得特定類別的子類別請求。
    """
    try:
        items = get_subcategory_items(c_id)
        log_event(
            event_type='browse_subcategory',
            endpoint=f'/item/category/{c_id}/subcategories',
            success=True,
            category_id=c_id,
        )
        return jsonify({"items": items}), 200
    except Exception as e:
        log_event(
            event_type='browse_subcategory',
            endpoint=f'/item/category/{c_id}/subcategories',
            success=False,
            error_reason=str(e),
        )
        return jsonify({"error": str(e)}), 500


@item_bp.get("/item/<int:i_id>/borrowed_time")
def get_this_item_borrowed_time(i_id):
    """
    處理取得物品借用時間請求。

    接收物品 ID，
    取得物品借用時間後回傳。
    """
    ok, result = get_item_borrowed_time(i_id)
    log_event(
        event_type='get_item_borrowed_time',
        endpoint=f'/item/{i_id}/borrowed_time',
        success=ok,
        item_id=i_id,
        error_reason=result if not ok else None
    )
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

    auth_header = request.headers.get("Authorization")

    # 檢查格式是否正確 (Bearer <token>)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    data = request.get_json() or {}
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
    auth_header = request.headers.get("Authorization")
     
    # 檢查格式是否正確 (Bearer <token>)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
        
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    data = request.get_json() or {}
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = update_item(token, i_id, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@item_bp.post("/item/<int:i_id>/report")
def report_this_item(i_id):
    """
    處理檢舉物品請求。

    接收物品 ID，
    檢舉物品後回傳。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    data = request.get_json() or {}
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = report_item(token, i_id, data)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

@item_bp.post("/item/<int:i_id>/verify")
def verify_this_item(i_id):
    """
    處理驗證物品請求。

    接收物品 ID，
    驗證物品後回傳。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]  # 取出 "Bearer " 後面的 token 字串
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    ok, result = verify_item(token, i_id)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

