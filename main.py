import json
import logging
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_allowed_origin() -> str:
    # Use only the site origin, not a full page URL/path.
    # Example: https://dg1010-rg.github.io
    return os.environ.get("ALLOWED_ORIGIN", "https://dg1010-rg.github.io")


def corsify_response(resp):
    origin = get_allowed_origin()
    resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Content-Type"] = "application/json"
    return resp


def success(data: dict, status_code: int = 200):
    resp = make_response(json.dumps(data), status_code)
    return corsify_response(resp)


def error(message: str, status_code: int = 400):
    resp = make_response(json.dumps({"error": message}), status_code)
    return corsify_response(resp)


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def send_email(subject: str, body: str) -> None:
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    notify_to = os.environ.get("NOTIFY_EMAIL")

    if not all([smtp_user, smtp_pass, notify_to]):
        logging.warning("SMTP env vars missing — email skipped.")
        return

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = notify_to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [notify_to], msg.as_string())
        logging.info("Email sent: %s", subject)
    except Exception as exc:
        logging.exception("Email failed: %s", exc)
        raise


@app.route("/", methods=["GET"])
def health():
    return success({"status": "ok", "service": "rustic-garden-api"})


@app.route("/api/contact", methods=["POST", "OPTIONS"])
def contact():
    if request.method == "OPTIONS":
        return success({"ok": True})

    if not request.is_json:
        return error("Content-Type must be application/json.", 400)

    body = request.get_json(silent=True)
    if body is None:
        return error("Invalid JSON.", 400)

    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip()
    message = str(body.get("message", "")).strip()

    if not all([name, email, message]):
        return error("name, email, and message are all required.", 400)

    if not validate_email(email):
        return error("Please supply a valid email address.", 400)

    try:
        send_email(
            subject=f"[Rustic Garden] Contact from {name}",
            body=(
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            ),
        )
    except Exception:
        return error("Could not send message right now. Please try again later.", 500)

    logging.info("Contact: %s <%s>", name, email)
    return success(
        {"message": "Thank you for reaching out — we will be in touch soon."},
        200,
    )


@app.route("/api/volunteer", methods=["POST", "OPTIONS"])
def volunteer():
    if request.method == "OPTIONS":
        return success({"ok": True})

    if not request.is_json:
        return error("Content-Type must be application/json.", 400)

    body = request.get_json(silent=True)
    if body is None:
        return error("Invalid JSON.", 400)

    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip()
    role = str(body.get("role", "General Volunteer")).strip()
    note = str(body.get("note", "")).strip()

    if not all([name, email]):
        return error("name and email are required.", 400)

    if not validate_email(email):
        return error("Please supply a valid email address.", 400)

    try:
        send_email(
            subject=f"[Rustic Garden] Volunteer Application — {name}",
            body=(
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Role: {role}\n\n"
                f"Note:\n{note or 'N/A'}"
            ),
        )
    except Exception:
        return error("Could not submit application right now. Please try again later.", 500)

    logging.info("Volunteer: %s <%s> — %s", name, email, role)
    return success({"message": "Application received! We will be in touch."}, 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
