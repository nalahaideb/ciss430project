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
def list_muscles():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT GROUP_CONCAT(DISTINCT ebpart SEPARATOR ', ') AS ebpart FROM Exercises;")
    muscle_arr = c.fetchall()
    muscle_string = str(muscle_arr[0])
    #print("MUSCLE STRING 1", muscle_string)
    muscle_string = muscle_string[11:len(muscle_string)-2]
    muscle_string = muscle_string.replace("'",'')
    muscle_string = muscle_string.replace('"','')
    muscle_string = muscle_string.replace(' ','')
    muscle_arr = muscle_string.split(',')
    for i in muscle_arr:
        i = i.replace(' ', '')
    return muscle_arr
    

def list_equipment():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT GROUP_CONCAT(DISTINCT eequip SEPARATOR ', ') AS equip FROM Exercises;")
    equip_arr = c.fetchall()
    equip_string = str(equip_arr[0])
    equip_string = equip_string[11:len(equip_string)-2]
    equip_arr = equip_string.split(',')
    equip_string = ''
    ret = []
    for i in equip_arr:
        #i dont know why it always prefaces each i with a space after the first entry, but this is a quick fix
        if i[0] == ' ':
            i = i[1:]
        i = "'" + i + "'"
        ret.append(i)
        #equip_string += "'" + i + "',"
        #equip_string += "'%s'," % i
    print("!!!!!!!!!!!!!!!!!!!EQUIP_ARR: ", ret)
    c.close()
    conn.close()

    return ret

def get_exercises(muscle_groups, equipment, level, name):
    conn = connect()
    c = conn.cursor()
    muscle_string = ''
    equip_string = ''
    print("GROUP TYPES", type(muscle_groups), type(equipment))
    if muscle_groups != None:
        for i in muscle_groups:
            muscle_string +="'%s'," % i
        muscle_string = muscle_string[:len(muscle_string) - 1]
    if equipment != None:
        for i in equipment:
            equip_string +="'%s'," % i
        equip_string = equip_string[:len(equip_string) - 1]
   
    print("select * from Exercises where ebpart in (%s) and eequip in (%s);" % (muscle_string, equip_string))
    c.execute("select * from Exercises where ebpart in (%s) and eequip in (%s);" % (muscle_string, equip_string))
    results = c.fetchall()
    conn.close()
    c.close()
    return results
