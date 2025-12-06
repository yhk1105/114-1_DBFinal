#!/usr/bin/env python3
"""
索引效能比較工具

比較 3 種索引配置的效能差異：
1. 無索引（只有主鍵和 UNIQUE 約束）
2. 基礎索引（單欄位索引）
3. 完整索引（包含複合索引、部分索引）
"""

import psycopg2
import argparse
import json
import os
from datetime import datetime
from benchmark_queries import (
    benchmark_time_conflict_check,
    benchmark_contribution_check,
    benchmark_rating_calculation,
    analyze_results,
    get_connection
)

# 索引定義
BASE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_reservation_detail_i_id ON reservation_detail(i_id);",
    "CREATE INDEX IF NOT EXISTS idx_category_parent_c_id ON category(parent_c_id);",
    "CREATE INDEX IF NOT EXISTS idx_contribution_m_id ON contribution(m_id);",
    "CREATE INDEX IF NOT EXISTS idx_review_reviewee_id ON review(reviewee_id);",
]

FULL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_item_c_id ON item(c_id);",
    "CREATE INDEX IF NOT EXISTS idx_reservation_m_id ON reservation(m_id);",
    "CREATE INDEX IF NOT EXISTS idx_reservation_detail_r_id ON reservation_detail(r_id);",
    "CREATE INDEX IF NOT EXISTS idx_reservation_detail_i_id ON reservation_detail(i_id);",
    "CREATE INDEX IF NOT EXISTS idx_reservation_detail_time_range ON reservation_detail(i_id, est_start_at, est_due_at);",
    "CREATE INDEX IF NOT EXISTS idx_contribution_m_id_i_id ON contribution(m_id, i_id);",
    "CREATE INDEX IF NOT EXISTS idx_category_parent_c_id ON category(parent_c_id);",
    "CREATE INDEX IF NOT EXISTS idx_review_l_id ON review(l_id);",
    "CREATE INDEX IF NOT EXISTS idx_review_reviewee_id ON review(reviewee_id);",
    "CREATE INDEX IF NOT EXISTS idx_report_s_id_conclusion ON report(s_id, r_conclusion);",
    "CREATE INDEX IF NOT EXISTS idx_category_ban_m_id ON category_ban(m_id) WHERE is_deleted = false;",
]


def drop_all_test_indexes(conn):
    """刪除所有測試索引（保留主鍵和 UNIQUE 約束）"""
    print("  🗑️  刪除現有索引...")
    cursor = conn.cursor()

    # 獲取所有非系統索引
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND indexname LIKE 'idx_%';
    """)

    indexes = [row[0] for row in cursor.fetchall()]

    for index in indexes:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index};")
            print(f"     - 已刪除：{index}")
        except Exception as e:
            print(f"     ⚠️  無法刪除 {index}: {e}")

    conn.commit()
    print("  ✅ 索引刪除完成")


def create_indexes(conn, indexes, label):
    """建立索引"""
    print(f"  📝 建立{label}...")
    cursor = conn.cursor()

    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            # 提取索引名稱
            index_name = index_sql.split("INDEX IF NOT EXISTS ")[1].split(" ON ")[0]
            print(f"     - 已建立：{index_name}")
        except Exception as e:
            print(f"     ⚠️  錯誤：{e}")

    conn.commit()

    # 執行 ANALYZE 更新統計資訊
    print("  📊 執行 ANALYZE...")
    conn.set_isolation_level(0)
    cursor.execute("ANALYZE;")
    conn.set_isolation_level(1)

    print(f"  ✅ {label}建立完成")


def run_tests(conn, config_name, iterations):
    """執行所有測試"""
    print(f"\n{'='*70}")
    print(f"🧪 測試配置：{config_name}")
    print(f"{'='*70}\n")

    results = {
        'config': config_name,
        'timestamp': datetime.now().isoformat(),
        'iterations': iterations,
        'queries': []
    }

    # 測試 1：時間衝突檢查
    print("1️⃣  測試時間衝突檢查...")
    times = benchmark_time_conflict_check(conn, iterations)
    query_result = analyze_results(times, "時間衝突檢查")
    results['queries'].append(query_result)
    print(f"   平均：{query_result['avg_ms']:.2f} ms | P95：{query_result['p95_ms']:.2f} ms")

    # 測試 2：貢獻檢查
    print("\n2️⃣  測試貢獻檢查...")
    times = benchmark_contribution_check(conn, iterations)
    query_result = analyze_results(times, "貢獻檢查")
    results['queries'].append(query_result)
    print(f"   平均：{query_result['avg_ms']:.2f} ms | P95：{query_result['p95_ms']:.2f} ms")

    # 測試 3：評分計算
    print("\n3️⃣  測試評分計算...")
    times = benchmark_rating_calculation(conn, iterations)
    query_result = analyze_results(times, "評分計算")
    results['queries'].append(query_result)
    print(f"   平均：{query_result['avg_ms']:.2f} ms | P95：{query_result['p95_ms']:.2f} ms")

    return results


def compare_results(all_results):
    """比較不同配置的結果"""
    print("\n" + "="*70)
    print("📊 效能比較總結")
    print("="*70)

    # 找出無索引的基準結果
    baseline = None
    for result in all_results:
        if result['config'] == '無索引':
            baseline = result
            break

    if not baseline:
        print("⚠️  找不到基準測試結果（無索引）")
        return

    print(f"\n{'查詢名稱':<15} | {'無索引':<12} | {'基礎索引':<12} | {'完整索引':<12} | {'提升倍數':<10}")
    print("-" * 80)

    query_names = ["時間衝突檢查", "貢獻檢查", "評分計算"]

    for i, query_name in enumerate(query_names):
        row = f"{query_name:<15}"

        for result in all_results:
            if i < len(result['queries']):
                avg_ms = result['queries'][i]['avg_ms']
                row += f" | {avg_ms:>10.2f} ms"

        # 計算提升倍數
        if len(all_results) >= 2:
            baseline_time = baseline['queries'][i]['avg_ms']
            full_index_time = all_results[-1]['queries'][i]['avg_ms']
            improvement = baseline_time / full_index_time if full_index_time > 0 else 0
            row += f" | {improvement:>8.1f}x"

        print(row)

    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description='索引效能比較測試')
    parser.add_argument('--iterations', type=int, default=100, help='每個測試的執行次數（預設：100）')
    parser.add_argument('--output', type=str, default='results/index_performance.json',
                        help='結果輸出檔案')
    parser.add_argument('--skip-setup', action='store_true',
                        help='跳過索引設置（使用現有配置）')

    args = parser.parse_args()

    print("="*70)
    print("🚀 索引效能比較測試工具")
    print("="*70)
    print(f"\n測試次數：{args.iterations}")
    print(f"輸出檔案：{args.output}\n")

    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    all_results = []
    conn = get_connection()

    try:
        # 配置 1：無索引
        if not args.skip_setup:
            print("\n🔧 配置 1：無索引")
            drop_all_test_indexes(conn)

        results = run_tests(conn, "無索引", args.iterations)
        all_results.append(results)

        # 配置 2：基礎索引
        if not args.skip_setup:
            print("\n🔧 配置 2：基礎索引")
            drop_all_test_indexes(conn)
            create_indexes(conn, BASE_INDEXES, "基礎索引")

        results = run_tests(conn, "基礎索引", args.iterations)
        all_results.append(results)

        # 配置 3：完整索引
        if not args.skip_setup:
            print("\n🔧 配置 3：完整索引")
            drop_all_test_indexes(conn)
            create_indexes(conn, FULL_INDEXES, "完整索引")

        results = run_tests(conn, "完整索引", args.iterations)
        all_results.append(results)

        # 比較結果
        compare_results(all_results)

        # 儲存結果
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'iterations': args.iterations,
                'configurations': all_results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 詳細結果已儲存至：{args.output}")
        print("\n✅ 所有測試完成！")

    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
