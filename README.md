# 114-1 資料庫管理 - Our things 校園閒置物品流通平台

## 專案簡介

在校園生活中，學生常有短期使用特定物品（如活動道具、露營器材、教科書）的需求，但購買新品不僅昂貴，使用後也常造成閒置浪費。雖然現有社群平台（如 Facebook 社團）提供二手交易管道，但缺乏信任基礎、物品狀態不透明，且難以管理借還流程。

**Our things** 是一個專為校園設計的閒置物品流通平台。我們透過實名制認證與貢獻度系統，建立互信的共享經濟生態。使用者可以將閒置物品上架借出，累積貢獻度，並用以借用他人分享的物品，達到資源的最佳化配置。

🔗 [展示影片連結](https://youtu.be/7tlkQRkWbl4) <!-- 之後填入 -->

## 使用者功能

### Member （一般使用者）

#### 使用者登入、註冊
*   **註冊**：強制使用校內信箱（@ntu.edu.tw）進行註冊，確保使用者皆為校內學生，建立信任基礎。
*   **登入**：系統驗證帳號密碼，並發放 JWT Token 進行身份維持。

#### 物品瀏覽與搜尋
*   **分類瀏覽**：透過遞迴式分類樹（Category Tree），使用者可依層級瀏覽物品。
*   **關鍵字搜尋**：可搜尋物品名稱或描述。
*   **查看詳情**：瀏覽物品照片、新舊狀況、可借用時段及物主評價。

#### 預約與借用
*   **建立預約**：選擇借用時段與取貨地點。系統會即時檢查時段是否與現有預約衝突。
*   **預約管理**：查看「我的預約」，可在規定時間前取消預約。

#### 物品管理 (Owner)
*   **上架物品**：填寫物品資訊、上傳照片、設定分類與預設取貨點。
*   **交易打卡**：
    *   **交付確認**：當面交付物品時，物主掃描或點擊確認，狀態轉為 `Loan`。
    *   **歸還確認**：歸還物品時，物主確認物品無損，狀態轉為 `Finished`，雙方互評。

#### 評價系統
*   交易完成後，借用方與出租方可互相給予 1-5 星評價及文字評論。

### Staff （管理員）

除了上述 Member 功能外，擁有後台管理權限：

#### 審核功能
*   **物品審核**：審核新上架的物品（Pending -> Verified）。審核通過後，物品才會顯示在搜尋結果中，且物主獲得貢獻度。
*   **檢舉處理**：查看使用者提交的檢舉（如物品損壞、惡意行為），執行下架物品、撤銷分類或停權等操作。

## 使用方法

### 環境設定
*   Python 3.10+
*   PostgreSQL 16
*   MongoDB

### 啟動步驟

1.  **資料庫設定**：
    請在 `.env` 或設定檔中配置 `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `MONGO_URI`。
格式如下：
```
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>
MONGODB_URI=mongodb://<user>:<password>@<host>:<port>/
SECRET_KEY=<secret_key>
```
其中：
* `<user>`：資料庫使用者名稱
* `<password>`：資料庫密碼
* `<host>`：資料庫主機
* `<port>`：資料庫連接埠
* `<db>`：資料庫名稱
* `<secret_key>`：Flask 使用的隨機字串
2.  **初始化資料庫**：
    執行初始化腳本以建立 Table Schema 並匯入預設分類資料。
    ```bash
    cd backend/app/db
    python SetDB.py
    ```

3.  **啟動後端伺服器**：
    ```bash
    cd backend
    python run.py
    ```

4.  **啟動前端**：
    開啟 `index.html` 或使用 Live Server 啟動。

## 技術細節

本專案結合關聯式資料庫 (PostgreSQL) 與 NoSQL (MongoDB)，針對不同資料特性進行優化。

### 交易管理 (Transaction Management)與併行控制

為了確保預約流程的正確性，避免「超賣」或「雙重花費」問題，我們實作了嚴格的交易控制：

1.  **預約時段搶訂 (Prevention of Double Booking)**
    *   **問題**：當多個使用者同時嘗試預約同一熱門物品的相同時段。
    *   **解決方案**：在 `create_reservation` 功能中，我們將 Transaction Isolation Level 設定為 **`SERIALIZABLE`**。
    *   **機制**：利用 PostgreSQL 的 SSI (Serializable Snapshot Isolation) 機制。若 User A 與 User B 同時讀取到時段可用並嘗試寫入，資料庫會偵測到 Read-Write Dependency 衝突，讓先提交者成功，後提交者收到 **Serialization Failure** 並被 Rollback。

2.  **貢獻度扣除 (Prevention of Double Spending)**
    *   **問題**：使用者可能快速發送多個請求，試圖用同一筆貢獻度預約多個物品。
    *   **解決方案**：使用 **Pessimistic Locking (`SELECT ... FOR UPDATE`)**。
    *   **機制**：在計算與扣除貢獻度前，先鎖定該使用者的 Contribution 紀錄。其他併發的交易必須等待鎖釋放後才能讀取最新的餘額，確保貢獻度不會被重複扣除。

### 資料庫優化 (Optimization)

1.  **複合索引 (Compound Index)**
    *   針對最高頻率的「時段重疊檢查」查詢：
        ```sql
        SELECT ... FROM reservation_detail
        WHERE i_id = ? AND OVERLAPS(start_at, end_at, ?, ?)
        ```
    *   建立了索引 `(i_id, est_start_at, est_due_at)`，大幅減少 Sequential Scan，提升預約檢查效率。

2.  **遞迴查詢優化 (Recursive Query)**
    *   針對多層級的物品分類（Category），使用 **Common Table Expression (CTE)** 配合 `WITH RECURSIVE` 語法來抓取子分類，取代傳統的多次應用層查詢。

3.  **NoSQL 應用 (MongoDB)**
    *   **用途**：Funnel Tracker (使用者行為漏斗分析)。
    *   **原因**：使用者點擊流（Clickstream）數據量大且結構多變（Schema-less）。使用 MongoDB 的高寫入吞吐量（High Write Throughput）特性來記錄 `browse`, `check_availability`, `reserve` 等事件，避免影響 PostgreSQL 的交易效能。

## 程式說明

### 目錄結構

*   `backend/`
    *   `app/`
        *   `routes/`: API 路由定義 (Item, Member, Reservation, Auth)。
        *   `models/`: SQLAlchemy ORM 模型定義。
        *   `services/`: 業務邏輯層 (處理 Transaction 與 Locking)。
        *   `db/`: 資料庫連線與初始化腳本 (`SetDB.py`)。
*   `frontend/`
    *   HTML/CSS/JS 構建的 SPA (Single Page Application) 架構。

### 關鍵程式碼片段參考

*   **Transaction Isolation**: 位於 `backend/app/services/reservation_service.py`
    ```python
    db.session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
    ```
*   **Funnel Logging**: 位於 `backend/app/utils/tracker.py`，使用 `pymongo` 寫入 MongoDB。

## 開發環境

*   **OS**: macOS / Windows
*   **Language**: Python 3.10, JavaScript (ES6+)
*   **Database**: PostgreSQL 16.4, MongoDB 7.0
*   **Framework**: Flask 3.0, SQLAlchemy 2.0
*   **Libraries**: `psycopg2-binary`, `pymongo`, `flask-jwt-extended`
