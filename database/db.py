import sqlite3
from contextlib import contextmanager
from datetime import datetime


class Database:
    """Простая обертка над SQLite для хранения расписания и записей."""

    def __init__(self, path: str) -> None:
        self.path = path

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS work_days (
                    work_date TEXT PRIMARY KEY,
                    is_closed INTEGER DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_date TEXT NOT NULL,
                    slot_time TEXT NOT NULL,
                    is_deleted INTEGER DEFAULT 0,
                    UNIQUE(work_date, slot_time)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    work_date TEXT NOT NULL,
                    slot_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    reminder_job_id TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    def add_work_day(self, work_date: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO work_days(work_date, is_closed) VALUES(?, 0)",
                (work_date,),
            )

    def set_day_closed(self, work_date: str, is_closed: bool) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO work_days(work_date, is_closed) VALUES(?, ?)",
                (work_date, int(is_closed)),
            )
            conn.execute(
                "UPDATE work_days SET is_closed = ? WHERE work_date = ?",
                (int(is_closed), work_date),
            )

    def is_day_closed(self, work_date: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT is_closed FROM work_days WHERE work_date = ?", (work_date,)
            ).fetchone()
            return bool(row and row["is_closed"])

    def add_slot(self, work_date: str, slot_time: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO work_days(work_date, is_closed) VALUES(?, 0)",
                (work_date,),
            )
            conn.execute(
                "INSERT OR IGNORE INTO slots(work_date, slot_time, is_deleted) VALUES(?, ?, 0)",
                (work_date, slot_time),
            )
            conn.execute(
                "UPDATE slots SET is_deleted = 0 WHERE work_date = ? AND slot_time = ?",
                (work_date, slot_time),
            )

    def delete_slot(self, work_date: str, slot_time: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE slots SET is_deleted = 1 WHERE work_date = ? AND slot_time = ?",
                (work_date, slot_time),
            )

    def get_available_dates(self, start_date: str, end_date: str) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT s.work_date
                FROM slots s
                LEFT JOIN work_days w ON w.work_date = s.work_date
                WHERE s.is_deleted = 0
                  AND s.work_date BETWEEN ? AND ?
                  AND COALESCE(w.is_closed, 0) = 0
                  AND NOT EXISTS (
                      SELECT 1 FROM appointments a
                      WHERE a.work_date = s.work_date
                        AND a.slot_time = s.slot_time
                        AND a.status = 'active'
                  )
                ORDER BY s.work_date
                """,
                (start_date, end_date),
            ).fetchall()
            return [r["work_date"] for r in rows]

    def get_available_slots(self, work_date: str) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT s.slot_time
                FROM slots s
                LEFT JOIN work_days w ON w.work_date = s.work_date
                WHERE s.work_date = ?
                  AND s.is_deleted = 0
                  AND COALESCE(w.is_closed, 0) = 0
                  AND NOT EXISTS (
                      SELECT 1 FROM appointments a
                      WHERE a.work_date = s.work_date
                        AND a.slot_time = s.slot_time
                        AND a.status = 'active'
                  )
                ORDER BY s.slot_time
                """,
                (work_date,),
            ).fetchall()
            return [r["slot_time"] for r in rows]

    def get_user_active_appointment(self, user_id: int):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT * FROM appointments
                WHERE user_id = ? AND status = 'active'
                ORDER BY id DESC LIMIT 1
                """,
                (user_id,),
            ).fetchone()

    def create_appointment(
        self,
        user_id: int,
        user_name: str,
        phone: str,
        work_date: str,
        slot_time: str,
        reminder_job_id: str | None,
    ) -> int:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO appointments(user_id, user_name, phone, work_date, slot_time, status, reminder_job_id, created_at)
                VALUES(?, ?, ?, ?, ?, 'active', ?, ?)
                """,
                (
                    user_id,
                    user_name,
                    phone,
                    work_date,
                    slot_time,
                    reminder_job_id,
                    datetime.utcnow().isoformat(),
                ),
            )
            return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

    def update_reminder_job(self, appointment_id: int, reminder_job_id: str | None) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE appointments SET reminder_job_id = ? WHERE id = ?",
                (reminder_job_id, appointment_id),
            )

    def cancel_appointment(self, appointment_id: int) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE appointments SET status = 'cancelled', reminder_job_id = NULL WHERE id = ?",
                (appointment_id,),
            )

    def get_active_appointments(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM appointments WHERE status = 'active'"
            ).fetchall()

    def get_schedule_for_date(self, work_date: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT s.slot_time,
                       a.user_name,
                       a.phone,
                       a.user_id,
                       a.status
                FROM slots s
                LEFT JOIN appointments a
                  ON a.work_date = s.work_date
                 AND a.slot_time = s.slot_time
                 AND a.status = 'active'
                WHERE s.work_date = ?
                  AND s.is_deleted = 0
                ORDER BY s.slot_time
                """,
                (work_date,),
            ).fetchall()

    def cancel_client_by_slot(self, work_date: str, slot_time: str):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM appointments
                WHERE work_date = ? AND slot_time = ? AND status = 'active'
                ORDER BY id DESC LIMIT 1
                """,
                (work_date, slot_time),
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE appointments SET status = 'cancelled', reminder_job_id = NULL WHERE id = ?",
                    (row["id"],),
                )
            return row
