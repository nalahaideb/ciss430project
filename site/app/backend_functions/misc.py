#from app import db
import pymysql.cursors
from werkzeug.security import generate_password_hash

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
        )

def add_user(user, email, password):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
        )
    phash = generate_password_hash(password)
    c = conn.cursor()
    c.execute("insert into User_Credentials (username, email, phash) values (%s, %s, %s);" % (username, email, phash)
    #will update this later, right now everyone has no names or bio
    c.execute("select ucid from User_Credentials where username = '%s';" % user)
    ucid = c.fetchone()
    c.execute("INSERT INTO User (ucid, fname, lname, bio) VALUES (%s, %s, %s, %s);" % (ucid, 'NULL', 'NULL', 'NULL')
