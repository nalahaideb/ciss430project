#DATABASE FOR EXERICSES NEEDS SOME WORK, WILL BE FIXING SOON, THERE ARE SOME POORLY FORMATTED ENTRIES DUE TO THE CSV FACTOR
# import pymysql
# from flask import render_template, request, redirect, url_for, session

def generate_filters():
    
    return

def filter_exercises():
    #join tables according to filters
    
    #return the level of exercise expertise selected
    level = request.form.get('ex_level')

    #some kind of loop to get all exercises w/ a certain body part
    target_muscles = request.form.getlist('muscle_group')

    #get equipment selected
    equipment_list = request.form.getlist('EQUIPMENT_CHECKBOX')

    #if no entry do not include rating in query, clear rating if not a number
    # rating = request.form.get('rating')
    # if isalpha(rating):
    #     rating = None
        
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = "select * from exercise where "
    #for i in
    cursor.execute(query, (firstname, lastname))
    
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()

    #     return render_template('', results=results)

    # return render_template('')
    return

def add_exercises():
    #if request.method == 'GET':
    ex_name = request.form.get('exercise_name')
    ex_desc = request.form.get('exercise_desc')
    ex_type = request.form.get('exercise_type')
    ex_bpart = request.form.get('exercise_bpart')
    ex_equip = request.form.get('exercise_equip')
    #get exercise rating and other data from table, return here
    
    return

def get_exercises():
    #run filter_exercises and generate_filters before this once implemented
    conn = pymysql.connect(user='root', passwd='root')
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute("use exdb;")

    target_muscles = request.form.getlist('muscle_group')
    print("TEST TEST TEST TEST TEST TEST TEST TEST ", target_muscles)
    c.execute("select ename, ebpart, erating from exercise;")
    
    #selected_categories = request.form.getlist('categories')

    if target_muscles:
        placeholders = ', '.join(['%s'] * len(selected_categories))
        query = f"select ename, ebpart, eequip from exercise where category IN ({placeholders})"
        print("QUERY TEST QUERY TEST QUERY TEST QUERY TEST QUERY TEST ", placeholders)
        c.execute(query, selected_categories)
        results = cursor.fetchall()
    else:
        results = []
    c.close()
    conn.close()
    return render_template('exdb_query_result.html', target_muscles=target_muscles, results=results)
