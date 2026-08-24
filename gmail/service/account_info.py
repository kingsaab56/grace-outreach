from googleapiclient.discovery import build

from gmail.oauth.oauth_login import authenticate


def get_account_info(profile_name):
    """
    Returns:
        {
            "email": "...",
            "messages_total": ...,
            "threads_total": ...
        }

    Returns None if OAuth is not available.
    """

    try:

        creds = authenticate(profile_name)

        service = build(
            "gmail",
            "v1",
            credentials=creds
        )

        profile = (
            service.users()
            .getProfile(userId="me")
            .execute()
        )

        return {
            "email": profile.get("emailAddress", ""),
            "messages_total": profile.get("messagesTotal", 0),
            "threads_total": profile.get("threadsTotal", 0)
        }

    except Exception as e:

        print(f"[ACCOUNT INFO ERROR] {profile_name}")

        print(e)

        return None