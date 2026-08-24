import base64
from email.mime.text import MIMEText

from automation.gmail_service import get_gmail_service


def create_draft(to_email, subject, body):

    service = get_gmail_service()

    message = MIMEText(body)

    message["to"] = to_email
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    draft = {
        "message": {
            "raw": raw
        }
    }

    result = (
        service.users()
        .drafts()
        .create(
            userId="me",
            body=draft
        )
        .execute()
    )

    return result