"""
Inbound Reply Detector, AI Intent Classifier & CRM/Suppression Synchronizer
"""

import re
from datetime import datetime
from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error, highlight


# Intent classification keywords
POSITIVE_SIGNALS = [
    "interested", "send details", "pricing", "quote", "call me", 
    "schedule", "meeting", "let's talk", "availabl", "rates", "cost"
]

NEGATIVE_SIGNALS = [
    "unsubscribe", "remove me", "not interested", "stop", "don't email", 
    "spam", "take off your list", "do not contact"
]

OOO_SIGNALS = [
    "out of office", "auto reply", "away from", "vacation", "maternity"
]


def classify_reply_intent(subject, body):
    """
    Classifies email text into: Interested, Unsubscribe, Out of Office, or Neutral.
    """
    text = f"{subject} {body}".lower()
    
    for word in NEGATIVE_SIGNALS:
        if word in text:
            return "Unsubscribe", "Negative / Remove"
            
    for word in POSITIVE_SIGNALS:
        if word in text:
            return "Interested", "Hot Lead"
            
    for word in OOO_SIGNALS:
        if word in text:
            return "Out of Office", "Temporary Away"
            
    return "Neutral", "General Inquiry"


def sync_suppression(email, reason="Auto-detected Unsubscribe"):
    """
    Adds lead to suppression list to prevent future dispatches.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT OR IGNORE INTO suppression_list (email, reason, added_on)
            VALUES (?, ?, ?)
            """,
            (email, reason, now_str)
        )
        # Update contacts table status to suppressed
        cursor.execute("UPDATE contacts SET status = 'suppressed' WHERE email = ?", (email,))
        conn.commit()
        return True
    finally:
        conn.close()


def record_reply_event(email, subject, body):
    """
    Saves reply into DB, runs intent classification and triggers auto-actions.
    """
    category, action = classify_reply_intent(subject, body)
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute(
            """
            INSERT INTO replies (email, subject, received_date, reply_type, action_taken)
            VALUES (?, ?, ?, ?, ?)
            """,
            (email, subject, now_str, category, action)
        )
        conn.commit()
        
        if category == "Unsubscribe":
            sync_suppression(email, f"Reply: {action}")
            
        return category, action
    finally:
        conn.close()


def display_replies_matrix():
    """
    Renders CRM Reply Dashboard with Action Badges.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, email, subject, received_date, reply_type, action_taken
            FROM replies
            ORDER BY id DESC
            LIMIT 50
            """
        )
        rows = cursor.fetchall()
        
        print_banner("INBOUND REPLIES & CRM INTENT DASHBOARD", "📬")
        if not rows:
            print(info("No incoming replies recorded yet."))
            return

        print(f"{'#':<4} │ {'Lead Email':<32} │ {'Intent Category':<16} │ {'Date':<18} │ {'Status / Action'}")
        print(f"{Colors.CYAN}{'─' * 95}{Colors.RESET}")

        for idx, r in enumerate(rows, start=1):
            rid, email, subj, rdate, rtype, action = r
            
            if rtype == "Interested":
                type_badge = f"{Colors.GREEN}★ INTERESTED{Colors.RESET}"
            elif rtype == "Unsubscribe":
                type_badge = f"{Colors.RED}✖ UNSUBSCRIBE{Colors.RESET}"
            else:
                type_badge = f"{Colors.YELLOW}● {rtype.upper()}{Colors.RESET}"

            print(f"{idx:<4} │ {email:<32} │ {type_badge:<25} │ {str(rdate)[:16]:<18} │ {action}")

        print(f"{Colors.CYAN}{'═' * 95}{Colors.RESET}\n")
    finally:
        conn.close()
