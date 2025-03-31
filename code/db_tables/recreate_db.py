'''
************************************************************************
#DO NOT RUN THIS UNLESS YOU WANT TO DROP **EVERYTHING** AND RECREATE IT#
#THE DATA WILL NOT BE SAVED UNTIL IT IS WRITTEN BY THE BACK END PROGRAM#
########################################################################
#                     table creation is as follows:                    #
#        user > user dependents > exercises > exercise dependents      # 
************************************************************************
'''
import pymysql
#local testing right now, implementing web testing soon
conn = pymysql.connect(user='root', passwd='root')
c = conn.cursor(pymysql.cursors.DictCursor)

# try:
c.execute("drop database exdb;")
#print("successfully dropped database, trying to recreate...")
c.execute("create database exdb;")
# except:
#     print("failure dropping database, continuing...")
#     c.execute("drop database exdb;")
#     c.execute("create database exdb;")
c.execute("use exdb;")

#i forget if we're actually giving email to this table or user-credentials
#also need to add uname to the user table in the UML diag
c.execute("create table user (uid INT AUTO_INCREMENT, fname VARCHAR(100) NOT NULL, lname VARCHAR(100) NOT NULL, username VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL, last_login DATETIME NOT NULL, creation_date DATETIME NOT NULL, primary key (uid));")

#need to update the user-credentials table in the UML diag with the 'uid' ref
#not gonna include email here, unless we want to have that as a sign in option
c.execute("create table user_credentials (ucid INT AUTO_INCREMENT, uc_uid INT NOT NULL, uc_username VARCHAR(100) NOT NULL, salt CHAR(32), primary key (ucid), foreign key (uc_uid) references user (uid));")

#i didnt like having 'user, user1, user2' ala our UML diag in this statement, buddy and chum are interchangeable and are just placeholders atm
c.execute("create table friends (buddy INT NOT NULL, chum INT NOT NULL, foreign key (buddy) references user (uid), foreign key (chum) references user (uid));")

#we can probably find something smarter to do with the 'friends' and 'messages' table, as they differ only with 'messages' having the 'content' field
c.execute("create table messages (buddy_from INT NOT NULL, chum_to INT NOT NULL, content VARCHAR(1000), foreign key (buddy_from) references user (uid), foreign key (chum_to) references user (uid));")

c.execute("create table exercise (eid INT, ename varchar(100), edesc varchar(500), etype varchar(100), ebpart varchar(100), eequip varchar(100), erating varchar(100), primary key (eid))engine=innodb;")

#gonna leave it short at 5 for now, we can expand it later
#im making these INT instead of VARCHAR like in the UML diag because they should be able to reference 'exercises' for more info on said exercise
c.execute("create table day (did INT AUTO_INCREMENT, ex1 INT, ex2 INT, ex3 INT, ex4 INT, ex5 INT, primary key (did), foreign key (ex1) references exercise (eid), foreign key (ex2) references exercise (eid), foreign key (ex3) references exercise (eid), foreign key (ex4) references exercise (eid), foreign key (ex5) references exercise (eid));")

c.execute("create table schedule (sid INT AUTO_INCREMENT, uid INT NOT NULL, d1 INT, d2 INT, d3 INT, d4 INT, d5 INT, d6 INT, d7 INT, primary key (sid));")

#didnt include uprogress, i think there are going to be multiple points of progression that align to different goals so that might have to go in a different table, namely progress (progress per goal as it were)
#ptype will be a lot of help when people look up 'xyz plan' in some sort of search bar, or 'plans made by user xyz' etc.
c.execute("create table user_plan (upid INT AUTO_INCREMENT, uid INT NOT NULL, up_uname VARCHAR(100) NOT NULL, ptype VARCHAR(100), up_usched INT, primary key (upid), foreign key (up_usched) references schedule (sid));")

#there'll have to be a clause later that will remove past records that have been broken, there should be at most 1 for each exercise
c.execute("create table user_records (urid INT AUTO_INCREMENT, ur_uid INT NOT NULL, record_num INT NOT NULL, ur_eid INT NOT NULL, record_date DATETIME NOT NULL, primary key (urid), foreign key (ur_uid) references user (uid), foreign key (ur_eid) references exercise (eid));")

c.execute("create table goals (gid INT AUTO_INCREMENT, g_uid INT NOT NULL, goal INT, g_exercise INT, primary key (gid), foreign key (g_uid) references user (uid), foreign key (g_exercise) references exercise (eid));")

c.execute("create table progress (pid INT AUTO_INCREMENT, p_gid INT NOT NULL, p_uid INT NOT NULL, primary key (pid), foreign key (p_gid) references goals (gid), foreign key (p_uid) references user (uid));")
