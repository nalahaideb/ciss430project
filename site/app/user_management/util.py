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

def get_friends(uid, limit=10, offset=0):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.uid, uc.username
                FROM Friends f
                JOIN User u ON (f.user1 = u.uid OR f.user2 = u.uid)
                JOIN User_Credentials uc ON u.ucid = uc.ucid
                WHERE (f.user1 = %s OR f.user2 = %s) AND u.uid != %s
                LIMIT %s OFFSET %s
            """, (uid, uid, uid, limit, offset))
            return cursor.fetchall()
    finally:
        conn.close()


def get_mutual_users(uid, limit=10, offset=0):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT u.uid, uc.username, u.fname, u.lname
                FROM Friends f1
                JOIN Friends f2 ON (
                    f1.user1 = f2.user1 OR f1.user1 = f2.user2 OR
                    f1.user2 = f2.user1 OR f1.user2 = f2.user2
                )
                JOIN User u ON (u.uid = f2.user1 OR u.uid = f2.user2)
                JOIN User_Credentials uc ON u.ucid = uc.ucid
                WHERE (f1.user1 = %s OR f1.user2 = %s)
                  AND u.uid NOT IN (
                      SELECT CASE
                               WHEN user1 = %s THEN user2
                               WHEN user2 = %s THEN user1
                             END
                      FROM Friends
                      WHERE user1 = %s OR user2 = %s
                  )
                  AND u.uid != %s
                LIMIT %s OFFSET %s
            """, (uid, uid, uid, uid, uid, uid, uid, limit, offset))
            return cursor.fetchall()
    finally:
        conn.close()


def search_users(query, exclude_uid, limit=10, offset=0):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.uid, uc.username, u.fname, u.lname
                FROM User u
                JOIN User_Credentials uc ON u.ucid = uc.ucid
                WHERE uc.username LIKE %s AND u.uid != %s
                ORDER BY uc.username ASC
                LIMIT %s OFFSET %s
            """, (f"%{query}%", exclude_uid, limit, offset))
            return cursor.fetchall()
    finally:
        conn.close()
