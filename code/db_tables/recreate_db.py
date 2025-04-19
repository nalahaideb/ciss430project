'''
************************************************************************
#DO NOT RUN THIS UNLESS YOU WANT TO DROP **EVERYTHING** AND RECREATE IT#
#THE DATA WILL NOT BE SAVED UNTIL IT IS WRITTEN BY THE BACK END PROGRAM#
########################################################################
#                     table creation is as follows:                    #
#        user > user dependents > exercises > exercise dependents      # 
************************************************************************
'''
import os
import pymysql
import csv
import random
from werkzeug.security import generate_password_hash

def setup_db():
    try:
        os.system("mysql --user=root --password=root < exercisedb.sql")
    except Exception as e:
        print("database creation error:", e)

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
    )

def cleanup(value, islist=False):
    value = value.replace('\n', '').replace('"', '').replace("'", '')
    if value == r'\N':
        return [] if islist else "N/A"
    return value if value else "N/A"

def create_exercises(conn, csv_path):
    with conn.cursor() as cursor:
        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)

                for row in reader:
                    cleaned = [cleanup(value) for value in row]
                    if len(cleaned) < 6:
                        continue

                    try:
                        ename = cleaned[1]
                        etype = cleaned[-6]
                        ebpart = cleaned[-5]
                        eequip = cleaned[-4]

                        cursor.execute(
                            "INSERT INTO Exercises (ename, etype, ebpart, eequip) VALUES (%s, %s, %s, %s);",
                            (ename, etype, ebpart, eequip)
                        )
                    except Exception as insert_err:
                        print("Insert failed:", insert_err)
                        print("Data:", cleaned)
                conn.commit()
        except Exception as file_err:
            print("File or transaction error:", file_err)

def add_users(conn, num_users):
    credentials = []
    users = []

    for i in range(num_users):
        username = f'testuser{i}'
        email = f'{username}@example.com'
        phash = generate_password_hash(username)
        credentials.append((username, email, phash))

    try:
        with conn.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO User_Credentials (username, email, phash) VALUES (%s, %s, %s);",
                credentials
            )

            cursor.execute("SELECT LAST_INSERT_ID() as first_ucid;")
            first_ucid = cursor.fetchone()['first_ucid']

            for i in range(num_users):
                ucid = first_ucid + i
                fname = f'testuser{i}fname'
                lname = f'testuser{i}lname'
                bio = f'testuser{i} bio'
                users.append((ucid, fname, lname, bio))

            cursor.executemany(
                "INSERT INTO User (ucid, fname, lname, bio) VALUES (%s, %s, %s, %s);",
                users
            )

        conn.commit()
        print(f"Successfully added {num_users} users.")

    except Exception as e:
        print("Error during bulk user insert:", e)
        conn.rollback()

def seed_friend_data(conn, max_friends=3, max_requests=2):
    """
    Randomly creates friendships and friend requests between users in the database.
    Each user can have up to `max_friends` confirmed friends and `max_requests` pending friend requests.

    Ensures:
    - No duplicate pairs in Friends or Friend_Requests
    - A user does not request someone who already requested them
    """

    with conn.cursor() as cursor:
        cursor.execute("SELECT uid FROM User;")
        users = [row['uid'] for row in cursor.fetchall()]
        if len(users) < 2:
            print("Not enough users to create relationships.")
            return

        random.shuffle(users)
        user_pairs = set()
        added_friends = set()
        added_requests = set()

        for i in range(len(users)):
            uid1 = users[i]

            # Friends
            friends_added = 0
            while friends_added < max_friends:
                uid2 = random.choice(users)
                if uid1 == uid2:
                    continue

                pair = tuple(sorted((uid1, uid2)))
                if pair in user_pairs:
                    continue

                # Add to Friends table
                cursor.execute(
                    "INSERT INTO Friends (user1, user2) VALUES (%s, %s);",
                    (pair[0], pair[1])
                )
                user_pairs.add(pair)
                added_friends.add(pair)
                friends_added += 1

            # Friend Requests
            requests_sent = 0
            while requests_sent < max_requests:
                uid2 = random.choice(users)
                if uid1 == uid2:
                    continue

                pair = tuple(sorted((uid1, uid2)))
                request_pair = (uid1, uid2)
                reverse_request_pair = (uid2, uid1)

                if pair in user_pairs or request_pair in added_requests or reverse_request_pair in added_requests:
                    continue

                # Add to Friend_Requests
                cursor.execute(
                    "INSERT INTO Friend_Requests (sender_id, receiver_id) VALUES (%s, %s);",
                    (uid1, uid2)
                )
                added_requests.add(request_pair)
                requests_sent += 1

        conn.commit()
        print(f"Friendships created: {len(added_friends)}")
        print(f"Friend requests created: {len(added_requests)}")

if __name__ == '__main__':
    setup_db()
    conn = get_connection()
    #/home/Desktop/ciss430/project/data/megaGymDataset.csv
    path1 = "/home/student/Desktop/ciss430/project/data/megaGymDataset.csv"
    path2 = "/home/student/work/ciss430project/data/megaGymDataset.csv"
    
    if conn:
        x = input()
        if x == 1:
            create_exercises(conn, path1)
        else:
            create_exercises(conn, path2)
        add_users(conn, 100)
        seed_friend_data(conn)
        conn.close()

