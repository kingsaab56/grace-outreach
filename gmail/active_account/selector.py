import json
from pathlib import Path

ACTIVE_FILE = Path("config") / "active_accounts.json"


def load_active_accounts():
    if not ACTIVE_FILE.exists():
        return {}

    with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_active_accounts(data):
    ACTIVE_FILE.parent.mkdir(exist_ok=True)

    with open(ACTIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def set_active(profile, email):
    data = load_active_accounts()
    data[profile] = email
    save_active_accounts(data)


def get_active(profile):
    data = load_active_accounts()
    return data.get(profile)


if __name__ == "__main__":
    set_active("Profile 24", "brydon.gracearchitectures.llc@gmail.com")
    print(get_active("Profile 24"))