from config.database import get_connection
from gmail.queue.queue_database import add_to_queue
from automation.personalize import personalize_template


def build_queue(
    profile,
    subject,
    body,
    limit=None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email,name,company,city
        FROM contacts
        WHERE status='clean'
        ORDER BY id
    """)

    contacts = cursor.fetchall()

    conn.close()

    if not contacts:

        print("\nNo clean contacts found.")

        return

    if limit:

        contacts = contacts[:limit]

    count = 0

    for contact in contacts:

        email = contact[0]

        data = {

            "name": contact[1] or "Contractor",

            "company": contact[2] or "Construction Company",

            "city": contact[3] or "Houston"

        }

        personalized_subject = personalize_template(
            subject,
            data
        )

        personalized_body = personalize_template(
            body,
            data
        )

        add_to_queue(

            email,

            data["name"],

            data["company"],

            profile,

            personalized_subject,

            personalized_body

        )

        count += 1

    print("\n==============================")
    print("QUEUE CREATED")
    print("==============================")
    print("Profile :", profile)
    print("Contacts:", count)