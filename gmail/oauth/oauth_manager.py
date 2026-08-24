from gmail.oauth.oauth_login import authenticate

from gmail.oauth.token_manager import (
    get_token_file,
    token_exists,
    get_token_status
)

from gmail.oauth.gmail_service import get_profile_email


def connect_account(profile_name):
    """
    Start a fresh OAuth authentication for a Gmail profile.
    """

    print("\n==========================================")
    print("        GMAIL ACCOUNT CONNECTION")
    print("==========================================")
    print("Profile:", profile_name)

    try:
        authenticate(profile_name)

    except Exception as e:
        print("\n[ERROR] OAuth authentication failed.")
        print(e)
        return None

    token_file = get_token_file(profile_name)

    if not token_file.exists():
        print("\n[ERROR] Token was not created.")
        return None

    try:
        email = get_profile_email(profile_name)

    except Exception as e:
        print("\n[ERROR] Could not detect Gmail account.")
        print(e)
        return None

    if not email:
        print("\n[ERROR] Gmail account email not detected.")
        return None

    print("\n------------------------------------------")
    print("OAuth Status :", "CONNECTED")
    print("Profile      :", profile_name)
    print("Gmail        :", email)
    print("Token        :", token_file)
    print("------------------------------------------")

    return {
        "profile": profile_name,
        "email": email,
        "token_file": str(token_file)
    }


def check_account(profile_name):
    """
    Check the current OAuth/token status.
    """

    status = get_token_status(profile_name)

    print("\n==========================================")
    print("          GMAIL ACCOUNT STATUS")
    print("==========================================")

    print("Profile :", profile_name)
    print("Token   :", "YES" if status["exists"] else "NO")
    print("Valid   :", "YES" if status["valid"] else "NO")
    print("Expired :", "YES" if status["expired"] else "NO")

    if status["exists"]:

        try:
            email = get_profile_email(profile_name)

            print("Gmail   :", email or "Unknown")

        except Exception as e:

            print("Gmail   : Unknown")
            print("Error   :", e)

    print("==========================================")

    return status


def connect_or_check(profile_name):
    """
    If the token is missing, expired, or invalid,
    start a fresh OAuth authentication.
    """

    if not token_exists(profile_name):
        return connect_account(profile_name)

    status = get_token_status(profile_name)

    if status["valid"] and not status["expired"]:
        return check_account(profile_name)

    print("\n[INFO] Existing OAuth token is invalid or expired.")
    print("[INFO] Starting fresh OAuth authentication...")

    return connect_account(profile_name)


if __name__ == "__main__":

    profile = input(
        "Profile Name: "
    ).strip()

    if not profile:
        print("Profile name is required.")

    else:
        connect_or_check(profile)