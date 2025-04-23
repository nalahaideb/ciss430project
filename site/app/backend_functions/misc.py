#from app import db
import pymysql.cursors
from werkzeug.security import generate_password_hash
from app.db import get_db_connection as connect

def add_user(user, email, password):
    conn = connect()
    c = conn.cursor()
    phash = generate_password_hash(password)
    c.execute("insert into User_Credentials (username, email, phash) values (%s, %s, %s);" % (username, email, phash))
    #will update this later, right now everyone has no names or bio
    c.execute("select ucid from User_Credentials where username = '%s';" % user)
    ucid = c.fetchone()
    if len(ucid) <= 0:
        c.execute("INSERT INTO User (ucid, fname, lname, bio) VALUES (%s, %s, %s, %s);" % (ucid, 'NONE', 'NONE', 'NONE'))
    else:
        print("NONUNIQUE EMAIL, NOT INSERTING")
    return

def select_exercises_for_plan(exercise_ids):
    if not exercise_ids:
        return []
    
    conn = connect()

    try:
        with conn.cursor() as c:
            placeholders = ','.join(['%s'] * len(exercise_ids))
            query = """
                SELECT 
                    eid as id,
                    ename as name,
                    etype as type,
                    ebpart as muscle_group,
                    eequip as equipment
                FROM Exercises 
                WHERE eid IN (%s)
            """ % placeholders
            
            c.execute(query, tuple(exercise_ids))
            exercises = []
            for row in c.fetchall():
                exercises.append({
                    'id': row['id'],
                    'ename': row['name'],
                    'type': row['type'],
                    'muscle_group': row['muscle_group'],
                    'equipment': row['equipment'],
                    'level': 'Intermediate'  
                })
            
            return exercises
            
    except Exception as e:
        print(f"Database error: {e}")
        return []
    conn.close()
    return
