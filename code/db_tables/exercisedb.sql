drop database if exists exercisedb;
create database exercisedb;
use exercisedb;

create table User_Credentials (
ucid INT AUTO_INCREMENT,
username VARCHAR(100) UNIQUE not NULL,
email VARCHAR(100) UNIQUE not NULL,
salt CHAR(32),
creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_login TIMESTAMP
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
