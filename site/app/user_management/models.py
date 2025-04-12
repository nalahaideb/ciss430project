# file: models.py
from flask_login import UserMixin
from app import login_manager
from app.db import get_db_connection

class User(UserMixin):
    def __init__(self, uid, ucid, username, email, phash, fname, lname, bio, creation_date, last_login):
        self.id = uid
        self.ucid = ucid
        self.username = username
        self.email = email
        self.phash = phash
        self.fname = fname
        self.lname = lname
        self.bio = bio
        self.creation_date = creation_date
        self.last_login = last_login

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.uid, u.ucid, uc.username, uc.email, uc.phash, u.fname, u.lname, u.bio,
                           uc.creation_date, uc.last_login
                    FROM User u
                    JOIN User_Credentials uc ON u.ucid = uc.ucid
                    WHERE uc.username = %s
                """, (username,))
                row = cursor.fetchone()
                if row:
                    return User(
                        row['uid'], row['ucid'], row['username'], row['email'], row['phash'],
                        row['fname'], row['lname'], row['bio'], row['creation_date'], row['last_login']
                    )
        finally:
            conn.close()
        return None

    @staticmethod
    def get_by_id(uid):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.uid, u.ucid, uc.username, uc.email, uc.phash, u.fname, u.lname, u.bio,
                           uc.creation_date, uc.last_login
                    FROM User u
                    JOIN User_Credentials uc ON u.ucid = uc.ucid
                    WHERE u.uid = %s
                """, (uid,))
                row = cursor.fetchone()
                if row:
                    return User(
                        row['uid'], row['ucid'], row['username'], row['email'], row['phash'],
                        row['fname'], row['lname'], row['bio'], row['creation_date'], row['last_login']
                    )
        finally:
            conn.close()
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
