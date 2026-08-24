import os

folders = [
    "contacts", "gmail", "ai", "templates", "template_manager", "campaign",
    "campaign_engine", "team_manager", "replies", "followup", "reports",
    "settings", "spam_checker", "suppression", "cleaner", "collector", "crm", "scheduler"
]

for f in folders:
    if os.path.exists(f) and os.path.isdir(f):
        py_files = [file for file in os.listdir(f) if file.endswith(".py")]
        print(f"[{f}]:", py_files)
