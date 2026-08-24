import shutil
from pathlib import Path

from config.gmail_profiles import delete_gmail_profile

BASE_DIR = Path(__file__).resolve().parents[1]

ACCOUNTS_DIR = BASE_DIR.parent / "accounts"


def remove_account(profile_name):

    account_path = ACCOUNTS_DIR / profile_name

    print("\n==========================================")
    print("         ACCOUNT CLEANUP")
    print("==========================================")
    print(f"Profile : {profile_name}")

    if account_path.exists():

        try:

            shutil.rmtree(account_path)

            print("OAuth Token : Removed")

        except Exception as e:

            print("OAuth Token : Failed")
            print(e)

    else:

        print("OAuth Token : Not Found")

    try:

        delete_gmail_profile(profile_name)

        print("Database    : Removed")

    except Exception as e:

        print("Database    : Failed")
        print(e)

    print("==========================================")


def cleanup_account():

    profile = input("\nProfile Name: ").strip()

    if not profile:

        print("\nInvalid Profile.")

        return

    confirm = input(
        f"\nRemove '{profile}'? (YES/NO): "
    ).strip().upper()

    if confirm != "YES":

        print("\nCancelled.")

        return

    remove_account(profile)

    input("\nPress Enter...")