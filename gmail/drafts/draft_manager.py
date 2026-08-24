import base64
from email.mime.text import MIMEText

from gmail.oauth.gmail_service import get_gmail_service


def create_draft(
    profile_name,
    account_email,
    to_email,
    subject,
    body
):
    """
    Create a Gmail draft using a specific
    OAuth-connected Gmail account.
    """

    if isinstance(profile_name, tuple):
        profile_name = profile_name[0]

    if not profile_name:
        print("[ERROR] Profile name is required.")
        return None

    if not account_email:
        print("[ERROR] Gmail account email is required.")
        return None

    if not to_email:
        print("[ERROR] Recipient email is required.")
        return None

    service = get_gmail_service(
        profile_name,
        account_email
    )

    if not service:
        print(
            f"[ERROR] Gmail service not available | "
            f"{profile_name} | {account_email}"
        )
        return None

    message = MIMEText(
        body or "",
        "plain",
        "utf-8"
    )

    message["To"] = to_email
    message["Subject"] = subject or ""

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    draft = {
        "message": {
            "raw": raw
        }
    }

    try:

        result = (
            service
            .users()
            .drafts()
            .create(
                userId="me",
                body=draft
            )
            .execute()
        )

        print(
            f"[OK] Draft Created | "
            f"{profile_name} | "
            f"{account_email} | "
            f"{to_email}"
        )

        return result

    except Exception as e:

        print(
            f"[FAILED] Draft Creation | "
            f"{profile_name} | "
            f"{account_email}"
        )

        print(e)

        return None