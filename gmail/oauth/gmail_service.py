import os
from datetime import datetime

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


def _save_credentials(
    token_file,
    creds
):

    try:

        with open(
            token_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                creds.to_json()
            )

        return True

    except Exception as e:

        print(
            f"[WARNING] Could not save refreshed token: {e}"
        )

        return False


def _load_credentials(
    token_file
):

    try:

        return Credentials.from_authorized_user_file(
            token_file,
            SCOPES
        )

    except Exception as e:

        print(
            f"[ERROR] Could not load credentials: {e}"
        )

        return None


def _refresh_credentials(
    token_file,
    creds
):

    if not creds:

        return False

    if not creds.expired:

        return creds.valid

    if not creds.refresh_token:

        return False

    try:

        creds.refresh(
            Request()
        )

        _save_credentials(
            token_file,
            creds
        )

        return creds.valid

    except Exception as e:

        print(
            f"[ERROR] OAuth refresh failed: {e}"
        )

        return False


def get_gmail_service(
    profile_name,
    account_email
):

    if not profile_name:

        print(
            "\n[ERROR] Profile name is required."
        )

        return None

    if not account_email:

        print(
            "\n[ERROR] Gmail account email is required."
        )

        return None

    token_file = get_token_file(
        profile_name,
        account_email
    )

    if not os.path.exists(token_file):

        print(
            "\nGmail account token not found."
        )

        print(
            f"Profile : {profile_name}"
        )

        print(
            f"Account : {account_email}"
        )

        print(
            "Please connect this Gmail account first."
        )

        return None

    creds = _load_credentials(
        token_file
    )

    if not creds:

        return None

    # ---------------------------------------------------------
    # REFRESH EXPIRED OAUTH CREDENTIALS
    # ---------------------------------------------------------

    if creds.expired:

        refreshed = _refresh_credentials(
            token_file,
            creds
        )

        if not refreshed:

            print(
                "\n[ERROR] Gmail credentials are expired "
                "and could not be refreshed."
            )

            print(
                f"Profile : {profile_name}"
            )

            print(
                f"Account : {account_email}"
            )

            return None

    # ---------------------------------------------------------
    # FINAL CREDENTIAL CHECK
    # ---------------------------------------------------------

    if not creds.valid:

        print(
            "\n[ERROR] Gmail credentials are not valid."
        )

        print(
            f"Profile : {profile_name}"
        )

        print(
            f"Account : {account_email}"
        )

        return None

    try:

        service = build(
            "gmail",
            "v1",
            credentials=creds,
            cache_discovery=False
        )

        return service

    except Exception as e:

        print(
            "\n[ERROR] Could not create Gmail API service."
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
        "checked_at": datetime.now().isoformat()
    }

    if not profile_name:

        result["reason"] = (
            "Profile name is missing."
        )

        return result

    if not account_email:

        result["reason"] = (
            "Gmail account email is missing."
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
            "OAuth token file is missing."
        )

        return result

    result["token_exists"] = True

    # ---------------------------------------------------------
    # LOAD CREDENTIALS
    # ---------------------------------------------------------

    creds = _load_credentials(
        token_file
    )

    if not creds:

        result["reason"] = (
            "OAuth credentials could not be loaded."
        )

        return result

    # ---------------------------------------------------------
    # REFRESH IF EXPIRED
    # ---------------------------------------------------------

    if creds.expired:

        refreshed = _refresh_credentials(
            token_file,
            creds
        )

        if not refreshed:

            result["reason"] = (
                "OAuth credentials are invalid "
                "or expired."
            )

            return result

    # ---------------------------------------------------------
    # VALIDITY CHECK
    # ---------------------------------------------------------

    if not creds.valid:

        result["reason"] = (
            "OAuth credentials are invalid "
            "or expired."
        )

        return result

    result["oauth_connected"] = True

    # ---------------------------------------------------------
    # GMAIL API IDENTITY CHECK
    # ---------------------------------------------------------

    try:

        service = build(
            "gmail",
            "v1",
            credentials=creds,
            cache_discovery=False
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

        if verified_email:

            verified_email = (
                verified_email
                .strip()
                .lower()
            )

        result["verified_email"] = (
            verified_email
        )

    except Exception as e:

        result["reason"] = (
            "Gmail API request failed: "
            f"{e}"
        )

        return result

    # ---------------------------------------------------------
    # IDENTITY MATCH
    # ---------------------------------------------------------

    if not result["verified_email"]:

        result["reason"] = (
            "Gmail API did not return an account identity."
        )

        return result

    if (
        result["verified_email"]
        != account_email.strip().lower()
    ):

        result["reason"] = (
            "OAuth identity mismatch."
        )

        return result

    result["identity_verified"] = True

    # ---------------------------------------------------------
    # FINAL HEALTH
    # ---------------------------------------------------------

    result["health"] = "HEALTHY"

    result["reason"] = (
        "OAuth connected and Gmail identity verified."
    )

    return result


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
        print("             GMAIL OAUTH CHECK")
        print("=" * 70)

        print(
            f"Profile          : {profile}"
        )

        print(
            f"Requested Email  : {email}"
        )

        print(
            f"Token            : "
            f"{'VALID' if result['token_exists'] else 'MISSING'}"
        )

        print(
            f"OAuth            : "
            f"{'CONNECTED' if result['oauth_connected'] else 'NOT CONNECTED'}"
        )

        print(
            f"Identity         : "
            f"{'VERIFIED' if result['identity_verified'] else 'NOT VERIFIED'}"
        )

        print(
            f"Verified Email   : "
            f"{result['verified_email'] or 'Unknown'}"
        )

        print(
            f"Health           : "
            f"{result['health']}"
        )

        print(
            f"Reason           : "
            f"{result['reason']}"
        )

        print("=" * 70)