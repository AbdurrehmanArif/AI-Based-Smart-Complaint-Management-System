import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ==========================================
# 📧 SMTP CONFIGURATION (Gmail)
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # ⚠️ REPLACE WITH REAL EMAIL
SENDER_PASSWORD = "your-app-password"  # ⚠️ REPLACE WITH APP PASSWORD

# Department Email Mapping
DEPARTMENT_EMAILS = {
    "IT Support": "it-support@example.com",
    "Billing": "billing@example.com",
    "Operations": "operations@example.com",
    "Customer Service": "support@example.com",
    "Human Resources": "hr@example.com",
    "General": "admin@example.com"
}

def send_html_email(to_email, subject, html_body):
    """
    Sends an HTML email using SMTP_SSL or STARTTLS.
    """
    try:
        if "your-email" in SENDER_EMAIL:
            print(f"⚠️ SMTP NOT CONFIGURED: Skipping email to {to_email}")
            return False

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to: {to_email}")
        return True
    except Exception as e:
        print(f"❌ FAILED to send email to {to_email}. Error: {e}")
        return False

def get_customer_confirmation_email(customer_name, tracking_id, category, priority, department, response_time):
    """
    Professional email template for customer complaint confirmation.
    """
    subject = f"Complaint Tracker - Complaint Received #{tracking_id}"
    
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
        .info-box {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #3b82f6; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .tracking-id {{ font-size: 24px; font-weight: bold; color: #3b82f6; text-align: center; padding: 15px; background: white; border-radius: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
        .priority-high {{ color: #dc3545; font-weight: bold; }}
        .priority-medium {{ color: #ffc107; font-weight: bold; }}
        .priority-low {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Complaint Tracker</h1>
            <p>Your Complaint Has Been Received</p>
        </div>
        <div class="content">
            <p>Dear <strong>{customer_name}</strong>,</p>
            
            <p>Thank you for reaching out to us. We have successfully received your complaint and our team is already working on it.</p>
            
            <div class="tracking-id">
                Tracking ID: {tracking_id}
            </div>
            
            <div class="info-box">
                <h3>📋 Complaint Details</h3>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Priority:</strong> <span class="priority-{priority.lower()}">{priority}</span></p>
                <p><strong>Assigned Department:</strong> {department}</p>
                <p><strong>Estimated Response Time:</strong> {response_time}</p>
            </div>
            
            <div class="info-box">
                <h3>📌 What Happens Next?</h3>
                <ul>
                    <li>Your complaint has been forwarded to the <strong>{department}</strong> department</li>
                    <li>Our team will review and prioritize your request</li>
                    <li>You will receive email updates as the status changes</li>
                    <li>Expected response within <strong>{response_time}</strong></li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>🔍 Track Your Complaint</h3>
                <p>You can track the status of your complaint anytime using your Tracking ID: <strong>{tracking_id}</strong></p>
                <p>Visit our portal and use the "Track Complaint" feature.</p>
            </div>
            
            <p>We appreciate your patience and assure you that we are committed to resolving your issue as quickly as possible.</p>
            
            <p>Best regards,<br>
            <strong>Complaint Tracker Team</strong></p>
            
            <div class="footer">
                <p>This is an automated message from Complaint Tracker.</p>
                <p>Please do not reply to this email. For inquiries, use your Tracking ID on our portal.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return subject, body


def get_status_update_email(customer_name, tracking_id, new_status, category):
    """
    Professional email template for complaint status updates.
    """
    subject = f"Complaint Tracker - Status Update #{tracking_id}"
    
    status_messages = {
        "In Progress": {
            "title": "🔄 Your Complaint is In Progress",
            "message": "Great news! Our team has started working on your complaint.",
            "color": "#007bff"
        },
        "Resolved": {
            "title": "✅ Your Complaint Has Been Resolved",
            "message": "We're pleased to inform you that your complaint has been successfully resolved!",
            "color": "#28a745"
        }
    }
    
    status_info = status_messages.get(new_status, {
        "title": f"📢 Status Update: {new_status}",
        "message": f"Your complaint status has been updated to {new_status}.",
        "color": "#6c757d"
    })
    
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, {status_info['color']} 0%, {status_info['color']}dd 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
        .status-box {{ background: white; padding: 25px; margin: 20px 0; border-left: 5px solid {status_info['color']}; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .tracking-id {{ font-size: 20px; font-weight: bold; color: {status_info['color']}; }}
        .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{status_info['title']}</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{customer_name}</strong>,</p>
            
            <p>{status_info['message']}</p>
            
            <div class="status-box">
                <p><strong>Tracking ID:</strong> <span class="tracking-id">{tracking_id}</span></p>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Current Status:</strong> <strong style="color: {status_info['color']};">{new_status}</strong></p>
            </div>
            
            {"<div class='status-box'><h3>🎉 Resolution Complete</h3><p>Thank you for your patience. If you have any questions about the resolution or need further assistance, please don't hesitate to submit a new complaint.</p></div>" if new_status == "Resolved" else ""}
            
            {"<div class='status-box'><h3>⏳ Next Steps</h3><p>Our team is actively working on your complaint. You will receive another update once it has been resolved.</p></div>" if new_status == "In Progress" else ""}
            
            <p>Thank you for using Complaint Tracker.</p>
            
            <p>Best regards,<br>
            <strong>Complaint Tracker Team</strong></p>
            
            <div class="footer">
                <p>This is an automated message from Complaint Tracker.</p>
                <p>Track your complaint anytime using Tracking ID: {tracking_id}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return subject, body


def get_department_notification_email(tracking_id, customer_name, customer_email, customer_phone, 
                                      city, address, complaint_text, category, priority, department, response_time):
    """
    Professional email template for department notification with urgency emphasis.
    """
    subject = f"🚨 URGENT: New {priority} Priority Complaint #{tracking_id} - Action Required"
    
    priority_colors = {
        "High": "#dc3545",
        "Medium": "#ffc107",
        "Low": "#28a745"
    }
    
    priority_color = priority_colors.get(priority, "#6c757d")
    
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, {priority_color} 0%, {priority_color}dd 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
        .urgent-banner {{ background: #fff3cd; border: 2px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 8px; text-align: center; }}
        .info-section {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .complaint-box {{ background: #f1f5f9; padding: 20px; margin: 15px 0; border-left: 5px solid {priority_color}; border-radius: 5px; }}
        .priority-badge {{ display: inline-block; padding: 8px 16px; background: {priority_color}; color: white; border-radius: 20px; font-weight: bold; }}
        .action-required {{ background: #dc3545; color: white; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }}
        .customer-details {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; }}
        td:first-child {{ font-weight: bold; width: 40%; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ New Complaint Assignment</h1>
            <h2>Complaint Tracker</h2>
        </div>
        <div class="content">
            <div class="urgent-banner">
                <h2 style="margin: 0; color: #856404;">⚠️ IMMEDIATE ACTION REQUIRED ⚠️</h2>
                <p style="margin: 5px 0; color: #856404;">A new complaint has been assigned to the <strong>{department}</strong> department</p>
            </div>
            
            <div class="info-section">
                <h3>📋 Complaint Overview</h3>
                <table>
                    <tr>
                        <td>Tracking ID:</td>
                        <td><strong style="color: {priority_color}; font-size: 18px;">{tracking_id}</strong></td>
                    </tr>
                    <tr>
                        <td>Priority Level:</td>
                        <td><span class="priority-badge">{priority}</span></td>
                    </tr>
                    <tr>
                        <td>Category:</td>
                        <td><strong>{category}</strong></td>
                    </tr>
                    <tr>
                        <td>Department:</td>
                        <td><strong>{department}</strong></td>
                    </tr>
                    <tr>
                        <td>Expected Response Time:</td>
                        <td><strong style="color: #dc3545;">{response_time}</strong></td>
                    </tr>
                </table>
            </div>
            
            <div class="info-section">
                <h3>👤 Customer Information</h3>
                <div class="customer-details">
                    <table>
                        <tr>
                            <td>Name:</td>
                            <td>{customer_name}</td>
                        </tr>
                        <tr>
                            <td>Email:</td>
                            <td><a href="mailto:{customer_email}">{customer_email}</a></td>
                        </tr>
                        <tr>
                            <td>Phone:</td>
                            <td><a href="tel:{customer_phone}">{customer_phone}</a></td>
                        </tr>
                        <tr>
                            <td>City:</td>
                            <td>{city}</td>
                        </tr>
                        <tr>
                            <td>Address:</td>
                            <td>{address}</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="info-section">
                <h3>📝 Complaint Details</h3>
                <div class="complaint-box">
                    <p style="margin: 0; white-space: pre-wrap;">{complaint_text}</p>
                </div>
            </div>
            
            <div class="action-required">
                <h3 style="margin-top: 0;">🎯 ACTION REQUIRED</h3>
                <p style="font-size: 16px; margin: 10px 0;">
                    <strong>This is a {priority} priority complaint that requires immediate attention!</strong>
                </p>
                <ul style="text-align: left; display: inline-block; margin: 15px 0;">
                    <li>Review the complaint details thoroughly</li>
                    <li>Contact the customer within the expected response time</li>
                    <li>Update the complaint status in the system as you progress</li>
                    <li>Resolve the issue as quickly as possible</li>
                </ul>
                <p style="font-size: 14px; margin-top: 15px;">
                    ⏰ <strong>Time is critical!</strong> The customer expects a response within <strong>{response_time}</strong>
                </p>
            </div>
            
            <div class="info-section">
                <h3>📊 System Instructions</h3>
                <ol>
                    <li>Log into the Admin Dashboard</li>
                    <li>Locate complaint <strong>#{tracking_id}</strong></li>
                    <li>Update status to "In Progress" once you begin working on it</li>
                    <li>Mark as "Resolved" once the issue is fixed</li>
                    <li>The customer will be automatically notified of status changes</li>
                </ol>
            </div>
            
            <p style="margin-top: 30px; font-size: 14px; color: #dc3545; text-align: center;">
                <strong>⚡ Remember: Quick resolution leads to higher customer satisfaction! ⚡</strong>
            </p>
            
            <div class="footer">
                <p>This is an automated notification from Complaint Tracker.</p>
                <p>Complaint ID: {tracking_id} | Department: {department} | Priority: {priority}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return subject, body


def send_complaint_notification(customer_email, tracking_id, department, status="received", 
                                customer_name="Valued Customer", category="General", priority="Medium",
                                response_time="24-48 hours", customer_phone="N/A", city="N/A", 
                                address="N/A", complaint_text=""):
    """
    Sends professional email notifications to customers and departments via SMTP.
    """
    
    # 1. Determine Emails to Send
    emails_to_send = []
    
    if status == "received":
        # A) Customer Confirmation
        subj_cust, body_cust = get_customer_confirmation_email(
            customer_name, tracking_id, category, priority, department, response_time
        )
        emails_to_send.append((customer_email, subj_cust, body_cust))
        
        # B) Department Notification
        subj_dept, body_dept = get_department_notification_email(
            tracking_id, customer_name, customer_email, customer_phone,
            city, address, complaint_text, category, priority, department, response_time
        )
        
        # Look up department email
        dept_email = DEPARTMENT_EMAILS.get(department, "admin@example.com")
        emails_to_send.append((dept_email, subj_dept, body_dept))
        
    else:
        # C) Status Update (Customer Only)
        subj_status, body_status = get_status_update_email(customer_name, tracking_id, status, category)
        emails_to_send.append((customer_email, subj_status, body_status))

    # 2. Send All Emails
    print(f"\n{'='*60}")
    print(f"� INITIATING EMAIL NOTIFICATIONS")
    print(f"{'='*60}")
    
    success_count = 0
    for recipient, subject, html_content in emails_to_send:
        print(f"Attempting to email: {recipient}...")
        if send_html_email(recipient, subject, html_content):
            success_count += 1
            
    print(f"{'='*60}")
    print(f"✅ Completed: {success_count}/{len(emails_to_send)} emails sent.")
    print(f"{'='*60}\n")
    
    return True
