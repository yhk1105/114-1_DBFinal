# MongoDB 漏斗追蹤資料欄位說明

本文檔說明 MongoDB 中 `user_sessions` collection 的所有欄位，以及如何用於漏斗圖分析。

## 資料庫與 Collection

- **資料庫名稱**: `our_things_funnel_tracking`
- **Collection 名稱**: `user_sessions`

---

## Collection 結構

### 主要欄位（Session 層級）

#### 1. `session_id` (String, 唯一索引)
- **說明**: 用戶會話的唯一識別碼
- **來源**: 前端在 Header 中傳送的 `X-Session-ID`，如果沒有則自動生成 UUID
- **用途**: 
  - 追蹤單一用戶的完整瀏覽流程
  - 計算轉換率（從瀏覽到預約的完整路徑）
  - 分析用戶行為序列

#### 2. `user_token` (String, 可選, 有索引)
- **說明**: JWT Token（如果用戶已登入）
- **來源**: 從 `Authorization` Header 中提取
- **用途**: 
  - 識別已登入用戶
  - 區分匿名用戶與登入用戶的行為差異

#### 3. `m_id` (Integer, 可選, 有索引)
- **說明**: 會員 ID（從 JWT Token 解析得出）
- **來源**: 解析 `user_token` 後取得
- **用途**: 
  - 追蹤特定用戶的完整行為歷史
  - 分析回頭客行為
  - 計算用戶生命週期價值（LTV）

#### 4. `funnel_stage` (String, 有索引)
- **說明**: 當前漏斗階段
- **可能值**:
  - `browse_category`: 瀏覽類別
  - `view_item`: 查看物品
  - `check_availability`: 檢查可用性
  - `view_pickup_places`: 查看取貨地點
  - `attempt_reservation`: 嘗試預約
  - `reservation_success`: 預約成功
  - `reservation_failed`: 預約失敗
  - `unknown`: 未知階段
- **用途**: 
  - **漏斗圖分析的核心欄位**
  - 計算各階段的轉換率
  - 識別流失點（在哪個階段用戶離開最多）

#### 5. `created_at` (DateTime, 有索引)
- **說明**: Session 建立時間（UTC）
- **用途**: 
  - 時間序列分析
  - 計算 Session 持續時間
  - 分析不同時段的轉換率

#### 6. `updated_at` (DateTime)
- **說明**: Session 最後更新時間（UTC）
- **用途**: 
  - 計算 Session 活躍時間
  - 識別閒置 Session

#### 7. `events` (Array)
- **說明**: 事件陣列，記錄所有用戶行為事件
- **結構**: 見下方「事件欄位」說明
- **用途**: 
  - **漏斗圖分析的主要資料來源**
  - 分析用戶行為序列
  - 計算各事件的發生次數和轉換率

---

## 事件欄位（Events Array 中的每個事件）

每個事件（event）包含以下欄位：

### 必填欄位

#### 1. `event_type` (String)
- **說明**: 事件類型
- **可能值**:
  - `browse_category`: 瀏覽類別物品
  - `browse_subcategory`: 瀏覽子類別
  - `get_item_detail`: 查看物品詳細資訊
  - `get_item_borrowed_time`: 查看物品借用時間
  - `get_pickup_places`: 查看取貨地點
  - `create_reservation`: 建立預約（成功或失敗）
- **用途**: 
  - **漏斗圖的核心欄位**
  - 識別用戶在哪個步驟
  - 計算各步驟的轉換率

#### 2. `timestamp` (DateTime)
- **說明**: 事件發生時間（UTC）
- **用途**: 
  - 計算步驟間的時間間隔
  - 分析用戶行為的時間模式
  - 識別快速流失的用戶

#### 3. `endpoint` (String)
- **說明**: API 端點路徑
- **範例**: `/item/category/1`, `/item/5`, `/reservation/create`
- **用途**: 
  - 追蹤用戶訪問的具體 API
  - 分析熱門功能
  - 識別問題端點

#### 4. `success` (Boolean)
- **說明**: 操作是否成功
- **用途**: 
  - 計算成功率
  - 識別失敗率高的步驟
  - 分析錯誤對轉換率的影響

### 可選欄位（根據事件類型不同）

#### 5. `error_reason` (String, 可選)
- **說明**: 失敗原因（當 `success=false` 時）
- **用途**: 
  - 分析失敗原因
  - 識別常見錯誤
  - 優化用戶體驗

#### 6. `category_id` (Integer, 可選)
- **說明**: 類別 ID
- **出現於**: `browse_category`, `browse_subcategory` 事件
- **用途**: 
  - 分析不同類別的轉換率
  - 識別熱門類別
  - 分析類別對預約的影響

#### 7. `item_id` (Integer, 可選)
- **說明**: 物品 ID
- **出現於**: `get_item_detail`, `get_item_borrowed_time`, `get_pickup_places` 事件
- **用途**: 
  - 追蹤特定物品的瀏覽次數
  - 分析熱門物品
  - 計算物品的轉換率

#### 8. `reservation_id` (Integer, 可選)
- **說明**: 預約 ID（當預約成功時）
- **出現於**: `create_reservation` 事件（成功時）
- **用途**: 
  - 追蹤成功預約
  - 計算最終轉換率

#### 9. `item_ids` (Array, 可選)
- **說明**: 物品 ID 列表（當預約失敗時，記錄嘗試預約的物品）
- **出現於**: `create_reservation` 事件（失敗時）
- **用途**: 
  - 分析哪些物品預約失敗率高
  - 識別問題物品

---

## 漏斗圖分析建議

### 1. 基本漏斗階段

根據 `funnel_stage` 欄位，可以建立以下漏斗：

```
瀏覽類別 (browse_category)
    ↓
查看物品 (view_item)
    ↓
檢查可用性 (check_availability)
    ↓
查看取貨地點 (view_pickup_places)
    ↓
嘗試預約 (attempt_reservation)
    ↓
預約成功 (reservation_success)
```

### 2. 關鍵指標計算

#### 轉換率計算
```javascript
// 範例：計算從「瀏覽類別」到「查看物品」的轉換率
const browseCount = db.user_sessions.countDocuments({
  "funnel_stage": "browse_category"
});

const viewItemCount = db.user_sessions.countDocuments({
  "funnel_stage": "view_item"
});

const conversionRate = (viewItemCount / browseCount) * 100;
```

#### 使用 events 陣列進行更精確的分析
```javascript
// 計算各事件類型的發生次數
db.user_sessions.aggregate([
  { $unwind: "$events" },
  { $group: {
      _id: "$events.event_type",
      count: { $sum: 1 },
      successCount: {
        $sum: { $cond: ["$events.success", 1, 0] }
      }
    }
  }
]);
```

### 3. 時間序列分析

```javascript
// 按日期分析轉換率
db.user_sessions.aggregate([
  {
    $group: {
      _id: {
        $dateToString: { format: "%Y-%m-%d", date: "$created_at" }
      },
      totalSessions: { $sum: 1 },
      successfulReservations: {
        $sum: {
          $cond: [{ $eq: ["$funnel_stage", "reservation_success"] }, 1, 0]
        }
      }
    }
  }
]);
```

### 4. 用戶分群分析

```javascript
// 區分登入用戶與匿名用戶
db.user_sessions.aggregate([
  {
    $group: {
      _id: {
        userType: { $cond: [{ $ifNull: ["$m_id", false] }, "logged_in", "anonymous"] },
        funnelStage: "$funnel_stage"
      },
      count: { $sum: 1 }
    }
  }
]);
```

### 5. 錯誤分析

```javascript
// 分析失敗原因
db.user_sessions.aggregate([
  { $unwind: "$events" },
  { $match: { "events.success": false } },
  { $group: {
      _id: "$events.error_reason",
      count: { $sum: 1 },
      eventTypes: { $addToSet: "$events.event_type" }
    }
  }
]);
```

---

## 索引建議

已建立的索引（見 `create_nosql_indexes.js`）：

1. `session_id` (唯一索引) - 快速查找特定 Session
2. `user_token` - 查找特定用戶的 Session
3. `m_id` - 查找特定會員的所有 Session
4. `created_at` - 時間範圍查詢
5. `funnel_stage` - **漏斗圖分析的核心索引**
6. `events.timestamp` - 事件時間查詢

### 建議新增的索引（如果需要）

```javascript
// 事件類型的複合索引
db.user_sessions.createIndex({ 
  "events.event_type": 1, 
  "events.timestamp": 1 
});

// 成功率的分析索引
db.user_sessions.createIndex({ 
  "events.success": 1, 
  "events.event_type": 1 
});
```

---

## 查詢範例

### 範例 1: 計算完整漏斗轉換率

```javascript
db.user_sessions.aggregate([
  {
    $group: {
      _id: "$funnel_stage",
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
]);
```

### 範例 2: 分析用戶行為序列

```javascript
db.user_sessions.aggregate([
  {
    $project: {
      session_id: 1,
      m_id: 1,
      eventSequence: "$events.event_type",
      eventTimestamps: "$events.timestamp"
    }
  },
  { $match: { "eventSequence": { $size: { $gte: 3 } } } }
]);
```

### 範例 3: 找出流失點

```javascript
// 找出在「查看物品」階段後沒有繼續的 Session
db.user_sessions.aggregate([
  {
    $match: {
      "events.event_type": "get_item_detail"
    }
  },
  {
    $project: {
      session_id: 1,
      lastEvent: { $arrayElemAt: ["$events", -1] },
      hasReservation: {
        $in: ["create_reservation", "$events.event_type"]
      }
    }
  },
  {
    $match: { hasReservation: false }
  }
]);
```

---

## 注意事項

1. **Session 生命週期**: Session 會持續更新，直到用戶完成預約或 Session 過期
2. **匿名用戶**: 未登入用戶只有 `session_id`，沒有 `m_id`
3. **事件順序**: `events` 陣列中的事件按時間順序排列
4. **錯誤處理**: `log_event` 函數內部有錯誤處理，即使 MongoDB 出錯也不會影響主要業務邏輯

---

## 資料範例

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "m_id": 123,
  "funnel_stage": "view_item",
  "created_at": ISODate("2024-12-04T15:30:00Z"),
  "updated_at": ISODate("2024-12-04T15:35:00Z"),
  "events": [
    {
      "event_type": "browse_category",
      "timestamp": ISODate("2024-12-04T15:30:00Z"),
      "endpoint": "/item/category/1",
      "success": true,
      "category_id": 1
    },
    {
      "event_type": "browse_subcategory",
      "timestamp": ISODate("2024-12-04T15:31:00Z"),
      "endpoint": "/item/category/1/subcategories",
      "success": true,
      "category_id": 1
    },
    {
      "event_type": "get_item_detail",
      "timestamp": ISODate("2024-12-04T15:32:00Z"),
      "endpoint": "/item/5",
      "success": true,
      "item_id": 5
    },
    {
      "event_type": "get_item_borrowed_time",
      "timestamp": ISODate("2024-12-04T15:33:00Z"),
      "endpoint": "/item/5/borrowed_time",
      "success": true,
      "item_id": 5
    },
    {
      "event_type": "get_pickup_places",
      "timestamp": ISODate("2024-12-04T15:34:00Z"),
      "endpoint": "/reservation/5",
      "success": true,
      "item_id": 5
    }
  ]
}
```

---

## 總結

### 用於漏斗圖分析的關鍵欄位：

1. **`funnel_stage`** - 當前漏斗階段（最直接）
2. **`events.event_type`** - 事件類型（最詳細）
3. **`events.success`** - 成功/失敗標記
4. **`events.timestamp`** - 時間戳記（計算步驟間隔）
5. **`m_id`** - 用戶識別（分析回頭客）
6. **`created_at`** - Session 建立時間（時間序列分析）

### 建議的分析維度：

- 按時間（日/週/月）
- 按用戶類型（登入/匿名）
- 按類別（`category_id`）
- 按物品（`item_id`）
- 按成功/失敗（`success`）

