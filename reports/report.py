from reports.campaign_progress import get_campaign_progress
from config.database import get_connection


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



def show_reports():

    total = get_total()

    valid = get_count("valid")
    invalid = get_count("invalid")
    draft = get_count("draft_ready")
    sent = get_count("sent")
    replied = get_count("replied")
    interested = get_count("interested")
    follow = get_count("follow_up")
    closed = get_count("closed")


    if total == 0:

        conversion = 0

    else:

        conversion = (interested / total) * 100



    progress = get_campaign_progress()



    print("\n========== REPORTS ==========\n")


    print(f"Total Emails      : {total}")
    print(f"Valid Emails      : {valid}")
    print(f"Invalid Emails    : {invalid}")
    print(f"Draft Ready       : {draft}")
    print(f"Sent              : {sent}")
    print(f"Replied           : {replied}")
    print(f"Interested        : {interested}")
    print(f"Follow Up         : {follow}")
    print(f"Closed            : {closed}")
    print(f"Conversion Rate   : {conversion:.2f}%")



    print("\n========== CAMPAIGN SUMMARY ==========\n")


    print(f"Campaign Total    : {progress['total']}")
    print(f"Processed         : {progress['completed']}")
    print(f"Remaining         : {progress['remaining']}")
    print(f"Progress          : {progress['progress']}%")


    input("\nPress Enter...")