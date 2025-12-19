import mysql.connector
from datetime import datetime, timedelta

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # default XAMPP
        database="nyx_sleep"
    )


# ---------- USERS ----------
def create_user(username, password, email):
    """Create user with email support"""
    db = get_connection()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (username, password, email) VALUES (%s,%s,%s)",
        (username, password, email)
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


def get_user_by_email(email):
    """Get user by email address"""
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    db.close()
    return user


def update_user_password(user_id, new_password):
    """Update user's password"""
    db = get_connection()
    cur = db.cursor()
    cur.execute(
        "UPDATE users SET password=%s WHERE user_id=%s",
        (new_password, user_id)
    )
    db.commit()
    db.close()


# ---------- PASSWORD RESET ----------
def save_reset_code(email, code):
    """Save password reset verification code"""
    db = get_connection()
    cur = db.cursor()
    
    expires_at = datetime.now() + timedelta(minutes=15)
    
    cur.execute("""
        INSERT INTO password_resets (email, code, expires_at)
        VALUES (%s, %s, %s)
    """, (email, code, expires_at))
    
    db.commit()
    db.close()


def verify_reset_code(email, code):
    """Verify password reset code"""
    db = get_connection()
    cur = db.cursor(dictionary=True)
    
    cur.execute("""
        SELECT * FROM password_resets 
        WHERE email=%s AND code=%s AND used=0 AND expires_at > NOW()
        ORDER BY created_at DESC LIMIT 1
    """, (email, code))
    
    result = cur.fetchone()
    
    if result:
        # Mark code as used
        cur.execute(
            "UPDATE password_resets SET used=1 WHERE id=%s",
            (result['id'],)
        )
        db.commit()
        db.close()
        return True
    
    db.close()
    return False


def delete_reset_code(email):
    """Delete all reset codes for an email"""
    db = get_connection()
    cur = db.cursor()
    cur.execute("DELETE FROM password_resets WHERE email=%s", (email,))
    db.commit()
    db.close()


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


# ---------- USER SETTINGS ----------
def save_user_settings(user_id, bedtime_enabled, bedtime_hour, bedtime_minute, bedtime_ampm,
                      alarm_enabled, alarm_hour, alarm_minute, alarm_ampm):
    """Save or update user's bedtime and alarm settings"""
    db = get_connection()
    cur = db.cursor()
    
    # Check if settings exist
    cur.execute("SELECT * FROM user_settings WHERE user_id=%s", (user_id,))
    existing = cur.fetchone()
    
    if existing:
        # Update existing settings
        cur.execute("""
            UPDATE user_settings 
            SET bedtime_enabled=%s, bedtime_hour=%s, bedtime_minute=%s, bedtime_ampm=%s,
                alarm_enabled=%s, alarm_hour=%s, alarm_minute=%s, alarm_ampm=%s,
                updated_at=NOW()
            WHERE user_id=%s
        """, (bedtime_enabled, bedtime_hour, bedtime_minute, bedtime_ampm,
              alarm_enabled, alarm_hour, alarm_minute, alarm_ampm, user_id))
    else:
        # Insert new settings
        cur.execute("""
            INSERT INTO user_settings 
            (user_id, bedtime_enabled, bedtime_hour, bedtime_minute, bedtime_ampm,
             alarm_enabled, alarm_hour, alarm_minute, alarm_ampm)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (user_id, bedtime_enabled, bedtime_hour, bedtime_minute, bedtime_ampm,
              alarm_enabled, alarm_hour, alarm_minute, alarm_ampm))
    
    db.commit()
    db.close()


def get_user_settings(user_id):
    """Retrieve user's bedtime and alarm settings"""
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM user_settings WHERE user_id=%s", (user_id,))
    settings = cur.fetchone()
    db.close()
    return settings
