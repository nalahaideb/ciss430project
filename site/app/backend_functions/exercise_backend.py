#import app.db
import pymysql.cursors
from datetime import datetime
from app.db import get_db_connection as connect

#defaults to selecting all muscles if nothing is selected
def list_muscles():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT GROUP_CONCAT(DISTINCT ebpart SEPARATOR ', ') AS ebpart FROM Exercises;")
    muscle_arr = c.fetchall()
    muscle_string = str(muscle_arr[0])
    muscle_string = muscle_string[11:len(muscle_string)-2]
    muscle_string = muscle_string.replace("'",'')
    muscle_string = muscle_string.replace('"','')
    muscle_string = muscle_string.replace(' ','')
    muscle_arr = muscle_string.split(',')
    for i in muscle_arr:
        i = i.replace(' ', '')
    return muscle_arr

#defaults to selecting all equipment if nothing is selected
def list_equipment():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT GROUP_CONCAT(DISTINCT eequip SEPARATOR ', ') AS equip FROM Exercises;")
    equip_arr = c.fetchall()
    equip_string = str(equip_arr[0])
    equip_string = equip_string[11:len(equip_string)-2]
    equip_arr = equip_string.split(',')
    ret = []
    for i in equip_arr:
        #i dont know why it always prefaces each i with a space after the first entry, but this is a quick fix
        if i[0] == ' ':
            i = i[1:]
        ret.append(i)
    c.close()
    conn.close()
    return ret

def get_exercises(muscle_groups, equipment, level, name=None, offset=0, limit=10):
    conn = connect()
    try:
        with conn.cursor() as c:
            where_clauses = []
            params = []

            if muscle_groups:
                where_clauses.append("ebpart IN %s")
                params.append(tuple(muscle_groups))
            if equipment:
                where_clauses.append("eequip IN %s")
                params.append(tuple(equipment))
            if level:
                where_clauses.append("etype = %s")
                params.append(level)
            if name:
                where_clauses.append("ename LIKE %s")
                params.append(f"%{name}%")

            where_sql = " AND ".join(where_clauses)
            if where_sql:
                where_sql = "WHERE " + where_sql

            # 1. Get total count (for pagination)
            count_sql = f"SELECT COUNT(*) as total FROM Exercises {where_sql}"
            c.execute(count_sql, tuple(params))
            total = c.fetchone()['total']

            # 2. Get paginated data
            data_sql = f"""
                SELECT eid, ename, etype, ebpart, eequip
                FROM Exercises
                {where_sql}
                ORDER BY ename ASC
                LIMIT %s OFFSET %s
            """
            c.execute(data_sql, tuple(params + [limit, offset]))
            results = c.fetchall()

            return total, results
    finally:
        conn.close()

def get_total_exercise_count(muscle_groups, equipment, level, name):
    conn = connect()
    c = conn.cursor()

    query = "SELECT COUNT(*) as total FROM Exercises WHERE 1=1"
    params = []

    if muscle_groups:
        placeholders = ','.join(['%s'] * len(muscle_groups))
        query += f" AND ebpart IN ({placeholders})"
        params.extend(muscle_groups)

    if equipment:
        placeholders = ','.join(['%s'] * len(equipment))
        query += f" AND eequip IN ({placeholders})"
        params.extend(equipment)

    if level:
        query += " AND etype = %s"
        params.append(level)

    if name:
        query += " AND ename LIKE %s"
        params.append(f"%{name}%")

    c.execute(query, params)
    result = c.fetchone()
    conn.close()
    return result['total'] if result else 0

def get_user_plan_days(user_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""SELECT main_pid FROM User WHERE uid = %s""", (user_id,))
        
        result = cursor.fetchone()
        if not result or not result['main_pid']:
            #find dis muhfucka a plan STAT
            cursor.execute("""SELECT pid FROM Exercise_Plan WHERE uid = %s ORDER BY creation_date DESC LIMIT 1""", (user_id,))
            result = cursor.fetchone()
            
            #broke boy dont wanna catch a bodyyyyy #baldisbasics #swag
            if not result:
                return []
            
            plan_id = result['pid']
            cursor.execute("""UPDATE User SET main_pid = %s WHERE uid = %s""", (plan_id, user_id))
            conn.commit()
        else:
            plan_id = result['main_pid']
            
        #get the days for d plan
        cursor.execute("""SELECT did as id, day_name as name, day_order FROM Exercise_Plan_Day WHERE pid = %s ORDER BY day_order, day_name""", (plan_id,))
        
        days = cursor.fetchall()
        
        #get the exercises for the selected day
        for day in days:
            cursor.execute("""
                SELECT e.eid as id, e.ename, e.etype as level, e.ebpart as muscle_group,
                       ee.sets, ee.reps, ee.duration, ee.notes
                FROM Exercises e
                JOIN Exercise_Entry ee ON e.eid = ee.eid
                WHERE ee.did = %s
                ORDER BY ee.exercise_order
            """, (day['id'],))
            
            day['exercises'] = cursor.fetchall()
        
        conn.close()
        return days
    except Exception as e:
        print(f"Error in get_user_plan_days: {e}")
        return []

def add_plan_day(user_id, day_name):
    try:
        conn = connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT main_pid FROM User
            WHERE uid = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result or not result['main_pid']:
            cursor.execute("""
                INSERT INTO Exercise_Plan (uid, plan_name, description)
                VALUES (%s, 'My Workout Plan', 'Custom workout plan with flexible days')
            """, (user_id,))
            
            plan_id = cursor.lastrowid
            
            cursor.execute("""
                UPDATE User
                SET main_pid = %s
                WHERE uid = %s
            """, (plan_id, user_id))
        else:
            plan_id = result['main_pid']
        
        cursor.execute("""
            SELECT MAX(day_order) AS max_order FROM Exercise_Plan_Day
            WHERE pid = %s
        """, (plan_id,))
        
        max_order_result = cursor.fetchone()
        max_order = max_order_result['max_order'] if max_order_result and max_order_result['max_order'] is not None else 0
        next_order = max_order + 1
        
        cursor.execute("""
            INSERT INTO Exercise_Plan_Day (pid, day_name, day_order)
            VALUES (%s, %s, %s)
        """, (plan_id, day_name, next_order))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in add_plan_day: {e}")
        return False

def add_exercises_to_day(day_id, exercise_ids):
    print("ADD EXERCISES", day_id, exercise_ids)
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(exercise_order) as max_order FROM Exercise_Entry
            WHERE did = %s
        """, (day_id,))
        result = cursor.fetchone()
        max_order = result['max_order'] if result else None
        next_order = 1 if max_order is None else max_order + 1
        print("orders", max_order, next_order)
        
        added_count = 0
        print("exerciseids", exercise_ids)
        
        for exercise_id in exercise_ids:
            #detecting duplicates
            try:
                cursor.execute("""
                    SELECT COUNT(*) as count FROM Exercise_Entry
                    WHERE did = %s AND eid = %s
                    """, (day_id, exercise_id))
                result = cursor.fetchone()
                count = result['count']
                
                if count == 0:
                    cursor.execute("""
                        INSERT INTO Exercise_Entry (did, eid, exercise_order, sets, reps)
                        VALUES (%s, %s, %s, 3, 10)
                        """, (day_id, exercise_id, next_order))
                    next_order += 1
                    added_count += 1
            except Exception as inner_e:
                print(f"Error adding exercise {exercise_id} to day {day_id}: {inner_e}")
                continue
        
        conn.commit()
        return added_count
        
    except Exception as e:
        print(f"Error in add_exercises_to_day: {e}")
        return 0
    conn.close()
            
def get_day_owner_id(day_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ep.uid
            FROM Exercise_Plan_Day epd
            JOIN Exercise_Plan ep ON epd.pid = ep.pid
            WHERE epd.did = %s
        """, (day_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['uid'] if result else None
    except Exception as e:
        print(f"Error in get_day_owner_id: {e}")
        return None
    
def remove_exercise_from_plan_day(day_id, exercise_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM Exercise_Entry
            WHERE did = %s AND eid = %s
        """, (day_id, exercise_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in remove_exercise_from_plan_day: {e}")
        return False

def update_plan_day_name(day_id, new_name):
    try:
        conn = connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Exercise_Plan_Day
            SET day_name = %s
            WHERE did = %s
        """, (new_name, day_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in update_plan_day_name: {e}")
        return False

def delete_plan_day(day_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Exercise_Entry
            WHERE did = %s
        """, (day_id,))
        cursor.execute("""
            DELETE FROM Exercise_Plan_Day
            WHERE did = %s
        """, (day_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in delete_plan_day: {e}")
        return False

def get_main_plan_with_days(user_id):
    conn = connect()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT main_pid FROM User WHERE uid = %s
            """, (user_id,))
            result = cursor.fetchone()
            if not result or not result['main_pid']:
                return None
            
            cursor.execute("""
            SELECT 
            p.pid,
            p.plan_name,
            p.creation_date,
            COUNT(d.did) as day_count,
            GROUP_CONCAT(d.day_order ORDER BY d.day_order) AS day_orders
            FROM Exercise_Plan p
            LEFT JOIN Exercise_Plan_Day d ON p.pid = d.pid
            WHERE p.pid = %s
            GROUP BY p.pid
            """, (result['main_pid'],))
            
            plan = cursor.fetchone()
            if not plan:
                return None
            creation_date = plan['creation_date']
            days_since_creation = (datetime.now() - creation_date).days
            plan['current_day'] = (days_since_creation % plan['day_count']) + 1 if plan['day_count'] > 0 else 0
            
            #pulling the exercises for the current day
            if plan['current_day'] > 0:
                cursor.execute("""
                    SELECT e.ename, epe.sets, epe.reps, epe.duration
                    FROM Exercise_Entry epe
                    JOIN Exercises e ON epe.eid = e.eid
                    JOIN Exercise_Plan_Day d ON epe.did = d.did
                    WHERE d.pid = %s AND d.day_order = %s
                    ORDER BY epe.exercise_order
                """, (plan['pid'], plan['current_day']))
                plan['exercises'] = cursor.fetchall()
            else:
                plan['exercises'] = []
            return plan
            
    except Exception as e:
        print(f"Database error: {e}")
        return None
    conn.close()
    return

def create_default_plan(user):
    conn = connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Exercise_Plan (uid, plan_name)
                VALUES (%s, 'My Workout Plan')
            """, (user.id,))
            plan_id = cursor.lastrowid
            user.set_main_plan(plan_id)
            
            conn.commit()
            return plan_id
    except Exception as e:
        print(f"Error creating default plan: {e}")
        conn.rollback()
        return None
    conn.close()
