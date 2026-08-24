from config.gmail_profiles import (
    get_gmail_profiles,
    save_gmail_profile,
)

from gmail.chrome_profiles.scanner import scan_profiles
from gmail.chrome_profiles.gmail_detector import detect_gmail_accounts
from gmail.chrome_profiles.profile_sync import sync_profiles
from gmail.business_filter.filter import filter_business_accounts
from gmail.active_account.selector import set_active


def show_accounts():

    print("\n========== GMAIL ACCOUNTS ==========\n")

    accounts = get_gmail_profiles()

    if not accounts:
        print("No Gmail accounts found.")
        input("\nPress Enter...")
        return

    for account in accounts:

        print(f"""
Profile       : {account[0]}
Gmail         : {account[1] or account[2]}
Health        : {account[4]}%
Status        : {account[5]}
Daily Limit   : {account[6]}
Sent Today    : {account[7]}
Recommended   : {account[8]} - {account[9]}
Rest Until    : {account[10]}
----------------------------------------
""")

    input("\nPress Enter...")


def add_account():

    print("\n========== ADD GMAIL ACCOUNT ==========\n")

    profile_name = input("Profile Name: ").strip()
    gmail = input("Gmail Address: ").strip().lower()

    if not profile_name or not gmail:

        print("\nInvalid Information.")
        input("\nPress Enter...")
        return

    save_gmail_profile(
        profile_name=profile_name,
        gmail=gmail
    )

    print("\nAccount Added Successfully.")

    input("\nPress Enter...")


def scan_chrome():

    print("\n========== CHROME PROFILES ==========\n")

    profiles = scan_profiles()

    if not profiles:

        print("No Chrome Profiles Found.")
        input("\nPress Enter...")
        return

    for i, profile in enumerate(profiles, 1):

        print(f"{i}. {profile}")

    input("\nPress Enter...")


def detect_accounts():

    print("\n========== DETECTED GMAIL ==========\n")

    accounts = detect_gmail_accounts()

    if not accounts:

        print("No Gmail Accounts Found.")
        input("\nPress Enter...")
        return

    for i, account in enumerate(accounts, 1):

        print(f"""
{i}.
Profile : {account["profile"]}
Name    : {account["name"]}
Email   : {account["email"]}
""")

    input("\nPress Enter...")


def business_accounts():

    print("\n========== BUSINESS ACCOUNTS ==========\n")

    accounts = detect_gmail_accounts()

    business = filter_business_accounts(accounts)

    if not business:

        print("No Business Accounts Found.")
        input("\nPress Enter...")
        return

    for i, account in enumerate(business, 1):

        print(f"""
{i}.
Profile : {account["profile"]}
Name    : {account["name"]}
Email   : {account["email"]}
""")

    input("\nPress Enter...")


def active_account():

    from config.gmail_profiles import get_gmail_profiles
    from gmail.active_account.selector import set_active

    accounts = get_gmail_profiles()

    if not accounts:

        print("\nNo Gmail Accounts Found.")
        input("\nPress Enter...")
        return

    print("\n========== ACTIVE ACCOUNT ==========\n")

    available = []

    for account in accounts:

        profile = account[0]
        gmail = account[1]
        status = account[5]

        if not profile or not gmail:
            continue

        available.append(
            {
                "profile": profile,
                "email": gmail,
                "status": status
            }
        )

    if not available:

        print("No configured Gmail accounts found.")
        input("\nPress Enter...")
        return

    for i, account in enumerate(available, 1):

        print(
            f"{i}. "
            f"{account['profile']} | "
            f"{account['email']} | "
            f"{account['status']}"
        )

    try:

        choice = int(
            input("\nSelect Account: ").strip()
        )

        if choice < 1 or choice > len(available):

            raise ValueError

        selected = available[choice - 1]

        set_active(
            selected["profile"],
            selected["email"]
        )

        print(
            "\nActive Account Updated."
        )

        print(
            f"Profile : {selected['profile']}"
        )

        print(
            f"Gmail   : {selected['email']}"
        )

        print(
            f"Status  : {selected['status']}"
        )

    except ValueError:

        print("\nInvalid Selection.")

    input("\nPress Enter...")


def refresh_everything():

    print("\n========== REFRESH ==========\n")

    try:

        sync_profiles()

        print("Chrome Scan     : ✓")
        print("Gmail Detection : ✓")
        print("Profile Sync    : ✓")
        print("Business Filter : ✓")
        print("\nRefresh Completed.")

    except Exception as e:

        print("\nRefresh Failed.")
        print(e)

    input("\nPress Enter...")


def start_account_manager():

    while True:

        print("""
==========================================
          GMAIL ACCOUNT MANAGER
==========================================

1. View Accounts
2. Add Account
3. Scan Chrome Profiles
4. Detect Gmail Accounts
5. Business Accounts
6. Active Gmail
7. Refresh Everything
8. Back

==========================================
""")

        choice = input("Select Option: ").strip()

        if choice == "1":

            show_accounts()

        elif choice == "2":

            add_account()

        elif choice == "3":

            scan_chrome()

        elif choice == "4":

            detect_accounts()

        elif choice == "5":

            business_accounts()

        elif choice == "6":

            active_account()

        elif choice == "7":

            refresh_everything()

        elif choice == "8":

            print("\nReturning...")

            break

        else:

            print("\nInvalid Option.")

            input("\nPress Enter...")


if __name__ == "__main__":

    start_account_manager()