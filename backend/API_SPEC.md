# API 規格文件

本文檔說明所有可用的 API endpoints，包括請求參數、認證要求和回應格式。

## 基礎資訊

- **Base URL**: `http://localhost:8000` (開發環境)
- **認證方式**: JWT Token (Bearer Token)
- **Content-Type**: `application/json`

## 認證說明

大部分 API 需要在 HTTP Header 中攜帶 JWT Token：

```
Authorization: Bearer <your_token>
```

Token 格式必須為 `Bearer <token>`，中間有一個空格。

---

## 1. 認證相關 API (Auth)

### 1.1 登入

**Endpoint**: `POST /login`

**是否需要 Token**: ❌ 否

**請求參數** (JSON Body):
```json
{
  "email": "string",           // 必填：使用者 email
  "password": "string",        // 必填：使用者密碼
  "login_as": "string"         // 選填：登入身份，可選 "member" 或 "staff"，預設為 "member"
}
```

**成功回應** (200):
```json
{
  "token": "string",           // JWT Token
  "role": "string",           // "member" 或 "staff"
  "m_id": "integer",          // 會員 ID (如果 role 是 member)
  "m_name": "string",         // 會員名稱 (如果 role 是 member)
  "s_id": "integer",          // 員工 ID (如果 role 是 staff)
  "s_name": "string"          // 員工名稱 (如果 role 是 staff)
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："member not found", "wrong password", "invalid login_as"
}
```

---

### 1.2 註冊

**Endpoint**: `POST /register`

**是否需要 Token**: ❌ 否

**請求參數** (JSON Body):
```json
{
  "name": "string",           // 必填：使用者名稱
  "email": "string",          // 必填：使用者 email (必須是 @ntu.edu.tw 結尾)
  "password": "string"        // 必填：使用者密碼
}
```

**成功回應** (200):
```json
{
  "m_id": "integer",          // 會員 ID
  "m_name": "string",         // 會員名稱
  "m_email": "string"         // 會員 email
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："only ntu.edu.tw email is allowed", "member already exists"
}
```

---

## 2. 物品相關 API (Item)

### 2.1 取得物品詳細資訊

**Endpoint**: `GET /item/<i_id>`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `i_id` (integer): 物品 ID

**請求參數**: 無

**成功回應** (200):
```json
{
  "item": {
    "i_name": "string",       // 物品名稱
    "status": "string",        // 物品狀態
    "description": "string",   // 物品描述
    "out_duration": "integer", // 外借時長
    "c_id": "integer"         // 類別 ID
  }
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Unauthorized: Missing or invalid token", "Item not found"
}
```

---

### 2.2 取得特定類別物品

**Endpoint**: `GET /item/category/<c_id>`

**是否需要 Token**: ❌ 否

**路徑參數**:
- `c_id` (integer): 類別 ID

**請求參數**: 無

**成功回應** (200):
```json
{
  "items": [
    {
      "i_id": "integer",
      "i_name": "string",
      "status": "string",
      "description": "string",
      "out_duration": "integer",
      "c_id": "integer"
    }
  ]
}
```

**錯誤回應** (400/401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Category ID is required", "Items not found"
}
```

---

### 2.3 取得類別的子類別

**Endpoint**: `GET /item/category/<c_id>/subcategories`

**是否需要 Token**: ❌ 否

**路徑參數**:
- `c_id` (integer): 類別 ID (如果為 0，則返回所有根類別)

**請求參數**: 無

**成功回應** (200):
```json
{
  "items": [
    {
      "c_id": "integer",        // 類別 ID
      "c_name": "string"        // 類別名稱
    }
  ]
}
```

**說明**:
- 當 `c_id` 為 0 時，返回所有根類別（parent_c_id 為 NULL 的類別）
- 當 `c_id` 不為 0 時，返回該類別的所有子類別（parent_c_id 等於該 c_id 的類別）

---

### 2.4 取得物品借用時間

**Endpoint**: `GET /item/<i_id>/borrowed_time`

**是否需要 Token**: ❌ 否

**路徑參數**:
- `i_id` (integer): 物品 ID

**請求參數**: 無

**成功回應** (200):
```json
{
  "borrowed_time": [
    {
      "est_start_at": "datetime",  // 預計開始時間
      "est_due_at": "datetime"     // 預計歸還時間
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："No borrowed time"
}
```

---

### 2.5 上傳新物品

**Endpoint**: `POST /item/upload`

**是否需要 Token**: ✅ 是

**請求參數** (JSON Body):
```json
{
  "i_name": "string",         // 必填：物品名稱
  "description": "string",    // 必填：物品描述
  "out_duration": "integer",  // 必填：外借時長
  "c_id": "integer",          // 必填：類別 ID
  "p_id_list": [              // 必填：取貨地點 ID 列表
    "integer"
  ]
}
```

**成功回應** (200):
```json
{
  "item_id": "integer",       // 物品 ID
  "name": "string",           // 物品名稱
  "status": "string"          // 物品狀態 (通常為 "Not verified")
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息
}
```

---

### 2.6 更新物品

**Endpoint**: `PUT /item/<i_id>`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `i_id` (integer): 物品 ID

**請求參數** (JSON Body，所有欄位皆為選填):
```json
{
  "i_name": "string",         // 選填：物品名稱
  "status": "string",         // 選填：物品狀態
  "description": "string",    // 選填：物品描述
  "out_duration": "integer",  // 選填：外借時長
  "c_id": "integer",          // 選填：類別 ID
  "p_id_list": [              // 選填：取貨地點 ID 列表
    "integer"
  ]
}
```

**成功回應** (200):
```json
{
  "item": {
    "i_id": "integer",
    "i_name": "string",
    "status": "string",
    "description": "string",
    "out_duration": "integer",
    "c_id": "integer"
  }
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Item not found", "Item is borrowed, cannot be edited"
}
```

---

### 2.7 檢舉物品

**Endpoint**: `POST /item/<i_id>/report`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `i_id` (integer): 物品 ID

**請求參數** (JSON Body):
```json
{
  "comment": "string"         // 必填：檢舉內容
}
```

**成功回應** (200):
```json
{
  "report_id": "integer"      // 檢舉 ID
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息
}
```

---

### 2.8 驗證物品

**Endpoint**: `POST /item/<i_id>/verify`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `i_id` (integer): 物品 ID

**請求參數**: 無

**成功回應** (200):
```json
{
  "item_verification_id": "integer"  // 驗證 ID
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Item not found", "No staff available"
}
```

---

## 3. 個人資料相關 API (Me)

### 3.1 取得個人資料

**Endpoint**: `GET /me/profile`

**是否需要 Token**: ✅ 是

**請求參數**: 無

**成功回應** (200):
```json
{
  "name": "string",           // 使用者名稱
  "email": "string",          // 使用者 email
  "owner_rate": "float",      // 作為物主的評分 (僅 member 有)
  "borrower_rate": "float"    // 作為借用人的評分 (僅 member 有)
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息
}
```

---

### 3.2 取得我的物品

**Endpoint**: `GET /me/items`

**是否需要 Token**: ✅ 是

**請求參數**: 無

**成功回應** (200):
```json
{
  "items": [
    {
      "i_id": "integer",
      "i_name": "string",
      "status": "string",
      "description": "string",
      "out_duration": "integer",
      "c_id": "integer"
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Only members can get items"
}
```

---

### 3.3 取得我的預約

**Endpoint**: `GET /me/reservations`

**是否需要 Token**: ✅ 是

**請求參數**: 無

**成功回應** (200):
```json
{
  "reservations": [
    {
      "r_id": "integer",      // 預約 ID
      "create_at": "datetime", // 建立時間
      "items": [               // 物品名稱列表
        "string"
      ]
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Only members can get reservations"
}
```

---

### 3.4 取得預約詳細資訊

**Endpoint**: `GET /me/reservation_detail/<r_id>`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `r_id` (integer): 預約 ID

**請求參數**: 無

**成功回應** (200):
```json
{
  "reservation_details": [
    {
      "est_start_at": "datetime",  // 預計開始時間
      "est_due_at": "datetime",    // 預計歸還時間
      "i_name": "string",          // 物品名稱
      "p_name": "string"           // 取貨地點名稱
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Only members can get reservation detail"
}
```

---

### 3.5 取得可評論的物品

**Endpoint**: `GET /me/reviewable_items`

**是否需要 Token**: ✅ 是

**請求參數**: 無

**成功回應** (200):
```json
{
  "reviewable_items": [
    {
      "review_target": "string",   // "owner" 或 "borrower"
      "l_id": "integer",          // 借用 ID
      "i_id": "integer",          // 物品 ID
      "i_name": "string",         // 物品名稱
      "object_name": "string",    // 被評論者名稱
      "actual_return_at": "datetime"  // 實際歸還時間
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Only members can get reviewable items"
}
```

---

### 3.6 評論物品

**Endpoint**: `POST /me/review_item/<l_id>`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `l_id` (integer): 借用 ID

**請求參數** (JSON Body):
```json
{
  "score": "integer",         // 必填：評分
  "comment": "string"         // 必填：評論內容
}
```

**成功回應** (200):
```json
{
  "review_id": "integer"      // 評論 ID
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Loan not found", "Item has not been returned yet", "You have already reviewed this loan"
}
```

---

### 3.7 取得貢獻與封鎖

**Endpoint**: `GET /me/contributions`

**是否需要 Token**: ✅ 是

**請求參數**: 無

**成功回應** (200):
```json
{
  "contributions": [
    {
      "i_id": "integer",
      "i_name": "string",
      "is_active": "boolean",
      "c_id": "integer",
      "c_name": "string"
    }
  ],
  "bans": [
    {
      "c_id": "integer",
      "c_name": "string"
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Only members can get contributions and bans"
}
```

---

## 4. 物主相關 API (Owner)

### 4.1 取得未來預約詳細資訊

**Endpoint**: `GET /owner/future_reservation_details`

**是否需要 Token**: ✅ 是

**請求參數**: 無

**成功回應** (200):
```json
{
  "result": [
    {
      "l_id": "integer",          // 借用 ID
      "i_id": "integer",          // 物品 ID
      "m_name": "string",         // 借用人名稱
      "est_start_at": "datetime", // 預計開始時間
      "est_return_at": "datetime" // 預計歸還時間
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息
}
```

---

### 4.2 打卡 (建立借用事件)

**Endpoint**: `POST /owner/punch_in_loan/<l_id>`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `l_id` (integer): 借用 ID

**請求參數** (JSON Body):
```json
{
  "event_type": "string"      // 必填：事件類型，可選 "Handover" (交貨) 或 "Return" (歸還)
}
```

**成功回應** (200):
```json
{
  "result": "OK"
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息
}
```

---

## 5. 預約相關 API (Reservation)

### 5.1 取得物品的取貨地點

**Endpoint**: `GET /reservation/<i_id>`

**是否需要 Token**: ❌ 否

**路徑參數**:
- `i_id` (integer): 物品 ID

**請求參數**: 無

**成功回應** (200):
```json
{
  "pickup_places": [
    {
      "p_id": "integer",        // 取貨地點 ID
      "p_name": "string"         // 取貨地點名稱
    }
  ]
}
```

**錯誤回應** (400/401):
```json
{
  "error": "string"           // 錯誤訊息
}
```

---

### 5.2 建立預約

**Endpoint**: `POST /reservation/create`

**是否需要 Token**: ✅ 是

**請求參數** (JSON Body):
```json
{
  "rd_list": [                // 必填：預約詳細資訊列表
    {
      "i_id": "integer",       // 必填：物品 ID
      "p_id": "integer",       // 必填：取貨地點 ID
      "est_start_at": "string", // 必填：預計開始時間 (ISO 格式字串，例如："2024-01-01T10:00:00")
      "est_due_at": "string"   // 必填：預計歸還時間 (ISO 格式字串)
    }
  ]
}
```

**成功回應** (200):
```json
{
  "result": {
    "reservation_id": "integer"  // 預約 ID
  }
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Item X is not available during selected time", "You are banned from X category", "Your contribution to X category (root category) is not active"
}
```

---

### 5.3 刪除預約

**Endpoint**: `DELETE /reservation/delete/<r_id>`

**是否需要 Token**: ✅ 是

**路徑參數**:
- `r_id` (integer): 預約 ID

**請求參數**: 無

**成功回應** (200):
```json
{
  "result": "OK"
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："You can only cancel the reservation within 24 hours before the start time"
}
```

---

## 6. 員工相關 API (Staff)

### 6.1 取得員工資訊

**Endpoint**: `GET /staff`

**是否需要 Token**: ✅ 是 (必須是 staff 身份)

**請求參數**: 無

**成功回應** (200):
```json
{
  "staff": {
    "s_id": "integer",
    "s_name": "string",
    "s_mail": "string",
    "role": "string",
    "is_deleted": "boolean"
  }
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Unauthorized: Missing or invalid token", "Staff not found"
}
```

---

### 6.2 取得未處理的檢舉

**Endpoint**: `GET /staff/report`

**是否需要 Token**: ✅ 是 (必須是 staff 身份)

**請求參數**: 無

**成功回應** (200):
```json
{
  "reports": [
    {
      "re_id": "integer",     // 檢舉 ID
      "comment": "string",     // 檢舉內容
      "create_at": "datetime", // 建立時間
      "conclude_at": "datetime", // 結案時間 (可能為 null)
      "m_id": "integer",      // 檢舉人 ID
      "i_id": "integer"       // 被檢舉物品 ID
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息
}
```

---

### 6.3 結案檢舉

**Endpoint**: `POST /staff/report/<re_id>`

**是否需要 Token**: ✅ 是 (必須是 staff 身份)

**路徑參數**:
- `re_id` (integer): 檢舉 ID

**請求參數** (JSON Body):
```json
{
  "r_conclusion": "string"    // 必填：結案結論，可選 "Withdraw" (撤回)、"Ban Category" (封鎖類別)、"Delist" (下架)
}
```

**成功回應** (200):
```json
{
  "message": "string"         // 成功訊息，可能包含額外資訊，例如："Success, canceled X pending reservations, WARNING: User has Y active loans"
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Invalid conclusion", "Report not found"
}
```

---

### 6.4 取得未處理的驗證

**Endpoint**: `GET /staff/verification`

**是否需要 Token**: ✅ 是 (必須是 staff 身份)

**請求參數**: 無

**成功回應** (200):
```json
{
  "verifications": [
    {
      "iv_id": "integer",     // 驗證 ID
      "i_id": "integer",      // 物品 ID
      "v_conclusion": "string", // 驗證結論 (通常為 "Pending")
      "create_at": "datetime"  // 建立時間
    }
  ]
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："No pending verifications"
}
```

---

### 6.5 結案驗證

**Endpoint**: `POST /staff/verification/<iv_id>`

**是否需要 Token**: ✅ 是 (必須是 staff 身份)

**路徑參數**:
- `iv_id` (integer): 驗證 ID

**請求參數** (JSON Body):
```json
{
  "v_conclusion": "string"   // 必填：驗證結論，可選 "Pass" (通過) 或 "Fail" (不通過)
}
```

**成功回應** (200):
```json
{
  "message": "Success"
}
```

**錯誤回應** (401):
```json
{
  "error": "string"           // 錯誤訊息，例如："Item verification not found"
}
```

---

## 錯誤處理

所有 API 在發生錯誤時都會回傳以下格式：

```json
{
  "error": "錯誤訊息"
}
```

常見的 HTTP 狀態碼：
- **200**: 成功
- **400**: 請求參數錯誤
- **401**: 未授權 (Token 無效或缺失)

## 注意事項

1. **Token 格式**: 所有需要認證的 API 都必須在 Header 中攜帶 `Authorization: Bearer <token>`
2. **時間格式**: 日期時間欄位使用 ISO 8601 格式字串，例如：`"2024-01-01T10:00:00"`
3. **角色限制**: 某些 API 僅限特定角色使用 (例如 staff API 僅限員工使用)
4. **Email 限制**: 註冊時 email 必須是 `@ntu.edu.tw` 結尾
5. **預約取消**: 只能在預約開始時間前 24 小時內取消

