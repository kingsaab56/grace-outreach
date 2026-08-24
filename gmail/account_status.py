from pathlib import Path

from config.gmail_profiles import get_gmail_profiles


BASE_DIR = Path(__file__).resolve().parents[1]

ACCOUNTS_DIR = BASE_DIR.parent / "accounts"


def get_token_path(profile_name):

    return ACCOUNTS_DIR / profile_name / "token.json"


def get_account_status():

    profiles = get_gmail_profiles()

    results = []

    for profile in profiles:

        profile_name = profile[0]

        token_file = get_token_path(profile_name)

        token_exists = token_file.exists()

        database_exists = True

        if token_exists:
            status = "Connected"

        else:
            status = "Inactive"

        results.append(
            {
                "profile_name": profile_name,
                "chrome": False,
                "token": token_exists,
                "database": database_exists,
                "status": status,
            }
        )

    return results


def show_account_status():

    statuses = get_account_status()

    print("\n==========================================")
    print("            ACCOUNT STATUS")
    print("==========================================")

    if not statuses:

        print("\nNo Gmail profiles found.")

        input("\nPress Enter...")
        return

    for account in statuses:

        print(
            f"\nProfile  : {account['profile_name']}"
        )

        print(
            f"Token    : {account['token']}"
        )

        print(
            f"Database : {account['database']}"
        )

        print(
            f"Status   : {account['status']}"
        )

        print("------------------------------------------")

    input("\nPress Enter...")


if __name__ == "__main__":

    show_account_status()