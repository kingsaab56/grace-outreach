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

    if isinstance(progress, list) and progress:
        tot_c = sum((c.get("total") or 0) for c in progress)
        comp_c = sum((c.get("completed") or 0) for c in progress)
        rem_c = sum((c.get("pending") or 0) for c in progress)
        pct_c = int((comp_c / tot_c) * 100) if tot_c > 0 else 0
        print(f"Total Campaigns   : {len(progress)}")
        print(f"Campaign Total    : {tot_c}")
        print(f"Processed         : {comp_c}")
        print(f"Remaining         : {rem_c}")
        print(f"Overall Progress  : {pct_c}%")
    elif isinstance(progress, dict):
        print(f"Campaign Total    : {progress.get('total', 0)}")
        print(f"Processed         : {progress.get('completed', 0)}")
        print(f"Remaining         : {progress.get('remaining', 0)}")
        print(f"Progress          : {progress.get('progress', 0)}%")
    else:
        print("No campaign data available yet.")

    input("\nPress Enter...")