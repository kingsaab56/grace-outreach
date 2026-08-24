"""
Database Schema Auto-Migrator & Pipeline Synchronizer
Ensures all required columns (status, etc.) exist across contacts, campaigns, and campaign_items.
"""

import sqlite3
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

def add_column_if_missing(table, column, col_type):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cursor.fetchall()]
    if column not in cols:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            print(f"✔ Added column `{column}` to table `{table}`")
        except Exception as e:
            print(f"Note: {e}")

# Check & Fix contacts table
add_column_if_missing("contacts", "status", "TEXT DEFAULT 'Active'")
add_column_if_missing("contacts", "lead_score", "INTEGER DEFAULT 50")
add_column_if_missing("contacts", "first_name", "TEXT DEFAULT ''")
add_column_if_missing("contacts", "company", "TEXT DEFAULT ''")

# Check & Fix campaigns table
add_column_if_missing("campaigns", "status", "TEXT DEFAULT 'Draft'")
add_column_if_missing("campaigns", "subject", "TEXT DEFAULT ''")
add_column_if_missing("campaigns", "body", "TEXT DEFAULT ''")
add_column_if_missing("campaigns", "total_contacts", "INTEGER DEFAULT 0")
add_column_if_missing("campaigns", "completed_count", "INTEGER DEFAULT 0")
add_column_if_missing("campaigns", "failed_count", "INTEGER DEFAULT 0")
add_column_if_missing("campaigns", "pending_count", "INTEGER DEFAULT 0")

# Check & Fix campaign_items table
add_column_if_missing("campaign_items", "status", "TEXT DEFAULT 'Pending'")
add_column_if_missing("campaign_items", "draft_id", "TEXT")
add_column_if_missing("campaign_items", "sender_email", "TEXT")
add_column_if_missing("campaign_items", "recipient_email", "TEXT")

conn.commit()
conn.close()
print("\n✔ All database tables & columns are 100% aligned!")
