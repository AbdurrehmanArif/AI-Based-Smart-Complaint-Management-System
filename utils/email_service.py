def send_complaint_notification(customer_email, tracking_id, department, status="received"):
    """
    Logs email notification (simulated).
    Email functionality disabled - notifications are logged to console only.
    """
    if status == "received":
        message = f"Complaint received - ID: {tracking_id}, Department: {department}"
    else:
        message = f"Complaint status updated - ID: {tracking_id}, Status: {status}"
    
    print(f"📧 Email notification: {customer_email} - {message}")
    return True
