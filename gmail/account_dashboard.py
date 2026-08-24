from gmail.account_status import get_account_status


def show_dashboard():

    statuses = get_account_status()

    print("\n==========================================")
    print("          GMAIL ACCOUNT DASHBOARD")
    print("==========================================")

    if not statuses:
        print("\nNo Gmail profiles found.")
        input("\nPress Enter...")
        return

    total = len(statuses)

    connected = sum(
        1 for account in statuses
        if account["status"] == "Connected"
    )

    inactive = sum(
        1 for account in statuses
        if account["status"] == "Inactive"
    )

    new = sum(
        1 for account in statuses
        if account["status"] == "New"
    )

    print(f"\nTotal Profiles : {total}")
    print(f"Connected      : {connected}")
    print(f"Inactive       : {inactive}")
    print(f"New            : {new}")

    print("\n------------------------------------------")

    for account in statuses:

        print(
            f"{account['profile_name']:<15}"
            f"{account['status']}"
        )

    print("\n==========================================")

    input("\nPress Enter...")


if __name__ == "__main__":
    show_dashboard()