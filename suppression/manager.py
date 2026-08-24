from suppression.database import create_suppression_table


def start_suppression_manager():

    create_suppression_table()

    while True:

        print("""
========== SUPPRESSION MANAGER ==========

1. View Suppression List
2. Add Email
3. Remove Email
4. Back
""")

        choice = input("Select: ")

        if choice == "1":

            print("\nView Module (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "2":

            print("\nAdd Module (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "3":

            print("\nRemove Module (Coming Soon)")
            input("\nPress Enter...")

        elif choice == "4":

            break

        else:

            print("Invalid Option.")