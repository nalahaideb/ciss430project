'''
###########################################################
########            FRONTEND FUNCTIONS             ########
###########################################################
'''

def generate_filters():
    return

def filter_exercises():
    #join tables according to filters
    
    #return the level of exercise expertise selected
    level = request.form.get('level')

    #some kind of loop to get all exercises w/ a certain body part
    target_muscles = request.form.getlist('MUSCLE_CHECKBOX')
    #get equipment selected
    equipment_list = request.form.getlist('EQUIPMENT_CHECKBOX')

    #if no entry do not include rating in query, clear rating if not a number
    rating = request.form.get('rating')
    if isalpha(rating):
        rating = None
        
        #conn = mysql.connector.connect(**db_config)
        #cursor = conn.cursor()

        # Execute the query
        query = "select * from exercise where "
        cursor.execute(query, (firstname, lastname))

        # Fetch the results
        results = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()

    #     return render_template('index.html', results=results)

    # return render_template('index.html')
    
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
