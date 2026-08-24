from config.gmail_profiles import (
    get_gmail_profiles,
    save_gmail_profile,
    delete_gmail_profile
)

from gmail.chrome_profiles.profile_manager import (
    show_profile_accounts,
    get_profile_accounts
)

from gmail.oauth.oauth_manager import connect_or_check


def show_profiles():

    print("\n========== GMAIL PROFILES ==========\n")

    profiles = get_gmail_profiles()

    if not profiles:
        print("No Gmail profiles found.")
        return

    seen = set()

    for profile in profiles:

        profile_name = profile[0]

        if profile_name in seen:
            continue

        seen.add(profile_name)

        print("------------------------------------------")
        print(f"Profile : {profile_name}")

        accounts = get_profile_accounts(
            profile_name
        )

        print(f"Accounts: {len(accounts)}")

        for index, account in enumerate(
            accounts,
            start=1
        ):

            name = account[2]
            gmail = account[3]
            connected = account[5]

            status = (
                "OAuth Connected"
                if connected
                else "Not Connected"
            )

            print(
                f"  {index}. {name} | "
                f"{gmail} | {status}"
            )

    print("------------------------------------------")


def view_profile_accounts():

    profile_name = input(
        "\nProfile Name: "
    ).strip()

    if not profile_name:
        print("Profile name is required.")
        return

    show_profile_accounts(
        profile_name
    )


def connect_oauth_account():

    print(
        "\n========== CONNECT OAUTH ACCOUNT ==========\n"
    )

    profile_name = input(
        "Profile Name: "
    ).strip()

    if not profile_name:
        print("Profile name is required.")
        return

    connect_or_check(
        profile_name
    )


def add_profile():

    print(
        "\n========== ADD GMAIL PROFILE ==========\n"
    )

    name = input(
        "Profile Name: "
    ).strip()

    gmail = input(
        "Gmail Address: "
    ).strip()

    if not name or not gmail:
        print(
            "\nProfile name and Gmail are required."
        )
        return

    save_gmail_profile(
        name,
        gmail
    )

    print(
        "\nProfile Added Successfully."
    )


def remove_profile():

    print(
        "\n========== DELETE PROFILE ==========\n"
    )

    name = input(
        "Profile Name: "
    ).strip()

    if not name:
        print("Profile name is required.")
        return

    delete_gmail_profile(
        name
    )

    print(
        "\nProfile Deleted Successfully."
    )


def start_profile_manager():

    while True:

        print(
            """
========== GMAIL PROFILE MANAGER ==========

1. View Profiles
2. View Profile Accounts
3. Connect OAuth Account
4. Add Profile
5. Delete Profile
6. Back

"""
        )

        choice = input(
            "Select: "
        ).strip()

        if choice == "1":

            show_profiles()
            input("\nPress Enter...")

        elif choice == "2":

            view_profile_accounts()
            input("\nPress Enter...")

        elif choice == "3":

            connect_oauth_account()
            input("\nPress Enter...")

        elif choice == "4":

            add_profile()
            input("\nPress Enter...")

        elif choice == "5":

            remove_profile()
            input("\nPress Enter...")

        elif choice == "6":

            break

        else:

            print("\nInvalid Option.")


if __name__ == "__main__":
    start_profile_manager()