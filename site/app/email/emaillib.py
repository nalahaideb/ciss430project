import random
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import pymysql
#from google_app_config import GMAIL, TO, GOOGLE_APP_PASSWORD
#from emailserver import sendgmail
#from google_app_config import GMAIL, TO, GOOGLE_APP_PASSWORD
GMAIL = 'mysqlpal@gmail.com'
GOOGLE_APP_PASSWORD = 'wjmm zspw uwgu maoq'
test_img = '/home/student/Desktop/ciss430/project/site/app/email/moustard.webp'
def sendgmail(to_,
              from_=GMAIL,
              subject='[NO SUBJECT]',
              text='this is a test',
              html='',
              attach=test_img, # list of paths or path or None
              google_app_password=GOOGLE_APP_PASSWORD
              ):
    try:
        if isinstance(attach, str):
            attaches = [attach]
        elif attach == None:
            attaches = []
        elif isinstance(attach, list):
            attaches = attach
            
        sender_pass = google_app_password
        msg = MIMEMultipart()
        msg['From'] = from_
        msg['Subject'] = subject
        alternative = MIMEMultipart('alternative')
        msg.attach(alternative)
        if text: alternative.attach(MIMEText(text))
        if html: alternative.attach(MIMEText(html, 'html'))
        # attachments
        for path in attaches:
            if not os.path.isfile(path):
                raise BaseException("email ERROR: path %s cannot be found" % path)
            ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(open(path, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment',
                            filename=os.path.split(path)[-1])
            msg.attach(part)
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(from_, sender_pass)
        session.sendmail(from_, to_, msg.as_string())
        session.quit()
    except Exception as e:
        print(e)
        NOW = datetime.datetime.now()
        raise Exception("[%s] ERROR: Please report error" % NOW)
if __name__ == '__main__':
    NOW = datetime.datetime.now()

def generate_OTP():
    return random.randrange(10000000, 99999999)

#runs two simple queries to determine if a user already has been registered with either the username or the email, both being unique
def verify_new_user(user, email, OTP):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='exercisedb',
        cursorclass=pymysql.cursors.DictCursor
        )
    c = conn.cursor()
    print("SELECT email FROM User_Credentials WHERE email LIKE %" + email + '%;')
    c.execute("SELECT email FROM User_Credentials WHERE email LIKE '%" + email + "%';")
    is_email = c.fetchone()
    c.execute("SELECT username FROM User_Credentials WHERE username LIKE '%" + user + "%';")
    is_user = c.fetchone()
    
    c.close()
    conn.close()
    print("ISEMAIL", is_email, "ISUSER", is_user)
    return True

def send_auth_email(useremail, username):
    message = "Welcome to MySQLPal. This is a clone of MyFitnessPal, dedicated to recording past exercises and setting goals for future exercises. To verify your account, enter the following OTP into the screen on the MySQLPal verification page:\n %s" % generate_OTP()
    subject = 'Welcome to MySQLPal %s !!!' % username
    sendgmail(useremail, GMAIL, subject, message)
    return

def send_confirmation_email(useremail, username):
    message = "Your account at %s, username %s has been successfully registered." % (useremail, username)
    subject = "MySQLPal Registration Successful"
    sendgmail(useremail, gmail, subject, message)
    return

#send_auth_email('nalahaideb1@cougars.ccis.edu', 'goober_ass_fella')

