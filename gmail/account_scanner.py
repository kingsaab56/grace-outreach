from pathlib import Path
import os


LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")

CHROME_USER_DATA = (
    Path(LOCALAPPDATA)
    / "Google"
    / "Chrome"
    / "User Data"
)


def scan_chrome_profiles():
    """
    Scan the local Chrome User Data directory.

    Only Default and Profile XX directories are treated
    as Chrome user profiles.
    """

    profiles = []

    if not CHROME_USER_DATA.exists():
        return profiles

    for folder in sorted(CHROME_USER_DATA.iterdir()):

        if not folder.is_dir():
            continue

        if (
            folder.name == "Default"
            or folder.name.startswith("Profile")
        ):

            profiles.append(
                {
                    "profile_name": folder.name,
                    "path": str(folder),
                    "exists": True
                }
            )

    return profiles


def get_chrome_user_data_path():
    """
    Return the Chrome User Data base directory.
    """

    return str(CHROME_USER_DATA)


def profile_exists(profile_name):
    """
    Check whether a specific Chrome profile exists.
    """

    profile_path = CHROME_USER_DATA / profile_name

    return profile_path.is_dir()


def get_profile_path(profile_name):
    """
    Return the absolute path of a Chrome profile.
    """

    profile_path = CHROME_USER_DATA / profile_name

    if profile_path.is_dir():
        return str(profile_path)

    return None


def print_chrome_profiles():

    profiles = scan_chrome_profiles()

    print("\n==========================================")
    print("          CHROME PROFILE SCANNER")
    print("==========================================")

    print(f"\nBase Location:")
    print(CHROME_USER_DATA)

    if not profiles:

        print("\nNo Chrome Profiles Found.")

        return

    print("\nDetected Profiles:\n")

    for index, profile in enumerate(profiles, start=1):

        print(
            f"{index}. "
            f"{profile['profile_name']}"
        )

        print(
            f"   Path   : "
            f"{profile['path']}"
        )

        print(
            f"   Exists : "
            f"{profile['exists']}"
        )

    print("\n==========================================")


if __name__ == "__main__":

    print_chrome_profiles()