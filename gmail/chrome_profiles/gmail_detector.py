import os
import json
from pathlib import Path


LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")

CHROME_USER_DATA = (
    Path(LOCALAPPDATA)
    / "Google"
    / "Chrome"
    / "User Data"
)


def detect_gmail_accounts():

    accounts = []

    if not CHROME_USER_DATA.exists():
        return accounts

    for folder in sorted(CHROME_USER_DATA.iterdir()):

        if not folder.is_dir():
            continue

        if (
            folder.name != "Default"
            and not folder.name.startswith("Profile")
        ):
            continue

        pref_file = folder / "Preferences"

        if not pref_file.exists():
            continue

        try:

            with open(
                pref_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except (
            OSError,
            json.JSONDecodeError
        ):

            continue

        account_info = data.get(
            "account_info",
            []
        )

        if not isinstance(
            account_info,
            list
        ):

            continue

        for account in account_info:

            if not isinstance(
                account,
                dict
            ):

                continue

            email = str(
                account.get(
                    "email",
                    ""
                )
            ).strip()

            full_name = str(
                account.get(
                    "full_name",
                    ""
                )
            ).strip()

            if not email:
                continue

            accounts.append(
                {
                    "profile": folder.name,
                    "name": full_name,
                    "email": email
                }
            )

    return accounts


def get_accounts_by_profile(profile_name):

    accounts = detect_gmail_accounts()

    return [
        account
        for account in accounts
        if account["profile"] == profile_name
    ]


def get_profile_account_count(profile_name):

    return len(
        get_accounts_by_profile(
            profile_name
        )
    )


def print_detected_accounts():

    accounts = detect_gmail_accounts()

    print("\n==========================================")
    print("          DETECTED GMAIL ACCOUNTS")
    print("==========================================")

    if not accounts:

        print("\nNo Gmail accounts detected.")
        return

    current_profile = None

    for account in accounts:

        profile = account["profile"]

        if profile != current_profile:

            current_profile = profile

            print(
                f"\n[{profile}]"
            )

        print(
            f"  {account['name']} | "
            f"{account['email']}"
        )

    print(
        f"\nTotal detected identities: "
        f"{len(accounts)}"
    )


if __name__ == "__main__":

    print_detected_accounts()