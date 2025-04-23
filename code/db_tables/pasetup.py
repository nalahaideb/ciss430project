import os
import pymysql
import csv

def get_connection():
    return pymysql.connect(
        host='mysqlpal.mysql.pythonanywhere-services.com',
        user='mysqlpal',
        password='PASICK123*',
        database='mysqlpal$exercisedb',
        cursorclass=pymysql.cursors.DictCursor
    )

def setup_db():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            with open("padb.sql", "r") as f:
                sql_commands = f.read().split(';')
                for command in sql_commands:
                    command = command.strip()
                    if command:
                        try:
                            cursor.execute(command)
                        except Exception as exec_err:
                            print("Command failed:", exec_err)
                            print("Offending command:", command)
        connection.commit()
        connection.close()
        print("Database setup complete.")
    except Exception as e:
        print("Database creation error:", e)

def cleanup(value, islist=False):
    value = value.replace('\n', '').replace('"', '').replace("'", '')
    if value == r'\N' or value.strip() == '':
        return [] if islist else "N/A"
    return value

def create_exercises(conn, csv_path):
    with conn.cursor() as cursor:
        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header

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
                print("Exercise import complete.")
        except Exception as file_err:
            print("File or transaction error:", file_err)

if __name__ == '__main__':
    setup_db()
    try:
        conn = get_connection()
        path = "megaGymDataset.csv"

        if conn:
            create_exercises(conn, path)
            conn.close()
    except Exception as final_err:
        print("Main execution error:", final_err)
