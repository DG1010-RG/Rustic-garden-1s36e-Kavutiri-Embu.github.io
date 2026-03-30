import json
import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import azure.functions as func


# ──────────────────────────────────────────────
#  CONTACT FORM HANDLER
# ──────────────────────────────────────────────
def handle_contact(req: func.HttpRequest, headers: dict) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON body.", 400, headers)

    name    = body.get("name", "").strip()
    email   = body.get("email", "").strip()
    message = body.get("message", "").strip()

    if not all([name, email, message]):
        return _error("Name, email, and message are required.", 400, headers)

    if "@" not in email:
        return _error("Invalid email address.", 400, headers)

    # Send email notification
    sent = _send_email(
        subject=f"[Rustic Garden] New Contact: {name}",
        body=f"From: {name} <{email}>\n\n{message}"
    )

    if not sent:
        return _error("Message received but email notification failed.", 500, headers)

    logging.info(f"Contact form submitted by {name} ({email})")
    return _success({"message": "Thank you! We will be in touch soon."}, headers)


# ──────────────────────────────────────────────
#  VOLUNTEER / JOIN PROGRAM HANDLER
# ──────────────────────────────────────────────
def handle_volunteer(req: func.HttpRequest, headers: dict) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON body.", 400, headers)

    name     = body.get("name", "").strip()
    email    = body.get("email", "").strip()
    interest = body.get("interest", "General").strip()  # e.g. "Researcher", "Coordinator"

    if not all([name, email]):
        return _error("Name and email are required.", 400, headers)

    sent = _send_email(
        subject=f"[Rustic Garden] New Volunteer: {name}",
        body=f"Volunteer Application\n\nName: {name}\nEmail: {email}\nInterest: {interest}"
    )

    if not sent:
        return _error("Application received but notification failed.", 500, headers)

    logging.info(f"Volunteer application from {name} — {interest}")
    return _success({"message": "Application received! We'll reach out soon."}, headers)


# ──────────────────────────────────────────────
#  EMAIL UTILITY  (uses Gmail SMTP via App Password)
#  Set these in Azure Function App → Configuration → App Settings
# ──────────────────────────────────────────────
def _send_email(subject: str, body: str) -> bool:
    smtp_user = os.environ.get("SMTP_USER")      # e.g. yourname@gmail.com
    smtp_pass = os.environ.get("SMTP_PASSWORD")   # Gmail App Password
    to_email  = os.environ.get("NOTIFY_EMAIL")    # where to send notifications

    if not all([smtp_user, smtp_pass, to_email]):
        logging.warning("SMTP environment variables not set. Skipping email.")
        return True  # Don't block the user; just log it

    try:
        msg = MIMEMultipart()
        msg["From"]    = smtp_user
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())

        return True
    except Exception as e:
        logging.error(f"Email send failed: {e}")
        return False


# ──────────────────────────────────────────────
#  RESPONSE HELPERS
# ──────────────────────────────────────────────
def _success(data: dict, headers: dict) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps(data),
        status_code=200,
        headers=headers
    )

def _error(message: str, code: int, headers: dict) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps({"error": message}),
        status_code=code,
        headers=headers
    )
