# MongoDB 安裝與設定指南（macOS）

本指南將幫助您在新的 Mac 上安裝和設定 MongoDB，以便運行此專案。

## 方法 1：使用 Homebrew 安裝（推薦）

### 步驟 1：安裝 Homebrew（如果尚未安裝）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 步驟 2：使用 Homebrew 安裝 MongoDB

```bash
# 更新 Homebrew
brew update

# 安裝 MongoDB Community Edition
brew tap mongodb/brew
brew install mongodb-community@7.0
```

### 步驟 3：啟動 MongoDB 服務

```bash
# 啟動 MongoDB 服務
brew services start mongodb-community@7.0

# 或者手動啟動（關閉終端機後會停止）
mongod --config /opt/homebrew/etc/mongod.conf
```

### 步驟 4：驗證安裝

開啟新的終端機視窗，執行：

```bash
# 連接到 MongoDB
mongosh

# 在 MongoDB shell 中執行
db.runCommand({ connectionStatus: 1 })
```

如果看到 `"ok" : 1`，表示安裝成功！

## 方法 2：使用官方安裝程式

### 步驟 1：下載 MongoDB

1. 前往 [MongoDB 官方下載頁面](https://www.mongodb.com/try/download/community)
2. 選擇：
   - Version: 7.0（或最新穩定版）
   - Platform: macOS
   - Package: TGZ
3. 下載並解壓縮

### 步驟 2：安裝 MongoDB

```bash
# 移動到解壓縮的目錄
cd ~/Downloads/mongodb-macos-x86_64-7.0.x

# 複製到系統目錄
sudo cp -R bin/* /usr/local/bin/

# 建立資料目錄
sudo mkdir -p /data/db
sudo chown -R $(whoami) /data/db
```

### 步驟 3：啟動 MongoDB

```bash
# 啟動 MongoDB
mongod --dbpath /data/db
```

## 設定專案

### 步驟 1：設定環境變數

在專案根目錄的 `.env` 檔案中，確認或設定 MongoDB 連線：

```env
# MongoDB 連線設定（預設值，通常不需要修改）
MONGODB_URI=mongodb://localhost:27017/
```

### 步驟 2：建立資料庫和索引

專案會在首次啟動時自動建立索引，但您也可以手動執行：

#### 方法 A：使用 MongoDB Compass（圖形化工具，推薦）

1. **下載並安裝 MongoDB Compass**
   ```bash
   # 使用 Homebrew 安裝
   brew install --cask mongodb-compass
   ```

2. **連接到 MongoDB**
   - 開啟 MongoDB Compass
   - 連線字串：`mongodb://localhost:27017`
   - 點擊「Connect」

3. **執行索引建立腳本**
   - 在 Compass 中，點擊左側的資料庫名稱
   - 選擇「Shell」標籤
   - 複製並執行 `backend/app/db/create_nosql_indexes.js` 的內容

#### 方法 B：使用命令行

```bash
# 連接到 MongoDB
mongosh

# 在 MongoDB shell 中執行
use our_things_funnel_tracking

# 建立索引（專案會自動建立，但可以手動執行）
db.user_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.user_sessions.createIndex({ "user_token": 1 });
db.user_sessions.createIndex({ "m_id": 1 });
db.user_sessions.createIndex({ "created_at": 1 });
db.user_sessions.createIndex({ "funnel_stage": 1 });
db.user_sessions.createIndex({ "events.timestamp": 1 });
```

## 驗證設定

### 測試 MongoDB 連線

```bash
# 方法 1：使用 mongosh
mongosh
# 執行
db.runCommand({ connectionStatus: 1 })

# 方法 2：使用 Python 測試腳本
cd backend
python3 -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://localhost:27017/')
    client.admin.command('ping')
    print('✅ MongoDB 連線成功')
except Exception as e:
    print(f'❌ MongoDB 連線失敗: {e}')
"
```

### 啟動專案並檢查日誌

```bash
cd backend
python run.py
```

如果看到以下訊息，表示 MongoDB 設定成功：
```
✅ MongoDB 連線成功
✅ MongoDB 索引建立完成
MongoDB 資料庫列表: ['admin', 'config', 'local', 'our_things_funnel_tracking']
```

## 常用命令

### 啟動/停止 MongoDB 服務

```bash
# 啟動（使用 Homebrew）
brew services start mongodb-community@7.0

# 停止
brew services stop mongodb-community@7.0

# 重啟
brew services restart mongodb-community@7.0

# 查看狀態
brew services list | grep mongodb
```

### 查看 MongoDB 日誌

```bash
# 使用 Homebrew 安裝的 MongoDB
tail -f /opt/homebrew/var/log/mongodb/mongo.log

# 或查看系統日誌
tail -f /opt/homebrew/var/mongodb/mongod.log
```

### 備份和還原

```bash
# 備份資料庫
mongodump --db our_things_funnel_tracking --out /path/to/backup

# 還原資料庫
mongorestore --db our_things_funnel_tracking /path/to/backup/our_things_funnel_tracking
```

## 故障排除

### 問題 1：無法啟動 MongoDB

**錯誤訊息**：`Address already in use`

**解決方法**：
```bash
# 檢查是否有其他 MongoDB 程序在運行
ps aux | grep mongod

# 終止程序
killall mongod

# 重新啟動
brew services start mongodb-community@7.0
```

### 問題 2：權限錯誤

**錯誤訊息**：`Permission denied`

**解決方法**：
```bash
# 檢查資料目錄權限
ls -la /opt/homebrew/var/mongodb

# 修改權限（如果需要）
sudo chown -R $(whoami) /opt/homebrew/var/mongodb
```

### 問題 3：找不到 mongosh 命令

**解決方法**：
```bash
# 檢查是否安裝
which mongosh

# 如果找不到，可能需要手動建立連結
brew link mongodb-community@7.0
```

### 問題 4：專案無法連接到 MongoDB

**檢查清單**：
1. ✅ MongoDB 服務是否正在運行：`brew services list | grep mongodb`
2. ✅ 連線字串是否正確：檢查 `.env` 檔案中的 `MONGODB_URI`
3. ✅ 防火牆是否阻擋：macOS 通常不需要特別設定
4. ✅ 查看後端日誌：檢查是否有 MongoDB 相關錯誤訊息

## 完整安裝流程總結

對於全新的 Mac，完整流程如下：

```bash
# 1. 安裝 Homebrew（如果沒有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安裝 MongoDB
brew tap mongodb/brew
brew install mongodb-community@7.0

# 3. 啟動 MongoDB
brew services start mongodb-community@7.0

# 4. 驗證安裝
mongosh --eval "db.runCommand({ connectionStatus: 1 })"

# 5. 安裝 MongoDB Compass（可選，但推薦）
brew install --cask mongodb-compass

# 6. 設定專案
cd /path/to/114-1_DBFinal/backend
pip install -r requirements.txt

# 7. 確認 .env 檔案中有 MongoDB 設定
# MONGODB_URI=mongodb://localhost:27017/

# 8. 啟動專案
python run.py
```

## 相關資源

- [MongoDB 官方文件](https://docs.mongodb.com/)
- [MongoDB Compass 下載](https://www.mongodb.com/try/download/compass)
- [Homebrew 官方網站](https://brew.sh/)

## 注意事項

1. **資料持久化**：MongoDB 的資料預設儲存在 `/opt/homebrew/var/mongodb/`（使用 Homebrew 安裝）
2. **自動啟動**：使用 `brew services start` 可以讓 MongoDB 在開機時自動啟動
3. **安全性**：預設安裝的 MongoDB 沒有啟用認證，僅適合開發環境使用
4. **版本相容性**：建議使用 MongoDB 7.0 或更新版本

---

如有問題，請檢查：
1. MongoDB 服務狀態
2. 後端應用程式日誌
3. MongoDB 日誌檔案

