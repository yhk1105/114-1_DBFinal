#!/usr/bin/env python3
"""
查詢效能測試腳本

測試 3 個最複雜查詢的執行時間，並比較不同索引配置的效能差異。
"""

import psycopg2
import time
import statistics
import argparse
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

# 資料庫連線設定
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'your_database'),
    'user': os.getenv('DB_USER', 'your_user'),
    'password': os.getenv('DB_PASSWORD', 'your_password')
}


def get_connection():
    """建立資料庫連線"""
    return psycopg2.connect(**DB_CONFIG)


def clear_cache(conn):
    """清空資料庫 cache"""
    cursor = conn.cursor()
    cursor.execute("DISCARD ALL;")
    conn.commit()


def benchmark_time_conflict_check(conn, iterations=100) -> List[float]:
    """
    測試查詢 1：時間衝突檢查（OVERLAPS）

    這是系統中最複雜的查詢之一，每次預約都會執行。
    """
    cursor = conn.cursor()
    times = []

    # 獲取隨機的 item_id
    cursor.execute("SELECT i_id FROM item WHERE status = 'Reservable' ORDER BY RANDOM() LIMIT 100;")
    item_ids = [row[0] for row in cursor.fetchall()]

    print(f"  測試時間衝突檢查查詢（{iterations} 次）...")

    for i in range(iterations):
        item_id = item_ids[i % len(item_ids)]
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)

        # 清空 cache
        if i % 10 == 0:
            clear_cache(conn)

        query_start = time.time()
        cursor.execute("""
            SELECT rd.rd_id
            FROM reservation_detail rd
            JOIN reservation r ON rd.r_id = r.r_id
            WHERE rd.i_id = %s
            AND r.is_deleted = false
            AND ((rd.est_start_at, rd.est_due_at) OVERLAPS (%s, %s))
        """, (item_id, start_time, end_time))

        result = cursor.fetchall()
        query_time = (time.time() - query_start) * 1000  # 轉換為毫秒

        times.append(query_time)

        if (i + 1) % 20 == 0:
            print(f"    進度：{i + 1}/{iterations}")

    return times


def benchmark_contribution_check(conn, iterations=100) -> List[float]:
    """
    測試查詢 2：貢獻檢查與遞迴分類查詢

    包含 WITH RECURSIVE 和多層 JOIN，是系統中最複雜的查詢。
    """
    cursor = conn.cursor()
    times = []

    # 獲取隨機的用戶和類別
    cursor.execute("""
        SELECT DISTINCT m.m_id, c.c_id
        FROM member m
        CROSS JOIN category c
        WHERE c.parent_c_id IS NULL
        ORDER BY RANDOM()
        LIMIT 100;
    """)
    test_data = cursor.fetchall()

    print(f"  測試貢獻檢查查詢（{iterations} 次）...")

    for i in range(iterations):
        m_id, root_c_id = test_data[i % len(test_data)]

        # 清空 cache
        if i % 10 == 0:
            clear_cache(conn)

        query_start = time.time()
        cursor.execute("""
            SELECT contribution.i_id
            FROM contribution
            JOIN item ON contribution.i_id = item.i_id
            WHERE contribution.m_id = %s
            AND contribution.is_active = true
            AND item.c_id IN (
                WITH RECURSIVE category_tree AS (
                    SELECT c_id FROM category WHERE c_id = %s
                    UNION ALL
                    SELECT c.c_id FROM category c
                    JOIN category_tree ct ON c.parent_c_id = ct.c_id
                )
                SELECT c_id FROM category_tree
            )
            LIMIT 1
        """, (m_id, root_c_id))

        result = cursor.fetchall()
        query_time = (time.time() - query_start) * 1000

        times.append(query_time)

        if (i + 1) % 20 == 0:
            print(f"    進度：{i + 1}/{iterations}")

    return times


def benchmark_rating_calculation(conn, iterations=100) -> List[float]:
    """
    測試查詢 3：用戶評分計算

    包含 CTE、多層 JOIN 和 AVG() 聚合函數。
    """
    cursor = conn.cursor()
    times = []

    # 獲取隨機用戶
    cursor.execute("SELECT m_id FROM member ORDER BY RANDOM() LIMIT 100;")
    member_ids = [row[0] for row in cursor.fetchall()]

    print(f"  測試評分計算查詢（{iterations} 次）...")

    for i in range(iterations):
        m_id = member_ids[i % len(member_ids)]

        # 清空 cache
        if i % 10 == 0:
            clear_cache(conn)

        query_start = time.time()
        cursor.execute("""
            WITH owner_rate AS (
                SELECT i.m_id, AVG(rv.score) as owner_rate
                FROM review rv
                JOIN loan l ON rv.l_id = l.l_id
                JOIN reservation_detail rd ON l.rd_id = rd.rd_id
                JOIN item i ON rd.i_id = i.i_id
                WHERE rv.reviewee_id = %s AND i.m_id = %s AND rv.is_deleted = false
                GROUP BY i.m_id
            ),
            borrower_rate AS (
                SELECT r.m_id, AVG(rv.score) as borrower_rate
                FROM review rv
                JOIN loan l ON rv.l_id = l.l_id
                JOIN reservation_detail rd ON l.rd_id = rd.rd_id
                JOIN reservation r ON rd.r_id = r.r_id
                WHERE rv.reviewee_id = %s AND r.m_id = %s AND rv.is_deleted = false
                GROUP BY r.m_id
            )
            SELECT m.m_name, m.m_mail,
                   owner_rate.owner_rate,
                   borrower_rate.borrower_rate
            FROM member m
            LEFT JOIN owner_rate ON m.m_id = owner_rate.m_id
            LEFT JOIN borrower_rate ON m.m_id = borrower_rate.m_id
            WHERE m.m_id = %s
        """, (m_id, m_id, m_id, m_id, m_id))

        result = cursor.fetchall()
        query_time = (time.time() - query_start) * 1000

        times.append(query_time)

        if (i + 1) % 20 == 0:
            print(f"    進度：{i + 1}/{iterations}")

    return times


def analyze_results(times: List[float], query_name: str) -> Dict:
    """分析測試結果"""
    times_sorted = sorted(times)
    p95_index = int(len(times_sorted) * 0.95)
    p99_index = int(len(times_sorted) * 0.99)

    results = {
        'query_name': query_name,
        'iterations': len(times),
        'avg_ms': statistics.mean(times),
        'median_ms': statistics.median(times),
        'min_ms': min(times),
        'max_ms': max(times),
        'p95_ms': times_sorted[p95_index],
        'p99_ms': times_sorted[p99_index],
        'stddev_ms': statistics.stdev(times) if len(times) > 1 else 0,
        'qps': 1000 / statistics.mean(times) if statistics.mean(times) > 0 else 0
    }

    return results


def print_results(results: Dict):
    """印出測試結果"""
    print(f"\n  📊 {results['query_name']} 測試結果:")
    print(f"     平均執行時間: {results['avg_ms']:.2f} ms")
    print(f"     中位數: {results['median_ms']:.2f} ms")
    print(f"     最小值: {results['min_ms']:.2f} ms")
    print(f"     最大值: {results['max_ms']:.2f} ms")
    print(f"     P95: {results['p95_ms']:.2f} ms")
    print(f"     P99: {results['p99_ms']:.2f} ms")
    print(f"     標準差: {results['stddev_ms']:.2f} ms")
    print(f"     吞吐量: {results['qps']:.2f} QPS")


def main():
    parser = argparse.ArgumentParser(description='資料庫查詢效能測試')
    parser.add_argument('--iterations', type=int, default=100, help='測試次數（預設：100）')
    parser.add_argument('--query', choices=['all', 'time_conflict', 'contribution', 'rating'],
                        default='all', help='測試的查詢類型')
    parser.add_argument('--output', type=str, help='結果輸出檔案（JSON 格式）')

    args = parser.parse_args()

    print("=" * 70)
    print("🔍 資料庫查詢效能測試")
    print("=" * 70)
    print(f"\n測試次數：{args.iterations}")
    print(f"測試查詢：{args.query}\n")

    conn = get_connection()
    all_results = []

    try:
        if args.query in ['all', 'time_conflict']:
            print("\n1️⃣  測試查詢 1：時間衝突檢查（OVERLAPS）")
            times = benchmark_time_conflict_check(conn, args.iterations)
            results = analyze_results(times, "時間衝突檢查")
            print_results(results)
            all_results.append(results)

        if args.query in ['all', 'contribution']:
            print("\n2️⃣  測試查詢 2：貢獻檢查與遞迴分類")
            times = benchmark_contribution_check(conn, args.iterations)
            results = analyze_results(times, "貢獻檢查")
            print_results(results)
            all_results.append(results)

        if args.query in ['all', 'rating']:
            print("\n3️⃣  測試查詢 3：用戶評分計算")
            times = benchmark_rating_calculation(conn, args.iterations)
            results = analyze_results(times, "評分計算")
            print_results(results)
            all_results.append(results)

        # 輸出結果到檔案
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'iterations': args.iterations,
                    'results': all_results
                }, f, indent=2, ensure_ascii=False)
            print(f"\n💾 結果已儲存至：{args.output}")

        print("\n" + "=" * 70)
        print("✅ 測試完成！")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
