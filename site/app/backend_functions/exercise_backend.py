import db
def get_exercises(muscle_groups=[], equipment=[]):
    #run filter_exercises and generate_filters before this once implemented
    # conn = pymysql.connect(user='root', passwd='root')
    # c = conn.cursor(pymysql.cursors.DictCursor)
    c = get_db_connection()
    muscle_string = ''
    equip_string = ''
    for i in muscle_groups:
        
    c.execute("use exercisedb;")
    c.execute("select * from Exercises where ebpart in (")
    c.close()
    return render_template('exdb_query_result.html', target_muscles=target_muscles, results=results)
