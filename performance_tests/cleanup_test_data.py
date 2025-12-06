#!/usr/bin/env python3
"""
測試資料清空工具

用於清空所有測試資料，但保留資料庫 schema 結構。
"""

import psycopg2
import sys
import os

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
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ 資料庫連線失敗: {e}")
        sys.exit(1)


def cleanup_all_data(conn):
    """清空所有測試資料"""
    print("\n🗑️  清空所有資料...")
    cursor = conn.cursor()

    # 按照外鍵依賴順序刪除資料
    tables = [
        'review',
        'loan_event',
        'loan',
        'reservation_detail',
        'reservation',
        'contribution',
        'item_verification',
        'item_pick',
        'report',
        'category_ban',
        'item',
        'category',
        'member',
        'staff',
        'pick_up_place'
    ]

    print("\n以下表格將被清空：")
    for table in tables:
        print(f"  - {table}")

    print("\n⚠️  這個操作無法復原！")
    response = input("\n確定要清空所有資料嗎？(yes/N): ")

    if response.lower() != 'yes':
        print("❌ 已取消")
        sys.exit(0)

    print("\n開始清空資料...")

    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
            print(f"  ✓ 已清空：{table}")
        except Exception as e:
            print(f"  ⚠️  無法清空 {table}: {e}")

    conn.commit()
    print("\n✅ 所有資料清空完成！")


def get_table_counts(conn):
    """顯示各表的資料筆數"""
    cursor = conn.cursor()

    tables = [
        'member', 'staff', 'category', 'item', 'reservation',
        'reservation_detail', 'contribution', 'loan', 'loan_event',
        'review', 'report', 'category_ban', 'pick_up_place'
    ]

    print("\n📊 目前資料量：")
    print("-" * 40)

    total = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            total += count
            if count > 0:
                print(f"  {table:<25} {count:>10,} 筆")
        except Exception as e:
            print(f"  {table:<25} {'錯誤':>10}")

    print("-" * 40)
    print(f"  {'總計':<25} {total:>10,} 筆")
    print()


def main():
    print("=" * 60)
    print("🗑️  資料庫測試資料清空工具")
    print("=" * 60)

    conn = get_connection()

    try:
        # 顯示目前資料量
        get_table_counts(conn)

        # 清空資料
        cleanup_all_data(conn)

        # 再次顯示資料量確認
        get_table_counts(conn)

        print("=" * 60)
        print("✅ 完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
