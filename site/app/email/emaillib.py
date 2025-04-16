import random
from google_app_config import GMAIL, TO, GOOGLE_APP_PASSWORD
from emailserver import sendgmail
def generate_OTP():
    return random.randrange(10000000, 99999999)

def send_auth_email(useremail, username):
    message = "Welcome to MySQLPal. This is a clone of MyFitnessPal, dedicated to recording past exercises and setting goals for future exercises. To verify your account, enter the following OTP into the screen on the MySQLPal verification page:\n %s" % generate_OTP()
    subject = 'Welcome to MySQLPal %s !!!' % username
    sendgmail(useremail, GMAIL, subject, message)
    return

def send_confirmation_email(useremail, username):
    message = "Your account at %s, username %s has been successfully registered." % useremail, username
    subject = "MySQLPal Registration Successful"
    sendgmail(useremail, gmail, subject, message)

send_auth_welcome_email('nalahaideb1@cougars.ccis.edu', 'goober_ass_fella')

