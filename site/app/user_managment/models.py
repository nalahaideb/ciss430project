# file: models.py
from flask_login import UserMixin
from db import get_db_connection

class User(UserMixIn):
    def __init__(self, uid, ucid, username, email, salt, fname, lname, bio, creation_date, last_login):
        self.id = uid
        self.ucid = ucid
        self.username = username
        self.email = email
        self.salt = salt
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
                select u.uid, uc.username, uc.email, uc.salt, u.fname, u.lname, u.bio, uc.creation_date, uc.last_login
                from User u
                join User_Credentials uc on u.ucid = uc.ucid
                where uc.username = %s
                """, (username,))
                row = cursor.fetchone()
                if row:
                    return User(
                        row['uid'], row['ucid'], row['username'], row['email'],
                        row['salt'], row['fname'], row['lname'], row['bio'],
                        row['creation_date'], row['last_login']
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
                select u.uid, uc.username, uc.email, uc.salt, u.fname, u.lname, u.bio, uc.creation_date, uc.last_login
                from User u
                join User_Credentials uc on u.ucid = uc.ucid
                where u.uid = %s
                """, (uid,))
                row = cursor.fetchone()
                if row:
                    return User(
                        row['uid'], row['ucid'], row['username'], row['email'],
                        row['salt'], row['fname'], row['lname'], row['bio'],
                        row['creation_date'], row['last_login']
                        )
        finally:
            conn.close()
        return None
    
    def get_id(self):
        return self.id
