"""
Send the digest by email. v1 sends plain text with the top matches and
a note of where each tailored CV was saved. If email isn't configured,
it just prints to the console instead.
"""

import smtplib
from email.message import EmailMessage
import config


def send_digest(body: str, subject: str = "Job agent — today's matches") -> None:
    if not (config.EMAIL_USER and config.EMAIL_PASS and config.EMAIL_TO):
        print("\n[notify] Email not configured — printing digest instead:\n")
        print(body)
        return

    msg = EmailMessage()
    msg["From"] = config.EMAIL_USER
    msg["To"] = config.EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.login(config.EMAIL_USER, config.EMAIL_PASS)
        server.send_message(msg)
    print(f"[notify] Digest sent to {config.EMAIL_TO}")
