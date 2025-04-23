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
    
def select_exercises_for_plan(exercise_ids):
    if not exercise_ids:
        return []
    
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
    )
    
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
