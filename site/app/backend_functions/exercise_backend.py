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
def get_exercises(muscle_groups, equipment):
    conn = connect()
    c = conn.cursor()
    muscle_string = ''
    equip_string = ''
    print("PASSED DATA TO GET_EXERCISES::: ", muscle_groups, equipment)
    if muscle_groups != None:
        for i in muscle_groups:
            #print("MUSCLE ENTRY = ", i)
            muscle_string +="'%s'," % i
        muscle_string = muscle_string[:len(muscle_string) - 1]
        print("MUSCLE STRING =", muscle_string, type(muscle_groups))
    else:
        c.execute("select distinct ebpart from Exercises;")
        muscle_string = c.fetchall()
    if equipment != None:
        for i in equipment:
            print("EQUIP ENTRY = ", i)
            equip_string.join("'%s,'" % i)
    else:
        c.execute("SELECT GROUP_CONCAT(DISTINCT eequip SEPARATOR ', ') AS equip FROM Exercises;")
        equip_arr = c.fetchall()
        equip_string = str(equip_arr[0])
        equip_string = equip_string[11:len(equip_string)-2]
        #print("equip results:", equip_string, type(equip_string))
        equip_arr = equip_string.split(',')
        equip_string = ''
        for i in equip_arr:
            equip_string += "\'%s\'," % i
        equip_string = equip_string[:len(equip_string) - 1]
        equip_string = equip_string.replace(' ', '')
        print("equipment:",equip_string)
    print("select * from Exercises where ebpart in (%s) and eequip in (%s)" % (muscle_string, equip_string))
    c.execute("select * from Exercises where ebpart in (%s) and eequip in (%s)" % (muscle_string, equip_string))
#results = []
    results = c.fetchall()
    c.close()
    return results
    # return render_template('exdb_query_result.html', target_muscles=target_muscles, results=results)
