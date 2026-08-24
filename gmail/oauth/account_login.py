from pathlib import Path

from gmail.oauth.oauth_login import authenticate
from gmail.oauth.gmail_service import get_profile_email
from gmail.oauth.token_manager import get_token_file
from config.gmail_profiles import (
    save_gmail_profile,
    get_gmail_profiles
)


def login_new_account(profile_name, account_email):
    """
    Authenticate one specific Gmail account inside a Chrome profile.

    Each Gmail account receives its own account-specific OAuth token.
    """

    profile_name = (profile_name or "").strip()
    account_email = (account_email or "").strip().lower()

    if not profile_name:
        print("\n[ERROR] Profile name is required.")
        return False

    if not account_email:
        print("\n[ERROR] Gmail account email is required.")
        return False

    print("\n==========================================")
    print("        GMAIL ACCOUNT LOGIN")
    print("==========================================")
    print(f"Profile : {profile_name}")
    print(f"Account : {account_email}")
    print("==========================================")

    # ---------------------------------------------------------
    # ACCOUNT-SPECIFIC OAUTH AUTHENTICATION
    # ---------------------------------------------------------

    try:
        authenticate(
            profile_name,
            account_email
        )

    except Exception as e:
        print("\n[ERROR] OAuth authentication failed.")
        print(e)
        return False

    # ---------------------------------------------------------
    # ACCOUNT-SPECIFIC TOKEN PATH
    # ---------------------------------------------------------

    token_file = get_token_file(
        profile_name,
        account_email
    )

    # ---------------------------------------------------------
    # VERIFY TOKEN FILE
    # ---------------------------------------------------------

    if not token_file.exists():
        print(
            "\n[ERROR] OAuth completed but token file "
            "was not created."
        )
        print(f"Expected Token: {token_file}")
        return False

    # ---------------------------------------------------------
    # VERIFY GMAIL IDENTITY
    # ---------------------------------------------------------

    oauth_email = ""

    try:
        oauth_email = get_profile_email(
            profile_name,
            account_email
        )

    except Exception as e:
        print("\n[ERROR] Gmail identity detection failed.")
        print(e)
        return False

    if not oauth_email:
        print(
            "\n[ERROR] Gmail API did not return "
            "an account email."
        )
        return False

    oauth_email = oauth_email.strip().lower()

    # ---------------------------------------------------------
    # IDENTITY MATCH
    # ---------------------------------------------------------

    if oauth_email != account_email:
        print("\n[ERROR] OAuth identity mismatch.")
        print(f"Requested : {account_email}")
        print(f"OAuth     : {oauth_email}")
        return False

    # ---------------------------------------------------------
    # UPDATE GMAIL PROFILE RECORD
    # ---------------------------------------------------------

    gmail = account_email

    try:
        accounts = get_gmail_profiles()

        for account in accounts:

            if account[0] == profile_name:

                if len(account) > 2 and account[2]:
                    gmail = account[2]

                elif len(account) > 1 and account[1]:
                    gmail = account[1]

                break

    except Exception as e:
        print(
            "\n[WARNING] Could not read existing "
            f"profile data: {e}"
        )

    try:
        save_gmail_profile(
            profile_name=profile_name,
            gmail=gmail,
            oauth_email=oauth_email,
            token_file=str(token_file)
        )

    except Exception as e:
        print(
            "\n[ERROR] Could not save Gmail profile."
        )
        print(e)
        return False

    # ---------------------------------------------------------
    # SUCCESS
    # ---------------------------------------------------------

    print("\n==========================================")
    print("        OAUTH COMPLETED SUCCESSFULLY")
    print("==========================================")
    print(f"Profile      : {profile_name}")
    print(f"Account      : {account_email}")
    print(f"OAuth Email  : {oauth_email}")
    print(f"Token        : {token_file}")
    print("Identity     : VERIFIED")
    print("Status       : READY")
    print("==========================================")

    return True


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

        login_new_account(
            profile,
            email
        )