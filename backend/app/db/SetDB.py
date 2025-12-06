#!/usr/bin/env python3
"""
PostgreSQL CSV 匯入工具
使用 pandas 和 psycopg2 將 CSV 檔案匯入 PostgreSQL 資料庫
包含完整的資料庫初始化流程
"""

import os
import csv
import psycopg2
from psycopg2.extras import execute_values
from urllib.parse import urlparse
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 資料庫連線設定
DATABASE_URL = os.getenv("DATABASE_URL")
TARGET_DB_NAME = "our_things"

# CSV 檔案路徑（相對於此腳本）
# 腳本在 backend/app/db/import_csv.py，CSV 在 backend/app/db/csv/
CSV_DIR = "csv"

# SQL 檔案路徑（相對於此腳本）
# 腳本在 backend/app/db/SetDB.py，SQL 在 backend/app/db/
SCHEMA_SQL_PATH = "schema.sql"
SETNEXTVAL_SQL_PATH = "setnextval.sql"
SETINDEX_SQL_PATH = "setindex.sql"

# 表格與 CSV 檔案的對應關係
TABLE_MAPPINGS = {
    "member": {
        "file": "member.csv",
        "columns": ["m_id", "m_name", "m_mail", "m_password", "is_active"]
    },
    "category": {
        "file": "category.csv",
        "columns": ["c_id", "c_name", "parent_c_id"]
    },
    "staff": {
        "file": "staff.csv",
        "columns": ["s_id", "s_name", "s_mail", "s_password", "role", "is_deleted"]
    },
    "pick_up_place": {
        "file": "pickup_place.csv",
        "columns": ["p_id", "p_name", "address", "note", "is_deleted"]
    },
    "item": {
        "file": "item.csv",
        "columns": ["i_id", "i_name", "status", "description", "out_duration", "m_id", "c_id"]
    },
    "item_pick": {
        "file": "item_pick.csv",
        "columns": ["i_id", "p_id", "is_deleted"]
    },
    "item_verification": {
        "file": "item_verification.csv",
        "columns": ["iv_id", "v_conclusion", "create_at", "i_id", "s_id"]
    },
    "reservation": {
        "file": "reservation.csv",
        "columns": ["r_id", "is_deleted", "create_at", "m_id"]
    },
    "reservation_detail": {
        "file": "reservation_detail.csv",
        "columns": ["rd_id", "est_start_at", "est_due_at", "r_id", "i_id", "p_id"]
    },
    "contribution": {
        "file": "contribution.csv",
        "columns": ["m_id", "i_id", "is_active"]
    },
    "category_ban": {
        "file": "category_ban.csv",
        "columns": ["s_id", "c_id", "m_id", "is_deleted", "ban_at"]
    },
    "report": {
        "file": "report.csv",
        "columns": ["re_id", "comment", "r_conclusion", "create_at", "conclude_at", "m_id", "i_id", "s_id"]
    },
    "loan": {
        "file": "loan.csv",
        "columns": ["l_id", "rd_id", "actual_start_at", "actual_return_at", "is_deleted"]
    },
    "loan_event": {
        "file": "loan_event.csv",
        "columns": ["timestamp", "event_type", "l_id"]
    },
    "review": {
        "file": "review.csv",
        "columns": ["review_id", "score", "comment", "reviewer_id", "reviewee_id", "l_id", "is_deleted"]
    }
}


def parse_database_url(database_url):
    """解析 DATABASE_URL 並返回連線參數"""
    parsed = urlparse(database_url)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/') if parsed.path else 'postgres'
    }


def get_admin_connection_params(database_url):
    """取得管理員連線參數（連接到 postgres 資料庫）"""
    params = parse_database_url(database_url)
    params['database'] = 'postgres'  # 連接到 postgres 資料庫來執行管理操作
    return params


def check_database_exists(conn_params, db_name):
    """檢查資料庫是否存在"""
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return exists
    except (psycopg2.Error, IOError) as e:
        print(f"   ⚠️  檢查資料庫時發生錯誤: {str(e)}")
        return False


def drop_database(conn_params, db_name):
    """強制刪除資料庫"""
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()

        # 終止所有連接到該資料庫的連線
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
            AND pid <> pg_backend_pid();
        """, (db_name,))

        # 強制刪除資料庫（PostgreSQL 13+ 支援 WITH (FORCE)）
        try:
            cursor.execute(
                f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE);')
        except psycopg2.Error:
            # 如果不支援 WITH (FORCE)，使用傳統方式
            cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}";')

        cursor.close()
        conn.close()
        print(f"   ✅ 已刪除資料庫: {db_name}")
        return True
    except (psycopg2.Error, IOError) as e:
        print(f"   ⚠️  刪除資料庫時發生錯誤: {str(e)}")
        return False


def create_database(conn_params, db_name):
    """建立資料庫"""
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f'CREATE DATABASE "{db_name}";')
        cursor.close()
        conn.close()
        print(f"   ✅ 已建立資料庫: {db_name}")
        return True
    except (psycopg2.Error, IOError) as e:
        print(f"   ❌ 建立資料庫失敗: {str(e)}")
        return False


def execute_sql_file(conn, sql_file_path):
    """執行 SQL 檔案"""
    try:
        # 取得腳本所在目錄的絕對路徑
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 構建 SQL 檔案的絕對路徑
        abs_sql_path = os.path.abspath(os.path.join(script_dir, sql_file_path))

        if not os.path.exists(abs_sql_path):
            print(f"   ⚠️  SQL 檔案不存在: {abs_sql_path}")
            return False

        print(f"   📄 執行 SQL 檔案: {os.path.basename(sql_file_path)}")

        with open(abs_sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        cursor = conn.cursor()

        # 使用 psycopg2 的 execute() 執行 SQL
        # PostgreSQL 允許在一個 execute() 中執行多個語句（用分號分隔）
        # 但為了更好的錯誤處理，我們逐行處理並按分號分割
        statements = []
        current_stmt = ""

        for line in sql_content.split('\n'):
            stripped = line.strip()
            # 跳過空行和註解行
            if not stripped or stripped.startswith('--'):
                continue

            current_stmt += line + '\n'

            # 如果這一行以分號結尾，表示一個完整的語句
            if stripped.endswith(';'):
                stmt = current_stmt.strip()
                if stmt:
                    statements.append(stmt)
                current_stmt = ""

        # 處理最後一個語句（如果沒有以分號結尾）
        if current_stmt.strip():
            statements.append(current_stmt.strip())

        # 執行每個語句
        executed_count = 0
        for stmt in statements:
            if stmt:
                try:
                    cursor.execute(stmt)
                    executed_count += 1
                except psycopg2.Error as e:
                    # 某些錯誤可以忽略（如已存在的物件）
                    error_msg = str(e).lower()
                    if 'already exists' not in error_msg and 'does not exist' not in error_msg:
                        print(f"      ⚠️  執行語句時發生錯誤: {str(e)[:100]}")
                        # 繼續執行其他語句

        conn.commit()
        cursor.close()

        print(f"   ✅ SQL 檔案執行成功（執行 {executed_count} 個語句）")
        return True
    except (psycopg2.Error, IOError, ValueError) as e:
        conn.rollback()
        print(f"   ❌ 執行 SQL 檔案失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def read_csv(file_path):
    """讀取 CSV 檔案並返回資料列表"""
    data = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:  # 使用 utf-8-sig 自動去除 BOM
        reader = csv.DictReader(f)
        # 取得實際的欄位名稱（去除前後空格和 BOM）
        fieldnames = [name.strip().lstrip('\ufeff')
                      for name in reader.fieldnames] if reader.fieldnames else []
        reader.fieldnames = fieldnames

        for row in reader:
            # 將空字串轉換為 None（NULL）
            processed_row = {}
            for key, value in row.items():
                # 去除鍵的前後空格和 BOM
                clean_key = key.strip().lstrip('\ufeff') if key else key
                if value == '' or value is None:
                    processed_row[clean_key] = None
                else:
                    processed_row[clean_key] = value.strip(
                    ) if isinstance(value, str) else value
            data.append(processed_row)
    return data


def import_table(conn, table_name, mapping):
    """匯入單一表格"""
    # 取得腳本所在目錄的絕對路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 構建 CSV 檔案的絕對路徑
    file_path = os.path.abspath(os.path.join(
        script_dir, CSV_DIR, mapping["file"]))

    if not os.path.exists(file_path):
        print(f"⚠️  檔案不存在: {file_path}")
        return False

    print(f"📂 正在匯入 {table_name}...")

    try:
        # 讀取 CSV
        data = read_csv(file_path)

        if not data:
            print(f"   ⚠️  {table_name} 檔案為空")
            return False

        # 準備資料
        columns = mapping["columns"]
        values = []

        # 檢查第一筆資料是否包含所有需要的欄位
        if data:
            missing_cols = [col for col in columns if col not in data[0]]
            if missing_cols:
                print(f"   ❌ CSV 檔案缺少欄位: {missing_cols}")
                print(f"   ℹ️  CSV 檔案實際欄位: {list(data[0].keys())}")
                return False

        for row in data:
            # 只取需要的欄位，並按照順序排列
            row_values = []
            for col in columns:
                value = row.get(col)
                if value is None and col in row:
                    # 欄位存在但值為空字串（已在 read_csv 中轉為 None）
                    pass
                elif value is None:
                    # 欄位不存在
                    print(f"   ⚠️  警告: 欄位 '{col}' 不存在於 CSV 中，將設為 NULL")
                row_values.append(value)
            values.append(row_values)

        # 建立 SQL 語句
        # execute_values 需要的格式：INSERT INTO table (cols) VALUES %s
        columns_str = ','.join(columns)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES %s"

        # 執行插入
        cursor = conn.cursor()
        execute_values(cursor, sql, values, page_size=1000)
        conn.commit()
        cursor.close()

        print(f"   ✅ 成功匯入 {len(values)} 筆資料到 {table_name}")
        return True

    except (psycopg2.Error, IOError, ValueError) as e:
        conn.rollback()
        print(f"   ❌ 匯入 {table_name} 失敗: {str(e)}")
        return False


def main():
    """主函數"""
    if not DATABASE_URL:
        print("❌ 錯誤: 請設定 DATABASE_URL 環境變數")
        return

    print("🚀 開始初始化資料庫並匯入 CSV 資料...")
    print(f"📁 CSV 目錄: {CSV_DIR}")
    print(f"🎯 目標資料庫: {TARGET_DB_NAME}\n")

    try:
        # 步驟 1: 取得管理員連線參數
        admin_params = get_admin_connection_params(DATABASE_URL)

        # 步驟 2: 檢查並刪除現有資料庫
        print("📋 步驟 1: 檢查資料庫是否存在...")
        if check_database_exists(admin_params, TARGET_DB_NAME):
            print(f"   ⚠️  資料庫 {TARGET_DB_NAME} 已存在")
            print("📋 步驟 2: 強制刪除現有資料庫...")
            if not drop_database(admin_params, TARGET_DB_NAME):
                print("❌ 無法刪除資料庫，終止程序")
                return
        else:
            print(f"   ℹ️  資料庫 {TARGET_DB_NAME} 不存在")

        # 步驟 3: 建立新資料庫
        print("\n📋 步驟 3: 建立新資料庫...")
        if not create_database(admin_params, TARGET_DB_NAME):
            print("❌ 無法建立資料庫，終止程序")
            return

        # 步驟 4: 連接到新建立的資料庫
        print("\n📋 步驟 4: 連接到新資料庫...")
        target_params = parse_database_url(DATABASE_URL)
        target_params['database'] = TARGET_DB_NAME
        conn = psycopg2.connect(**target_params)
        print("✅ 資料庫連線成功\n")

        # 步驟 5: 執行 schema.sql 建立表格
        print("📋 步驟 5: 建立資料表結構...")
        if not execute_sql_file(conn, SCHEMA_SQL_PATH):
            print("❌ 無法建立資料表結構，終止程序")
            conn.close()
            return

        # 步驟 6: 匯入 CSV 資料
        print("\n📋 步驟 6: 匯入 CSV 資料...")
        import_order = [
            "member",
            "category",
            "staff",
            "pick_up_place",
            "item",
            "item_pick",
            "item_verification",
            "reservation",
            "reservation_detail",
            "contribution",
            "category_ban",
            "report",
            "loan",
            "loan_event",
            "review"
        ]

        success_count = 0
        for table_name in import_order:
            if table_name in TABLE_MAPPINGS:
                if import_table(conn, table_name, TABLE_MAPPINGS[table_name]):
                    success_count += 1

        print(f"\n✨ CSV 匯入完成！成功匯入 {success_count}/{len(import_order)} 個表格")

        # 步驟 7: 執行 setnextval.sql 調整序列
        print("\n📋 步驟 7: 調整序列 (auto increment)...")
        if not execute_sql_file(conn, SETNEXTVAL_SQL_PATH):
            print("⚠️  調整序列時發生錯誤，但資料已匯入")
        else:
            print("✅ 序列調整完成")

        # 步驟 8: 執行 setindex.sql 建立索引
        print("\n📋 步驟 8: 建立資料庫索引...")
        if not execute_sql_file(conn, SETINDEX_SQL_PATH):
            print("⚠️  建立索引時發生錯誤，但資料已匯入")
        else:
            print("✅ 索引建立完成")

        # 關閉連線
        conn.close()

        print(f"\n🎉 所有步驟完成！資料庫 {TARGET_DB_NAME} 已準備就緒")

    except (psycopg2.Error, IOError, ValueError) as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
