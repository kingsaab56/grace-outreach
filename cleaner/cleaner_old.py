import re

from cleaner.modules.validator import clean_email_list
from config.database import get_connection


def paste_mode():

    print("\n========== PASTE EMAILS ==========\n")
    print("Paste emails (one per line)")
    print("Type END when finished.\n")

    emails = []

    while True:

        line = input().strip()

        if line.upper() == "END":
            break

        if line:
            emails.append(line)

    result = clean_email_list(emails)

    print("\n========== RESULT ==========\n")

    print(f"Total Emails : {result['total']}")
    print(f"Valid Gmail  : {result['valid']}")
    print(f"Duplicates   : {result['duplicates']}")
    print(f"Invalid      : {result['invalid']}")

    print("\n========== CLEAN EMAILS ==========\n")

    for email in result["emails"]:
        print(email)

    save = input("\nSave valid emails to database? (Y/N): ").strip().lower()

    if save == "y":

        conn = get_connection()
        cursor = conn.cursor()

        for email in result["emails"]:

            cursor.execute(
                """
                INSERT OR IGNORE INTO contacts(email,status)
                VALUES(?,?)
                """,
                (email, "valid")
            )

        conn.commit()
        conn.close()

        print("\nSaved successfully.")

    input("\nPress Enter...")


def database_mode():

    print("\n========== DATABASE CLEANER ==========\n")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,email FROM contacts"
    )

    contacts = cursor.fetchall()

    valid = 0
    invalid = 0

    regex = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"

    for contact_id, email in contacts:

        email = email.strip().lower()

        if re.match(regex, email):

            cursor.execute(
                "UPDATE contacts SET status='valid' WHERE id=?",
                (contact_id,)
            )

            valid += 1

        else:

            cursor.execute(
                "UPDATE contacts SET status='invalid' WHERE id=?",
                (contact_id,)
            )

            invalid += 1

    conn.commit()
    conn.close()

    print(f"Valid Gmail : {valid}")
    print(f"Invalid     : {invalid}")

    input("\nPress Enter...")


def start_cleaner():

    print("""
========== EMAIL CLEANER ==========

1. Paste Emails

2. Clean Database

0. Back

==========================
""")

    choice = input("Select: ")

    if choice == "1":
        paste_mode()

    elif choice == "2":
        database_mode()