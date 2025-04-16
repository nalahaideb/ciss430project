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
                SELECT u.uid, uc.username, u.fname, u.lname
                FROM Friends f
                JOIN User u ON (f.user1 = u.uid OR f.user2 = u.uid)
                JOIN User_Credentials uc ON u.ucid = uc.ucid
                WHERE (f.user1 = %s OR f.user2 = %s) AND u.uid != %s
                ORDER BY uc.username ASC
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
                ORDER BY uc.username ASC
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

def get_friend_requests(receiver_id, limit=5, offset=0):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT fr.frid, uc.username, u.fname, u.lname
                FROM Friend_Requests fr
                JOIN User u ON u.uid = fr.sender_id
                JOIN User_Credentials uc ON u.ucid = uc.ucid
                WHERE fr.receiver_id = %s
                ORDER BY fr.request_date DESC
                LIMIT %s OFFSET %s
            """, (receiver_id, limit, offset))
            return cursor.fetchall()
    finally:
        conn.close()

def send_friend_request(sender_id, receiver_id):
    if sender_id == receiver_id:
        return "self_request"

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Already friends?
            cursor.execute("""
                SELECT 1 FROM Friends
                WHERE (user1 = %s AND user2 = %s) OR (user1 = %s AND user2 = %s)
            """, (sender_id, receiver_id, receiver_id, sender_id))
            if cursor.fetchone():
                return "already_friends"

            # Already sent a friend request?
            cursor.execute("""
                SELECT 1 FROM Friend_Requests
                WHERE sender_id = %s AND receiver_id = %s
            """, (sender_id, receiver_id))
            if cursor.fetchone():
                return "already_requested"

            # Insert new request
            cursor.execute("""
                INSERT INTO Friend_Requests (sender_id, receiver_id)
                VALUES (%s, %s)
            """, (sender_id, receiver_id))
            conn.commit()
            return "success"
    except Exception as e:
        conn.rollback()
        print("Error in send_friend_request:", e)
        return "error"
    finally:
        conn.close()

def approve_friend_request(frid, receiver_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verify the request exists and is valid
            cursor.execute("""
                SELECT sender_id FROM Friend_Requests
                WHERE frid = %s AND receiver_id = %s
            """, (frid, receiver_id))
            row = cursor.fetchone()
            if not row:
                return "invalid_request"

            sender_id = row['sender_id']

            # Add to friends table
            cursor.execute("""
                INSERT INTO Friends (user1, user2)
                VALUES (%s, %s)
            """, (sender_id, receiver_id))

            # Delete the original friend request
            cursor.execute("""
                DELETE FROM Friend_Requests WHERE frid = %s
            """, (frid,))
            conn.commit()
            return "success"
    except Exception as e:
        conn.rollback()
        print("Error approving friend request:", e)
        return "error"
    finally:
        conn.close()


def reject_friend_request(frid, receiver_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Friend_Requests
                WHERE frid = %s AND receiver_id = %s
            """, (frid, receiver_id))
            conn.commit()
            return "success"
    except Exception as e:
        conn.rollback()
        print("Error rejecting friend request:", e)
        return "error"
    finally:
        conn.close()

def remove_friend(uid1, uid2):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Friends
                WHERE (user1 = %s AND user2 = %s)
                   OR (user1 = %s AND user2 = %s)
            """, (uid1, uid2, uid2, uid1))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print("Error removing friend:", e)
        return False
    finally:
        conn.close()

def is_friends(uid1, uid2):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM Friends
                WHERE (user1 = %s AND user2 = %s)
                   OR (user1 = %s AND user2 = %s)
            """, (uid1, uid2, uid2, uid1))
            return cursor.fetchone() is not None
    finally:
        conn.close()
