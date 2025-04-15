import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
from google_app_config import GMAIL, TO, GOOGLE_APP_PASSWORD

def sendgmail(to_=TO,
              from_=GMAIL,
              subject='[NO SUBJECT]',
              text='this is a test',
              html='',
              attach=None, # list of paths or path or None
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
    sendgmail(to_=[GMAIL],
              subject='this is a test %s' % NOW,
              text='this is a test',
              html='<html><body><h1>This is a test</h1>This is a test</body></html>',
              attach=['myemail.py']
)
