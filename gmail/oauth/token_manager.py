from pathlib import Path
from google.oauth2.credentials import Credentials


BASE_DIR = Path(__file__).resolve().parents[2]


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]


def _safe_email(email):
    return (
        email
        .strip()
        .lower()
        .replace("@", "_at_")
        .replace(".", "_")
    )


def get_token_file(profile_name, account_email=None):

    token_dir = (
        BASE_DIR
        / "accounts"
        / profile_name
    )

    token_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    if account_email:

        safe_email = _safe_email(
            account_email
        )

        return (
            token_dir
            / f"token_{safe_email}.json"
        )

    return (
        token_dir
        / "token.json"
    )


def token_exists(
    profile_name,
    account_email=None
):

    token_file = get_token_file(
        profile_name,
        account_email
    )

    return token_file.exists()


def load_credentials(
    profile_name,
    account_email=None
):

    token_file = get_token_file(
        profile_name,
        account_email
    )

    if not token_file.exists():

        return None

    try:

        return Credentials.from_authorized_user_file(
            str(token_file),
            SCOPES
        )

    except Exception as e:

        print(
            f"[ERROR] Failed to load token "
            f"for {profile_name}: {e}"
        )

        return None


def get_token_status(
    profile_name,
    account_email=None
):

    creds = load_credentials(
        profile_name,
        account_email
    )

    if not creds:

        return {
            "profile": profile_name,
            "email": account_email,
            "exists": False,
            "valid": False,
            "expired": False
        }

    return {
        "profile": profile_name,
        "email": account_email,
        "exists": True,
        "valid": bool(creds.valid),
        "expired": bool(creds.expired)
    }