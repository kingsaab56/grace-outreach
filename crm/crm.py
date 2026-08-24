from config.database import get_connection

from contacts.contacts import (
    save_email,
    update_status,
    get_all_contacts,
    search_email
)

from contacts.contacts import export_contacts

from crm.personalized_campaign import show_personalized_email
from logger.activity_logger import write_log


def get_count(status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM contacts WHERE status=?",
        (status,)
    )

    count = cursor.fetchone()[0]
    conn.close()

    return count



def get_total():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM contacts")

    total = cursor.fetchone()[0]
    conn.close()

    return total



def show_contacts():

    print("\n========== CONTACT LIST ==========\n")

    rows = get_all_contacts()

    if not rows:
        print("No contacts found.")
        return

    for email, status in rows:
        print(f"{email} --> {status}")



def change_status():

    print("\n========== UPDATE STATUS ==========\n")

    email = input("Email: ").strip().lower()
    status = input("New Status: ").strip().lower()

    update_status(email, status)

    print("\nStatus Updated Successfully.")

    write_log(
        "CRM",
        f"{email} status changed to {status}"
    )



def search_lead():

    print("\n========== SEARCH RESULT ==========\n")

    keyword = input("Search Email: ").strip()

    results = search_email(keyword)

    if not results:
        print("No lead found.")
        return

    for email, status in results:
        print(f"{email} --> {status}")



def start_personalized_campaign():

    template = """
Hello {{name}},

We provide professional architectural drawings and construction estimating services for {{company}}.

We would like to support your projects in {{city}}.

Thank you.
"""


    contact = {

        "name": input("Name: ").strip(),

        "company": input("Company: ").strip(),

        "city": input("City: ").strip()

    }


    show_personalized_email(
        template,
        contact
    )



def start_crm():

    while True:

        print("""
========== CRM DASHBOARD ==========

1. Dashboard
2. View Contacts
3. Update Status
4. Search Lead
5. Export CSV
6. Back

""")

        choice = input("Select: ")


        if choice == "1":

            print(f"\nTotal Emails : {get_total()}")
            print(f"New          : {get_count('new')}")
            print(f"Draft Ready  : {get_count('draft_ready')}")
            print(f"Sent         : {get_count('sent')}")
            print(f"Replied      : {get_count('replied')}")

            input("\nPress Enter...")


        elif choice == "2":

            show_contacts()
            input("\nPress Enter...")


        elif choice == "3":

            change_status()
            input("\nPress Enter...")


        elif choice == "4":

            search_lead()
            input("\nPress Enter...")


        elif choice == "5":

            export_contacts()
            input("\nPress Enter...")


        elif choice == "6":

            break


        else:

            print("Invalid Option.")