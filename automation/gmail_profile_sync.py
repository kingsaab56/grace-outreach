from gmail.service.account_info import get_account_info
from config.gmail_profiles import (
    get_gmail_profiles,
    save_gmail_profile,
)


def sync_gmail_profiles():

    profiles = get_gmail_profiles()

    for row in profiles:

        profile_name = row[0]

        try:

            info = get_account_info(profile_name)

            if not info:
                continue

            save_gmail_profile(
                profile_name=profile_name,
                gmail=info["email"],
                oauth_email=info["email"],
                token_file=f"accounts/{profile_name}/token.json"
            )

            print(f"[SYNCED] {profile_name} -> {info['email']}")

        except Exception as e:

            print(f"[FAILED] {profile_name}")

            print(e)