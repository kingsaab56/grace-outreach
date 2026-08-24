"""
System Healer: Fixes missing database tables and connects legacy module wrappers.
"""

import os
import sqlite3
from config.database import get_connection

# 1. Create missing tables
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS campaign_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    contact_id INTEGER,
    gmail_account_id INTEGER,
    sender_email TEXT,
    recipient_email TEXT,
    subject TEXT,
    body TEXT,
    draft_id TEXT,
    message_id TEXT,
    status TEXT DEFAULT 'Pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
    FOREIGN KEY(contact_id) REFERENCES contacts(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    event_type TEXT,
    description TEXT,
    level TEXT DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("✔ Database schema healed (campaign_items, activity_logs created).")

# 2. Build modules structure for Legacy V1 compatibility
os.makedirs("modules", exist_ok=True)
with open("modules/__init__.py", "w") as f:
    pass

legacy_modules = [
    ("collector.py", "collector_menu", "Email Collector"),
    ("cleaner.py", "cleaner_menu", "Email Cleaner"),
    ("campaign.py", "campaign_menu", "Campaign Manager"),
    ("spam_checker.py", "spam_checker_menu", "Spam Checker"),
    ("crm.py", "crm_menu", "CRM Dashboard"),
    ("lead_scorer.py", "lead_scorer_menu", "Lead Scoring"),
    ("template_analyzer.py", "template_analyzer_menu", "AI Template Analyzer"),
    ("subject_analyzer.py", "subject_analyzer_menu", "Subject Analyzer"),
    ("templates.py", "template_menu", "Template Manager"),
    ("reports.py", "reports_menu", "Reports"),
    ("activity_log.py", "activity_log_menu", "Activity Logs"),
    ("personalized_campaign.py", "personalized_campaign_menu", "Personalized Campaign"),
    ("progress.py", "progress_menu", "Campaign Progress"),
    ("settings.py", "settings_menu", "System Settings"),
    ("gmail_draft_assistant.py", "draft_assistant_menu", "Gmail Draft Assistant"),
    ("profile_manager.py", "profile_manager_menu", "Gmail Profile Manager"),
    ("followup.py", "followup_menu", "Follow-up Manager"),
    ("suppression.py", "suppression_menu", "Suppression Manager"),
    ("replies.py", "replies_menu", "Reply Manager"),
    ("account_manager.py", "account_manager_menu", "Gmail Account Manager"),
    ("draft_queue.py", "draft_queue_menu", "Draft Queue Manager"),
]

for filename, func_name, title in legacy_modules:
    code = f'''"""
Legacy Wrapper for {title}
"""
def {func_name}():
    print("\\n" + "="*50)
    print("  🚀 {title}")
    print("="*50)
    print("ℹ Upgraded: Use [22] Campaign Engine V2 for fully automated flows.")
    input("\\nPress Enter to return...")
'''
    with open(os.path.join("modules", filename), "w", encoding="utf-8") as f:
        f.write(code)

print("✔ All 21 Legacy Module Wrappers generated successfully.")
