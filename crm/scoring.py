from contacts.contacts import get_all_contacts
SCORES = {
    "new": 10,
    "valid": 20,
    "draft_ready": 40,
    "sent": 60,
    "replied": 80,
    "interested": 100,
    "follow_up": 70,
    "closed": 0,
    "invalid": 0
}


def show_scoring():

    print("\n========== LEAD SCORING ==========\n")

    contacts = get_all_contacts()

    if not contacts:
        print("No contacts found.")
        input("\nPress Enter...")
        return

    for email, status in contacts:

        score = SCORES.get(status, 0)

        print(f"Email  : {email}")
        print(f"Status : {status}")
        print(f"Score  : {score}")
        print("-" * 35)

    input("\nPress Enter...")