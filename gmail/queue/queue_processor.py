from gmail.queue.queue_database import (
    get_pending_queue,
    update_queue_status
)

from gmail.drafts.draft_manager import create_draft


def process_queue(limit=None):

    queue = get_pending_queue()

    if not queue:

        print("\nQueue Empty.")

        return

    if limit:

        queue = queue[:limit]

    total = len(queue)

    success = 0
    failed = 0

    print("\n========== PROCESSING QUEUE ==========\n")

    for item in queue:

        (
            queue_id,
            email,
            name,
            company,
            profile,
            subject,
            body,
            status
        ) = item

        try:

            result = create_draft(
                profile,
                email,
                subject,
                body
            )

            if result:

                update_queue_status(
                    queue_id,
                    "draft_created"
                )

                success += 1

                print(f"[OK] {email}")

            else:

                update_queue_status(
                    queue_id,
                    "failed"
                )

                failed += 1

        except Exception as e:

            update_queue_status(
                queue_id,
                "failed"
            )

            failed += 1

            print(f"[FAILED] {email}")

            print(e)

    print("\n==============================")
    print("QUEUE COMPLETE")
    print("==============================")
    print(f"Total   : {total}")
    print(f"Success : {success}")
    print(f"Failed  : {failed}")