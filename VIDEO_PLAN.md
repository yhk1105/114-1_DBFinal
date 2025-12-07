# 期末專案展示影片與簡報規劃 (Video & Presentation Plan)

這份規劃是根據 `project_guidline.txt` 的要求量身打造，目標是讓你在 10-15 分鐘內，不僅展示功能，還能清楚呈現「資料庫設計」與「併行控制」這兩個拿分重點。

---

## 一、 簡報架構 (Presentation Slides)

依規定你需要製作投影片並轉為 PDF 繳交，建議約 8-10 頁。影片的前 2-3 分鐘與最後 1-2 分鐘配合投影片解說。

| 頁數 | 標題 | 內容重點 |
| :--- | :--- | :--- |
| **P1** | **首頁** | 專案名稱、組別、組員學號姓名。 |
| **P2** | **專案動機與解決方案** | 為什麼做這個系統？解決什麼問題？(例如：校園閒置物品流通平台)。 |
| **P3** | **系統架構 (System Architecture)** | 簡單的架構圖：Client (Terminal UI) <-> Backend (Flask) <-> DB (PostgreSQL + MongoDB)。 |
| **P4** | **資料庫設計 (ER Diagram)** | 放上你的 ER Diagram。簡單解釋核心 Table 關聯 (Member, Item, Reservation, Loan)。 |
| **P5** | **NoSQL 的應用** | 說明 MongoDB 用在哪裡 (Funnel Tracker / Log)，為什麼這裡適合用 NoSQL。 |
| **P6** | **資料庫優化與索引** | 說明你在哪些欄位加了 Index，以及對 Query 效能的分析 (Explain Analyze)。 |
| **P7** | **關鍵技術：交易與併行控制** | **(重要)** 列出你的策略：Isolation Level (Serializable)、Locking (FOR UPDATE)、Retry 機制。 |
| **P8** | **分工與心得** | 簡述分工表、遇到的困難與心得。 |

---

## 二、 影片流程規劃 (10-15 分鐘)

### 第一部分：前導與介紹 (約 2-3 分鐘)
*   **畫面**：播放投影片 (P1-P3)。
*   **旁白**：快速介紹專案主題、解決的問題、系統架構。重點在於讓助教知道這是一個完整的 Client-Server 架構。

### 第二部分：功能展示 (約 4-5 分鐘)
*   **畫面**：電腦桌面，**同時開啟兩個 Terminal 視窗** (分別登入 User A 和 User B)。
*   **旁白**：
    1.  **註冊/登入**：快速帶過。
    2.  **一般使用者功能**：User A 上架物品、User B 瀏覽物品、User B 預約物品、User A 審核/查看。
    3.  **NoSQL 展示**：操作幾個動作後，展示 MongoDB 裡紀錄的 Log 或 Funnel 數據。

### 第三部分：技術深究 - 併行控制 Demo (約 3-4 分鐘) ★★★ 加分關鍵
*   **畫面**：兩個 Terminal 並排，展示「搶預約」或「資料更新衝突」的過程。
*   **情境**：這部分需要展示「當兩個人同時想預約同一個時段」時，系統如何保護資料一致性。
*   *(詳細操作請參考下方「併行控制示範劇本」)*

### 第四部分：設計理念與結尾 (約 2-3 分鐘)
*   **畫面**：切回投影片 (P4-P8)。
*   **旁白**：
    1.  解說 ER Diagram 的正規化考量。
    2.  解釋剛剛 Demo 的技術原理 (Serializable, Locking)。
    3.  心得與未來展望。

---

## 三、 併行控制與上鎖示範劇本 (Concurrency Control Demo)

為了在影片中清楚展示「鎖定 (Locking)」的效果，建議使用 **「人工延遲法」**。
因為電腦執行速度太快，肉眼很難看到「Blocked (被擋住)」的瞬間，我們可以在程式碼中暫時加入 `time.sleep` 來模擬長時間的交易處理。

### 步驟 1：準備工作 (修改程式碼)
在錄影前，暫時修改 `backend/app/services/reservation_service.py` 的 `create_reservation` 函式。

在 `db.session.commit()` 之前加入延遲：

```python
# ... 在 create_reservation 函式最後面 ...

# [Demo Only] 為了影片展示，加入 10 秒延遲，模擬正在處理複雜邏輯或網路延遲
import time
print(">>> [Demo] Transaction Starting... Sleeping for 10 seconds to simulate long process")
time.sleep(10) 
print(">>> [Demo] Waking up and Committing!")

db.session.commit() # 原本的 commit
return True, {"r_id": new_reservation.r_id}
```

### 步驟 2：錄影操作流程 (雙視窗操作)

**場景**：物品 ID 100 號，User A 和 User B 都想要預約 **同一天 10:00 - 12:00**。

1.  **左邊視窗 (User A)**：
    *   進入預約流程，選好時間 (10:00-12:00)。
    *   **按下 Enter 送出預約**。
    *   *現象*：因為我們加了 `sleep(10)`，User A 的畫面會「卡住/轉圈圈」，後端 Terminal 會顯示 `Sleeping...`。
    *   *旁白*：「現在 User A 送出了預約請求，系統正在處理中（模擬交易尚未 Commit）。」

2.  **右邊視窗 (User B)**：
    *   **在 User A 還在卡住的時候**，User B 迅速選好 **相同時間 (10:00-12:00)**。
    *   **按下 Enter 送出預約**。
    *   *現象*：
        *   因為你有用 `FOR UPDATE` 鎖定相關資料列 (Reservation Detail) 或是因為 `SERIALIZABLE` 隔離層級，User B 的交易會發生以下兩種情況之一（看你的 DB 設定）：
            *   **情況 1 (Blocking)**：User B 的視窗也「卡住」，他在等待 User A 釋放鎖定。
            *   **情況 2 (Immediate Fail)**：如果是 `NOWAIT` 模式，User B 會馬上收到錯誤訊息。
        *   *(建議展示情況 1，視覺效果較好，代表資料庫正在排隊)*

3.  **結果揭曉**：
    *   10 秒後，User A 的畫面顯示 **「預約成功」**。
    *   緊接著，User B 的畫面解除卡住狀態，但顯示 **「預約失敗：時間衝突」** (或類似的錯誤訊息)。

### 步驟 3：旁白解說 (重要)
這時候你要搭配旁白解釋發生了什麼事：
> 「各位可以看到，當 User A 的交易還沒結束（還沒 Commit）時，我們使用了 `SERIALIZABLE` 隔離層級加上 `FOR UPDATE` 鎖，這導致 User B 的請求會被資料庫暫時擋住（Block），直到 User A 完成後，User B 才能繼續執行。當 User B 繼續執行時，會發現時間已經被佔用了，因此預約失敗。這證明了我們的系統能有效防止『重複預約 (Double Booking)』的問題。」

---

## 四、 備忘錄：錄影前檢查清單

1.  [ ] 確認資料庫內有足夠的範例資料（至少要有幾個物品、分類）。
2.  [ ] 確認 `requirements.txt` 已經安裝完畢，兩個 Frontend Terminal 都能順利連上 Backend。
3.  [ ] **記得錄影完要把 `time.sleep(10)` 移除！**
4.  [ ] 準備好投影片 PDF。
5.  [ ] 測試麥克風收音清楚。

祝你錄影順利！這個 Demo 絕對會讓助教印象深刻。

