# 漏斗追蹤埋點指南

本指南說明如何在各個 API 端點埋入 MongoDB 追蹤代碼。

## 需要追蹤的 API 端點

### 1. 查詢階段（不需要 token）

#### `GET /item/category/<c_id>` - 瀏覽類別物品
```python
from app.mongodb.funnel_tracker import log_event

@item_bp.get("/item/category/<int:c_id>")
def get_this_category_items(c_id):
    ok, result = get_category_items(c_id)
    
    # 埋點：記錄瀏覽類別事件
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
```

#### `GET /item/category/<c_id>/subcategories` - 瀏覽子類別
```python
@item_bp.get("/item/category/<int:c_id>/subcategories")
def get_this_subcategory_items(c_id):
    items = get_subcategory_items(c_id)
    
    # 埋點：記錄瀏覽子類別事件
    log_event(
        event_type='view_subcategory',
        endpoint=f'/item/category/{c_id}/subcategories',
        success=True,
        category_id=c_id
    )
    
    return jsonify({"items": items}), 200
```

#### `GET /item/<i_id>/borrowed_time` - 查看借用時間
```python
@item_bp.get("/item/<int:i_id>/borrowed_time")
def get_this_item_borrowed_time(i_id):
    ok, result = get_item_borrowed_time(i_id)
    
    # 埋點：記錄檢查可用時間事件
    log_event(
        event_type='check_availability',
        endpoint=f'/item/{i_id}/borrowed_time',
        success=ok,
        item_id=i_id,
        error_reason=result if not ok else None
    )
    
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)
```

#### `GET /reservation/<i_id>` - 查看取貨地點
```python
@reservation_bp.get("/reservation/<int:i_id>")
def get_this_pickup_places(i_id):
    pickup_places = get_pickup_places(i_id)
    
    # 埋點：記錄查看取貨地點事件
    log_event(
        event_type='view_pickup_places',
        endpoint=f'/reservation/{i_id}',
        success=True,
        item_id=i_id
    )
    
    return jsonify({"pickup_places": pickup_places}), 200
```

### 2. 查看階段（需要 token）

#### `GET /item/<i_id>` - 查看物品詳情
```python
@item_bp.get("/item/<int:i_id>")
def get_this_item_detail(i_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    
    token = auth_header.split(" ")[1]
    ok, result = get_item_detail(i_id)
    
    # 埋點：記錄查看物品詳情事件
    log_event(
        event_type='view_item',
        endpoint=f'/item/{i_id}',
        success=ok,
        item_id=i_id,
        error_reason=result if not ok else None
    )
    
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)
```

### 3. 預約階段（需要 token）

#### `POST /reservation/create` - 建立預約
```python
@reservation_bp.post("/reservation/create")
def create_this_reservation():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    
    token = auth_header.split(" ")[1]
    data = request.get_json() or {}
    ok, result = create_reservation(token, data)
    
    # 埋點：記錄預約嘗試事件
    if ok:
        # 預約成功
        log_event(
            event_type='reservation_success',
            endpoint='/reservation/create',
            success=True,
            reservation_id=result.get('reservation_id') if isinstance(result, dict) else None
        )
    else:
        # 預約失敗
        log_event(
            event_type='reservation_failed',
            endpoint='/reservation/create',
            success=False,
            error_reason=result,
            item_ids=[rd.get('i_id') for rd in data.get('rd_list', [])] if isinstance(data, dict) else []
        )
    
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify({"result": result}), 200
```

## 完整範例：修改後的 routes/item.py

```python
from flask import Blueprint, request, jsonify
from app.services.item_service import get_item_detail, get_category_items, get_item_borrowed_time, get_subcategory_items
from app.mongodb.funnel_tracker import log_event

item_bp = Blueprint("item", __name__)

@item_bp.get("/item/category/<int:c_id>")
def get_this_category_items(c_id):
    if not c_id:
        return jsonify({"error": "Category ID is required"}), 400
    
    ok, result = get_category_items(c_id)
    
    # 埋點
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

@item_bp.get("/item/<int:i_id>")
def get_this_item_detail(i_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid token"}), 401
    
    token = auth_header.split(" ")[1]
    ok, result = get_item_detail(i_id)
    
    # 埋點
    log_event(
        event_type='view_item',
        endpoint=f'/item/{i_id}',
        success=ok,
        item_id=i_id,
        error_reason=result if not ok else None
    )
    
    if not ok:
        return jsonify({"error": result}), 401
    return jsonify(result)

# ... 其他端點類似處理
```

## 重要提醒

1. **錯誤處理**：`log_event` 函數內部已經有 try-except，即使 MongoDB 出錯也不會影響主要業務邏輯
2. **Session ID**：前端需要在每個請求的 Header 中帶上 `X-Session-ID`
3. **Token 處理**：如果有 token，會自動解析並記錄 `m_id`
4. **非阻塞**：追蹤是異步的，不會影響 API 回應速度

## 前端配合

前端需要在每個 API 請求中帶上 Session ID：

```javascript
// 第一次訪問時生成並保存
let sessionId = localStorage.getItem('session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID(); // 或使用其他 UUID 生成方式
    localStorage.setItem('session_id', sessionId);
}

// 每次 API 請求都帶上
fetch('/item/category/1', {
    headers: {
        'X-Session-ID': sessionId,
        // 如果有 token 也一起帶上
        'Authorization': `Bearer ${token}`
    }
});
```

