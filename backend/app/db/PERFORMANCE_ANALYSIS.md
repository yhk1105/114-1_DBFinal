# 資料庫效能分析與優化報告

## 1. 最複雜查詢識別與分析

### 1.1 系統最關鍵的複雜查詢

經過分析，我們識別出系統中最複雜、執行時間最長的查詢為：**預約時的貢獻檢查（Reservation Contribution Check）**

**查詢位置：** [reservation_service.py:145-171](../services/reservation_service.py#L145-L171)

**查詢內容：**
```sql
-- 檢查用戶在 root category 下是否有 active contribution
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND item.c_id IN (
    -- 遞迴查詢 root category 下的所有子類別
    WITH RECURSIVE category_tree AS (
        SELECT c_id FROM category WHERE c_id = :root_c_id
        UNION ALL
        SELECT c.c_id FROM category c
        JOIN category_tree ct ON c.parent_c_id = ct.c_id
    )
    SELECT c_id FROM category_tree
)
LIMIT 1
FOR UPDATE OF contribution;
```

**複雜度來源：**
1. **遞迴查詢（WITH RECURSIVE）**：需要遍歷整個分類樹
2. **多表 JOIN**：contribution + item + category（遞迴）
3. **併發鎖定（FOR UPDATE）**：防止並發問題
4. **高頻執行**：每次預約都會執行此查詢

---

## 2. 測試資料準備

### 2.1 大量測試資料生成

為了準確測試效能，我們需要生成大量測試資料：

**目標資料量：**
- **Category:** 500 筆（5 層樹狀結構，每層約 100 個分類）
- **Member:** 10,000 筆
- **Item:** 100,000 筆
- **Contribution:** 100,000 筆
- **Reservation:** 50,000 筆
- **Reservation_detail:** 200,000 筆

### 2.2 測試資料生成腳本

```sql
-- generate_test_data.sql

-- 1. 生成分類樹（5 層，每層 100 個節點）
DO $$
DECLARE
    root_id BIGINT;
    level1_id BIGINT;
    level2_id BIGINT;
    level3_id BIGINT;
    i INT;
    j INT;
    k INT;
    l INT;
BEGIN
    -- Root categories (10 個)
    FOR i IN 1..10 LOOP
        INSERT INTO category (c_name, parent_c_id)
        VALUES ('Root_' || i, NULL)
        RETURNING c_id INTO root_id;

        -- Level 1 (每個 root 10 個子類別)
        FOR j IN 1..10 LOOP
            INSERT INTO category (c_name, parent_c_id)
            VALUES ('Root_' || i || '_L1_' || j, root_id)
            RETURNING c_id INTO level1_id;

            -- Level 2 (每個 L1 5 個子類別)
            FOR k IN 1..5 LOOP
                INSERT INTO category (c_name, parent_c_id)
                VALUES ('Root_' || i || '_L1_' || j || '_L2_' || k, level1_id)
                RETURNING c_id INTO level2_id;

                -- Level 3 (每個 L2 2 個子類別)
                FOR l IN 1..2 LOOP
                    INSERT INTO category (c_name, parent_c_id)
                    VALUES ('Root_' || i || '_L1_' || j || '_L2_' || k || '_L3_' || l, level2_id);
                END LOOP;
            END LOOP;
        END LOOP;
    END LOOP;

    RAISE NOTICE 'Generated % categories', (SELECT COUNT(*) FROM category);
END $$;

-- 2. 生成會員資料（10,000 筆）
INSERT INTO member (m_name, m_mail, m_password, is_active)
SELECT
    'member_' || i,
    'member_' || i || '@test.com',
    '$2b$12$dummypasswordhash',
    true
FROM generate_series(1, 10000) AS i;

-- 3. 生成物品資料（100,000 筆）
INSERT INTO item (i_name, status, description, out_duration, m_id, c_id)
SELECT
    'item_' || i,
    CASE (random() * 3)::int
        WHEN 0 THEN 'Reservable'
        WHEN 1 THEN 'Not verified'
        WHEN 2 THEN 'Borrowed'
        ELSE 'Not reservable'
    END,
    'Description for item ' || i,
    (random() * 30 + 1)::int * 86400, -- 1-30 天（秒）
    (random() * 9999 + 1)::bigint, -- 隨機 member
    (SELECT c_id FROM category ORDER BY random() LIMIT 1) -- 隨機 category
FROM generate_series(1, 100000) AS i;

-- 4. 生成貢獻資料（100,000 筆）
INSERT INTO contribution (m_id, i_id, is_active)
SELECT
    m_id,
    i_id,
    CASE WHEN random() < 0.3 THEN true ELSE false END -- 30% active
FROM item;

-- 5. 生成預約資料（50,000 筆）
INSERT INTO reservation (m_id, create_at, is_deleted)
SELECT
    (random() * 9999 + 1)::bigint,
    NOW() - (random() * 365 || ' days')::interval,
    CASE WHEN random() < 0.1 THEN true ELSE false END -- 10% deleted
FROM generate_series(1, 50000) AS i;

-- 6. 生成預約詳細資料（200,000 筆，每個預約 4 個物品）
INSERT INTO reservation_detail (r_id, i_id, p_id, est_start_at, est_due_at)
SELECT
    r.r_id,
    (random() * 99999 + 1)::bigint, -- 隨機 item
    (random() * 4 + 1)::bigint, -- 隨機取貨地點
    NOW() + (random() * 180 || ' days')::interval,
    NOW() + (random() * 180 + 7 || ' days')::interval
FROM reservation r
CROSS JOIN generate_series(1, 4);

-- 7. 更新統計資訊
VACUUM ANALYZE;

-- 8. 顯示資料量
SELECT 'category' AS table_name, COUNT(*) FROM category
UNION ALL
SELECT 'member', COUNT(*) FROM member
UNION ALL
SELECT 'item', COUNT(*) FROM item
UNION ALL
SELECT 'contribution', COUNT(*) FROM contribution
UNION ALL
SELECT 'reservation', COUNT(*) FROM reservation
UNION ALL
SELECT 'reservation_detail', COUNT(*) FROM reservation_detail;
```

---

## 3. 效能測試方案

### 3.1 測試環境設定

```sql
-- 測試前準備
SET work_mem = '256MB';
SET maintenance_work_mem = '512MB';
SET shared_buffers = '1GB';

-- 確保統計資訊是最新的
ANALYZE category;
ANALYZE item;
ANALYZE contribution;
```

### 3.2 測試案例設計

我們將測試 **4 種不同的查詢寫法 + 3 種索引配置**，共 12 種組合：

#### 方案 A：原始查詢（子查詢 + IN）
```sql
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND item.c_id IN (
    WITH RECURSIVE category_tree AS (
        SELECT c_id FROM category WHERE c_id = :root_c_id
        UNION ALL
        SELECT c.c_id FROM category c
        JOIN category_tree ct ON c.parent_c_id = ct.c_id
    )
    SELECT c_id FROM category_tree
)
LIMIT 1;
```

#### 方案 B：改用 EXISTS（可能更快）
```sql
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND EXISTS (
    WITH RECURSIVE category_tree AS (
        SELECT c_id FROM category WHERE c_id = :root_c_id
        UNION ALL
        SELECT c.c_id FROM category c
        JOIN category_tree ct ON c.parent_c_id = ct.c_id
    )
    SELECT 1 FROM category_tree WHERE category_tree.c_id = item.c_id
)
LIMIT 1;
```

#### 方案 C：JOIN 遞迴查詢結果（可能有不同的執行計畫）
```sql
WITH RECURSIVE category_tree AS (
    SELECT c_id FROM category WHERE c_id = :root_c_id
    UNION ALL
    SELECT c.c_id FROM category c
    JOIN category_tree ct ON c.parent_c_id = ct.c_id
)
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
JOIN category_tree ON item.c_id = category_tree.c_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
LIMIT 1;
```

#### 方案 D：物化 CTE（強制先計算分類樹）
```sql
WITH RECURSIVE category_tree AS (
    SELECT c_id FROM category WHERE c_id = :root_c_id
    UNION ALL
    SELECT c.c_id FROM category c
    JOIN category_tree ct ON c.parent_c_id = ct.c_id
)
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND item.c_id = ANY(ARRAY(SELECT c_id FROM category_tree))
LIMIT 1;
```

### 3.3 索引配置

#### 配置 1：無索引（基準線）
```sql
-- 移除所有索引（測試用）
DROP INDEX IF EXISTS idx_category_parent_c_id;
DROP INDEX IF EXISTS idx_contribution_active;
DROP INDEX IF EXISTS idx_item_c_id;
```

#### 配置 2：基本索引
```sql
CREATE INDEX idx_category_parent_c_id ON category(parent_c_id);
CREATE INDEX idx_contribution_m_id ON contribution(m_id);
CREATE INDEX idx_item_c_id ON item(c_id);
```

#### 配置 3：優化索引（部分索引 + 覆蓋索引）
```sql
CREATE INDEX idx_category_parent_c_id ON category(parent_c_id);
CREATE INDEX idx_category_parent_with_name ON category(parent_c_id) INCLUDE (c_name);
CREATE INDEX idx_contribution_active ON contribution(m_id, is_active) WHERE is_active = true;
CREATE INDEX idx_item_c_id ON item(c_id);
```

---

## 4. 效能測試腳本

### 4.1 測試執行腳本

```sql
-- performance_test.sql

-- 變數設定
\set m_id 100
\set root_c_id 1

-- 清除快取（模擬冷啟動）
DISCARD PLANS;

-- ============================================================
-- 測試 1：方案 A + 配置 1（無索引）
-- ============================================================
\echo '=========================================='
\echo 'Test 1: Query A + No Index'
\echo '=========================================='

EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND item.c_id IN (
    WITH RECURSIVE category_tree AS (
        SELECT c_id FROM category WHERE c_id = :root_c_id
        UNION ALL
        SELECT c.c_id FROM category c
        JOIN category_tree ct ON c.parent_c_id = ct.c_id
    )
    SELECT c_id FROM category_tree
)
LIMIT 1;

-- 重複執行 10 次取平均（模擬熱啟動）
\timing on
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND item.c_id IN (
    WITH RECURSIVE category_tree AS (
        SELECT c_id FROM category WHERE c_id = :root_c_id
        UNION ALL
        SELECT c.c_id FROM category c
        JOIN category_tree ct ON c.parent_c_id = ct.c_id
    )
    SELECT c_id FROM category_tree
)
LIMIT 1;
-- 重複 9 次...
\timing off

-- ============================================================
-- 測試 2：方案 A + 配置 2（基本索引）
-- ============================================================
CREATE INDEX idx_category_parent_c_id ON category(parent_c_id);
CREATE INDEX idx_contribution_m_id ON contribution(m_id);
CREATE INDEX idx_item_c_id ON item(c_id);

ANALYZE;

\echo '=========================================='
\echo 'Test 2: Query A + Basic Index'
\echo '=========================================='

EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND item.c_id IN (
    WITH RECURSIVE category_tree AS (
        SELECT c_id FROM category WHERE c_id = :root_c_id
        UNION ALL
        SELECT c.c_id FROM category c
        JOIN category_tree ct ON c.parent_c_id = ct.c_id
    )
    SELECT c_id FROM category_tree
)
LIMIT 1;

-- [重複測試...]

-- ============================================================
-- 測試 3：方案 A + 配置 3（優化索引）
-- ============================================================
DROP INDEX idx_contribution_m_id;
CREATE INDEX idx_contribution_active ON contribution(m_id, is_active) WHERE is_active = true;

ANALYZE;

\echo '=========================================='
\echo 'Test 3: Query A + Optimized Index'
\echo '=========================================='

EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND item.c_id IN (
    WITH RECURSIVE category_tree AS (
        SELECT c_id FROM category WHERE c_id = :root_c_id
        UNION ALL
        SELECT c.c_id FROM category c
        JOIN category_tree ct ON c.parent_c_id = ct.c_id
    )
    SELECT c_id FROM category_tree
)
LIMIT 1;

-- [繼續測試其他方案...]
```

### 4.2 自動化測試腳本（Python）

```python
# performance_benchmark.py
import psycopg2
import time
import statistics
from typing import List, Dict

def run_query_benchmark(
    conn,
    query: str,
    params: dict,
    iterations: int = 10
) -> Dict:
    """執行查詢並測量效能"""
    cursor = conn.cursor()
    times = []

    # 預熱
    cursor.execute(query, params)
    cursor.fetchall()

    # 測試
    for _ in range(iterations):
        start = time.perf_counter()
        cursor.execute(query, params)
        cursor.fetchall()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # 轉換為毫秒

    return {
        'min': min(times),
        'max': max(times),
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'raw_times': times
    }

def get_explain_analyze(conn, query: str, params: dict) -> str:
    """取得 EXPLAIN ANALYZE 結果"""
    cursor = conn.cursor()
    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE) {query}"
    cursor.execute(explain_query, params)
    return '\n'.join([row[0] for row in cursor.fetchall()])

# 測試配置
QUERIES = {
    'A_IN': """
        SELECT contribution.i_id
        FROM contribution
        JOIN item ON contribution.i_id = item.i_id
        WHERE contribution.m_id = %(m_id)s
        AND contribution.is_active = true
        AND item.c_id IN (
            WITH RECURSIVE category_tree AS (
                SELECT c_id FROM category WHERE c_id = %(root_c_id)s
                UNION ALL
                SELECT c.c_id FROM category c
                JOIN category_tree ct ON c.parent_c_id = ct.c_id
            )
            SELECT c_id FROM category_tree
        )
        LIMIT 1
    """,
    'B_EXISTS': """
        SELECT contribution.i_id
        FROM contribution
        JOIN item ON contribution.i_id = item.i_id
        WHERE contribution.m_id = %(m_id)s
        AND contribution.is_active = true
        AND EXISTS (
            WITH RECURSIVE category_tree AS (
                SELECT c_id FROM category WHERE c_id = %(root_c_id)s
                UNION ALL
                SELECT c.c_id FROM category c
                JOIN category_tree ct ON c.parent_c_id = ct.c_id
            )
            SELECT 1 FROM category_tree WHERE category_tree.c_id = item.c_id
        )
        LIMIT 1
    """,
    'C_JOIN': """
        WITH RECURSIVE category_tree AS (
            SELECT c_id FROM category WHERE c_id = %(root_c_id)s
            UNION ALL
            SELECT c.c_id FROM category c
            JOIN category_tree ct ON c.parent_c_id = ct.c_id
        )
        SELECT contribution.i_id
        FROM contribution
        JOIN item ON contribution.i_id = item.i_id
        JOIN category_tree ON item.c_id = category_tree.c_id
        WHERE contribution.m_id = %(m_id)s
        AND contribution.is_active = true
        LIMIT 1
    """,
    'D_ARRAY': """
        WITH RECURSIVE category_tree AS (
            SELECT c_id FROM category WHERE c_id = %(root_c_id)s
            UNION ALL
            SELECT c.c_id FROM category c
            JOIN category_tree ct ON c.parent_c_id = ct.c_id
        )
        SELECT contribution.i_id
        FROM contribution
        JOIN item ON contribution.i_id = item.i_id
        WHERE contribution.m_id = %(m_id)s
        AND contribution.is_active = true
        AND item.c_id = ANY(ARRAY(SELECT c_id FROM category_tree))
        LIMIT 1
    """
}

INDEX_CONFIGS = {
    'no_index': [],
    'basic': [
        "CREATE INDEX idx_category_parent_c_id ON category(parent_c_id)",
        "CREATE INDEX idx_contribution_m_id ON contribution(m_id)",
        "CREATE INDEX idx_item_c_id ON item(c_id)"
    ],
    'optimized': [
        "CREATE INDEX idx_category_parent_c_id ON category(parent_c_id)",
        "CREATE INDEX idx_category_parent_with_name ON category(parent_c_id) INCLUDE (c_name)",
        "CREATE INDEX idx_contribution_active ON contribution(m_id, is_active) WHERE is_active = true",
        "CREATE INDEX idx_item_c_id ON item(c_id)"
    ]
}

def main():
    conn = psycopg2.connect(
        host="localhost",
        database="our_things",
        user="postgres",
        password="your_password"
    )

    results = []

    for config_name, index_sqls in INDEX_CONFIGS.items():
        print(f"\n{'='*60}")
        print(f"Testing Index Configuration: {config_name}")
        print(f"{'='*60}")

        # 清除所有索引
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 'DROP INDEX IF EXISTS ' || indexname || ';'
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexname LIKE 'idx_%'
        """)
        for row in cursor.fetchall():
            cursor.execute(row[0])
        conn.commit()

        # 建立索引
        for sql in index_sqls:
            cursor.execute(sql)
        conn.commit()
        cursor.execute("ANALYZE")
        conn.commit()

        # 測試每個查詢
        for query_name, query in QUERIES.items():
            print(f"\n  Testing Query: {query_name}")

            params = {'m_id': 100, 'root_c_id': 1}

            # 效能測試
            perf = run_query_benchmark(conn, query, params)

            # EXPLAIN ANALYZE
            explain = get_explain_analyze(conn, query, params)

            results.append({
                'config': config_name,
                'query': query_name,
                'performance': perf,
                'explain': explain
            })

            print(f"    Mean: {perf['mean']:.2f}ms")
            print(f"    Median: {perf['median']:.2f}ms")
            print(f"    StdDev: {perf['stdev']:.2f}ms")

    # 生成報告
    generate_report(results)

    conn.close()

def generate_report(results: List[Dict]):
    """生成 Markdown 格式的報告"""
    with open('performance_report.md', 'w') as f:
        f.write("# 效能測試報告\n\n")
        f.write("## 測試結果摘要\n\n")

        # 建立表格
        f.write("| 索引配置 | 查詢方案 | 平均時間 (ms) | 中位數 (ms) | 標準差 (ms) |\n")
        f.write("|---------|---------|--------------|------------|------------|\n")

        for r in results:
            f.write(f"| {r['config']} | {r['query']} | "
                   f"{r['performance']['mean']:.2f} | "
                   f"{r['performance']['median']:.2f} | "
                   f"{r['performance']['stdev']:.2f} |\n")

        # 詳細 EXPLAIN 結果
        f.write("\n## 詳細執行計畫\n\n")
        for r in results:
            f.write(f"### {r['config']} - {r['query']}\n\n")
            f.write("```\n")
            f.write(r['explain'])
            f.write("\n```\n\n")

if __name__ == '__main__':
    main()
```

---

## 5. 預期測試結果

### 5.1 效能提升預估

基於理論分析，我們預期：

| 配置 | 查詢方案 | 預期執行時間 | 提升倍數 |
|------|---------|------------|---------|
| 無索引 | A (IN) | 500-1000ms | 基準 |
| 無索引 | B (EXISTS) | 400-800ms | 1.2x |
| 無索引 | C (JOIN) | 450-900ms | 1.1x |
| 無索引 | D (ARRAY) | 600-1200ms | 0.8x |
| 基本索引 | A (IN) | 50-100ms | **10-20x** ⭐ |
| 基本索引 | B (EXISTS) | 40-80ms | **12-25x** ⭐ |
| 基本索引 | C (JOIN) | 30-60ms | **16-33x** ⭐⭐ |
| 基本索引 | D (ARRAY) | 80-120ms | 6-12x |
| 優化索引 | A (IN) | 20-40ms | **25-50x** ⭐⭐ |
| 優化索引 | B (EXISTS) | 15-30ms | **33-66x** ⭐⭐ |
| 優化索引 | C (JOIN) | **10-20ms** | **50-100x** ⭐⭐⭐ |
| 優化索引 | D (ARRAY) | 30-50ms | 20-33x |

### 5.2 最佳組合預測

**最優方案：方案 C (JOIN) + 優化索引配置**

**原因：**
1. JOIN 允許 PostgreSQL 優化器選擇最佳 JOIN 順序
2. 部分索引 `idx_contribution_active` 大幅減少掃描範圍
3. 覆蓋索引避免回表
4. 遞迴查詢受益於 `idx_category_parent_c_id`

---

## 6. 報告撰寫建議

### 6.1 報告結構

```markdown
## SQL 查詢優化與索引效能分析

### 1. 最複雜查詢識別
- 查詢功能說明
- 為何是最複雜的查詢（多表 JOIN + 遞迴 + 高頻）
- 業務重要性

### 2. 測試資料準備
- 資料量設計（100萬筆級別）
- 資料分佈特性
- 生成方法

### 3. 優化方案設計
- 4 種不同 SQL 寫法
- 3 種索引配置
- 共 12 種測試組合

### 4. 效能測試結果
- 詳細測試數據表格
- EXPLAIN ANALYZE 執行計畫分析
- 效能提升倍數對比圖表

### 5. 最佳方案與結論
- 最終選擇的 SQL 寫法
- 最終選擇的索引配置
- 實際效能提升數據（例如：從 800ms 降至 15ms，提升 53 倍）

### 6. 索引設計決策
- 為何選擇部分索引（Partial Index）
- 為何選擇覆蓋索引（Covering Index）
- 空間成本 vs 效能收益分析
```

### 6.2 圖表建議

1. **執行時間對比圖**（柱狀圖）
2. **不同查詢方案效能對比**（折線圖）
3. **索引配置效能提升**（雷達圖）
4. **EXPLAIN 執行計畫樹狀圖**

---

## 7. 執行步驟總結

1. **準備測試環境**
   ```bash
   # 建立測試資料庫
   psql -U postgres -c "CREATE DATABASE test_performance"

   # 載入 schema
   psql -U postgres -d test_performance -f schema.sql

   # 生成測試資料
   psql -U postgres -d test_performance -f generate_test_data.sql
   ```

2. **執行效能測試**
   ```bash
   # 手動測試
   psql -U postgres -d test_performance -f performance_test.sql > results.txt

   # 或使用 Python 自動化
   python3 performance_benchmark.py
   ```

3. **分析結果**
   - 查看 `performance_report.md`
   - 比較不同方案的 EXPLAIN ANALYZE
   - 識別瓶頸

4. **撰寫報告**
   - 整理測試數據
   - 繪製圖表
   - 說明優化決策

---

## 8. 額外優化建議

### 8.1 快取策略

對於頻繁查詢的 root category 結果，可以使用應用層快取：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_root_category_cached(session, c_id: int) -> int:
    """帶快取的 root category 查詢"""
    return get_root_category(session, c_id)
```

### 8.2 物化視圖（Materialized View）

對於極少變動的分類樹，可以建立物化視圖：

```sql
CREATE MATERIALIZED VIEW category_tree_paths AS
WITH RECURSIVE tree AS (
    SELECT c_id, c_id as root_c_id, ARRAY[c_id] as path
    FROM category WHERE parent_c_id IS NULL

    UNION ALL

    SELECT c.c_id, t.root_c_id, t.path || c.c_id
    FROM category c
    JOIN tree t ON c.parent_c_id = t.c_id
)
SELECT * FROM tree;

CREATE INDEX idx_cat_tree_c_id ON category_tree_paths(c_id);
CREATE INDEX idx_cat_tree_root ON category_tree_paths(root_c_id);

-- 定期更新
REFRESH MATERIALIZED VIEW CONCURRENTLY category_tree_paths;
```

使用物化視圖後的查詢：

```sql
SELECT contribution.i_id
FROM contribution
JOIN item ON contribution.i_id = item.i_id
JOIN category_tree_paths ctp ON item.c_id = ctp.c_id
WHERE contribution.m_id = :m_id
AND contribution.is_active = true
AND ctp.root_c_id = :root_c_id
LIMIT 1;
```

預期效能：**5-10ms**，提升 **100-200x** 🚀

---

**文件版本：** v1.0
**最後更新：** 2025-12-06
**測試目標：** 100 萬筆資料級別的效能驗證
