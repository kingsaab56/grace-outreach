import os
from pathlib import Path

from config.gmail_profiles import (
    get_gmail_profiles,
    save_gmail_profile,
)


LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")

CHROME_USER_DATA = (
    Path(LOCALAPPDATA)
    / "Google"
    / "Chrome"
    / "User Data"
)


TEAM_NAMES = {
    "Profile 6": "Calvin Chase",
    "Profile 17": "David Walker",
    "Profile 22": "Michael Scott",
    "Profile 24": "Anees",
    "Profile 25": "Nabeel",
    "Profile 27": "Adeel",
    "Profile 28": "New Account",
}


PREFERRED_PROFILES = [
    "Profile 6",
    "Profile 17",
    "Profile 22",
    "Profile 24",
    "Profile 25",
    "Profile 27",
    "Profile 28",
]


def sync_profiles():
    """
    Synchronize Chrome profiles with the Gmail profile database.

    Existing Gmail information is preserved when the profile
    already exists in the database.
    """

    profiles = get_gmail_profiles()

    existing = {}

    for row in profiles:
        if not row:
            continue

        profile_name = row[0]

        gmail = ""
        if len(row) > 1 and row[1]:
            gmail = row[1]

        existing[profile_name] = gmail

    for profile in PREFERRED_PROFILES:

        folder = CHROME_USER_DATA / profile

        if not folder.exists():
            continue

        old_email = existing.get(profile, "")

        save_gmail_profile(
            profile_name=profile,
            gmail=old_email,
        )


def get_profiles():
    """
    Return synchronized Gmail profiles.
    """

    sync_profiles()

    return get_gmail_profiles()


def choose_profile():
    """
    Display active Gmail profiles and allow the user
    to select one.
    """

    profiles = get_profiles()

    if not profiles:
        print("\nNo Gmail Profiles Found.")
        input("\nPress Enter...")
        return None

    print("\n========================================")
    print("        ACTIVE GMAIL PROFILES")
    print("========================================\n")

    active_profiles = []

    for row in profiles:

        if not row:
            continue

        profile_name = row[0]

        gmail = row[1] if len(row) > 1 else ""
        oauth_email = row[2] if len(row) > 2 else ""

        health_score = row[4] if len(row) > 4 else 0
        status = row[5] if len(row) > 5 else "Unknown"
        daily_limit = row[6] if len(row) > 6 else 0
        sent_today = row[7] if len(row) > 7 else 0
        recommended_min = row[8] if len(row) > 8 else 0
        recommended_max = row[9] if len(row) > 9 else 0
        rest_until = row[10] if len(row) > 10 else ""

        # Skip profiles with no Gmail/OAuth account.
        if not gmail and not oauth_email:
            continue

        active_profiles.append(row)

    if not active_profiles:
        print("No logged-in Gmail account found.")
        input("\nPress Enter...")
        return None

    for i, row in enumerate(active_profiles, start=1):

        profile_name = row[0]

        gmail = row[1] if len(row) > 1 else ""
        oauth_email = row[2] if len(row) > 2 else ""

        health_score = row[4] if len(row) > 4 else 0
        status = row[5] if len(row) > 5 else "Unknown"
        daily_limit = row[6] if len(row) > 6 else 0
        sent_today = row[7] if len(row) > 7 else 0
        recommended_min = row[8] if len(row) > 8 else 0
        recommended_max = row[9] if len(row) > 9 else 0
        rest_until = row[10] if len(row) > 10 else ""

        display_name = TEAM_NAMES.get(
            profile_name,
            profile_name,
        )

        print(f"{i}. {display_name}")
        print(f"   Chrome : {profile_name}")
        print(f"   Gmail  : {gmail or oauth_email}")
        print(f"   Health : {health_score}%")
        print(f"   Status : {status}")
        print(f"   Today  : {sent_today}/{daily_limit}")
        print(f"   AI     : {recommended_min}-{recommended_max}")

        if rest_until:
            print(f"   Rest Until : {rest_until}")

        print()

    try:
        choice = int(
            input("Select Active Profile: ")
        )

        if 1 <= choice <= len(active_profiles):
            return active_profiles[choice - 1][0]

    except ValueError:
        pass

    print("\nInvalid Selection.")
    input("\nPress Enter...")

    return None