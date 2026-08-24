import sqlite3
import csv

from config.path_manager import DATABASE


DB_PATH = str(DATABASE)



def get_connection():

    return sqlite3.connect(DB_PATH)



def init_db():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        email TEXT UNIQUE,

        name TEXT DEFAULT '',

        company TEXT DEFAULT '',

        city TEXT DEFAULT '',

        status TEXT DEFAULT 'new'

    )
    """)


    cursor.execute(
        "PRAGMA table_info(contacts)"
    )

    existing_columns = [
        row[1]
        for row in cursor.fetchall()
    ]


    upgrades = {

        "name": "TEXT DEFAULT ''",

        "company": "TEXT DEFAULT ''",

        "city": "TEXT DEFAULT ''"

    }


    for column, datatype in upgrades.items():

        if column not in existing_columns:

            cursor.execute(
                f"ALTER TABLE contacts ADD COLUMN {column} {datatype}"
            )



    conn.commit()
    conn.close()




def save_email(email):

    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            "INSERT INTO contacts (email) VALUES (?)",
            (email,)
        )

        conn.commit()


    except sqlite3.IntegrityError:

        pass


    conn.close()




def update_contact(email, name, company, city):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE contacts
        SET name=?, company=?, city=?
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
        SELECT email, name, company, city, status
        FROM contacts
        ORDER BY email
        """
    )
    cursor.execute("""
CREATE TABLE IF NOT EXISTS gmail_profiles (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    profile_name TEXT UNIQUE,

    gmail TEXT UNIQUE,

    oauth_email TEXT,

    client_id TEXT,

    token_file TEXT,

    status TEXT DEFAULT 'healthy',

    daily_limit INTEGER DEFAULT 100,

    sent_today INTEGER DEFAULT 0,

    replies INTEGER DEFAULT 0,

    bounces INTEGER DEFAULT 0,

    spam_score REAL DEFAULT 0,

    health_score INTEGER DEFAULT 100,

    recommended_min INTEGER DEFAULT 40,

    recommended_max INTEGER DEFAULT 120,

    rest_until TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")


    rows = cursor.fetchall()

    conn.close()

    return rows




def search_email(keyword):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT email, name, company, city, status
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




def export_contacts():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT email, name, company, city, status
        FROM contacts
        ORDER BY email
        """
    )
    cursor.execute("""
CREATE TABLE IF NOT EXISTS gmail_profiles (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    profile_name TEXT UNIQUE,

    gmail TEXT UNIQUE,

    oauth_email TEXT,

    client_id TEXT,

    token_file TEXT,

    status TEXT DEFAULT 'Healthy',

    daily_limit INTEGER DEFAULT 80,

    sent_today INTEGER DEFAULT 0,

    replies INTEGER DEFAULT 0,

    bounces INTEGER DEFAULT 0,

    spam_score REAL DEFAULT 0,

    health_score INTEGER DEFAULT 100,

    recommended_min INTEGER DEFAULT 20,

    recommended_max INTEGER DEFAULT 60,

    rest_until TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")


    rows = cursor.fetchall()


    with open(
        "contacts_export.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:


        writer = csv.writer(file)


        writer.writerow(
            [
                "Email",
                "Name",
                "Company",
                "City",
                "Status"
            ]
        )


        writer.writerows(rows)



    conn.close()


    print("\nContacts exported successfully.")
def get_gmail_profiles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            profile_name,
            gmail,
            health_score,
            status,
            daily_limit,
            sent_today,
            recommended_min,
            recommended_max,
            rest_until
        FROM gmail_profiles
        ORDER BY profile_name
    """)

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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO gmail_profiles
        (
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