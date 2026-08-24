from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parents[2]

SETTINGS_DIR = BASE_DIR / "settings"
SETTINGS_FILE = SETTINGS_DIR / "campaign_settings.json"


DEFAULT_SETTINGS = {
    "emails_per_profile": 10,
    "min_delay": 5,
    "max_delay": 15
}


def ensure_settings_file():
    SETTINGS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not SETTINGS_FILE.exists():

        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                DEFAULT_SETTINGS,
                file,
                indent=4
            )


def load_campaign_settings():
    ensure_settings_file()

    try:

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        data = {}

    settings = DEFAULT_SETTINGS.copy()

    if isinstance(data, dict):

        settings.update(data)

    return settings


def save_campaign_settings(settings):
    ensure_settings_file()

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            settings,
            file,
            indent=4
        )


def get_campaign_settings():
    """
    Return saved campaign settings.

    This function does NOT ask for user input.
    """

    return load_campaign_settings()


def edit_campaign_settings():
    """
    Interactive Campaign Settings editor.
    """

    settings = load_campaign_settings()

    print(
        "\n========== CAMPAIGN SETTINGS ==========\n"
    )

    print(
        f"Current Emails Per Profile : "
        f"{settings['emails_per_profile']}"
    )

    print(
        f"Current Minimum Delay      : "
        f"{settings['min_delay']} sec"
    )

    print(
        f"Current Maximum Delay      : "
        f"{settings['max_delay']} sec"
    )

    print(
        "\nPress Enter to keep the current value."
    )

    # =========================
    # EMAILS PER PROFILE
    # =========================

    while True:

        value = input(
            f"\nEmails Per Profile "
            f"[{settings['emails_per_profile']}]: "
        ).strip()

        if value == "":
            emails_per_profile = settings[
                "emails_per_profile"
            ]
            break

        try:

            emails_per_profile = int(value)

            if emails_per_profile > 0:
                break

        except ValueError:
            pass

        print(
            "Please enter a valid positive number."
        )

    # =========================
    # MIN DELAY
    # =========================

    while True:

        value = input(
            f"Minimum Delay "
            f"[{settings['min_delay']}]: "
        ).strip()

        if value == "":
            min_delay = settings["min_delay"]
            break

        try:

            min_delay = int(value)

            if min_delay >= 0:
                break

        except ValueError:
            pass

        print(
            "Please enter a valid number."
        )

    # =========================
    # MAX DELAY
    # =========================

    while True:

        value = input(
            f"Maximum Delay "
            f"[{settings['max_delay']}]: "
        ).strip()

        if value == "":
            max_delay = settings["max_delay"]
            break

        try:

            max_delay = int(value)

            if max_delay >= min_delay:
                break

        except ValueError:
            pass

        print(
            "Maximum delay must be "
            "greater than or equal to "
            "minimum delay."
        )

    new_settings = {
        "emails_per_profile": emails_per_profile,
        "min_delay": min_delay,
        "max_delay": max_delay
    }

    save_campaign_settings(
        new_settings
    )

    print(
        "\nCampaign settings saved successfully."
    )

    print(
        f"\nEmails Per Profile : "
        f"{emails_per_profile}"
    )

    print(
        f"Minimum Delay      : "
        f"{min_delay} sec"
    )

    print(
        f"Maximum Delay      : "
        f"{max_delay} sec"
    )

    input("\nPress Enter...")


def show_campaign_settings():
    settings = load_campaign_settings()

    print(
        "\n========== CAMPAIGN SETTINGS ==========\n"
    )

    print(
        f"Emails Per Profile : "
        f"{settings['emails_per_profile']}"
    )

    print(
        f"Minimum Delay      : "
        f"{settings['min_delay']} sec"
    )

    print(
        f"Maximum Delay      : "
        f"{settings['max_delay']} sec"
    )

    input("\nPress Enter...")