import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - Credentials loaded from .env file
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")

def send_complaint_notification(customer_email, tracking_id, department, status="received"):
    """
    Sends an email notification to the customer.
    Requires SENDER_EMAIL and SENDER_PASSWORD in .env file.
    """
    # Skip if credentials not configured
    if SENDER_EMAIL == "your-email@gmail.com" or SENDER_PASSWORD == "your-app-password":
        print(f"⚠️ Email not configured. Set SENDER_EMAIL and SENDER_PASSWORD in .env file")
        print(f"DEBUG: Email would be sent to {customer_email} for tracking ID {tracking_id}")
        return False
    
    subject = f"Complaint Update - Tracking ID: {tracking_id}"
    
    if status == "received":
        body = f"""
        Dear Customer,
        
        Your complaint has been successfully received and forwarded to the {department} department.
        Tracking ID: {tracking_id}
        
        We will get back to you shortly.
        
        Regards,
        Support Team
        """
    else:
        body = f"""
        Dear Customer,
        
        The status of your complaint (ID: {tracking_id}) has been updated to: {status}.
        
        Regards,
        Support Team
        """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = customer_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {customer_email} for tracking ID {tracking_id}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False
