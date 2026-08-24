"""
Campaign Engine V2 - Execution & Runner with Dynamic Sender Injection
"""

import os
import sys
import time
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error
from campaign_engine.builder_pipeline import archive_and_clean_sent_contacts, extract_sender_name

VAULT_DIR = os.path.abspath("./tokens_vault_backup")

def _get_active_oauth_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT gmail, token_file FROM gmail_accounts WHERE oauth_connected = 1")
        rows = cursor.fetchall()
        valid = []
        for email, tok in rows:
            token_path = tok
            if not token_path or not os.path.exists(token_path):
                sanitized = email.replace("@", "_at_").replace(".", "_")
                vault_tok = os.path.join(VAULT_DIR, f"vault_token_{sanitized}.json")
                if os.path.exists(vault_tok):
                    token_path = vault_tok
            if token_path and os.path.exists(token_path):
                valid.append({"email": email, "token_path": token_path})
        return valid
    finally:
        conn.close()

def _create_gmail_draft(service, sender_email, to_email, subject, body):
    message = MIMEMultipart()
    message['to'] = to_email
    message['from'] = sender_email
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft = {'message': {'raw': raw}}
    return service.users().drafts().create(userId='me', body=draft).execute()

def run_campaign_flow(campaign_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, status, total_contacts FROM campaigns WHERE id = ?", (campaign_id,))
    camp = cursor.fetchone()
    if not camp:
        print(error(f"Campaign #{campaign_id} not found."))
        conn.close()
        return

    camp_name, camp_status, total_contacts = camp
    
    cursor.execute("""
        SELECT id, recipient_email, subject, body 
        FROM campaign_items 
        WHERE campaign_id = ? AND status = 'Pending'
    """, (campaign_id,))
    pending_items = cursor.fetchall()
    
    if not pending_items:
        print(info(f"No pending items found for Campaign #{campaign_id} ({camp_name})."))
        conn.close()
        return

    active_accounts = _get_active_oauth_accounts()
    if not active_accounts:
        print(error("No active OAuth connected accounts found in Vault! Please connect at least 1 account in Option [12]."))
        conn.close()
        return

    print_banner(f"RUNNING CAMPAIGN #{campaign_id}: {camp_name}", "🚀")
    print(f" {Colors.CYAN}Queue Items   :{Colors.RESET} {len(pending_items)}")
    print(f" {Colors.GREEN}Sender Pool   :{Colors.RESET} {len(active_accounts)} accounts\n")

    services = {}
    for acc in active_accounts:
        try:
            creds = Credentials.from_authorized_user_file(acc["token_path"])
            services[acc["email"]] = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        except Exception as e:
            print(warning(f"Could not initialize service for {acc['email']}: {e}"))

    if not services:
        print(error("Failed to initialize Gmail API clients."))
        conn.close()
        return

    sender_emails = list(services.keys())
    acc_idx = 0
    success_count = 0
    fail_count = 0
    sent_records = []

    print(f"{Colors.BOLD}{'#':<4} │ {'Recipient':<32} │ {'Sender Account':<32} │ {'Status'}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 88}{Colors.RESET}")

    for idx, item in enumerate(pending_items, start=1):
        item_id, to_email, subj, body = item
        current_sender = sender_emails[acc_idx % len(sender_emails)]
        service = services[current_sender]

        # Dynamic Sender Name Injection
        sender_first_name = extract_sender_name(current_sender)
        final_body = body.replace("{sender_name}", sender_first_name).replace("{my_name}", sender_first_name)
        final_subj = subj.replace("{sender_name}", sender_first_name).replace("{my_name}", sender_first_name)

        try:
            draft_res = _create_gmail_draft(service, current_sender, to_email, final_subj, final_body)
            draft_id = draft_res.get("id", "OK")
            
            cursor.execute("""
                UPDATE campaign_items 
                SET status = 'Drafted', sender_email = ?, draft_id = ? 
                WHERE id = ?
            """, (current_sender, draft_id, item_id))
            conn.commit()

            print(f"{idx:<4} │ {to_email[:30]:<32} │ {current_sender[:30]:<32} │ {Colors.GREEN}DRAFTED ({sender_first_name}) ✔{Colors.RESET}")
            success_count += 1
            sent_records.append({"email": to_email, "sender": current_sender, "draft_id": draft_id, "timestamp": time.time()})
        except Exception as e:
            cursor.execute("UPDATE campaign_items SET status = 'Failed' WHERE id = ?", (item_id,))
            conn.commit()
            print(f"{idx:<4} │ {to_email[:30]:<32} │ {current_sender[:30]:<32} │ {Colors.RED}FAILED ✖{Colors.RESET}")
            fail_count += 1

        acc_idx += 1
        time.sleep(0.5)

    cursor.execute("""
        UPDATE campaigns 
        SET completed_count = completed_count + ?, 
            failed_count = failed_count + ?, 
            status = CASE WHEN (SELECT COUNT(*) FROM campaign_items WHERE campaign_id = ? AND status = 'Pending') = 0 THEN 'Completed' ELSE 'In Progress' END
        WHERE id = ?
    """, (success_count, fail_count, campaign_id, campaign_id))
    conn.commit()
    conn.close()

    print(f"{Colors.CYAN}{'─' * 88}{Colors.RESET}")
    print(f"\n{success(f'Finished: {success_count} Drafted, {fail_count} Failed.')}")

    if sent_records:
        archive_and_clean_sent_contacts(campaign_id, camp_name, sent_records)

    input("\nPress Enter to return to menu...")
