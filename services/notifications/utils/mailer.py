from email.message import EmailMessage
import aiosmtplib
from app.core.config import settings
from app.templates import NotificationContent


async def send_email(content: NotificationContent):
    print("Sending email...")
    message = EmailMessage()
    message["From"] = settings.SMTP_USERNAME
    message["To"] =  content.recipient_email
    message["Subject"] = content.subject

    message.set_content(content.body)

    smtp_params = {
        "hostname": settings.SMTP_HOSTNAME,
        "port": settings.SMTP_PORT,
        "use_tls": settings.SMTP_USE_TLS,
        "start_tls": settings.SMTP_START_TLS,
        "username": settings.SMTP_USERNAME,
        "password": settings.SMTP_PASSWORD,
    }
    try:
        smtp_client = aiosmtplib.SMTP(**smtp_params)
        await smtp_client.connect()
        print("Connected to SMTP server...")
        await smtp_client.send_message(message)
        print("Message sent...")
        await smtp_client.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
