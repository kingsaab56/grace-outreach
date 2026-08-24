import json
import os
from pathlib import Path

from gmail.queue.queue_builder import build_queue
from automation.personalize import personalize_template
from gmail.drafts.draft_manager import create_draft
from automation.profile_manager import choose_profile
from config.database import get_connection
from ai.template_analyzer import analyze_template

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
TEMPLATE_FILE = BASE_DIR / "templates" / "email_templates.json"


def load_templates():

    if not TEMPLATE_FILE.exists():
        return {}

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def start_gmail_assistant():

    print("\n========== GMAIL DRAFT ASSISTANT ==========\n")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT email,name,company,city
        FROM contacts
        WHERE status='clean'
        ORDER BY id
    """)

    contacts = cur.fetchall()
    conn.close()

    if not contacts:
        print("No clean contacts found.")
        input("Press Enter...")
        return

    print("VALID CONTACTS\n")

    for i, c in enumerate(contacts, 1):
        print(f"{i}. {c[0]}")

    try:
        selected_contact = contacts[
            int(input("\nSelect Contact Number: ")) - 1
        ]
    except:
        print("Invalid Selection")
        input("Press Enter...")
        return

    personal_data = {
        "name": selected_contact[1] or "Contractor",
        "company": selected_contact[2] or "Construction Company",
        "city": selected_contact[3] or "Houston"
    }

    templates = load_templates()

    if not templates:
        print("No Templates Found")
        input("Press Enter...")
        return

    print("\nAVAILABLE TEMPLATES\n")

    names = list(templates.keys())

    for i, n in enumerate(names, 1):
        print(f"{i}. {n}")

    try:
        template = templates[
            names[int(input("\nSelect Template: ")) - 1]
        ]
    except:
        print("Invalid Template")
        input("Press Enter...")
        return

    profile = choose_profile()

    if profile is None:
        return

    subject = personalize_template(
        template["subject"],
        personal_data
    )

    body = personalize_template(
        template["body"],
        personal_data
    )

    analyze_template(subject, body)


    print("""
======== SEND MODE ========

1. Create Single Draft
2. Add All Clean Contacts To Queue

""")


    mode = input("Select Mode: ")


    if mode == "2":

        build_queue(
            profile,
            template["subject"],
            template["body"]
        )

        print("\nContacts added to Draft Queue.")

        input("\nPress Enter...")

        return


    if input("\nContinue creating draft? (Y/N): ").strip().lower() != "y":
        return


    create_draft(
        profile,
        selected_contact[0],
        subject,
        body
    )

    print("\nDraft created successfully.")

    input("\nPress Enter...")