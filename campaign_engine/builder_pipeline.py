"""
Universal Campaign Builder with Noise Filtration, Time Greetings & Dynamic Fallbacks
"""

import os
import re
import json
import sqlite3
from datetime import datetime
from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error

ARCHIVE_DIR = os.path.abspath("./reports/archived_sent_contacts")
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Words to strip out from email handles
NOISE_KEYWORDS = [
    'realtor', 'realestate', 'realty', 'homes', 'home', 'properties', 'property',
    'invest', 'investments', 'group', 'team', 'broker', 'agent', 'sales', 'corp',
    'llc', 'inc', 'design', 'architecture', 'services', 'office', 'admin', 'info',
    'contact', 'support', 'help', 'mail', 'official', 'usa', 'tx', 'fl', 'ca', 'recycler'
]

def get_time_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def extract_clean_recipient_name(raw_name, email):
    """
    Extracts a pristine first name, stripping out any real estate or generic keywords.
    Returns clean name if valid, otherwise None.
    """
    # 1. If DB already has a clean human name
    if raw_name and str(raw_name).strip() and str(raw_name).strip().lower() not in ('none', 'null', 'nan'):
        first = str(raw_name).strip().split()[0]
        if len(first) > 1 and first.isalpha():
            return first.capitalize()

    # 2. Extract from Email Prefix
    if not email or "@" not in email:
        return None

    prefix = email.split("@")[0].lower()
    
    # Strip common noise keywords
    for noise in NOISE_KEYWORDS:
        prefix = re.sub(rf'{noise}\b|{noise}', '', prefix)

    # Remove digits and punctuation
    clean_prefix = re.sub(r'[0-9]+', '', prefix)
    parts = [p.strip() for p in re.split(r'[._\-\+]+', clean_prefix) if p.strip()]

    # Extract first valid alphabetic piece
    for part in parts:
        if len(part) >= 3 and part.isalpha() and part not in NOISE_KEYWORDS:
            return part.capitalize()

    return None

def extract_sender_name(sender_email):
    """
    Extracts sender's first name dynamically (e.g. adriel -> Adriel).
    """
    if not sender_email or "@" not in sender_email:
        return "Grace Team"
    prefix = sender_email.split("@")[0]
    parts = re.split(r'[._\-]+', prefix)
    first = parts[0].strip()
    return first.capitalize() if first.isalpha() else "Grace Team"

def get_contacts_pool_stats():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(contacts)")
        cols = [r[1].lower() for r in cursor.fetchall()]
        email_col = next((c for c in cols if 'email' in c or 'mail' in c), cols[1] if len(cols) > 1 else 'id')
        
        cursor.execute(f"SELECT COUNT(*) FROM contacts WHERE {email_col} IS NOT NULL AND {email_col} != ''")
        total_contacts = cursor.fetchone()[0]

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campaign_items'")
        has_items = cursor.fetchone()
        
        used_emails = set()
        if has_items:
            cursor.execute("SELECT DISTINCT recipient_email FROM campaign_items WHERE status IN ('Sent', 'Drafted', 'Completed')")
            used_emails = {r[0].lower().strip() for r in cursor.fetchall() if r[0]}

        available = max(0, total_contacts - len(used_emails))
        return total_contacts, len(used_emails), available, email_col
    finally:
        conn.close()

def fetch_fresh_contacts(limit=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(contacts)")
        cols_info = cursor.fetchall()
        cols = [r[1] for r in cols_info]
        
        email_col = next((c for c in cols if 'email' in c.lower()), cols[0])
        name_col = next((c for c in cols if 'name' in c.lower() or 'first' in c.lower()), None)
        comp_col = next((c for c in cols if 'comp' in c.lower() or 'org' in c.lower()), None)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campaign_items'")
        has_items = cursor.fetchone()
        used_emails = set()
        if has_items:
            cursor.execute("SELECT DISTINCT recipient_email FROM campaign_items WHERE status IN ('Sent', 'Drafted', 'Completed')")
            used_emails = {r[0].lower().strip() for r in cursor.fetchall() if r[0]}

        cursor.execute("SELECT rowid, * FROM contacts")
        rows = cursor.fetchall()

        fresh_contacts = []
        for r in rows:
            row_dict = {cols_info[i][1]: r[i+1] for i in range(len(cols_info))}
            email_val = str(row_dict.get(email_col, '')).strip()
            
            if not email_val or '@' not in email_val:
                continue
                
            if email_val.lower() in used_emails:
                continue
                
            raw_name = row_dict.get(name_col, '') if name_col else ''
            clean_name = extract_clean_recipient_name(raw_name, email_val)
            
            fresh_contacts.append({
                "contact_id": r[0],
                "email": email_val,
                "first_name": clean_name, # None if cannot determine cleanly
                "company": row_dict.get(comp_col, '') if comp_col else ''
            })
            
            if limit and len(fresh_contacts) >= limit:
                break

        return fresh_contacts
    finally:
        conn.close()

def archive_and_clean_sent_contacts(campaign_id, campaign_name, sent_records):
    if not sent_records:
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_name = "".join(c for c in campaign_name if c.isalnum() or c in (' ', '_', '-')).strip()
    filename = f"sent_archive_Camp{campaign_id}_{sanitized_name}_{timestamp}.json"
    archive_path = os.path.join(ARCHIVE_DIR, filename)

    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump({
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "archive_time": datetime.now().isoformat(),
            "total_sent": len(sent_records),
            "records": sent_records
        }, f, indent=2)
    return archive_path

def build_campaign_pipeline(campaign_id, campaign_name, subject, body, limit=None):
    total, used, available, _ = get_contacts_pool_stats()
    print_banner(f"BUILDING QUEUE: {campaign_name}", "⚙️")

    contacts_to_queue = fetch_fresh_contacts(limit)
    if not contacts_to_queue:
        print(warning("No fresh contacts left to queue."))
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    try:
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
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        queued_count = 0
        fallback_greeting = get_time_greeting()

        for item in contacts_to_queue:
            target_name = item["first_name"]
            
            # Smart Dynamic Greeting Logic
            if target_name:
                greeting_val = f"Hi {target_name}"
                subj_name_val = target_name
            else:
                greeting_val = fallback_greeting
                subj_name_val = ""

            # Replace recipient placeholders in Subject & Body
            personalized_subject = subject
            personalized_body = body

            # Subject cleanup: if no name, clean up extra spaces/commas gracefully
            if target_name:
                personalized_subject = personalized_subject.replace("{name}", subj_name_val).replace("{first_name}", subj_name_val)
            else:
                personalized_subject = personalized_subject.replace("{name}", "").replace("{first_name}", "")
                personalized_subject = re.sub(r'\s{2,}', ' ', personalized_subject).replace(" ,", ",").replace(" !", "!")

            replacements = {
                "{greeting}": greeting_val,
                "{Greeting}": greeting_val,
                "{name}": target_name if target_name else fallback_greeting,
                "{first_name}": target_name if target_name else fallback_greeting,
                "{company}": item["company"] or ""
            }

            for ph, val in replacements.items():
                personalized_body = personalized_body.replace(ph, val)

            cursor.execute("""
                INSERT INTO campaign_items (campaign_id, contact_id, recipient_email, subject, body, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (campaign_id, item["contact_id"], item["email"], personalized_subject, personalized_body))
            queued_count += 1

        cursor.execute("UPDATE campaigns SET total_contacts = ?, status = 'Ready' WHERE id = ?", (queued_count, campaign_id))
        conn.commit()

        print(f"{success(f'Successfully Queued {queued_count} Clean Contacts for Campaign #{campaign_id}!')}")
        return queued_count
    finally:
        conn.close()
