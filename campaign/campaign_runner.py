import json
from pathlib import Path
from datetime import datetime

from engine.campaign_engine import start_campaign_engine
from settings.campaign_settings import get_campaign_settings
from automation.profile_manager import get_profiles
from config.database import get_connection


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_FILE = BASE_DIR / "templates" / "email_templates.json"


def load_templates():
    if not TEMPLATE_FILE.exists():
        return {}

    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return {}


def get_valid_contacts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email
        FROM contacts
        WHERE status = 'valid'
        ORDER BY id
    """)

    contacts = cursor.fetchall()

    conn.close()

    return contacts


def create_campaign_record(
    template_name,
    profile_name,
    total_contacts,
    draft_limit
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat(timespec="seconds")

    campaign_name = (
        f"{template_name} - "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    cursor.execute("""
        INSERT INTO campaigns (
            name,
            template,
            total_contacts,
            draft_limit,
            status,
            created_at,
            completed_count,
            pending_count,
            failed_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        campaign_name,
        template_name,
        total_contacts,
        draft_limit,
        "Created",
        now,
        0,
        total_contacts,
        0
    ))

    campaign_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return campaign_id


def create_campaign_queue(
    campaign_id,
    contacts,
    profile_name,
    subject,
    body
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat(timespec="seconds")

    for _, email in contacts:

        cursor.execute("""
            INSERT INTO campaign_queue (
                campaign_id,
                contact_email,
                profile_name,
                subject,
                body,
                status,
                attempts,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_id,
            email,
            profile_name,
            subject,
            body,
            "pending",
            0,
            now
        ))

    conn.commit()
    conn.close()


def create_campaign_profile(
    campaign_id,
    profile_name,
    assigned,
    daily_limit
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO campaign_profiles (
            campaign_id,
            profile_name,
            assigned,
            completed,
            daily_limit
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        campaign_id,
        profile_name,
        assigned,
        0,
        daily_limit
    ))

    conn.commit()
    conn.close()


def log_campaign_event(
    campaign_id,
    event,
    message
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO campaign_logs (
            campaign_id,
            event,
            message,
            time
        )
        VALUES (?, ?, ?, ?)
    """, (
        campaign_id,
        event,
        message,
        now
    ))

    conn.commit()
    conn.close()


def run_campaign():

    templates = load_templates()

    if not templates:
        print("\nNo Templates Found.")
        input("\nPress Enter...")
        return

    names = list(templates.keys())

    print("\n========== SELECT TEMPLATE ==========\n")

    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")

    try:
        template_choice = int(
            input("\nSelect Template: ")
        )

        template = templates[
            names[template_choice - 1]
        ]

    except (ValueError, IndexError):

        print("\nInvalid Selection.")
        input("\nPress Enter...")
        return

    template_name = names[template_choice - 1]

    print("\nTemplate Selected Successfully.\n")

    print("Subject:")
    print(template.get("subject", ""))

    print("\nBody Preview:\n")
    print(template.get("body", "")[:300])

    profiles = get_profiles()

    if not profiles:

        print("\nNo Chrome Profiles Found.")
        input("\nPress Enter...")
        return

    print("\n========== SELECT PROFILE ==========\n")

    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile}")

    try:

        profile_choice = int(
            input("\nSelect Profile: ")
        )

        selected_profile = profiles[
            profile_choice - 1
        ]

    except (ValueError, IndexError):

        print("\nInvalid Selection.")
        input("\nPress Enter...")
        return

    print(
        f"\nSelected Profile : "
        f"{selected_profile}"
    )

    settings = get_campaign_settings()

    contacts = get_valid_contacts()

    if not contacts:

        print("\nNo valid contacts found.")
        input("\nPress Enter...")
        return

    emails_per_profile = int(
        settings.get("emails_per_profile", 0)
    )

    min_delay = settings.get(
        "min_delay",
        0
    )

    max_delay = settings.get(
        "max_delay",
        0
    )

    daily_limit = emails_per_profile

    print("\n========== SUMMARY ==========\n")

    print(f"Template : {template_name}")
    print(f"Profile  : {selected_profile}")
    print(f"Contacts : {len(contacts)}")
    print(f"Draft Limit : {emails_per_profile}")
    print(
        f"Delay    : "
        f"{min_delay} - {max_delay} sec"
    )

    confirm = input(
        "\nCreate Campaign Queue? (Y/N): "
    ).strip().lower()

    if confirm != "y":

        print("\nCampaign Cancelled.")
        input("\nPress Enter...")
        return

    print("\nCreating Campaign...\n")

    campaign_id = create_campaign_record(
        template_name=template_name,
        profile_name=selected_profile,
        total_contacts=len(contacts),
        draft_limit=emails_per_profile
    )

    create_campaign_profile(
        campaign_id=campaign_id,
        profile_name=selected_profile,
        assigned=len(contacts),
        daily_limit=daily_limit
    )

    create_campaign_queue(
        campaign_id=campaign_id,
        contacts=contacts,
        profile_name=selected_profile,
        subject=template.get("subject", ""),
        body=template.get("body", "")
    )

    log_campaign_event(
        campaign_id,
        "CREATED",
        f"Campaign created with {len(contacts)} contacts."
    )

    print(
        f"Campaign ID : {campaign_id}"
    )

    print(
        f"Queue       : {len(contacts)} contacts"
    )

    print(
        "\nCampaign queue created successfully."
    )

    print(
        "\nStarting Campaign Engine...\n"
    )

    start_campaign_engine(
        selected_profile,
        template,
        settings,
        campaign_id=campaign_id
    )