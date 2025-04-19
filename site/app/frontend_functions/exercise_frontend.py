import pymysql

# def generate_filters():
#     conn = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='root',
#         database='exercisedb',
#         cursorclass=pymysql.cursors.DictCursor
#         )
#     cursor = conn.cursor()
#     bodyparts = []
#     equipment = []
#     ex_type = []
#     cursor.execute("select distinct ebpart from Exercises;")
#     bodyparts = cursor.fetchall()
#     cursor.execute("select distinct eequip from Exercises;")
#     equipment = cursor.fetchall()
#     cursor.execute("select distinct etype from Exercises;")
#     ex_type = cursor.fetchall()
#     print(bodyparts, equipment, ex_type)
#     return bodyparts, equipment, ex_type


def add_exercises():
    #if request.method == 'GET':
    ex_name = request.form.get('exercise_name')
    ex_desc = request.form.get('exercise_desc')
    ex_type = request.form.get('exercise_type')
    ex_bpart = request.form.get('exercise_bpart')
    ex_equip = request.form.get('exercise_equip')
    #get exercise rating and other data from table, return here
    
    return
