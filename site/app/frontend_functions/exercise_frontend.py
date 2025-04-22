import pymysql

def add_exercises():
    #if request.method == 'GET':
    ex_name = request.form.get('exercise_name')
    ex_desc = request.form.get('exercise_desc')
    ex_type = request.form.get('exercise_type')
    ex_bpart = request.form.get('exercise_bpart')
    ex_equip = request.form.get('exercise_equip')
    #get exercise rating and other data from table, return here
    
    return
