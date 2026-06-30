from db import get_db_connection

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "status": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "username": user["username"]
            }
        }
    else:
        return {
            "status": False,
            "message": "Invalid username or password"
        }