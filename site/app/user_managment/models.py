# file: models.py
from flask_login import UserMixin
from db import get_db_connection

class User(UserMixIn):
    def __init__(self, uid, ucid, username, email, salt, fname, lname, bio,
    
    def get_id(self):
        return self.id
