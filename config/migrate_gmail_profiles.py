import sqlite3
from config.path_manager import DATABASE


DB_PATH = str(DATABASE)


def migrate():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE gmail_profiles_new (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        profile_name TEXT UNIQUE,

        gmail TEXT,

        oauth_email TEXT DEFAULT '',

        client_id TEXT DEFAULT '',

        token_file TEXT DEFAULT '',

        health_score INTEGER DEFAULT 100,

        status TEXT DEFAULT 'Healthy',

        daily_limit INTEGER DEFAULT 80,

        sent_today INTEGER DEFAULT 0,

        recommended_min INTEGER DEFAULT 20,

        recommended_max INTEGER DEFAULT 60,

        rest_until TEXT

    )
    """)


    cursor.execute("""
    INSERT INTO gmail_profiles_new
    (
        id,
        profile_name,
        gmail,
        oauth_email,
        client_id,
        token_file,
        health_score,
        status,
        daily_limit,
        sent_today,
        recommended_min,
        recommended_max,
        rest_until
    )
    SELECT
        id,
        profile_name,
        gmail,
        oauth_email,
        client_id,
        token_file,
        health_score,
        status,
        daily_limit,
        sent_today,
        recommended_min,
        recommended_max,
        rest_until
    FROM gmail_profiles
    """)


    cursor.execute("""
    DROP TABLE gmail_profiles
    """)


    cursor.execute("""
    ALTER TABLE gmail_profiles_new
    RENAME TO gmail_profiles
    """)


    conn.commit()
    conn.close()


    print("Gmail profile migration completed.")



if __name__ == "__main__":

    migrate()