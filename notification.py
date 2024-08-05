import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

os.environ['MAIL_USERNAME'] = 'no.reply.pro.mini@gmail.com'
os.environ['MAIL_PASSWORD'] = 'ssoq rutt sfaf qzqq'
os.environ['MAIL_DEFAULT_SENDER'] = 'no.reply.pro.mini@gmail.com'
# Load environment variables
load_dotenv()
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

#Function to send email
def send_email(recipient, subject, body):
    msg = MIMEMultipart()
    msg['From'] = MAIL_DEFAULT_SENDER
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        smtp = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        smtp.starttls()
        smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtp.sendmail(MAIL_DEFAULT_SENDER, recipient, msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Function to send email notification
def send_email_notification(email, message):
    subject = "Notification: Helmet Offense Detected!!!"
    body = f"Dear User,\n\n{message}\n\nRegards,\nHelmet Detection Team"
    if send_email(email, subject, body):
        return True
    else:
        return False
    