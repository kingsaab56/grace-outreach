from gmail.queue.queue_database import (
    add_to_queue,
    get_pending_queue,
    update_queue_status
)


def add_draft_to_queue(
    contact_email,
    contact_name,
    company,
    profile_name,
    subject,
    body
):

    add_to_queue(
        contact_email,
        contact_name,
        company,
        profile_name,
        subject,
        body
    )


    print(
        f"Queued: {contact_email}"
    )



def show_queue():

    queue = get_pending_queue()


    if not queue:

        print("\nQueue Empty.")

        return



    print("\n========== DRAFT QUEUE ==========\n")


    for item in queue:

        print(
            f"""
ID      : {item[0]}
Email   : {item[1]}
Company : {item[3]}
Profile : {item[4]}
Status  : {item[7]}
-----------------------------
"""
        )



def mark_completed(queue_id):

    update_queue_status(
        queue_id,
        "draft_created"
    )


    print(
        "Queue updated."
    )