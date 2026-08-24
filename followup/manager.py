from followup.templates import show_templates
from followup.database import create_followup_tables


def start_followup_manager():

    create_followup_tables()

    while True:

        print("""
========== FOLLOW-UP MANAGER ==========

1. Templates
2. Pending Follow-ups
3. Send Follow-ups
4. AI Advisor
5. Reports
6. Back
""")

        choice = input("Select: ")

        if choice == "1":

         show_templates()

         input("\nPress Enter...")

        elif choice == "2":
            print("Pending Follow-ups (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "3":
            print("Sending Follow-ups (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "4":
            print("AI Advisor (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "5":
            print("Reports (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "6":
            break

        else:
            print("Invalid Option.")