from googleapiclient.discovery import build

from gmail.oauth.oauth_login import authenticate


def get_gmail_service(profile_name):
    """
    Returns authenticated Gmail API service
    """

    creds = authenticate(profile_name)

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service