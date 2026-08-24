import sys
import os
from config.database import get_connection

C_TITLE = "\033[38;5;48m"   # Mint Green
C_INFO  = "\033[38;5;220m"  # Gold
C_STAT  = "\033[38;5;84m"   # Seafoam Green
C_ERR   = "\033[38;5;196m"  # Red
C_RST   = "\033[0m"
C_BOLD  = "\033[1m"


def run_cleaner():
    print(f"\n{C_TITLE}{C_BOLD}========== EMAIL CLEANER & VALIDATOR =========={C_RST}\n")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, email FROM contacts WHERE status IS NULL OR status = ''")
        rows = cursor.fetchall()

        if not rows:
            print(f"{C_INFO}No uncleaned contacts found.{C_RST}\n")
            return

        cleaned_count = 0
        invalid_count = 0

        for row_id, email in rows:
            clean_email = str(email).strip().lower()
            if "@" in clean_email and "." in clean_email.split("@")[-1]:
                cursor.execute("UPDATE contacts SET email = ?, status = 'valid' WHERE id = ?", (clean_email, row_id))
                cleaned_count += 1
            else:
                cursor.execute("UPDATE contacts SET status = 'invalid' WHERE id = ?", (row_id,))
                invalid_count += 1

        conn.commit()
        print(f"{C_STAT}Cleaned & Validated: {cleaned_count}{C_RST}")
        print(f"{C_ERR}Invalid Emails Flagged: {invalid_count}{C_RST}\n")

    except Exception as e:
        print(f"{C_ERR}Cleaner Error: {e}{C_RST}")
    finally:
        conn.close()
