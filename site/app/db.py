# file: db.py
import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='Exercisedb',
        cursorclass=pymysql.cursors.DictCursor
        )
