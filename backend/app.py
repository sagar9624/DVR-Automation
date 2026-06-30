#111111111111111111111111111
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import subprocess
import os
import pickle
import base64
import numpy as np
import cv2
import face_recognition
from datetime import datetime
import shutil

# ================= CAMERA SYSTEM (ADD ONLY) =================
from flask import Response

cap = None
camera_running = False
camera_connected = False

RTSP_URL = ""
USE_RTSP = False   # toggle

def get_source():
    if USE_RTSP and RTSP_URL.strip():
        return RTSP_URL
    return 0

def start_camera_source():
    global cap, camera_connected

    source = get_source()
    print("Starting camera with:", source)

    cap = cv2.VideoCapture(source)
    camera_connected = cap.isOpened()

    return camera_connected
# ============================================================

app = Flask(__name__)
CORS(app)



# ================= DATABASE =================
DB_PATH = "database.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()

def init_db():
    conn, cursor = get_db()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        emp_id TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        time TEXT,
        logout_time TEXT,
        total_hours REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= PATH =================
DATASET_PATH = "dataset"
ENCODING_PATH = os.path.join("encodings", "faces.pkl")

# ================= LOAD ENCODINGS =================
def load_encodings():
    if os.path.exists(ENCODING_PATH):
        with open(ENCODING_PATH, "rb") as f:
            return pickle.load(f)
    return {"encodings": [], "names": []}

# ================= HOME =================
@app.route("/")
def home():
    return "DVR Backend Running ✅"


# ================= CAMERA CONTROL (ADD ONLY) =================

@app.route("/toggle_mode")
def toggle_mode():
    global USE_RTSP
    USE_RTSP = not USE_RTSP
    return jsonify({"mode": "RTSP" if USE_RTSP else "Webcam"})


@app.route("/set_rtsp", methods=["POST"])
def set_rtsp():
    global RTSP_URL
    data = request.get_json()
    RTSP_URL = data.get("url", "").strip()
    return jsonify({"status": "saved"})


@app.route("/start_camera")
def start_camera():
    global camera_running, camera_connected, cap

    # 🔥 reset old camera
    if cap is not None:
        cap.release()
        cap = None

    # 🔥 choose source
    if USE_RTSP:
        if not RTSP_URL.strip():
            return jsonify({"status": "no_rtsp"})
        source = RTSP_URL
    else:
        source = 0

    cap = cv2.VideoCapture(source)
    camera_connected = cap.isOpened()

    if not camera_connected:
        return jsonify({"status": "failed"})

    camera_running = True
    return jsonify({"status": "started"})


@app.route("/stop_camera")
def stop_camera():
    global camera_running, cap, camera_connected

    camera_running = False

    if cap is not None:
        cap.release()
        cap = None

    camera_connected = False

    return jsonify({"status": "stopped"})

# ============================================================

# ================= ADD EMPLOYEE =================
@app.route("/add_employee", methods=["POST"])
def add_employee():
    data = request.get_json()

    name = data.get("name").strip().lower()
    emp_id = str(data.get("emp_id")).strip()

    if not name or not emp_id:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    conn, cursor = get_db()

    cursor.execute(
        "INSERT INTO employees (name, emp_id) VALUES (?, ?)",
        (name, emp_id)
    )

    conn.commit()
    conn.close()

    os.makedirs(os.path.join(DATASET_PATH, f"{name}_{emp_id}"), exist_ok=True)

    return jsonify({"status": "success"})


@app.route("/get_employees")
def get_employees():
    conn, cursor = get_db()

    cursor.execute("SELECT name, emp_id FROM employees")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([{"name": r[0], "emp_id": r[1]} for r in rows])


@app.route("/delete_employee/<emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    try:
        conn, cursor = get_db()

        cursor.execute("SELECT name FROM employees WHERE emp_id=?", (emp_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"status": "error", "message": "Not found"}), 404

        name = row[0]

        cursor.execute("DELETE FROM employees WHERE emp_id=?", (emp_id,))
        conn.commit()
        conn.close()

        folder = os.path.join(DATASET_PATH, f"{name}_{emp_id}")
        if os.path.exists(folder):
            shutil.rmtree(folder)

        if os.path.exists(ENCODING_PATH):
            os.remove(ENCODING_PATH)

        subprocess.call(["python3", "train_model.py"])

        return jsonify({"status": "success"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error"})

def start_capture(name, emp_id):
    subprocess.Popen(["python3", "capture_faces.py", name, str(emp_id)])

@app.route("/capture_face/<emp_id>")
def capture_face(emp_id):
    conn, cursor = get_db()

    cursor.execute("SELECT name FROM employees WHERE emp_id=?", (emp_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        start_capture(row[0], emp_id)
        return jsonify({"status": "success"})

    return jsonify({"status": "error"})

def mark_attendance(name):
    conn, cursor = get_db()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT * FROM attendance
        WHERE name=? AND substr(time,1,10)=? AND (logout_time IS NULL OR logout_time='')
    """, (name, today))

    if cursor.fetchone():
        conn.close()
        return "Already Marked"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO attendance (name, time)
        VALUES (?, ?)
    """, (name, now))

    conn.commit()
    conn.close()

    return "Marked"

@app.route('/logout', methods=['POST'])
def logout():
    try:
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({"status": "error", "message": "Name missing"})

        name = data.get("name").strip().lower()

        conn, cursor = get_db()

        today = datetime.now().strftime("%Y-%m-%d")

        # Ensure columns exist (SAFE)
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN logout_time TEXT")
        except:
            pass

        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN total_hours REAL")
        except:
            pass

        cursor.execute("""
            SELECT id, time FROM attendance
            WHERE name=? 
            AND substr(time,1,10)=?
            AND (logout_time IS NULL OR logout_time='')
            ORDER BY time DESC LIMIT 1
        """, (name, today))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"status": "already_logged_out"})

        record_id = row[0]
        login_time_full = row[1]


        login_dt = datetime.strptime(login_time_full, "%Y-%m-%d %H:%M:%S")
        logout_dt = datetime.now()

        total_hours = round((logout_dt - login_dt).total_seconds() / 3600, 2)

        logout_time_str = logout_dt.strftime("%H:%M:%S")

        # 🔥 UPDATE
        cursor.execute("""
            UPDATE attendance
            SET logout_time=?, total_hours=?
            WHERE id=?
        """, (logout_time_str, total_hours, record_id))

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "logout_time": logout_time_str,
            "hours": float(total_hours)
        })

    except Exception as e:
        print("LOGOUT ERROR:", e)
        return jsonify({"status": "error"})

@app.route("/monthly_report")
def monthly_report():
    try:
        conn, cursor = get_db()

        # Ensure columns exist
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN total_hours REAL")
        except:
            pass

        cursor.execute("""
            SELECT 
                name,
                COUNT(*) as days,
                SUM(total_hours)
            FROM attendance
            WHERE substr(time,1,7)=strftime('%Y-%m','now')
            GROUP BY name
        """)

        rows = cursor.fetchall()
        conn.close()

        return jsonify([
            {
                "name": r[0],
                "days": r[1],
                "hours": round(r[2] if r[2] else 0, 2)
            }
            for r in rows
        ])

    except Exception as e:
        print("REPORT ERROR:", e)
        return jsonify([])
    

@app.route("/report_details")
def report_details():
    try:
        conn, cursor = get_db()

        cursor.execute("""
            SELECT name, time, logout_time, total_hours
            FROM attendance
            ORDER BY time DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        result = []

        for index,r in enumerate(rows,start=1):
            full_time = r[1]  # "YYYY-MM-DD HH:MM:SS"

            if full_time:
                date_part = full_time.split(" ")[0]
                login_part = full_time.split(" ")[1]
                day_name=datetime.strptime(date_part,"%Y-%m-%d").strftime("%A")
                day_label=f"{index} - {day_name}"
            else:
                date_part = ""
                login_part = ""
                day_name

            result.append({
                "name": r[0],
                "date": date_part,
                "day":day_label,
                "login": login_part,
                "logout": r[2] if r[2] else "",
                "hours": round(r[3] if r[3] else 0, 2)
            })

        return jsonify(result)

    except Exception as e:
        print("DETAIL REPORT ERROR:", e)
        return jsonify([])



@app.route("/attendance_full")
def attendance_full():
    conn, cursor = get_db()

    try:
        cursor.execute("ALTER TABLE attendance ADD COLUMN logout_time TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE attendance ADD COLUMN total_hours REAL")
    except:
        pass

    cursor.execute("""
        SELECT id, name, time, logout_time, total_hours 
        FROM attendance 
        ORDER BY time DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "name": r[1],
            "time": r[2],
            "logout_time": r[3] if r[3] else "",

            # 🔥 FIX HERE (VERY IMPORTANT)
            "total_hours": round(float(r[4]) ,2) if r[4] not in (None,"") else None
        }
        for r in rows
    ])

@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        data = request.get_json()
        img_data = data.get("image")

        img_bytes = base64.b64decode(img_data.split(",")[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb, model="hog")
        face_encodings = face_recognition.face_encodings(rgb, face_locations)

        data_db = load_encodings()

        results = []

        for encoding, location in zip(face_encodings, face_locations):

            name = "Unknown"
            status = "Unknown"

            if data_db["encodings"]:
                matches = face_recognition.compare_faces(data_db["encodings"], encoding)
                distances = face_recognition.face_distance(data_db["encodings"], encoding)

                if len(distances) > 0:
                    idx = np.argmin(distances)

                    if matches[idx] and distances[idx] < 0.5:
                        full = data_db["names"][idx]
                        name = full.split("_")[0]
                        status = mark_attendance(name)

            top, right, bottom, left = location

            results.append({
                "name": name,
                "status": status,
                "box": [top, right, bottom, left]
            })

        return jsonify(results)

    except Exception as e:
        print("ERROR:", e)
        return jsonify([])

@app.route("/attendance")
def attendance():
    conn, cursor = get_db()

    cursor.execute("SELECT id, name, time FROM attendance ORDER BY time DESC")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "name": r[1], "time": r[2]}
        for r in rows
    ])

@app.route("/reports")
def reports():
    conn, cursor = get_db()

    cursor.execute("SELECT id, name, time FROM attendance ORDER BY time DESC")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "name": r[1], "time": r[2]}
        for r in rows
    ])

@app.route("/delete_attendance/<int:id>", methods=["DELETE"])
def delete_attendance(id):
    try:
        conn, cursor = get_db()
        cursor.execute("DELETE FROM attendance WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        print("DELETE ERROR:", e)
        return jsonify({"status": "error"})

@app.route("/delete_report/<int:id>", methods=["DELETE"])
def delete_report(id):
    try:
        conn, cursor = get_db()
        cursor.execute("DELETE FROM attendance WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        print("DELETE ERROR:", e)
        return jsonify({"status": "error"})


@app.route("/dashboard")
def dashboard():
    try:
        conn, cursor = get_db()

        cursor.execute("SELECT COUNT(*) FROM employees")
        emp_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance")
        att_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance")
        rep_count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "employees": emp_count,
            "attendance": att_count,
            "reports": rep_count,
            "camera": "Ready"
        })

    except Exception as e:
        print("DASHBOARD ERROR:", e)
        return jsonify({
            "employees": 0,
            "attendance": 0,
            "reports": 0,
            "camera": "Error"
        })
    

def generate_frames():
    global cap, camera_running

    while camera_running:
        if cap is None:
            break

        success, frame = cap.read()

        if not success:
            break

        frame = cv2.resize(frame, (640, 480))

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


 
if __name__ == "__main__":
    app.run(debug=True)

