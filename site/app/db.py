# file: db.py
import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
        )
