import os

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


def _safe_email(email):

    return (
        email
        .strip()
        .lower()
        .replace("@", "_at_")
        .replace(".", "_")
    )


def get_token_file(
    profile_name,
    account_email=None
):

    token_dir = os.path.join(
        BASE_DIR,
        "accounts",
        profile_name
    )

    os.makedirs(
        token_dir,
        exist_ok=True
    )

    if account_email:

        safe_email = _safe_email(
            account_email
        )

        return os.path.join(
            token_dir,
            f"token_{safe_email}.json"
        )

    return os.path.join(
        token_dir,
        "token.json"
    )


def _load_credentials(
    profile_name,
    account_email
):

    if not profile_name:
        return None, "Profile name is required."

    if not account_email:
        return None, "Gmail account email is required."

    token_file = get_token_file(
        profile_name,
        account_email
    )

    if not os.path.exists(token_file):

        return (
            None,
            "OAuth token file not found."
        )

    try:

        creds = Credentials.from_authorized_user_file(
            token_file,
            SCOPES
        )

    except Exception as e:

        return (
            None,
            f"Could not load OAuth credentials: {e}"
        )

    # ---------------------------------------------------------
    # REFRESH EXPIRED ACCESS TOKEN
    # ---------------------------------------------------------

    if not creds.valid:

        if creds.expired and creds.refresh_token:

            try:

                creds.refresh(
                    Request()
                )

            except Exception as e:

                return (
                    None,
                    f"OAuth token refresh failed: {e}"
                )

        else:

            return (
                None,
                "OAuth credentials are invalid or expired."
            )

    # ---------------------------------------------------------
    # SAVE REFRESHED TOKEN
    # ---------------------------------------------------------

    try:

        with open(
            token_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                creds.to_json()
            )

    except Exception:
        # Token may still be usable even if saving fails.
        pass

    return creds, None


def get_gmail_service(
    profile_name,
    account_email
):

    creds, error = _load_credentials(
        profile_name,
        account_email
    )

    if not creds:

        print(
            "\n[ERROR] Gmail credentials unavailable."
        )

        print(
            f"Profile : {profile_name}"
        )

        print(
            f"Account : {account_email}"
        )

        print(
            f"Reason  : {error}"
        )

        return None

    try:

        service = build(
            "gmail",
            "v1",
            credentials=creds
        )

        return service

    except Exception as e:

        print(
            "\n[ERROR] Could not create Gmail API service."
        )

        print(e)

        return None


def get_profile_email(
    profile_name,
    account_email
):

    service = get_gmail_service(
        profile_name,
        account_email
    )

    if not service:

        return None

    try:

        result = (
            service
            .users()
            .getProfile(
                userId="me"
            )
            .execute()
        )

        return result.get(
            "emailAddress"
        )

    except Exception as e:

        print(
            "\n[ERROR] Gmail API request failed."
        )

        print(e)

        return None


def check_oauth_account(
    profile_name,
    account_email
):

    result = {
        "token_exists": False,
        "oauth_connected": False,
        "identity_verified": False,
        "verified_email": None,
        "health": "BLOCKED",
        "reason": "",
    }

    if not profile_name:

        result["reason"] = (
            "Profile name is required."
        )

        return result

    if not account_email:

        result["reason"] = (
            "Gmail account email is required."
        )

        return result

    token_file = get_token_file(
        profile_name,
        account_email
    )

    # ---------------------------------------------------------
    # TOKEN CHECK
    # ---------------------------------------------------------

    if not os.path.exists(token_file):

        result["reason"] = (
            "OAuth token file not found."
        )

        return result

    result["token_exists"] = True

    # ---------------------------------------------------------
    # LOAD / REFRESH CREDENTIALS
    # ---------------------------------------------------------

    creds, error = _load_credentials(
        profile_name,
        account_email
    )

    if not creds:

        result["reason"] = error

        return result

    result["oauth_connected"] = True

    # ---------------------------------------------------------
    # GMAIL API IDENTITY CHECK
    # ---------------------------------------------------------

    try:

        service = build(
            "gmail",
            "v1",
            credentials=creds
        )

        profile = (
            service
            .users()
            .getProfile(
                userId="me"
            )
            .execute()
        )

        verified_email = (
            profile.get(
                "emailAddress"
            )
        )

    except Exception as e:

        result["reason"] = (
            f"Gmail API verification failed: {e}"
        )

        return result

    if not verified_email:

        result["reason"] = (
            "Gmail API returned no account identity."
        )

        return result

    result["verified_email"] = (
        verified_email
    )

    # ---------------------------------------------------------
    # IDENTITY MATCH
    # ---------------------------------------------------------

    if (
        verified_email.strip().lower()
        != account_email.strip().lower()
    ):

        result["reason"] = (
            "OAuth identity does not match "
            "the detected Gmail account."
        )

        result["identity_verified"] = False

        return result

    result["identity_verified"] = True

    # ---------------------------------------------------------
    # FINAL HEALTH
    # ---------------------------------------------------------

    result["health"] = "HEALTHY"

    result["reason"] = (
        "OAuth connected, Gmail API accessible, "
        "and account identity verified."
    )

    return result


if __name__ == "__main__":

    profile = input(
        "Profile Name: "
    ).strip()

    email = input(
        "Gmail Address: "
    ).strip()

    if not profile:

        print(
            "Profile name is required."
        )

    elif not email:

        print(
            "Gmail address is required."
        )

    else:

        result = check_oauth_account(
            profile,
            email
        )

        print("\n")
        print("=" * 70)
        print("             GMAIL ACCOUNT HEALTH")
        print("=" * 70)

        print(
            "Profile          :",
            profile
        )

        print(
            "Requested Email  :",
            email
        )

        print(
            "Token            :",
            "VALID"
            if result["token_exists"]
            else "MISSING"
        )

        print(
            "OAuth            :",
            "CONNECTED"
            if result["oauth_connected"]
            else "NOT CONNECTED"
        )

        print(
            "Identity         :",
            "VERIFIED"
            if result["identity_verified"]
            else "NOT VERIFIED"
        )

        print(
            "Verified Email   :",
            result["verified_email"]
        )

        print(
            "Health           :",
            result["health"]
        )

        print(
            "Reason           :",
            result["reason"]
        )

        print("=" * 70)