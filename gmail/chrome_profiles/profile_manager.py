from config.database import get_connection
from gmail.oauth.oauth_manager import connect_or_check


def get_profile_accounts(profile_name):
    """
    Return all Gmail accounts linked to a Chrome profile.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            profile_name,
            account_name,
            gmail,
            token_file,
            oauth_connected
        FROM gmail_accounts
        WHERE profile_name=?
        ORDER BY account_name
        """,
        (profile_name,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def show_profile_accounts(profile_name):
    """
    Display Gmail accounts for a selected Chrome profile.
    """

    accounts = get_profile_accounts(profile_name)

    print("\n==========================================")
    print("        PROFILE GMAIL ACCOUNTS")
    print("==========================================")
    print(f"Profile: {profile_name}")

    if not accounts:
        print("\nNo Gmail accounts found.")
        print("==========================================")
        return accounts

    for index, account in enumerate(accounts, start=1):

        account_id = account[0]
        account_name = account[2]
        gmail = account[3]
        token_file = account[4]
        oauth_connected = account[5]

        status = (
            "OAuth Connected"
            if oauth_connected
            else "Not Connected"
        )

        print("\n------------------------------------------")
        print(f"{index}. {account_name}")
        print(f"   Gmail  : {gmail}")
        print(f"   Status : {status}")
        print(f"   ID     : {account_id}")

        if token_file:
            print(f"   Token  : {token_file}")

    print("\n==========================================")

    return accounts


def connect_profile_oauth(profile_name):
    """
    Connect/check OAuth for a Chrome profile.
    """

    print("\n==========================================")
    print("          PROFILE OAUTH CONNECTION")
    print("==========================================")
    print(f"Profile: {profile_name}")

    try:
        return connect_or_check(profile_name)

    except Exception as e:
        print("\n[ERROR] OAuth connection failed.")
        print(e)
        return None


def select_profile():
    """
    Select a Gmail account from a Chrome profile.
    """

    profile_name = input(
        "\nProfile Name: "
    ).strip()

    if not profile_name:
        print("\nProfile name is required.")
        return None

    accounts = show_profile_accounts(profile_name)

    if not accounts:
        return None

    while True:

        print("\n1. Select Gmail Account")
        print("2. Connect/Check OAuth")
        print("3. Back")

        choice = input(
            "\nSelect Option: "
        ).strip()

        if choice == "1":

            account_choice = input(
                "\nSelect Gmail Account Number: "
            ).strip()

            if not account_choice.isdigit():
                print("\nInvalid selection.")
                continue

            index = int(account_choice) - 1

            if index < 0 or index >= len(accounts):
                print("\nInvalid account number.")
                continue

            selected = accounts[index]

            print("\n==========================================")
            print("          SELECTED GMAIL ACCOUNT")
            print("==========================================")
            print("Profile :", selected[1])
            print("Name    :", selected[2])
            print("Gmail   :", selected[3])
            print(
                "OAuth   :",
                "Connected"
                if selected[5]
                else "Not Connected"
            )
            print("==========================================")

            return selected

        elif choice == "2":

            connect_profile_oauth(profile_name)

            input("\nPress Enter...")

            accounts = show_profile_accounts(
                profile_name
            )

        elif choice == "3":

            return None

        else:

            print("\nInvalid Option.")


if __name__ == "__main__":
    select_profile()