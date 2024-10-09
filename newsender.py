import csv
import time
import random
import requests
from os import getenv


def send_email_via_mailgun(recipient_email, paper_title):
    subject = "Invitation to Pubnect's CSAC Conference"
    body =  subject = "Invitation to Pubnect's CSAC Conference"
    body = f"""\
    <html>
      <body>
        <p>Hello,<br><br>
        I hope you are doing well. We're intrigued by your research: <strong>{paper_title}</strong>.<br><br>
        We would like to invite you and your team to present at the <strong>Computer Science Advancements Conference (CSAC)</strong>, which will be a virtual conference on<strong> October 19th, 2024 at 20:00 UTC (3:00 PM CST)</strong>. This conference consists of presentations from other cutting edge researchers in various Computer Science fields, covering a wide range of topics.<br><br>
        Registering and presenting is <strong>without charge</strong> for researchers that are receiving this invitation. This is a <strong>virtual conference</strong>, so presenters will submit a 10-15 minute recording of their keynote research presentation. Attendance in the live conference is highly encouraged in order to answer audience questions, but not mandatory.<br><br>
        
        <strong>**Please note that not everyone on your team will have received this email; confirm with your team to register your paper.</strong><br><br>

        If you are interested, please use the following link to register your paper: <a href=''>Registration Link</a>.<br>

        
        This code is <strong>UNIQUE</strong> to your research paper. Enter it in the appropriate field when registering. <strong>Do NOT share this code with anyone.</strong> <br><br>
        <mark>Unique Registration Code: <strong>{random.randint(10000,99999)}</strong> </mark> </br>

        
        <br><br>
        <strong>About Pubnect:</strong><br><br>
        Pubnect is a platform designed to bridge the gap between researchers/publishers and the broader academic community. By focusing on virtual conferences, we offer an accessible way for researchers to present their work to a global audience. Learn more about Pubnect and CSAC at pubnect.com<br><br>
        Sincerely,<br>
        <strong>Pubnect Team</strong>
        </p>
      </body>
    </html>
    """

    requests.post(
        f"https://api.mailgun.net/v3/{getenv('DOMAIN')}/messages",
        auth=("api", getenv('API_KEY')),
        data={
            "from": getenv('SENDER_EMAIL'),
            "to": recipient_email,
            "subject": subject,
            "html": body
        }
    )

def send_emails_from_csv(csv_filename):
    email_count = 0
    with open(csv_filename, 'r', newline = '', encoding = 'UTF-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            recipient_email = row['email']
            paper_title = row['title']
            retries = 2  
            while retries > 0:
                try:
                    send_email_via_mailgun(recipient_email, paper_title)
                    email_count += 1
                    print(f"Email sent successfully to {recipient_email}! {email_count}")
                    break  
                except Exception as e:
                    print(f"Error sending email to {recipient_email}: {e}")
                    retries -= 1
                    if retries == 0:
                        print("Maximum retries reached. Moving to the next email.")
                    else:
                        print(f"Retrying... {retries}")
                        time.sleep(20)  

csv_filename = 'title_email.csv' 
send_emails_from_csv(csv_filename)