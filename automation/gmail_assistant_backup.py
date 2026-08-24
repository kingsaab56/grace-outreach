import json
import os
from pathlib import Path

from automation.personalize import personalize_template
from automation.gmail_draft import create_draft
from automation.profile_manager import choose_profile
from config.database import get_connection
from ai.template_analyzer import analyze_template

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
TEMPLATE_FILE = BASE_DIR / "templates" / "email_templates.json"


def load_templates():

    if not TEMPLATE_FILE.exists():
        return {}

    with open(
        TEMPLATE_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def start_gmail_assistant():

    print("\n========== GMAIL DRAFT ASSISTANT ==========\n")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email, name, company, city
        FROM contacts
        WHERE status='clean'
        ORDER BY id
    """)

    contacts = cursor.fetchall()

    conn.close()

    if not contacts:

        print("\nNo valid contacts found.")

        input("\nPress Enter...")

        return

    print("VALID CONTACTS\n")

    for i, contact in enumerate(contacts, start=1):

        email, name, company, city = contact

        print(f"{i}. {email} | {company} | {city}")

    try:

        choice = int(input("\nSelect Contact Number: "))

        selected_contact = contacts[choice - 1]

    except (ValueError, IndexError):

        print("\nInvalid Selection.")

        input("\nPress Enter...")

        return

    selected_email = selected_contact[0]

    personal_data = {

        "name": selected_contact[1] or "Contractor",

        "company": selected_contact[2] or "Construction Company",

        "city": selected_contact[3] or "Houston"

    }

    templates = load_templates()

    if not templates:

        print("\nNo templates available.")

        input("\nPress Enter...")

        return

    print("\nAVAILABLE TEMPLATES\n")

    template_names = list(templates.keys())

    for i, name in enumerate(template_names, start=1):

        print(f"{i}. {name}")

    try:

        choice = int(input("\nSelect Template: "))

        template = templates[template_names[choice - 1]]

    except (ValueError, IndexError):

        print("\nInvalid Template.")

        input("\nPress Enter...")

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

    print("\n========== PERSONALIZED EMAIL ==========\n")

    print("Subject:")
    print(subject)

    print("\nBody:\n")
    print(body)

    print(f"\nSelected Profile: {profile}")

    # -----------------------------
    # AI TEMPLATE ANALYZER
    # -----------------------------

    analysis = analyze_template(subject, body)

    choice = input(
        "\nContinue creating draft? (Y/N): "
    ).strip().lower()

    if choice != "y":

        print("\nDraft creation cancelled.")

        input("\nPress Enter...")

        return

    # -----------------------------
    # CREATE GMAIL DRAFT
    # -----------------------------

    print("\nCreating Gmail Draft...\n")

    try:

        create_draft(
            selected_email,
            subject,
            body
        )

        print("\n====================================")
        print(" Draft Created Successfully")
        print("====================================")

        print(f"To      : {selected_email}")
        print(f"Subject : {subject}")

        print("\nSaved in Gmail Drafts.")

    except Exception as e:

        print("\nFailed to create draft.")

        print(e)

    input("\nPress Enter...")