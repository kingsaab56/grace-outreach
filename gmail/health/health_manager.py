def show_health_dashboard():
    print("\n========== ACCOUNT HEALTH ==========\n")

    accounts = get_gmail_profiles()

    if not accounts:
        print("No Accounts Found.")
        return

    for account in accounts:
        print(f"""
Profile      : {account[0]}
Gmail        : {account[1]}

Health       : {account[2]}%
Status       : {account[3]}

Daily Limit  : {account[4]}
Sent Today   : {account[5]}

Warm-up Days : {account[6]}
Reply Delay  : {account[7]} min

OAuth        : {account[8]}
""")


if __name__ == "__main__":
    show_health_dashboard()