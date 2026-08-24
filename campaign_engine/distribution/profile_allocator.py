from config.gmail_profiles import get_gmail_profiles
from gmail.chrome_profiles.gmail_detector import detect_gmail_accounts


def allocate_profiles(total):
    profiles = get_gmail_profiles()

    if not profiles:
        return []

    detected_accounts = detect_gmail_accounts()

    accounts_by_profile = {}

    for account in detected_accounts:
        profile_name = account.get("profile", "Unknown")

        accounts_by_profile.setdefault(
            profile_name,
            []
        )

        accounts_by_profile[profile_name].append(account)

    allocation = []
    remaining = total

    for profile in profiles:
        profile_name = profile[0]
        status = profile[5]
        daily_limit = int(profile[6])
        sent_today = int(profile[7])

        if status != "Healthy":
            continue

        available = daily_limit - sent_today

        if available <= 0:
            continue

        assign = min(
            available,
            remaining
        )

        if assign <= 0:
            continue

        profile_accounts = accounts_by_profile.get(
            profile_name,
            []
        )

        allocation.append({
            "profile": profile_name,
            "assigned": assign,
            "accounts": profile_accounts
        })

        remaining -= assign

        if remaining <= 0:
            break

    if remaining > 0:
        print(
            f"\nWARNING: {remaining} contacts "
            "could not be assigned."
        )

    print(
        "\n========== PROFILE DISTRIBUTION ==========\n"
    )

    for item in allocation:
        print(
            f"{item['profile']} -> "
            f"{item['assigned']} drafts"
        )

        accounts = item.get("accounts", [])

        if accounts:
            print("  Login Accounts:")

            for index, account in enumerate(
                accounts,
                start=1
            ):
                name = account.get("name", "")
                email = account.get("email", "")

                print(
                    f"    {index}. "
                    f"{name} | {email}"
                )

            print(
                f"  Accounts Available : "
                f"{len(accounts)}"
            )

        else:
            print(
                "  Login Accounts     : "
                "None detected"
            )

        print()

    print(
        "=========================================="
    )

    return allocation