import os
import pymysql
import random
try:
    os.system("mysql --user=root --password=root < exercisedb.sql")    
    conn = pymysql.connect(user='root', passwd='root')
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute('use exercisedb;')
except Exception as e:
    print("ERROR", e)
def cleanup(x, islist=False):
    x = x.replace('\n', '')
    x = x.replace('"', '')
    x = x.replace("'", '')
    if x == r'\N':
        if islist:
            x = []
    elif x == '':
        x = "N/A"
    return x

#later ill have to add parameters to reference which connection is being opened by the cursor, "HOST, PORT, USER, PASS" etc
def create_exercises():
#Title,Desc,Type,BodyPart,Equipment,Level,Rating,RatingDesc
#all values are varchar, null values are replaced with a "N/A"
    f = open("/home/student/Desktop/ciss430/project/data/megaGymDataset.csv")
    f.readline()
    for e in f:
        exercise = e.split(',')
        entry = []
        for i in exercise:
            entry.append(cleanup(i))
            #dataset was made by actual honest to god fucking retards so there will be exclusions because there are commas in both the desc and title, no way to tell how many commas exist before the 'bodypart' field appears.
        try:
            c.execute("start transaction;")
            #enter the following values of entry deliniated by commas: 1, n-5, n-4, n-3, n-2, n-1, n
            entry_len = len(entry)
            #old insert
            c.execute("insert into Exercises (ename, etype, ebpart, eequip) values ('" + entry[1] + "', '"  + entry[entry_len - 6] + "', '" + entry[entry_len - 5] + "', '" + entry[entry_len - 4] + "');")
            #print("INSERTED", entry)
            c.execute("commit;")
        except Exception as e:
            print(e)
            print("ENTRY FAILED,", entry[1:], "!!!",entry_len,"!!!")
    return

def insert_test_users():
    megalist = ''
    for i in range(1000):
        fname = 'retard' + str(i)
        lname = 'goober' + str(i)
        username = fname + str(i % 10) + lname
        email = fname + lname + '@gmail.com'
        last_login = '00:00:00'
        creation_date = '00:00:00'
        entry = str("('" + fname + "', '" + lname + "', '" + username + "', '" + email + "', '" + last_login + "', '" + creation_date + "'), ")
        megalist = megalist + entry
    #print(megalist)
    megalist = megalist[:len(megalist)-3] + ')'
    #entry = [fname, lname, username, email, last_login, creation_date]
    try:
        c.execute("start transaction;")
        c.execute("insert into user (fname, lname, username, email, last_login, creation_date) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST USER INSERT FAILED: ", e)
    return

def insert_premade_days():
    megalist = ''
    for i in range(1000):
        ex1 = random.randrange(0, 2587)
        ex2 = random.randrange(0, 2587)
        ex3 = random.randrange(0, 2587)
        ex4 = random.randrange(0, 2587)
        ex5 = random.randrange(0, 2587)
        entry = "(" + str(ex1) + ", " + str(ex2) + ", " + str(ex3) + ", " + str(ex4) + ", " + str(ex5) + "), "
        megalist = megalist + entry
    try:
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into day (ex1, ex2, ex3, ex4, ex5) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST DAY INSERT FAILED: ", e)
    return

#this is fucking up only sometimes, im certain its because its entering the same relation with friend1 and friend 2, whatever 
def insert_test_friends():
    megalist = ''
    for i in range(1000):
        friend1 = random.randrange(0, 1000)
        friend2 = random.randrange(0, 1000)
        relation = '(' + str(friend1) + ', ' + str(friend2) + '), ' 
        megalist = megalist + relation
    try:
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into friends (buddy, chum) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST INSERT FRIENDS FAILURE: ", e)
    return

def insert_premade_schedules():
    megalist = ''
    for i in range(1000):
        day_array = '('
        for k in range(7):
            day_array = day_array + str(random.randrange(0,1000)) + ', '
        day_array = day_array + str(random.randrange(0,1000)) + '), '
        megalist = megalist + day_array
    try:
        #print(megalist)
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into schedule (uid, d1, d2, d3, d4, d5, d6, d7) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST INSERT SCHEDULE FAILURE: ", e)
    return

def insert_test_progress():
    megalist = ''
    for i in range(1000):
        gid = random.randrange(0, 1000)
        uid = random.randrange(0, 200)
        progress = '(' + str(gid) + ', ' + str(uid) + '), '
        megalist = megalist + progress
    try:
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into progress (p_gid, p_uid) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST INSERT PROGRESS FAILURE: ", e)
        print(megalist)
    return

def insert_test_plans():
    megalist = ''
    for i in range(1000):
        uid = random.randrange(0,1000)
        uname = 'retardgoober' + str(i * random.randrange(0,1000))
        ptype = 'STUPID'
        usched = random.randrange(0, 1000)
        #omitting this for atomicity
        #uprogress = random.randrange(0, 1000)
        plan = '(' + str(uid) + ", '" + uname + "', '" + ptype + "', " + str(usched) + '), ' #+ ', ' + str(uprogress)
        megalist = megalist + plan
    try:
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into user_plan (up_uid, up_uname, ptype, up_usched) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST INSERT PLANS FAILURE: ", e)
        print("insert into user_plan (uid, uname, ptype, usched, uprogress) values " + megalist + ";")
    return

def insert_test_goals():
    megalist = ''
    for i in range(1000):
        uid = random.randrange(0, 1000)
        goal = random.randrange(0, 200)
        ex = "3 sets of bottle flips x F"
        goal = '(' + str(uid) + ', ' + str(goal) + ', ' + ex + '), '
        megalist = megalist + goal
    try:
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into goals (g_uid, goal, g_exercise) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST INSERT GOALS FAILURE: ", e)
        print(megalist)
    return

def insert_test_credentials():
    megalist = ''
    for i in range(1000):
        uname = 'retardgoober' + str(i * random.randrange(0,1000))
        uid = str(random.randrange(0, 1000))
        salt = random.randrange(72, 100)
        login = '(' + uid + ', ' + uname + ', ' + str(salt) + '), '
    try:
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into user_credentials (uc_uid, uc_username, salt) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST INSERT CREDENTIALS FAILURE: ", e)        
        print(megalist)
    return

def insert_test_messages():
    megalist = ''
    for i in range(1000):
        user1 = random.randrange(0, 1000)
        user2 = random.randrange(0, 1000)
        content = 'AAAAAUUUUUUGGGGHHHHHHHHHABFUNU1NU1' + chr(random.randrange(72, 100))
        message = '(' + str(user1) + ', ' + str(user2) + ', ' + content + '), '
    try:
        megalist = megalist[:len(megalist)-3] + ')'
        c.execute("start transaction;")
        c.execute("insert into messages (buddy_from, chum_to, content) values " + megalist + ";")
        c.execute("commit;")
    except Exception as e:
        print("TEST INSERT MESSAGES FAILURE: ", e)
        print(megalist)
    return
