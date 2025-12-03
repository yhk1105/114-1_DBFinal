from app.extensions import db
from sqlalchemy import text
from app.models.reservation_detail import ReservationDetail
from datetime import datetime, timedelta


def create_loan_for_upcoming_reservations(hours_ahead: int = 24):
    """
    為即將到來的預約自動建立 Loan。
    類似「揀貨單」生成：在預約開始前一段時間，預先建立 Loan 記錄，
    讓物品擁有者知道需要準備物品。
    """
    try:
        db.session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
        target_time = datetime.now() + timedelta(hours=hours_ahead)

        # 使用原生 SQL 執行批量插入，效率較高
        # 我們需要生成 l_id，可以使用 sequence 或者 MAX(l_id) + row_number
        # 這裡假設 l_id 是手動管理的 (schema 沒寫 serial)，所以用 MAX + ROW_NUMBER 方式

        # 先鎖定 loan 表以計算 ID
        # 找出需要建立 loan 的 rd_id
        pending_details = db.session.execute(text("""
            SELECT rd.rd_id, rd.est_start_at, rd.est_due_at
            FROM reservation_detail rd
            JOIN reservation r ON rd.r_id = r.r_id
            LEFT JOIN loan l ON rd.rd_id = l.rd_id
            WHERE r.is_deleted = false
            AND l.l_id IS NULL
            AND rd.est_start_at <= :target_time
        """), {"target_time": target_time}).mappings().all()

        if not pending_details:
            return 0

        # 批量插入 Loan
        values = []
        for idx, detail in enumerate(pending_details):
            # 注意：actual_start_at 和 actual_due_at 初始值設為 est 值，或者設為 null (視 schema 限制)
            # Schema 定義 loan 的 actual_start_at/due_at 是 NOT NULL
            # 所以這裡我們暫時填入 est 的時間作為預設，等到實際 Handover 時再更新 (或是 schema 設計上這兩個欄位應該要是 nullable?)
            # 假設這兩個欄位代表「實際發生」的時間，那在建立揀貨單時填入 est 時間當作「預計」是合理的，或者應該修 schema 改成 nullable
            # 根據現有 schema NOT NULL constraint，我們先填入 est 時間

            values.append({
                "rd_id": detail["rd_id"],
                "actual_start_at": None,  # 暫填
                "actual_return_at": None,     # 暫填
                "is_deleted": False
            })

        if values:
            db.session.execute(text("""
                INSERT INTO loan (rd_id, actual_start_at, actual_return_at, is_deleted)
                VALUES (:rd_id, :actual_start_at, :actual_return_at, :is_deleted)
            """), values)

        db.session.commit()
        return len(values)

    except Exception as e:
        db.session.rollback()
        print(f"Error creating loans: {e}")
        return 0
