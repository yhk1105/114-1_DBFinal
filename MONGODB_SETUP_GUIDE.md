# MongoDB Windows 安裝與設定指南

本指南將協助您在 Windows 上安裝 MongoDB 並使用圖形介面工具來管理資料庫。

## 📋 目錄

1. [安裝 MongoDB Community Server](#1-安裝-mongodb-community-server)
2. [安裝 MongoDB Compass（圖形介面工具）](#2-安裝-mongodb-compass圖形介面工具)
3. [啟動 MongoDB 服務](#3-啟動-mongodb-服務)
4. [使用 MongoDB Compass 建立 Schema](#4-使用-mongodb-compass-建立-schema)
5. [驗證連線](#5-驗證連線)

---

## 1. 安裝 MongoDB Community Server

### 方法一：使用 MSI 安裝程式（推薦）

1. **下載 MongoDB Community Server**
   - 前往官方網站：https://www.mongodb.com/try/download/community
   - 選擇：
     - Version: 最新穩定版（建議 7.0 或以上）
     - Platform: Windows
     - Package: MSI
   - 點擊「Download」下載

2. **執行安裝程式**
   - 雙擊下載的 `.msi` 檔案
   - 選擇「Complete」完整安裝
   - **重要**：勾選「Install MongoDB as a Service」
   - 選擇「Run service as Network Service user」（預設）
   - 勾選「Install MongoDB Compass」（可選，但建議另外下載最新版）
   - 點擊「Install」開始安裝

3. **驗證安裝**
   - 開啟 PowerShell 或命令提示字元
   - 執行以下命令檢查版本：
   ```powershell
   mongod --version
   ```

### 方法二：使用 Chocolatey（如果已安裝）

```powershell
choco install mongodb
```

---

## 2. 安裝 MongoDB Compass（圖形介面工具）

MongoDB Compass 是官方提供的免費圖形介面工具，非常適合管理 MongoDB。

### 下載與安裝

1. **下載 MongoDB Compass**
   - 前往：https://www.mongodb.com/try/download/compass
   - 選擇 Windows 版本
   - 下載並執行安裝程式

2. **啟動 MongoDB Compass**
   - 安裝完成後，從開始選單啟動 MongoDB Compass
   - 首次啟動會要求連線，預設連線字串為：`mongodb://localhost:27017`

---

## 3. 啟動 MongoDB 服務

### 檢查服務狀態

1. **使用服務管理員**
   - 按 `Win + R`，輸入 `services.msc`，按 Enter
   - 找到「MongoDB」服務
   - 確認狀態為「執行中」，如果沒有，右鍵選擇「啟動」

2. **使用命令列**
   ```powershell
   # 檢查服務狀態
   Get-Service MongoDB
   
   # 啟動服務（如果需要）
   Start-Service MongoDB
   
   # 停止服務
   Stop-Service MongoDB
   ```

### 手動啟動 MongoDB（如果服務未安裝）

如果安裝時沒有選擇安裝為服務，可以手動啟動：

```powershell
# 建立資料目錄（如果不存在）
mkdir C:\data\db

# 啟動 MongoDB
mongod --dbpath C:\data\db
```

---

## 4. 使用 MongoDB Compass 建立 Schema

### 連線到 MongoDB

1. **開啟 MongoDB Compass**
   - 啟動 MongoDB Compass
   - 連線字串：`mongodb://localhost:27017`
   - 點擊「Connect」

### 建立資料庫和 Collection

根據您的專案，需要建立以下結構：

#### 資料庫：`our_things_funnel_tracking`

1. **建立資料庫**
   - 在 Compass 左側面板，點擊「Create Database」
   - Database Name: `our_things_funnel_tracking`
   - Collection Name: `user_sessions`
   - 點擊「Create Database」

2. **建立索引（提升查詢效能）**

   在 `user_sessions` collection 中建立以下索引：

   **索引 1：session_id（唯一索引）**
   - 點擊 `user_sessions` collection
   - 切換到「Indexes」標籤
   - 點擊「Create Index」
   - Index Name: `session_id_1`
   - Index Definition: `{ "session_id": 1 }`
   - 勾選「Unique」
   - 點擊「Create Index」

   **索引 2：user_token**
   - 點擊「Create Index」
   - Index Name: `user_token_1`
   - Index Definition: `{ "user_token": 1 }`
   - 點擊「Create Index」

   **索引 3：m_id**
   - 點擊「Create Index」
   - Index Name: `m_id_1`
   - Index Definition: `{ "m_id": 1 }`
   - 點擊「Create Index」

   **索引 4：created_at**
   - 點擊「Create Index」
   - Index Name: `created_at_1`
   - Index Definition: `{ "created_at": 1 }`
   - 點擊「Create Index」

   **索引 5：funnel_stage**
   - 點擊「Create Index」
   - Index Name: `funnel_stage_1`
   - Index Definition: `{ "funnel_stage": 1 }`
   - 點擊「Create Index」

   **索引 6：events.timestamp（複合索引）**
   - 點擊「Create Index」
   - Index Name: `events.timestamp_1`
   - Index Definition: `{ "events.timestamp": 1 }`
   - 點擊「Create Index」

### Schema 結構說明

根據 `backend/app/mongodb/funnel_tracker.py`，`user_sessions` collection 的文件結構如下：

```json
{
  "session_id": "string (UUID, 唯一)",
  "user_token": "string (JWT token, 可選)",
  "m_id": "integer (會員 ID, 可選)",
  "events": [
    {
      "event_type": "string (例如: 'browse_category', 'view_item')",
      "timestamp": "ISODate",
      "endpoint": "string (API endpoint)",
      "success": "boolean",
      "error_reason": "string (可選)",
      "item_id": "integer (可選)",
      "category_id": "integer (可選)",
      "reservation_id": "integer (可選)"
    }
  ],
  "funnel_stage": "string (例如: 'browse_category', 'view_item', 'reservation_success')",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### 使用 Compass 查看和編輯資料

1. **查看文件**
   - 在 Compass 中選擇 `user_sessions` collection
   - 可以在「Documents」標籤中查看所有文件
   - 使用篩選器來查詢特定文件

2. **插入測試資料**
   - 點擊「Insert Document」
   - 選擇「JSON」格式
   - 貼上以下測試資料：
   ```json
   {
     "session_id": "test-session-001",
     "user_token": null,
     "m_id": null,
     "events": [],
     "funnel_stage": null,
     "created_at": "2024-01-01T00:00:00.000Z",
     "updated_at": "2024-01-01T00:00:00.000Z"
   }
   ```
   - 點擊「Insert」

---

## 5. 驗證連線

### 在專案中驗證

1. **設定環境變數**
   - 確認 `.env` 檔案中有以下設定：
   ```
   MONGODB_URI=mongodb://localhost:27017/
   ```

2. **啟動後端服務**
   ```powershell
   cd backend
   python run.py
   ```

3. **檢查日誌**
   - 如果看到以下訊息，表示連線成功：
   ```
   ✅ MongoDB 連線成功
   ✅ MongoDB 索引建立完成
   MongoDB 資料庫列表: ['admin', 'config', 'local', 'our_things_funnel_tracking']
   ```

### 使用 MongoDB Compass 驗證

1. 在 Compass 中連線到 `mongodb://localhost:27017`
2. 確認可以看到 `our_things_funnel_tracking` 資料庫
3. 確認 `user_sessions` collection 存在
4. 確認所有索引都已建立

---

## 🔧 疑難排解

### 問題 1：無法連線到 MongoDB

**解決方法：**
- 確認 MongoDB 服務正在執行（`services.msc`）
- 確認防火牆允許 27017 埠
- 檢查 MongoDB 日誌檔案（通常在 `C:\Program Files\MongoDB\Server\<version>\log\mongod.log`）

### 問題 2：Compass 無法啟動

**解決方法：**
- 確認已安裝最新版本的 Compass
- 嘗試以系統管理員身分執行
- 檢查是否有其他程序佔用 27017 埠

### 問題 3：索引建立失敗

**解決方法：**
- 確認索引名稱不重複
- 如果索引已存在，Compass 會顯示錯誤，這是正常的
- 可以在 Compass 的「Indexes」標籤中查看現有索引

### 問題 4：專案無法連線到 MongoDB

**解決方法：**
- 確認 `.env` 檔案中的 `MONGODB_URI` 設定正確
- 確認 MongoDB 服務正在執行
- 檢查後端日誌中的錯誤訊息

---

## 📚 其他有用的工具

### Studio 3T（進階圖形介面工具）

- 功能更強大的 MongoDB 管理工具
- 下載：https://studio3t.com/download/

### MongoDB Shell (mongosh)

- 命令列工具，適合進階使用者
- 通常會隨 MongoDB 一起安裝
- 使用方式：
  ```powershell
  mongosh
  ```

---

## ✅ 完成檢查清單

- [ ] MongoDB Community Server 已安裝
- [ ] MongoDB 服務正在執行
- [ ] MongoDB Compass 已安裝並可以連線
- [ ] 資料庫 `our_things_funnel_tracking` 已建立
- [ ] Collection `user_sessions` 已建立
- [ ] 所有必要的索引已建立
- [ ] 後端應用程式可以成功連線到 MongoDB
- [ ] 測試資料可以正常插入和查詢

---

## 📖 參考資源

- MongoDB 官方文件：https://docs.mongodb.com/
- MongoDB Compass 文件：https://docs.mongodb.com/compass/
- MongoDB 社群論壇：https://www.mongodb.com/community/forums/

---

**注意**：本專案使用 MongoDB 來追蹤用戶漏斗行為，主要用於分析用戶從查詢到預約的完整流程。MongoDB 的 schema 是動態的（NoSQL 特性），但建議遵循上述的文件結構以保持資料一致性。

