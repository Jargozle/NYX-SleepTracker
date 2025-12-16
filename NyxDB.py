import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # default XAMPP
        database="nyx_sleep"
    )


# ---------- USERS ----------
def create_user(username, password, profile_pic="assets/profile.png"):
    db = get_connection()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (username, password, profile_pic) VALUES (%s,%s,%s)",
        (username, password, profile_pic)
    )
    db.commit()
    db.close()


def validate_user(username, password):
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cur.fetchone()
    db.close()
    return user


def get_user_by_name(username):
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    db.close()
    return user


# ---------- SLEEP ----------
def add_sleep_session(user_id, year, month, day, hours):
    db = get_connection()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO sleep_sessions (user_id, year, month, day, hours) VALUES (%s,%s,%s,%s,%s)",
        (user_id, year, month, day, hours)
    )
    db.commit()
    db.close()


def get_all_sessions(user_id):
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM sleep_sessions WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    sessions = cur.fetchall()
    db.close()
    return sessions
