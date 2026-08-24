from config.database import get_connection
import csv


def save_email(email):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO contacts (email)
            VALUES (?)
            """,
            (email,)
        )

        conn.commit()

    except Exception:
        pass

    finally:
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
        (status, email)
    )

    conn.commit()
    conn.close()



def get_all_contacts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT email, status
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
        SELECT email, status
        FROM contacts
        WHERE email LIKE ?
        ORDER BY email
        """,
        (f"%{keyword}%",)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows



def get_contact(email):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM contacts
        WHERE email=?
        """,
        (email,)
    )

    row = cursor.fetchone()

    conn.close()

    return row
def export_contacts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM contacts
        """
    )

    rows = cursor.fetchall()

    conn.close()


    if not rows:
        print("\nNo contacts found.")
        return



    with open(
        "contacts_export.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "ID",
                "Email",
                "Status"
            ]
        )

        writer.writerows(rows)



    print(
        "\nContacts exported successfully."
    )