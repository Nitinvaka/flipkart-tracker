import os
import smtplib
from email.message import EmailMessage

def alert_system(product, link, receiver_email):
    email_id = os.getenv("EMAIL_ID")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_id or not email_pass:
        print("❌ Email credentials not found in environment variables.")
        return

    msg = EmailMessage()
    msg['Subject'] = "📢 Flipkart Price Drop Alert!"
    msg['From'] = email_id
    msg['To'] = receiver_email

    msg.set_content(f"Hi,\n\nThe price of '{product}' has dropped!\n\nCheck it out here:\n{link}\n\n— Flipkart Tracker Bot")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_id, email_pass)
            smtp.send_message(msg)
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
