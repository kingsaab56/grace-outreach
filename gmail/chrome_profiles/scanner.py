import os
from pathlib import Path

LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")

CHROME_USER_DATA = (
    Path(LOCALAPPDATA)
    / "Google"
    / "Chrome"
    / "User Data"
)


def scan_profiles():

    profiles = []

    if not CHROME_USER_DATA.exists():
        return profiles

    for folder in CHROME_USER_DATA.iterdir():

        if folder.is_dir():

            if (
                folder.name == "Default"
                or folder.name.startswith("Profile")
            ):

                profiles.append(folder.name)

    return sorted(profiles)


if __name__ == "__main__":

    for profile in scan_profiles():

        print(profile)