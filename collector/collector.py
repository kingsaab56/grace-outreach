import sys
import os
from config.database import get_connection

# Colors
C_TITLE = "\033[38;5;51m"   # Aqua
C_INFO  = "\033[38;5;220m"  # Gold
C_PROMPT= "\033[38;5;46m"   # Neon Green
C_STAT  = "\033[38;5;84m"   # Seafoam Green
C_RST   = "\033[0m"
C_BOLD  = "\033[1m"


def start_collector():
    print(f"\n{C_TITLE}{C_BOLD}========== EMAIL COLLECTOR (DB MODE) =========={C_RST}\n")
    print(f"{C_INFO}Enter emails (type '{C_BOLD}stop{C_RST}{C_INFO}' to finish){C_RST}\n")

    conn = get_connection()
    cursor = conn.cursor()

    added = 0
    skipped = 0

    try:
        while True:
            email = input(f"{C_PROMPT}{C_BOLD}Email: {C_RST}").strip()

            if email.lower() == "stop":
                break

            if not email:
                continue

            try:
                cursor.execute("INSERT INTO contacts (email) VALUES (?)", (email,))
                conn.commit()
                added += 1
            except Exception:
                skipped += 1

        print(f"\n{C_STAT}Added: {added}{C_RST}")
        print(f"{C_INFO}Skipped (duplicate): {skipped}{C_RST}\n")

    finally:
        conn.close()
