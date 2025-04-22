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
    conn = get_db_connection()
    phash = generate_password_hash(password)
    c = conn.cursor()
    c.execute("insert into User_Credentials (username, email, phash) values (%s, %s, %s);" % (username, email, phash))
    #will update this later, right now everyone has no names or bio
    c.execute("select ucid from User_Credentials where username = '%s';" % user)
    ucid = c.fetchone()
    c.execute("INSERT INTO User (ucid, fname, lname, bio) VALUES (%s, %s, %s, %s);" % (ucid, 'NONE', 'NONE', 'NONE'))

def select_exercises_for_plan(exercises):
    if len(exercises) <= 0:
        no_ex = []
        return no_ex
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
        )
    c = conn.cursor()
    ex_string = ''
    #print("EXERCISES IN SELECT_EXERCISES_FOR_PLAN:",exercises)
    for i in exercises:
        ex_string += "%s," % i
    #print("ex_string=",ex_string)
    ex_string = ex_string[:len(ex_string) - 1]
    c.execute("select * from Exercises where eid in (%s);" % ex_string)
    ex_list = c.fetchall()
    #print("ex_list = ", ex_list)
    return ex_list
