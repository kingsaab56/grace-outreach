from config.database import get_connection


def save_email(email):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO contacts(email)
            VALUES(?)
            """,
            (email,)
        )

        conn.commit()

    except Exception:
        pass

    conn.close()


def update_contact(email, name, company, city):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE contacts
        SET
            name=?,
            company=?,
            city=?
        WHERE email=?
        """,
        (
            name,
            company,
            city,
            email
        )
    )

    conn.commit()
    conn.close()


def update_status(email, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE contacts
        SET status=?
        WHERE email=?
        """,
        (
            status,
            email
        )
    )

    conn.commit()
    conn.close()


def get_all_contacts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            email,
            name,
            company,
            city,
            status
        FROM contacts
        ORDER BY email
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def search_email(keyword):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            email,
            name,
            company,
            city,
            status
        FROM contacts
        WHERE email LIKE ?
        """,
        (
            f"%{keyword}%",
        )
    )

    rows = cursor.fetchall()

    conn.close()

    return rows