#temporary db connection data, to be replaced when the project goes live. for now it is local
import os
import pymysql
conn = pymysql.connect(user='root', passwd='root')
c = conn.cursor(pymysql.cursors.DictCursor)

# try:
#     c.execute("create database exdb;")
c.execute("use exdb;")
# except:
#     c.execute("drop database exdb;")
#     c.execute("create database exdb;")
#     c.execute("use exdb;")
#adding exercises to table
def cleanup(x, islist=False):
    x = x.replace('\n', '')
    x = x.replace('"', '')
    x = x.replace("'", '')
    if x == r'\N':
        if islist:
            x = []
    elif x == '':
        x = "N/A"
    # elif islist:
    #     x = x.split(',')
    #     if x == ['']:
    #         x = []
    return x

#Title,Desc,Type,BodyPart,Equipment,Level,Rating,RatingDesc
#all values are varchar, null values are replaced with a "N/A"
f = open("/home/student/Desktop/ciss430/project/data/megaGymDataset.csv")
f.readline()
try:
    c.execute("create table exercise (id INT, title_ varchar(100), desc_ varchar(500), type_ varchar(100), bodypart_ varchar(100), equipment_ varchar(100), rating_ varchar(100), primary key (id))engine=innodb;")
except:
    print("table made, continuing...")
for e in f:
    exercise = e.split(',')
    entry = []
    for i in exercise:
        entry.append(cleanup(i))
    try:
        c.execute("start transaction;")
        c.execute("insert into exercise (id, title_, desc_, type_, bodypart_, equipment_, rating_) values (" + entry[0] + ", '" + entry[1] + "', '" + entry[2] + "', '" + entry[3] + "', '" + entry[4] + "', '" + entry[5] + "', '" + entry[6] + "');")
        c.execute("commit;")
    except:
        print("erm uh oh stinky, this didnt go in:", "insert into exercise (id, title_, desc_, type_, bodypart_, equipment_, rating_) values (" + entry[0] + ", '" + entry[1] + "', '" + entry[2] + "', '" + entry[3] + "', '" + entry[4] + "', '" + entry[5] + "', '" + entry[6] + "');")
