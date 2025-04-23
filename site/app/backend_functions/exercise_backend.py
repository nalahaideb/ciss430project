#import app.db
import pymysql.cursors
#temporarily until i figure out how to PROPERLY FUCKIN IMPORT db.py
def connect():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
    )

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

def get_exercises(muscle_groups, equipment, level, name):
    conn = connect()
    c = conn.cursor()
    muscle_string = ''
    equip_string = ''
    if len(muscle_groups) > 0:
        for i in muscle_groups:
            muscle_string +="'%s'," % i
        muscle_string = muscle_string[:len(muscle_string) - 1]
    else:
        muscle_string = str(list_muscles())
        muscle_string = muscle_string[1:len(muscle_string)-1]
    if len(equipment) > 0:
        for i in equipment:
            equip_string +="'%s'," % i
        equip_string = equip_string[:len(equip_string) - 1]
    else:
        equip_string = str(list_equipment())
        equip_string = equip_string[1:len(equip_string)-1]
        
    print("select * from Exercises where ebpart in (%s) and eequip in (%s);" % (muscle_string, equip_string))
    c.execute("select * from Exercises where ebpart in (%s) and eequip in (%s);" % (muscle_string, equip_string))
    results = c.fetchall()
    conn.close()
    c.close()
    return results

def get_user_plan_days(user_id):
    """
    Get all exercise plan days for a user's active plan
    
    Parameters:
    user_id (int): The ID of the user
    
    Returns:
    list: A list of day objects, each containing id, name, and exercises
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""SELECT main_pid FROM User WHERE uid = %s""", (user_id,))
        
        result = cursor.fetchone()
        if not result or not result['main_pid']:
            # If user has no main plan, try to get any plan they own
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
    """
    Add a new day to the user's exercise plan
    
    Parameters:
    user_id (int): The ID of the user
    day_name (str): The name of the day
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        conn = connect()  # Use your existing connect function
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
        
        # Get the highest day_order
        cursor.execute("""
            SELECT MAX(day_order) AS max_order FROM Exercise_Plan_Day
            WHERE pid = %s
        """, (plan_id,))
        
        max_order_result = cursor.fetchone()
        # Use the named column from the result dictionary
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
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # Ensure dictionary cursor
        
        # Get max exercise order
        cursor.execute("""
            SELECT MAX(exercise_order) as max_order FROM Exercise_Entry
            WHERE did = %s
        """, (day_id,))
        result = cursor.fetchone()
        max_order = result['max_order'] if result else None  # Access as dictionary
        next_order = 1 if max_order is None else max_order + 1
        print("orders", max_order, next_order)
        
        added_count = 0
        print("exerciseids", exercise_ids)
        
        for exercise_id in exercise_ids:
            try:
                # Check if this exercise is already in this day
                cursor.execute("""
                    SELECT COUNT(*) as count FROM Exercise_Entry
                    WHERE did = %s AND eid = %s
                    """, (day_id, exercise_id))
                result = cursor.fetchone()
                count = result['count']  # Access as dictionary
                
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
    """
    Get the ID of the user who owns a day
    
    Parameters:
    day_id (int): The ID of the day
    
    Returns:
    int: The ID of the user who owns the day, or None if not found
    """
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
    """
    Remove an exercise from a day in the user's plan
    
    Parameters:
    day_id (int): The ID of the day
    exercise_id (int): The ID of the exercise
    
    Returns:
    bool: True if successful, False otherwise
    """
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
    """
    Update the name of a day in the user's plan
    
    Parameters:
    day_id (int): The ID of the day
    new_name (str): The new name for the day
    
    Returns:
    bool: True if successful, False otherwise
    """
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
    """
    Delete a day from the user's plan and all its exercises
    
    Parameters:
    day_id (int): The ID of the day
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # First delete all exercises for this day
        cursor.execute("""
            DELETE FROM Exercise_Entry
            WHERE did = %s
        """, (day_id,))
        
        # Then delete the day itself
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
