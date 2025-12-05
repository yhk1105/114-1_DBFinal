from flask import Blueprint, request, jsonify
from app.services.reservation_service import create_reservation, delete_reservation, get_pickup_places
from app.mongodb.funnel_tracker import log_event

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
    if ok:
        log_event(
            event_type='create_reservation',
            endpoint=f'/reservation/create',
            success=True,
            reservation_id=result["r_id"],
        )
    if not ok:
        log_event(
            event_type='create_reservation',
            endpoint=f'/reservation/create',
            success=False,
            error_reason=result,
            item_ids=[rd.get('i_id') for rd in data.get('rd_list', [])] if isinstance(data, dict) else []
        )
        return jsonify({"error": result}), 401
    return jsonify({"result": result}), 200

@reservation_bp.delete("/reservation/delete/<int:r_id>")
def delete_this_reservation(r_id):
    """
    處理刪除預約請求。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]
    ok, result = delete_reservation(token, r_id)
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify({"result": result}), 200

@reservation_bp.get("/reservation/<int:i_id>/pickup_places")
def get_this_pickup_places(i_id):
    """
    處理取得物品可取貨地點請求。
    """
    pickup_places = get_pickup_places(i_id)
    log_event(
        event_type='get_pickup_places',
        endpoint=f'/reservation/{i_id}',
        success=True,
        item_id=i_id,
    )
    return jsonify({"pickup_places": pickup_places}), 200

