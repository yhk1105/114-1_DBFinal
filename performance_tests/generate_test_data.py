#!/usr/bin/env python3
"""
測試資料生成工具

用於生成大量測試資料以評估索引效能。
預設生成約 75 萬筆資料（約 1.2 GB）。
"""

import psycopg2
import argparse
import sys
from datetime import datetime
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


def cleanup_existing_data(conn):
    """清空所有測試資料（保留 schema）"""
    print("\n🗑️  清空現有資料...")
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

    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
            print(f"  ✓ 已清空：{table}")
        except Exception as e:
            print(f"  ⚠️  無法清空 {table}: {e}")

    conn.commit()
    print("✅ 資料清空完成\n")


def generate_members(conn, count=10000):
    """生成會員資料"""
    print(f"📝 生成 {count:,} 筆 member 資料...")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO member (m_name, m_mail, m_password, is_active)
        SELECT
            'TestUser_' || i,
            'testuser' || i || '@example.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5uRlGJqH7L5bO',  -- password: test123
            random() > 0.1  -- 90% active
        FROM generate_series(1, %s) i
        ON CONFLICT (m_name) DO NOTHING;
    """, (count,))

    conn.commit()
    print(f"✅ Member 資料生成完成")


def generate_categories(conn, total=500, depth=5):
    """生成分類樹資料（遞迴結構）"""
    print(f"📝 生成 {total} 筆 category 資料（{depth} 層深度）...")
    cursor = conn.cursor()

    # 第 1 層：根類別
    root_count = 10
    cursor.execute("""
        INSERT INTO category (c_name, parent_c_id)
        SELECT 'RootCat_' || i, NULL
        FROM generate_series(1, %s) i
        RETURNING c_id;
    """, (root_count,))

    # 獲取所有根類別 ID
    root_ids = [row[0] for row in cursor.fetchall()]

    # 第 2-5 層：子類別
    per_layer = (total - root_count) // (depth - 1)
    current_parent_ids = root_ids

    for layer in range(2, depth + 1):
        print(f"  生成第 {layer} 層...")
        parent_count = len(current_parent_ids)
        children_per_parent = max(1, per_layer // parent_count)

        new_ids = []
        for parent_id in current_parent_ids:
            cursor.execute("""
                INSERT INTO category (c_name, parent_c_id)
                SELECT
                    'Cat_L' || %s || '_' || i,
                    %s
                FROM generate_series(1, %s) i
                RETURNING c_id;
            """, (layer, parent_id, children_per_parent))

            new_ids.extend([row[0] for row in cursor.fetchall()])

        current_parent_ids = new_ids

    conn.commit()
    print(f"✅ Category 資料生成完成")


def generate_items(conn, count=100000):
    """生成物品資料"""
    print(f"📝 生成 {count:,} 筆 item 資料...")
    cursor = conn.cursor()

    # 獲取有效的 member 和 category ID
    cursor.execute("SELECT MAX(m_id) FROM member")
    max_member_id = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(c_id) FROM category")
    max_category_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO item (m_id, c_id, i_name, status, description, out_duration)
        SELECT
            (random() * %s + 1)::int,  -- 隨機 owner
            (random() * %s + 1)::int,   -- 隨機類別
            'TestItem_' || i,
            CASE (random() * 2)::int
                WHEN 0 THEN 'Reservable'
                WHEN 1 THEN 'Not reservable'
                ELSE 'Not verified'
            END,
            'Test description for performance testing item ' || i,
            (random() * 604800 + 86400)::int  -- 1-7 天（秒數）
        FROM generate_series(1, %s) i;
    """, (max_member_id, max_category_id, count))

    conn.commit()
    print(f"✅ Item 資料生成完成")


def generate_reservations(conn, reservation_count=50000):
    """生成預約及預約詳細資料"""
    print(f"📝 生成 {reservation_count:,} 筆 reservation 資料...")
    cursor = conn.cursor()

    # 獲取有效的 member ID
    cursor.execute("SELECT MAX(m_id) FROM member")
    max_member_id = cursor.fetchone()[0]

    # 1. 生成預約
    cursor.execute("""
        INSERT INTO reservation (m_id, create_at, is_deleted)
        SELECT
            (random() * %s + 1)::int,
            NOW() - (random() * interval '365 days'),
            random() > 0.9  -- 10%% 已刪除
        FROM generate_series(1, %s) i
        RETURNING r_id;
    """, (max_member_id, reservation_count))

    reservation_ids = [row[0] for row in cursor.fetchall()]

    # 2. 生成預約詳細（每筆預約 2-4 個物品）
    print(f"📝 生成約 {reservation_count * 3:,} 筆 reservation_detail 資料...")

    cursor.execute("SELECT MAX(i_id) FROM item")
    max_item_id = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(p_id) FROM pick_up_place")
    max_place_id = cursor.fetchone()[0] or 1

    # 批次插入提升效能
    batch_size = 1000
    for i in range(0, len(reservation_ids), batch_size):
        batch = reservation_ids[i:i+batch_size]

        cursor.execute("""
            INSERT INTO reservation_detail (r_id, i_id, p_id, est_start_at, est_due_at)
            SELECT
                r.r_id,
                (random() * %s + 1)::int,
                (random() * %s + 1)::int,
                r.create_at + interval '1 day',
                r.create_at + interval '7 days'
            FROM unnest(%s::bigint[]) AS r(r_id)
            CROSS JOIN generate_series(1, (random() * 2 + 2)::int);
        """, (max_item_id, max_place_id, batch))

    conn.commit()
    print(f"✅ Reservation 相關資料生成完成")


def generate_contributions(conn):
    """生成貢獻資料（基於已存在的 item）"""
    print(f"📝 生成 contribution 資料（約 80% item）...")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contribution (m_id, i_id, is_active)
        SELECT
            i.m_id,
            i.i_id,
            random() > 0.3  -- 70% active
        FROM item i
        WHERE random() > 0.2  -- 80% 物品有貢獻
        ON CONFLICT (m_id, i_id) DO NOTHING;
    """)

    conn.commit()
    print(f"✅ Contribution 資料生成完成")


def generate_loans_and_reviews(conn):
    """生成 loan, loan_event 和 review 資料"""
    print(f"📝 生成 loan 相關資料...")
    cursor = conn.cursor()

    # 1. 生成 loan（基於 reservation_detail）
    cursor.execute("""
        INSERT INTO loan (rd_id, actual_start_at, actual_return_at)
        SELECT
            rd.rd_id,
            rd.est_start_at + (random() * interval '2 days'),
            CASE
                WHEN random() > 0.2 THEN rd.est_due_at - (random() * interval '1 day')
                ELSE NULL  -- 20% 尚未歸還
            END
        FROM reservation_detail rd
        JOIN reservation r ON rd.r_id = r.r_id
        WHERE r.is_deleted = false
        AND random() > 0.2  -- 80% 預約有實際借用
        LIMIT 120000;
    """)

    # 2. 生成 loan_event
    print(f"📝 生成 loan_event 資料...")
    cursor.execute("""
        INSERT INTO loan_event (timestamp, event_type, l_id)
        SELECT
            EXTRACT(EPOCH FROM l.actual_start_at) * 1000,
            'Handover',
            l.l_id
        FROM loan l
        WHERE l.actual_start_at IS NOT NULL;
    """)

    cursor.execute("""
        INSERT INTO loan_event (timestamp, event_type, l_id)
        SELECT
            EXTRACT(EPOCH FROM l.actual_return_at) * 1000,
            'Return',
            l.l_id
        FROM loan l
        WHERE l.actual_return_at IS NOT NULL;
    """)

    # 3. 生成 review（約 70% 已歸還的 loan 有評論）
    print(f"📝 生成 review 資料...")
    cursor.execute("""
        WITH loan_members AS (
            SELECT
                l.l_id,
                r.m_id as borrower_id,
                i.m_id as owner_id
            FROM loan l
            JOIN reservation_detail rd ON l.rd_id = rd.rd_id
            JOIN reservation r ON rd.r_id = r.r_id
            JOIN item i ON rd.i_id = i.i_id
            WHERE l.actual_return_at IS NOT NULL
        )
        INSERT INTO review (score, comment, reviewer_id, reviewee_id, l_id, is_deleted)
        SELECT
            (random() * 4 + 1)::int,  -- 1-5 分
            'Test review comment for performance testing',
            CASE WHEN random() > 0.5 THEN lm.borrower_id ELSE lm.owner_id END,
            CASE WHEN random() > 0.5 THEN lm.owner_id ELSE lm.borrower_id END,
            lm.l_id,
            random() > 0.95  -- 5% 已刪除
        FROM loan_members lm
        WHERE random() > 0.3  -- 70% 有評論
        ON CONFLICT DO NOTHING;
    """)

    conn.commit()
    print(f"✅ Loan 及 Review 資料生成完成")


def generate_reports(conn, count=5000):
    """生成檢舉資料"""
    print(f"📝 生成 {count:,} 筆 report 資料...")
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(m_id) FROM member")
    max_member_id = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(i_id) FROM item")
    max_item_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO report (comment, r_conclusion, create_at, m_id, i_id, s_id)
        SELECT
            'Test report comment ' || i,
            CASE (random() * 3)::int
                WHEN 0 THEN 'Pending'
                WHEN 1 THEN 'Withdraw'
                WHEN 2 THEN 'Ban Category'
                ELSE 'Delist'
            END,
            NOW() - (random() * interval '180 days'),
            (random() * %s + 1)::int,
            (random() * %s + 1)::int,
            (random() * 19 + 1)::int  -- 假設有 20 個員工
        FROM generate_series(1, %s) i;
    """, (max_member_id, max_item_id, count))

    conn.commit()
    print(f"✅ Report 資料生成完成")


def generate_category_bans(conn, count=2000):
    """生成類別禁用資料"""
    print(f"📝 生成 {count:,} 筆 category_ban 資料...")
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(m_id) FROM member")
    max_member_id = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(c_id) FROM category")
    max_category_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO category_ban (s_id, c_id, m_id, ban_at, is_deleted)
        SELECT
            (random() * 19 + 1)::int,
            (random() * %s + 1)::int,
            (random() * %s + 1)::int,
            NOW() - (random() * interval '90 days'),
            random() > 0.7  -- 30%% 已解除
        FROM generate_series(1, %s) i
        ON CONFLICT (c_id, m_id) DO NOTHING;
    """, (max_category_id, max_member_id, count))

    conn.commit()
    print(f"✅ Category_ban 資料生成完成")


def main():
    parser = argparse.ArgumentParser(description='生成測試資料用於索引效能測試')
    parser.add_argument('--members', type=int, default=10000, help='會員數量（預設：10000）')
    parser.add_argument('--categories', type=int, default=500, help='分類數量（預設：500）')
    parser.add_argument('--items', type=int, default=100000, help='物品數量（預設：100000）')
    parser.add_argument('--reservations', type=int, default=50000, help='預約數量（預設：50000）')
    parser.add_argument('--reports', type=int, default=5000, help='檢舉數量（預設：5000）')
    parser.add_argument('--bans', type=int, default=2000, help='禁用記錄數量（預設：2000）')
    parser.add_argument('--skip-cleanup', action='store_true', help='跳過清空現有資料（不推薦）')

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 資料庫測試資料生成工具")
    print("=" * 60)
    print(f"\n📊 預計生成資料量：")
    print(f"  - Members: {args.members:,}")
    print(f"  - Categories: {args.categories:,} (5 層深度)")
    print(f"  - Items: {args.items:,}")
    print(f"  - Reservations: {args.reservations:,}")
    print(f"  - Reports: {args.reports:,}")
    print(f"  - Category Bans: {args.bans:,}")
    print(f"\n⚠️  總計約 75 萬筆資料，預計需要 10-15 分鐘")

    if not args.skip_cleanup:
        print(f"⚠️  將會先清空所有現有資料！")

    print(f"⚠️  請確保已備份資料庫！\n")

    response = input("是否繼續？(y/N): ")
    if response.lower() != 'y':
        print("❌ 已取消")
        sys.exit(0)

    start_time = datetime.now()
    conn = get_connection()

    try:
        # 清空現有資料
        if not args.skip_cleanup:
            cleanup_existing_data(conn)

        # 依序生成各表資料
        generate_members(conn, args.members)
        generate_categories(conn, args.categories)
        generate_items(conn, args.items)
        generate_reservations(conn, args.reservations)
        generate_contributions(conn)
        generate_loans_and_reviews(conn)
        generate_reports(conn, args.reports)
        generate_category_bans(conn, args.bans)

        # 執行 VACUUM ANALYZE 優化查詢計畫
        print("\n📊 執行 VACUUM ANALYZE...")
        conn.set_isolation_level(0)  # AUTOCOMMIT
        cursor = conn.cursor()
        cursor.execute("VACUUM ANALYZE;")
        conn.set_isolation_level(1)  # READ COMMITTED

        elapsed = datetime.now() - start_time
        print("\n" + "=" * 60)
        print(f"✅ 所有測試資料生成完成！")
        print(f"⏱️  總耗時：{elapsed}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
