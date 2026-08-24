from replies.database import create_reply_table


def start_reply_manager():

    create_reply_table()

    while True:

        print("""
========== REPLY MANAGER ==========

1. View Replies
2. Scan Gmail Replies
3. AI Classify Replies
4. Back
""")

        choice = input("Select: ")

        if choice == "1":

            print("\nReply Viewer (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "2":

            print("\nGmail Scanner (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "3":

            print("\nAI Reply Classifier (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "4":

            break

        else:

            print("Invalid Option.")