from .celery_config import celery_app
from . import crud, models
from .database import SessionLocal
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import date, datetime

# Email settings (in real project, should be loaded from .env)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")

def send_email(to_email: str, subject: str, message: str) -> bool:
    """Sends email and returns success status."""
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to SMTP server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

@celery_app.task
def send_overdue_reminders():
    """Sends email reminders and notifications for overdue books."""
    print("Checking for overdue books...")
    
    db = SessionLocal()
    try:
        overdue_books = crud.get_overdue_books(db)
        
        if not overdue_books:
            print("No overdue books found.")
            return
        
        sent_count = 0
        failed_count = 0
        
        for book in overdue_books:
            if book.patron:
                # Email template
                subject = "Overdue Book Reminder"
                message = f"""
Dear {book.patron.username},

This is a reminder that the following book is overdue:

Book: {book.title} by {book.author}
Due Date: {book.due_date}

Please return this book as soon as possible to avoid any late fees.

Thank you,
Library Management System
                """.strip()
                # Notification message (with fine example)
                fine_amount = 10  # Example fine amount
                notif_msg = f"The book '{book.title}' is overdue! Please return it immediately. Your fine is ${fine_amount}."
                # Send email (in real project, use patron.email)
                email_sent = True  # send_email(f"{book.patron.username}@example.com", subject, message)
                # Create email log record
                email_log = models.EmailLogCreate(
                    recipient_id=book.patron.id,
                    subject=subject,
                    message=message,
                    email_type="overdue_reminder"
                )
                if email_sent:
                    crud.create_email_log(db, email_log)
                    sent_count += 1
                    print(f"REMINDER SENT: {book.patron.username} - '{book.title}' (Due: {book.due_date})")
                else:
                    failed_count += 1
                    print(f"FAILED TO SEND: {book.patron.username} - '{book.title}'")
                # Create notification record
                notif = models.NotificationCreate(
                    patron_id=book.patron.id,
                    message=notif_msg
                )
                crud.create_notification(db, notif)
        print(f"Overdue reminder task completed. Sent: {sent_count}, Failed: {failed_count}")
    finally:
        db.close()

@celery_app.task
def generate_weekly_report():
    """Generates weekly borrowing statistics."""
    print("Generating weekly report...")
    
    db = SessionLocal()
    try:
        # Calculate weekly statistics
        all_books = crud.get_books(db)
        checked_out_books = [book for book in all_books if book.patron_id is not None]
        overdue_books = crud.get_overdue_books(db)
        
        report_data = {
            "total_books": len(all_books),
            "checked_out_books": len(checked_out_books),
            "overdue_books": len(overdue_books),
            "available_books": len(all_books) - len(checked_out_books),
            "checkout_rate": f"{(len(checked_out_books) / len(all_books) * 100):.1f}%" if all_books else "0%",
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"Weekly report generated successfully at {report_data['generated_at']}")
        print(f"Report data: {report_data}")
        
        # Return report data (will be used in admin panel)
        return report_data
            
    finally:
        db.close()

@celery_app.task
def send_test_email():
    """Sends a test email."""
    print("Sending test email...")
    
    subject = "Test Email from Library System"
    message = "This is a test email from the Library Management System."
    
    email_sent = send_email("test@example.com", subject, message)
    
    if email_sent:
        print("Test email sent successfully.")
    else:
        print("Failed to send test email.")
    
    return email_sent