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
'''
THE STRING REPLACEMENT FOR REMOVING SPACES IS CAUSING MULTI-WORD EQUIPMENT AND MUSCLES TO CONCAT, NEED TO FIX OR WORK AROUND LATER
'''
def list_muscles():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT GROUP_CONCAT(DISTINCT ebpart SEPARATOR ', ') AS ebpart FROM Exercises;")
    muscle_arr = c.fetchall()
    muscle_string = str(muscle_arr[0])
    muscle_string = muscle_string[11:len(muscle_string)-2]
    muscle_arr = muscle_string.split(',')
    muscle_string = ''
    for i in muscle_arr:
        muscle_string += "\'%s\'," % i
    muscle_string = muscle_string[:len(muscle_string) - 1]
    muscle_string = muscle_string.replace(' ', '')
    c.close()
    conn.close()
    return muscle_string

def list_equipment():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT GROUP_CONCAT(DISTINCT eequip SEPARATOR ', ') AS equip FROM Exercises;")
    equip_arr = c.fetchall()
    equip_string = str(equip_arr[0])
    equip_string = equip_string[11:len(equip_string)-2]
    equip_arr = equip_string.split(',')
    equip_string = ''
    for i in equip_arr:
        equip_string += "\'%s\'," % i
    equip_string = equip_string[:len(equip_string) - 1]
    equip_string = equip_string.replace(' ', '')
    c.close()
    conn.close()
    return equip_string

def get_exercises(muscle_groups, equipment, level, name):
    conn = connect()
    c = conn.cursor()
    muscle_string = ''
    equip_string = ''
    #print("PASSED DATA TO GET_EXERCISES::: ", muscle_groups, equipment)
    if muscle_groups != None:
        for i in muscle_groups:
            muscle_string +="'%s'," % i
        muscle_string = muscle_string[:len(muscle_string) - 1]
    else:
        muscle_string = list_muscles()
    equip_string = list_equipment()
        # c.execute("SELECT GROUP_CONCAT(DISTINCT eequip SEPARATOR ', ') AS equip FROM Exercises;")
        # equip_arr = c.fetchall()
        # equip_string = str(equip_arr[0])
        # equip_string = equip_string[11:len(equip_string)-2]
        # #print("equip results:", equip_string, type(equip_string))
        # equip_arr = equip_string.split(',')
        # equip_string = ''
        # for i in equip_arr:
        #     equip_string += "\'%s\'," % i
        # equip_string = equip_string[:len(equip_string) - 1]
        # equip_string = equip_string.replace(' ', '')
        #print("equipment:",equip_string)
    print("select * from Exercises where ebpart in (%s) and eequip in (%s)" % (muscle_string, equip_string))
    c.execute("select * from Exercises where ebpart in (%s) and eequip in (%s)" % (muscle_string, equip_string))
    results = c.fetchall()
    conn.close()
    c.close()
    return results
   
