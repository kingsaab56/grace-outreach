from googleapiclient.discovery import build

from automation.gmail_auth import authenticate


def get_gmail_service():
    """
    Returns authenticated Gmail API service.
    """

    credentials = authenticate()

    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    return service