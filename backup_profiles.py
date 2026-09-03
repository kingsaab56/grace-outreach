import os
import subprocess
from pathlib import Path

LOCALAPPDATA = os.environ.get("LOCALAPPDATA")

CHROME_USER_DATA = Path(LOCALAPPDATA) / "Google" / "Chrome" / "User Data"
BACKUP_FOLDER = Path(__file__).parent / "backups"


def backup_profiles():

    if not CHROME_USER_DATA.exists():
        print("Chrome User Data not found.")
        input("Press Enter...")
        return

    BACKUP_FOLDER.mkdir(exist_ok=True)

    print("\n========== BACKUP START ==========\n")

    for folder in CHROME_USER_DATA.iterdir():

        if folder.is_dir() and (
            folder.name == "Default"
            or folder.name.startswith("Profile")
        ):

            destination = BACKUP_FOLDER / folder.name

            print(f"Backing up {folder.name}...")

            subprocess.run([
                "robocopy",
                str(folder),
                str(destination),
                "/MIR",
                "/R:1",
                "/W:1",
                "/XD", "Crashpad",
                "/XF",
                "Cookies",
                "Cookies-journal",
                "History",
                "History-journal",
                "Current Session",
                "Current Tabs",
                "Last Session",
                "Last Tabs",
                "Safe Browsing Cookies",
                "Safe Browsing Cookies-journal"
            ], stdout=subprocess.DEVNULL)

    print("\n=================================")
    print("Backup Completed Successfully.")
    print("=================================")

    input("\nPress Enter...")


if __name__ == "__main__":
    backup_profiles()
