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

#def get_db_connection():
#    return pymysql.connect(
#        host='mysqlpal.mysql.pythonanywhere-services.com',
#        user='mysqlpal',
#        password='PASICK123*',
#        database='mysqlpal$exercisedb',
#        cursorclass=pymysql.cursors.DictCursor
#    )
