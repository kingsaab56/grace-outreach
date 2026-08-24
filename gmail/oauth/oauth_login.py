from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]


BASE_DIR = Path(__file__).resolve().parents[2]


CREDENTIALS_FILE = (
    BASE_DIR
    / "credentials"
    / "credentials.json"
)


def _safe_email(email):

    return (
        email
        .strip()
        .lower()
        .replace("@", "_at_")
        .replace(".", "_")
    )


def get_account_token_file(
    profile_name,
    account_email
):

    if not profile_name:
        raise ValueError(
            "Profile name is required."
        )

    if not account_email:
        raise ValueError(
            "Gmail account email is required."
        )

    token_dir = (
        BASE_DIR
        / "accounts"
        / profile_name
    )

    token_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_email = _safe_email(
        account_email
    )

    return (
        token_dir
        / f"token_{safe_email}.json"
    )


def authenticate(
    profile_name,
    account_email
):

    if not profile_name:
        raise ValueError(
            "Profile name is required."
        )

    if not account_email:
        raise ValueError(
            "Gmail account email is required."
        )

    if not CREDENTIALS_FILE.exists():

        raise FileNotFoundError(
            f"Credentials file not found: "
            f"{CREDENTIALS_FILE}"
        )

    token_file = get_account_token_file(
        profile_name,
        account_email
    )

    creds = None

    if token_file.exists():

        try:

            creds = (
                Credentials
                .from_authorized_user_file(
                    str(token_file),
                    SCOPES
                )
            )

        except Exception:

            creds = None

    if creds and creds.valid:

        return creds

    if (
        creds
        and creds.expired
        and creds.refresh_token
    ):

        try:

            creds.refresh(
                Request()
            )

        except Exception:

            creds = None

    if not creds or not creds.valid:

        print(
            "\n=========================================="
        )

        print(
            "        GMAIL ACCOUNT AUTHENTICATION"
        )

        print(
            "=========================================="
        )

        print(
            f"Profile : {profile_name}"
        )

        print(
            f"Account : {account_email}"
        )

        print(
            "=========================================="
        )

        flow = (
            InstalledAppFlow
            .from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )
        )

        creds = flow.run_local_server(
            port=0,
            access_type="offline",
            prompt="consent"
        )

    token_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        token_file,
        "w",
        encoding="utf-8"
    ) as token:

        token.write(
            creds.to_json()
        )

    return creds


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

        authenticate(
            profile,
            email
        )

        print(
            "\nOAuth authentication completed."
        )