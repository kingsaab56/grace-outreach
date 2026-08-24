import inspect

targets = [
    ("collector.collector", "collector"),
    ("cleaner.service", "cleaner"),
    ("campaign.campaign_manager", "campaign"),
    ("spam_checker.spam_checker", "spam_checker"),
    ("crm.crm", "crm"),
    ("crm.scoring", "lead_scoring"),
    ("ai.template_analyzer", "template_analyzer"),
    ("ai.subject_analyzer", "subject_analyzer"),
    ("template_manager.manager", "template_manager"),
    ("reports.report", "reports"),
    ("settings.campaign_settings", "settings"),
    ("gmail.account_status", "gmail_status"),
    ("gmail.profile_manager", "gmail_profiles"),
    ("followup.manager", "followup"),
    ("suppression.manager", "suppression"),
    ("replies.tracker", "replies"),
    ("gmail.account_dashboard", "gmail_dashboard")
]

for mod_name, label in targets:
    try:
        mod = __import__(mod_name, fromlist=["*"])
        funcs = [f[0] for f in inspect.getmembers(mod, inspect.isfunction)]
        print(f"[{label} ({mod_name})]: {funcs}")
    except Exception as e:
        print(f"[{label} ERROR]: {e}")
