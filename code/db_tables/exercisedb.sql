drop database if exists exercisedb;
create database exercisedb;
use exercisedb;

create table User_Credentials (
ucid INT AUTO_INCREMENT,
username VARCHAR(100) UNIQUE not NULL,
email VARCHAR(100) UNIQUE not NULL,
phash VARCHAR(255) not NULL,
creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_login TIMESTAMP,
primary key (ucid)
)engine=innodb;

create table User (
uid INT AUTO_INCREMENT,
ucid INT not NULL,
fname VARCHAR(100) DEFAULT 'Firstname',
lname VARCHAR(100) DEFAULT 'Lastname',
bio VARCHAR(1024) DEFAULT 'user bio',
primary key (uid),
foreign key (ucid) references User_Credentials(ucid) on delete CASCADE
)engine=innodb;

create table Friends (
fid INT AUTO_INCREMENT,
user1 INT not NULL,
user2 INT not NULL,
primary key (fid),
foreign key (user1) references User(uid) on delete CASCADE,
foreign key (user2) references User(uid) on delete CASCADE
)engine=innodb;

create table Messages (
mid INT AUTO_INCREMENT,
sender_id INT not NULL,
receiver_id INT not NULL,
message_text VARCHAR(1024) not NULL,
sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
primary key (mid),
foreign key (sender_id) references User(uid) on delete CASCADE,
foreign key (receiver_id) references User(uid) on delete CASCADE
)engine=innodb;

create table Exercises (
eid INT AUTO_INCREMENT,
ename VARCHAR(100) not NULL,
etype ENUM('Strength', 'Cardio', 'Stretching', 'Plyometrics',
'Strongman', 'Olympic Weightlifting') not NULL,
ebpart ENUM('Abdominals', 'Biceps', 'Chest', 'Cardio', 'Back',
'Glutes', 'Triceps', 'Forearms', 'Shoulders', 'Hamstrings') not NULL,
eequip VARCHAR(100),
primary key (eid)
)engine=innodb;

create table Exercise_Plan (
pid INT AUTO_INCREMENT,
uid INT not NULL,
plan_name VARCHAR(100) not NULL,
description TEXT,
creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
primary key (pid),
foreign key (uid) references User(uid) on delete CASCADE
)engine=innodb;

create table Exercise_Plan_Day (
did INT AUTO_INCREMENT,
pid INT not NULL,
day_name VARCHAR(50) not NULL,
day_order INT,
primary key (did),
foreign key (pid) references Exercise_Plan(pid) on delete CASCADE
)engine=innodb;

create table Exercise_Entry (
entry_id INT AUTO_INCREMENT,
did INT not NULL,
eid INT not NULL,
exercise_order INT,
sets INT,
reps INT,
duration INT,
notes TEXT,
primary key (entry_id),
foreign key (did) references Exercise_Plan_Day(did) on delete CASCADE,
foreign key (eid) references Exercises(eid)
)engine=innodb;


alter table User
add column main_pid INT,
add foreign key (main_pid) references Exercise_Plan(pid) on delete set NULL;


-- test user creation
insert into User_Credentials(username, email, phash)
values ('test', 'test@example.com', 'scrypt:32768:8:1$cPRqTQ9ZEEvxlrNQ$4f210848058e3c13b719b8cd64f3019c7c802c0c5a3707291d3ffa8f421855525740fdd59d512e4b4b1f0ec21d57146c444c6246a2cd117a5e77ce7ec18ad49b');

insert into User (ucid, fname, lname, bio)
values (
(select ucid from User_Credentials where username = 'test'),
'testfname', 'testlname', 'test bio'
);

insert into User_Credentials(username, email, phash)
values ('test2', 'test2@example.com', 'scrypt:32768:8:1$cPRqTQ9ZEEvxlrNQ$4f210848058e3c13b719b8cd64f3019c7c802c0c5a3707291d3ffa8f421855525740fdd59d512e4b4b1f0ec21d57146c444c6246a2cd117a5e77ce7ec18ad49b');

insert into User (ucid, fname, lname, bio)
values (
(select ucid from User_Credentials where username = 'test2'),
'test2fname', 'test2lname', 'test2 bio'
);
