#from app import db
import pymysql.cursors
from werkzeug.security import generate_password_hash
from app.db import get_db_connection as connect

def add_user(user, email, password):
    conn = connect()
    try:
        with conn.cursor() as c:
            phash = generate_password_hash(password)
            
            # Insert credentials
            print("INSERTING User_Credentials")
            c.execute(
                "INSERT INTO User_Credentials (username, email, phash) VALUES (%s, %s, %s);",
                (user, email, phash)
            )

            # Get ucid back
            print("SELECTING ucid")
            c.execute("SELECT ucid FROM User_Credentials WHERE username = %s;", (user,))
            row = c.fetchone()

            if row and 'ucid' in row:
                ucid = row['ucid']
                print(f"INSERTING User with ucid={ucid}")
                c.execute(
                    "INSERT INTO User (ucid, fname, lname, bio) VALUES (%s, %s, %s, %s);",
                    (ucid, 'NONE', 'NONE', 'NONE')
                )
            else:
                print("Failed to retrieve ucid after credential insert.")
                return False

        conn.commit()
        print("User successfully added.")
        return True

    except Exception as e:
        print(f"Error in add_user: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

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
