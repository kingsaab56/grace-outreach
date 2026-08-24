import json
from pathlib import Path


SETTINGS_FILE = Path("config") / "settings.json"



def load_settings():

    if not SETTINGS_FILE.exists():

        return {}

    with open(
        SETTINGS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



def save_settings(data):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )



def show_settings():

    settings = load_settings()


    print("\n========== SYSTEM SETTINGS ==========\n")


    print(
        "Company:",
        settings["company"]["name"]
    )

    print(
        "Website:",
        settings["company"]["website"]
    )


    print(
        "\nSender:",
        settings["sender"]["name"]
    )


    print(
        "\nCampaign Mode:",
        settings["campaign"]["mode"]
    )


    print(
        "\nAI Analysis:",
        settings["ai"]["template_analysis"]
    )


    input("\nPress Enter...")



def update_setting(section, key, value):

    settings = load_settings()


    if section in settings:

        settings[section][key] = value

        save_settings(settings)

        return True


    return False