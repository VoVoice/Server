# VoVoice Email Utilities
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
from datetime import datetime, timedelta
from database.db import db


def generate_verification_token():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))


def create_verification_token(user_id):
    token = generate_verification_token()
    db.create_verification_token(user_id, token)
    return token


def send_verification_email(to_email, verification_token, domain=None):
    from config import load_config
    config = load_config()

    if not config.email.smtp_host or not config.email.smtp_user:
        print(f"SMTP not configured. Verification token: {verification_token}")
        return {"status": "skipped", "reason": "SMTP not configured"}

    verify_url = f"https://{domain or config.server.domain}/verify?token={verification_token}"

    from_address = config.email.from_address or config.email.smtp_user

    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_email
    msg["Subject"] = "VoVoice - Verify Your Email"

    html = f"""
    <html>
    <body>
        <h2>Welcome to VoVoice!</h2>
        <p>Click the link below to verify your email address:</p>
        <p><a href="{verify_url}">Verify Email</a></p>
        <p>This link expires in 24 hours.</p>
        <p>If you didn't create an account, please ignore this email.</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(config.email.smtp_host, config.email.smtp_port) as server:
            server.starttls()
            server.login(config.email.smtp_user, config.email.smtp_password)
            server.send_message(msg)
        return {"status": "sent"}
    except Exception as e:
        print(f"Failed to send email: {e}")
        return {"status": "failed", "reason": str(e)}
