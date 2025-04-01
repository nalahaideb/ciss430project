import os
import pymysql
import random
conn = pymysql.connect(user='root', passwd='root')
c = conn.cursor(pymysql.cursors.DictCursor)
c.execute('use exdb;')

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
    # try:
    #     # c.execute("create table exercise (eid INT, ename varchar(100), edesc varchar(500), etype varchar(100), ebpart varchar(100), eequip varchar(100), erating varchar(100), primary key (id))engine=innodb;")
    # except:
    #     print("table made, continuing...")
    for e in f:
        exercise = e.split(',')
        entry = []
        for i in exercise:
            entry.append(cleanup(i))
            #dataset was made by actual honest to god fucking retards so there will be exclusions because there are commas in both the desc and title, no way to tell how many commas exist before the 'bodypart' field appears.
        try:
            c.execute("start transaction;")
            c.execute("insert into exercise (ename, edesc, etype, ebpart, eequip, erating) values ('" + entry[1] + "', '" + entry[2] + "', '" + entry[3] + "', '" + entry[4] + "', '" + entry[5] + "', '" + entry[6] + "');")
            c.execute("commit;")
        except Exception as e:
            print(e)
            print("ENTRY FAILED,", entry[1:])
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
    return

def insert_premade_plans():
    return
