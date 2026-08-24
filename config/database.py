import sqlite3
from config.path_manager import DATABASE

DB_PATH = str(DATABASE)


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # CONTACTS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        status TEXT DEFAULT 'new'
    )
    """)

    # =========================
    # GMAIL PROFILES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gmail_profiles (
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

    # =========================
    # TEAM PROFILES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT
    )
    """)

    # =========================
    # CAMPAIGNS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        template TEXT,
        total_contacts INTEGER DEFAULT 0,
        draft_limit INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Created',
        created_at TEXT,
        completed_count INTEGER DEFAULT 0,
        pending_count INTEGER DEFAULT 0,
        failed_count INTEGER DEFAULT 0
    )
    """)

    # =========================
    # CAMPAIGN QUEUE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaign_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        contact_email TEXT,
        profile_name TEXT,
        subject TEXT,
        body TEXT,
        status TEXT DEFAULT 'pending',
        attempts INTEGER DEFAULT 0,
        created_at TEXT,
        completed_at TEXT
    )
    """)

    # =========================
    # CAMPAIGN PROFILES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaign_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        profile_name TEXT,
        assigned INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        daily_limit INTEGER DEFAULT 80
    )
    """)

    # =========================
    # CAMPAIGN LOGS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaign_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        event TEXT,
        message TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


def init_campaign_tables():
    """
    Backward-compatible function.

    Campaign tables are now created by init_db().
    This function is kept so existing modules
    calling init_campaign_tables() do not break.
    """
    init_db()
    print("Campaign tables initialized.")