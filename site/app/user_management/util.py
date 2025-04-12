# file: util.py
from app.db import get_db_connection
from datetime import datetime

def update_user_profile(uid, ucid, fname, lname, email, bio):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE User
            SET fname = %s, lname = %s, bio = %s
            WHERE uid = %s
            """, (fname, lname, bio, uid))

            cursor.execute("""
            UPDATE User_Credentials
            SET email = %s
            WHERE ucid = %s
            """, (email, ucid))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Profile update error:", e)
        return False
    finally:
        conn.close()

def update_last_login(ucid):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE User_Credentials
            SET last_login = %s
            WHERE ucid = %s
            """, (datetime.now(), ucid))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Last login update error:", e)
    finally:
        conn.close()
