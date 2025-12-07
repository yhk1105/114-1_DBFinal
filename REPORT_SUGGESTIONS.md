# 期末專案報告撰寫建議指南

這份指南是根據你的程式碼庫（特別是 `backend/app/services`）分析而來，目的是協助你完成期末報告中的「系統實作」、「交易管理」與「併行控制」章節。

你的專案程式碼品質很高，包含了許多進階的資料庫觀念（如 Isolation Levels, CTEs, Explicit Locking, Retry Logic），這些都是報告中的加分亮點。

---

## 1. 值得寫入報告的關鍵交易 (Key Transactions)

在報告的「系統實作」或「交易管理」章節，建議挑選以下 2-3 個最具代表性的交易來詳細說明。

### 交易一：建立預約 (Create Reservation)
*   **對應程式碼**: `backend/app/services/reservation_service.py` 中的 `create_reservation`
*   **為什麼值得寫**: 這是整個系統最核心、邏輯最複雜的交易。它不僅僅是寫入一筆資料，還牽涉到跨資料表的檢查與更新。
*   **涉及步驟 (ACID 原子性展示)**:
    1.  **權限檢查**: 確認 Token 與會員資格。
    2.  **設定隔離層級**: `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE` (最高規格)。
    3.  **寫入主表**: 建立 `Reservation` 紀錄。
    4.  **迴圈處理細項**: 針對每個預約物品 (`rd_list`)：
        *   **時間衝突檢查**: 使用 SQL `OVERLAPS` 運算子檢查時間重疊，並使用 `FOR UPDATE` 鎖定相關預約細節。
        *   **黑名單檢查**: 檢查使用者是否被該類別 (Category) 禁止 (Category Ban)。
        *   **貢獻度檢查 (重點)**: 使用 **遞迴查詢 (Recursive CTE)** 檢查使用者在該類別樹狀結構下是否有活躍的貢獻 (`contribution`)，並將其標記為已使用 (`is_active = true`)。這是為了防止「一稿多投」或是「無貢獻借物」。
        *   **寫入細項**: 建立 `ReservationDetail`。
    5.  **Commit/Rollback**: 全部成功才 Commit，任何一步失敗（如時間衝突、資格不符）則全面 Rollback。

### 交易二：物品更新與併發重試 (Item Update with Retry Logic)
*   **對應程式碼**: `backend/app/services/item_service.py` 中的 `update_item`
*   **為什麼值得寫**: 這個功能展示了「應用層面的併行控制」，特別是你實作了 **Retry (重試) 機制**。
*   **涉及步驟**:
    1.  **狀態檢查**: 檢查物品是否被借出，若被借出則禁止修改特定欄位。
    2.  **連鎖更新**: 修改物品類別 (`c_id`) 或狀態 (`status`) 時，可能需要連帶更新 `contribution` 表的狀態，甚至觸發重新審核。
    3.  **異常處理**: 捕捉 `Serialization Failure` (PostgreSQL error 40001) 或 `Deadlock`。
    4.  **指數退避 (Exponential Backoff)**: 遇到併發衝突時，程式會暫停一段時間 (`time.sleep`) 後重試，最多重試 3 次。這在資料庫報告中是非常專業的實作細節。

### 交易三：取消預約與歸還權益 (Cancel Reservation)
*   **對應程式碼**: `backend/app/services/reservation_service.py` 中的 `delete_reservation`
*   **為什麼值得寫**: 這是 `create_reservation` 的反向操作，展示了如何正確地「復原」使用者的權益。
*   **涉及步驟**:
    1.  **時間限制檢查**: 檢查是否在 24 小時前。
    2.  **尋找並恢復權益**: 透過遞迴查詢找到該使用者在該類別下一個 `inactive` 的 `contribution`，將其改回 `active = true` (歸還借物權限)。
    3.  **Soft Delete**: 更新 `is_deleted = true` 而非物理刪除資料。

---

## 2. 交易控制與併行控制 (Transaction & Concurrency Control)

這部分對應報告中的「3.2.3 系統實作 - 交易管理和併行控制」以及評分標準的 (d) 項。

### (1) 隔離層級 (Isolation Levels)
*   **你的實作**: 你的程式碼在關鍵交易中顯式地設定了 **SERIALIZABLE** 隔離層級。
    ```python
    db.session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
    ```
*   **報告論述點**:
    *   說明為什麼選擇 SERIALIZABLE（為了資料絕對一致性，防止 Phantom Read, Non-repeatable Read, Dirty Read）。
    *   特別是在「檢查庫存/時間衝突」後緊接著「寫入預約」的過程中，如果沒有足夠的隔離層級，可能會發生 **Race Condition**（兩人同時訂到同一時段）。

### (2) 應用層重試機制 (Application-side Retry Logic)
*   **你的實作**: 在 `item_service.py` 中使用了 `try...except OperationalError` 搭配 `max_retries`。
*   **報告論述點**:
    *   當資料庫隔離層級很高 (Serializable) 時，資料庫更有可能因為偵測到衝突而拋出錯誤 (Serialization Failure)。
    *   你透過在應用層實作重試邏輯，解決了這個副作用，提升了使用者體驗（使用者不需要手動重按，系統會自動重試）。

---

## 3. 鎖定機制 (Locking)

這部分可以用來補充說明你是如何避免 Race Condition。

### (1) 顯式列鎖定 (Explicit Row Locking - FOR UPDATE)
*   **位置**: `check_item_available` 函數中。
    ```sql
    SELECT ... FROM reservation_detail ... FOR UPDATE OF rd
    ```
*   **論述**: 在檢查某個時段是否被佔用時，你鎖定了相關的 `reservation_detail` 列。這確保了在檢查完成直到交易結束前，沒有其他交易可以修改這些紀錄，防止了「檢查時沒衝突，寫入時卻衝突」的情況。

### (2) 貢獻度鎖定 (Contribution Locking)
*   **位置**: `create_reservation` 函數中。
    ```sql
    SELECT ... FROM contribution ... FOR UPDATE OF contribution
    ```
*   **論述**: 這是為了防止「雙重花費 (Double Spending)」。如果不鎖定，同一個使用者可能開啟兩個視窗，同時送出預約請求，兩邊都讀到該使用者有「1 個可用貢獻」，導致他用 1 個貢獻借了 2 樣物品。鎖定後，第一個交易會先拿走權限，第二個交易在讀取時就會被擋住（或讀到已使用）。

---

## 4. 進階 SQL 技巧 (Bonus)

這些雖不是直接的交易控制，但展示了你對 SQL 的掌握度，適合放在「系統實作」的 SQL 指令說明中。

*   **遞迴查詢 (Recursive CTE)**:
    *   在 `check_contribution` 和 `get_category_items` 中使用了 `WITH RECURSIVE`。
    *   用來處理「類別樹 (Category Tree)」，例如借用「球類」權限可以涵蓋「籃球」、「足球」等子類別。這在資料庫設計上是處理階層資料的標準做法。
*   **時間重疊運算子 (OVERLAPS)**:
    *   在 `check_item_available` 中使用了 `(start, end) OVERLAPS (start, end)`。
    *   這是標準 SQL 處理時間區間衝突最優雅的方式，比手寫 `(start1 <= end2) AND (end1 >= start2)` 更易讀且不易出錯。

