# ─────────────────────────────────────────────────────────────────────────────
#  Rustic Garden — Azure Function App  |  main.py
#  Entry point registered in function.json.
#  Handles: POST /api/contact  and  POST /api/volunteer
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# ─────────────────────────────────────────────
#  ROUTE: POST /api/contact
# ─────────────────────────────────────────────
@app.route(route="contact", methods=["POST", "OPTIONS"])
def contact(req: func.HttpRequest) -> func.HttpResponse:
    headers = _cors_headers()

    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=headers)

    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON.", 400, headers)

    name    = body.get("name", "").strip()
    email   = body.get("email", "").strip()
    message = body.get("message", "").strip()

    if not all([name, email, message]):
        return _error("name, email, and message are all required.", 400, headers)

    if "@" not in email:
        return _error("Please supply a valid email address.", 400, headers)

    _send_email(
        subject=f"[Rustic Garden] Contact from {name}",
        body=f"Name:    {name}\nEmail:   {email}\n\nMessage:\n{message}"
    )

    logging.info(f"Contact: {name} <{email}>")
    return _success({"message": "Thank you for reaching out — we will be in touch soon."}, headers)


# ─────────────────────────────────────────────
#  ROUTE: POST /api/volunteer
# ─────────────────────────────────────────────
@app.route(route="volunteer", methods=["POST", "OPTIONS"])
def volunteer(req: func.HttpRequest) -> func.HttpResponse:
    headers = _cors_headers()

    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=headers)

    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON.", 400, headers)

    name     = body.get("name", "").strip()
    email    = body.get("email", "").strip()
    role     = body.get("role", "General Volunteer").strip()   # Coordinator / Researcher / Digital Advocate
    note     = body.get("note", "").strip()

    if not all([name, email]):
        return _error("name and email are required.", 400, headers)

    _send_email(
        subject=f"[Rustic Garden] Volunteer Application — {name}",
        body=(
            f"Name:   {name}\n"
            f"Email:  {email}\n"
            f"Role:   {role}\n\n"
            f"Note:\n{note or 'N/A'}"
        )
    )

    logging.info(f"Volunteer: {name} <{email}> — {role}")
    return _success({"message": "Application received! We will be in touch."}, headers)


# ─────────────────────────────────────────────
#  EMAIL UTILITY
#  Configure these in Azure Portal →
#    Function App → Settings → Environment Variables
# ─────────────────────────────────────────────
def _send_email(subject: str, body: str) -> None:
    smtp_user = os.environ.get("SMTP_USER")       # your Gmail address
    smtp_pass = os.environ.get("SMTP_PASSWORD")    # Gmail App Password (16-char)
    notify_to = os.environ.get("NOTIFY_EMAIL")     # destination inbox

    if not all([smtp_user, smtp_pass, notify_to]):
        logging.warning("SMTP env vars missing — email skipped.")
        return

    try:
        msg = MIMEMultipart()
        msg["From"]    = smtp_user
        msg["To"]      = notify_to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, notify_to, msg.as_string())

        logging.info(f"Email sent: {subject}")
    except Exception as exc:
        logging.error(f"Email failed: {exc}")


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def _cors_headers() -> dict:
    # 🔧 Replace with your actual GitHub Pages URL, e.g.:
    #    https://yourname.github.io  OR  https://yourdomain.com
    origin = os.environ.get("ALLOWED_ORIGIN", "https://dg1010-rg.github.io/Rustic-garden-1s36e-Kavutiri-Embu.github.io/")
    return {
        "Access-Control-Allow-Origin":  origin,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }

def _success(data: dict, headers: dict) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(data), status_code=200, headers=headers)

def _error(msg: str, code: int, headers: dict) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"error": msg}), status_code=code, headers=headers)
