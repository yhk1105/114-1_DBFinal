from flask import Blueprint, request, jsonify
from app.services.pickup_places_service import get_all_pickup_places

pp_bp = Blueprint("pickup-places", __name__)


@pp_bp.get("/pickup-places")
def get_pickup_places():
    """
    處理取得取貨地點請求。
    """
    pickup_places = get_all_pickup_places()
    return jsonify({"pickup_places": pickup_places}), 200