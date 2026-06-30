
import sqlite3
from config import Config


# ================= CONNECTION =================
def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INIT DATABASE =================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # EMPLOYEES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        employee_id TEXT UNIQUE NOT NULL,
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ATTENDANCE TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        UNIQUE(employee_id, date)
    )
    """)

    conn.commit()

    # ================= NEW COLUMNS (SAFE ADD) =================
    try:
        cursor.execute("ALTER TABLE attendance ADD COLUMN logout_time TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE attendance ADD COLUMN total_hours REAL")
    except:
        pass

    conn.commit()
    conn.close()


# ================= ADD ATTENDANCE =================
def insert_attendance(employee_id, name, date, time):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO attendance (employee_id, name, date, time)
        VALUES (?, ?, ?, ?)
        """, (employee_id, name, date, time))

        conn.commit()
        return "Marked"

    except sqlite3.IntegrityError:
        return "Already Marked"

    finally:
        conn.close()


# ================= GET ATTENDANCE =================
def get_all_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, date, time
    FROM attendance
    ORDER BY date DESC, time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "time": f"{row['date']} {row['time']}"
        }
        for row in rows
    ]


# ================= DELETE ATTENDANCE =================
def delete_attendance_by_id(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    return True


# ================= CLEAR ALL ATTENDANCE (OPTIONAL) =================
def clear_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()

    return True


# ============================================================
# ================= NEW FEATURES (ADDED ONLY) =================
# ============================================================

# ================= LOGOUT UPDATE =================
def update_logout(employee_id, date, logout_time, total_hours):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE attendance
    SET logout_time = ?, total_hours = ?
    WHERE employee_id = ? AND date = ?
    """, (logout_time, total_hours, employee_id, date))

    conn.commit()
    conn.close()

    return True


# ================= FULL ATTENDANCE (WITH LOGOUT) =================
def get_full_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, date, time, logout_time, total_hours
    FROM attendance
    ORDER BY date DESC, time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "date": row["date"],
            "login": row["time"],
            "logout": row["logout_time"],
            "hours": row["total_hours"]
        }
        for row in rows
    ]


# ================= MONTHLY REPORT =================
def get_monthly_report():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        name,
        COUNT(*) as days,
        SUM(total_hours) as hours
    FROM attendance
    WHERE substr(date,1,7) = strftime('%Y-%m','now')
    GROUP BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "name": row["name"],
            "days": row["days"],
            "hours": round(row["hours"] if row["hours"] else 0, 2)
        }
        for row in rows
    ]
