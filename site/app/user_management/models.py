# file: models.py
from datetime import datetime
from flask_login import UserMixin
from app import login_manager
from app.db import get_db_connection

class User(UserMixin):
    def __init__(self, uid, ucid, username, email, phash, fname, lname, bio, creation_date, last_login, main_pid):
        self.id = uid
        self.ucid = ucid
        self.username = username
        self.email = email
        self.phash = phash
        self.fname = fname
        self.lname = lname
        self.bio = bio
        self.creation_date = creation_date
        self.last_login = last_login
        self.main_pid = main_pid

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.uid, u.ucid, uc.username, uc.email, uc.phash, u.fname, u.lname, u.bio,
                           uc.creation_date, uc.last_login, u.main_pid
                    FROM User u
                    JOIN User_Credentials uc ON u.ucid = uc.ucid
                    WHERE uc.username = %s
                """, (username,))
                row = cursor.fetchone()
                if row:
                    return User(
                        row['uid'], row['ucid'], row['username'], row['email'], row['phash'],
                        row['fname'], row['lname'], row['bio'], row['creation_date'], row['last_login'], row['main_pid']
                    )
        finally:
            conn.close()
    #new stuff to load the main plan automatically if one exists
    @property
    def main_plan(self):
        if not self.main_pid:
            return None
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, 
                           (SELECT COUNT(*) FROM Exercise_Plan_Day WHERE pid = p.pid) AS day_count
                    FROM Exercise_Plan p
                    WHERE p.pid = %s
                """, (self.main_pid,))
                return cursor.fetchone()
        finally:
            conn.close()

    def set_main_plan(self, plan_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE User SET main_pid = %s WHERE uid = %s
                """, (plan_id, self.id))
                conn.commit()
                self.main_pid = plan_id 
        finally:
            conn.close()
        return None
    def get_current_plan_day(self):
        """Get the current day of the plan with exercises"""
        if not self.main_pid:
            return None
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Get plan details and day count
                cursor.execute("""
                SELECT 
                p.pid,
                p.plan_name,
                p.creation_date,
                COUNT(d.did) as day_count
                FROM Exercise_Plan p
                LEFT JOIN Exercise_Plan_Day d ON p.pid = d.pid
                WHERE p.pid = %s
                GROUP BY p.pid
                """, (self.main_pid,))
                plan = cursor.fetchone()
            
                if not plan or not plan['day_count']:
                    return None
            
                # Calculate current day (1-based index)
                creation_date = plan['creation_date']
                if isinstance(creation_date, str):
                    creation_date = datetime.strptime(creation_date, '%Y-%m-%d %H:%M:%S')
                    days_since_creation = (datetime.now() - creation_date).days
                    current_day = (days_since_creation % plan['day_count']) + 1
                cursor.execute("""
                SELECT 
                e.ename as name,
                epe.sets,
                epe.reps,
                epe.duration,
                e.etype as type,
                e.ebpart as muscle_group
                FROM Exercise_Entry epe
                JOIN Exercises e ON epe.eid = e.eid
                JOIN Exercise_Plan_Day d ON epe.did = d.did
                WHERE d.pid = %s AND d.day_order = %s
                ORDER BY epe.exercise_order
                """, (self.main_pid, current_day))
                
                exercises = cursor.fetchall()
                
                return {
                    'plan_name': plan['plan_name'],
                    'current_day': current_day,
                    'total_days': plan['day_count'],
                    'exercises': exercises,
                    'creation_date': plan['creation_date']
                }
            
        except Exception as e:
            print(f"Error getting current plan day: {e}")
            return None
        finally:
            conn.close()
            #end new additions########################
    @staticmethod
    def get_by_id(uid):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.uid, u.ucid, uc.username, uc.email, uc.phash, u.fname, u.lname, u.bio,
                           uc.creation_date, uc.last_login, u.main_pid
                    FROM User u
                    JOIN User_Credentials uc ON u.ucid = uc.ucid
                    WHERE u.uid = %s
                """, (uid,))
                row = cursor.fetchone()
                if row:
                    return User(
                        row['uid'], row['ucid'], row['username'], row['email'], row['phash'],
                        row['fname'], row['lname'], row['bio'], row['creation_date'], row['last_login'], row['main_pid']
                    )
        finally:
            conn.close()
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
