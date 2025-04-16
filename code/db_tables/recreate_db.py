'''
************************************************************************
#DO NOT RUN THIS UNLESS YOU WANT TO DROP **EVERYTHING** AND RECREATE IT#
#THE DATA WILL NOT BE SAVED UNTIL IT IS WRITTEN BY THE BACK END PROGRAM#
########################################################################
#                     table creation is as follows:                    #
#        user > user dependents > exercises > exercise dependents      # 
************************************************************************
'''
from recreate_helper_func import * 
#local testing right now, uncomment when project goes live and replace ip with target ip, port with target port
#TARGET_IP = 'localhost'
#TARGET_PORT = 5000
#ADMIN = 'userhere'
#ADMINPASS = 'passhere'
#conn = pymysql.connect(host=TARGET_IP, user=ADMIN, password=ADMINPASS, port=TARGET_PORT)

#input all dat shiiiiiiiii
create_exercises()

#insert_test_users()

#insert_premade_days()

#insert_test_friends()

#insert_premade_schedules()

#insert_test_plans()

# insert_test_goals()

# insert_test_progress()

# insert_test_credentials()

# insert_test_messages()
