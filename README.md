# Our Things — 部署與執行指南

本文件說明如何在本機建置並啟動後端與前端。請依序完成環境準備、資料庫初始化，再啟動服務。

## 環境需求
- Python 3.10+、pip（建議使用 venv 虛擬環境）
- PostgreSQL 13+（含 `psql` 指令）
- MongoDB 7.0+（用於漏斗追蹤功能）
- macOS 使用者建議透過 Homebrew 安裝：
  - PostgreSQL：`brew install postgresql@16`
  - MongoDB：`brew tap mongodb/brew && brew install mongodb-community@7.0`

## 專案結構（重點）
- `backend/`：Flask API（預設埠 8070）
- `backend/app/db/`：SQL/CSV 與初始化腳本 `SetDB.py`
- `frontend/`：純 HTML/JS 前端（預設埠 8080）

## 建議的安裝步驟
1) 取得程式碼並進入專案根目錄。
2) 建立虛擬環境並啟用（可選但建議）：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\\Scripts\\activate
   ```
3) 安裝後端依賴：
   ```bash
   pip install -r backend/requirements.txt
   ```

## 設定環境變數
在專案根目錄或 `backend/` 下建立 `.env`（`SetDB.py` 與後端都會讀取）。範例：
```
# 格式：postgresql://<使用者>:<密碼>@<主機>:<port>/<資料庫>
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
# 格式：mongodb://<使用者>:<密碼>@<主機>:<port>/
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=dev-secret
```
說明：
- `DATABASE_URL`：`postgresql://<user>:<password>@<host>:<port>/<db>`。請將 `<user>`、`<password>`、`<host>`、`<port>`、`<db>` 改成你實際的 PostgreSQL 帳號/密碼與連線資訊；需有建立/刪除資料庫權限，腳本會在其中建立目標 DB `our_things`。
- `MONGODB_URI`：若有帳密，格式同上；預設本機無帳密可用 `mongodb://localhost:27017/`。
- `SECRET_KEY`：Flask 用的隨機字串。

## 準備資料庫服務
- 啟動 PostgreSQL，確認能以 `psql` 連線。
- 啟動 MongoDB：
  ```bash
  brew services start mongodb-community@7.0  # macOS
  # 或以您慣用方式啟動 mongod 服務
  ```

## 初始化資料庫（PostgreSQL + MongoDB）
> 注意：`SetDB.py` 會**刪除並重建**目標資料庫 `our_things`。

```bash
cd backend/app/db
python SetDB.py
```
腳本會依序：建立/重建 PostgreSQL DB → 執行 `schema.sql` → 匯入 `csv/` 中的測試資料 → 執行 `setnextval.sql` 與 `setindex.sql` → 初始化 MongoDB 資料庫與索引。

## 啟動後端 (Flask API)
```bash
cd backend
python run.py
```
- 預設埠：`http://localhost:8070`
- 若需更改埠，請修改 `backend/run.py` 或調整前端的 `API_BASE_URL`。

## 啟動前端
```bash
cd frontend
python -m http.server 8080
# 瀏覽器開啟 http://localhost:8080
```
- 前端預設呼叫 `http://localhost:8070`（見 `frontend/app.js` 的 `API_BASE_URL`）。若後端埠有變更，請同步修改。

## 常見問題排查
- 後端無法啟動：確認 `.env` 內 `DATABASE_URL` 正確，`pip install -r backend/requirements.txt` 已完成，且埠 8070 未被占用。
- PostgreSQL/Mongo 連不上：確認服務已啟動並可由命令列連線；重新檢查 `DATABASE_URL`/`MONGODB_URI`。
- 資料未載入：重跑 `backend/app/db/SetDB.py`，留意它會清空並重建 `our_things`。
- 前端呼叫失敗：確認後端在 8070 運行，並確定 `frontend/app.js` 的 `API_BASE_URL` 與後端埠一致；務必透過 HTTP 伺服器開啟前端（不要直接雙擊 HTML）。

完成以上步驟後，後端應在 8070，前端在 8080，可直接於瀏覽器操作系統功能。
