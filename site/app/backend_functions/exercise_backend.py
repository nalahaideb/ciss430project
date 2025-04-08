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
