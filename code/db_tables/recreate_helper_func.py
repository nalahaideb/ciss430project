import os
import pymysql
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
    conn = pymysql.connect(user='root', passwd='root')
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute('use exdb;')
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
        print("ex len = ", len(exercise))
        for i in exercise:
            entry.append(cleanup(i))
        #this dataset was made by actual honest to god fucking retards so there will be exclusions.
        try:
           c.execute("start transaction;")
            c.execute("insert into exercise (eid, ename, edesc, etype, ebpart, eequip, erating) values (" + entry[0] + ", '" + entry[1] + "', '" + entry[2] + "', '" + entry[3] + "', '" + entry[4] + "', '" + entry[5] + "', '" + entry[6] + "');")
            c.execute("commit;")
        except:
            print("erm uh oh stinky, this didnt go in:", "insert into exercise (id, title_, desc_, type_, bodypart_, equipment_, rating_) values (" + entry[0] + ", '" + entry[1] + "', '" + entry[2] + "', '" + entry[3] + "', '" + entry[4] + "', '" + entry[5] + "', '" + entry[6] + "');")

def insert_test_users():
    megalist = []
    for in range(1000):
        fname = ' '
        lname = ' '
        username = ' '
        email = ' '
        last_login = ' '
        creation_date = ' '
    c.execute("insert into user (fname, lname, username, email, last_login, creation_date) values (" + megalist + ");")
        
    return

def insert_premade_days():
    return

def insert_premade_schedules():
    return

def insert_premade_plans():
