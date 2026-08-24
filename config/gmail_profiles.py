from dataclasses import dataclass

from config.database import get_connection


@dataclass
class GmailProfile:
    profile_name: str
    gmail: str
    chrome_profile: str
    health_score: int = 100
    status: str = "Healthy"
    daily_limit: int = 100
    sent_today: int = 0
    replies: int = 0
    bounces: int = 0
    spam_score: float = 0.0
    recommended_min: int = 40
    recommended_max: int = 100
    rest_hours: int = 0


def get_gmail_profiles():
    """
    Return all configured Gmail profiles.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            profile_name,
            gmail,
            oauth_email,
            token_file,
            health_score,
            status,
            daily_limit,
            sent_today,
            recommended_min,
            recommended_max,
            rest_until
        FROM gmail_profiles
        WHERE profile_name IS NOT NULL
          AND TRIM(profile_name) != ''
        ORDER BY profile_name
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def save_gmail_profile(
    profile_name,
    gmail,
    oauth_email="",
    client_id="",
    token_file=""
):
    """
    Save or update a Gmail profile.
    """

    conn = get_connection()
    cursor = conn.cursor()

    print("\n========== SAVE PROFILE ==========")
    print("PROFILE :", profile_name)
    print("GMAIL   :", gmail)
    print("OAUTH   :", oauth_email)

    cursor.execute(
        """
        SELECT profile_name
        FROM gmail_profiles
        WHERE profile_name=?
        """,
        (profile_name,)
    )

    exists = cursor.fetchone()

    if exists:

        print("ACTION  : UPDATE")

        cursor.execute(
            """
            UPDATE gmail_profiles
            SET
                gmail=?,
                oauth_email=?,
                client_id=?,
                token_file=?
            WHERE profile_name=?
            """,
            (
                gmail,
                oauth_email,
                client_id,
                token_file,
                profile_name
            )
        )

    else:

        print("ACTION  : INSERT")

        cursor.execute(
            """
            INSERT INTO gmail_profiles(
                profile_name,
                gmail,
                oauth_email,
                client_id,
                token_file
            )
            VALUES (?,?,?,?,?)
            """,
            (
                profile_name,
                gmail,
                oauth_email,
                client_id,
                token_file
            )
        )

    conn.commit()
    conn.close()


def sync_oauth_email(
    profile_name,
    oauth_email
):
    """
    Synchronize the database Gmail identity
    with the verified OAuth Gmail identity.
    """

    if not profile_name:
        return False

    if not oauth_email:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE gmail_profiles
        SET
            gmail=?,
            oauth_email=?
        WHERE profile_name=?
        """,
        (
            oauth_email,
            oauth_email,
            profile_name
        )
    )

    updated = cursor.rowcount

    conn.commit()
    conn.close()

    if updated:

        print("\n========== OAUTH SYNC ==========")
        print("PROFILE :", profile_name)
        print("GMAIL   :", oauth_email)
        print("STATUS  : SYNCHRONIZED")
        print("================================")

        return True

    return False


def delete_gmail_profile(profile_name):
    """
    Delete a Gmail profile.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM gmail_profiles
        WHERE profile_name=?
        """,
        (profile_name,)
    )

    conn.commit()
    conn.close()