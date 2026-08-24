from gmail.chrome_profiles.scanner import scan_profiles
from gmail.chrome_profiles.gmail_detector import detect_gmail_accounts
from config.database import get_connection


def _ensure_gmail_accounts_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS gmail_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_name TEXT NOT NULL,
            account_name TEXT,
            gmail TEXT NOT NULL,
            token_file TEXT,
            oauth_connected INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(profile_name, gmail)
        )
        """
    )

    conn.commit()
    conn.close()


def sync_profiles():

    _ensure_gmail_accounts_table()

    profiles = scan_profiles()
    accounts = detect_gmail_accounts()

    conn = get_connection()
    cursor = conn.cursor()

    synced = 0

    for profile in profiles:

        profile_accounts = [
            account
            for account in accounts
            if account.get("profile") == profile
        ]

        for account in profile_accounts:

            gmail = account.get(
                "email",
                ""
            ).strip()

            name = account.get(
                "name",
                ""
            ).strip()

            if not gmail:
                continue

            cursor.execute(
                """
                INSERT INTO gmail_accounts (
                    profile_name,
                    account_name,
                    gmail
                )
                VALUES (?, ?, ?)
                ON CONFLICT(profile_name, gmail)
                DO UPDATE SET
                    account_name=excluded.account_name,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    profile,
                    name,
                    gmail
                )
            )

            synced += 1

    conn.commit()
    conn.close()

    print("\n==========================================")
    print("          PROFILE SYNC COMPLETE")
    print("==========================================")
    print(
        f"Profiles Detected : {len(profiles)}"
    )
    print(
        f"Accounts Synced   : {synced}"
    )
    print("==========================================")


if __name__ == "__main__":
    sync_profiles()