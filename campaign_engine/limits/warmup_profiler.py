"""
Account Warm-up & Dynamic Ramp-up Throttle Profiler
"""

from datetime import datetime
from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, success, info, warning, highlight


def _ensure_warmup_table():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS account_warmup_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                profile_name TEXT,
                warmup_stage INTEGER DEFAULT 1,
                daily_safe_cap INTEGER DEFAULT 15,
                days_active INTEGER DEFAULT 1,
                last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_warmup_tier(email, profile_name):
    _ensure_warmup_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT warmup_stage, daily_safe_cap, days_active FROM account_warmup_profiles WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()

        if not row:
            cursor.execute(
                """
                INSERT OR IGNORE INTO account_warmup_profiles (email, profile_name, warmup_stage, daily_safe_cap, days_active)
                VALUES (?, ?, 1, 15, 1)
                """,
                (email, profile_name)
            )
            conn.commit()
            return {"stage": 1, "tier": "Tier 1 (New)", "safe_cap": 15, "days_active": 1}

        stage, cap, days = row
        tier_names = {
            1: "Tier 1 (New)",
            2: "Tier 2 (Warming)",
            3: "Tier 3 (Established)",
            4: "Tier 4 (Matured)"
        }
        return {
            "stage": stage,
            "tier": tier_names.get(stage, "Tier 1 (New)"),
            "safe_cap": cap,
            "days_active": days
        }
    finally:
        conn.close()


def display_warmup_summary():
    _ensure_warmup_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Pull distinct accounts from gmail_accounts (using gmail column)
        cursor.execute("SELECT gmail, profile_name FROM gmail_accounts ORDER BY profile_name ASC, gmail ASC")
        accounts = cursor.fetchall()

        print_banner("ACCOUNT WARM-UP & SAFE THROTTLE MATRIX", "🔥")
        if not accounts:
            print(info("No Gmail accounts found to evaluate."))
            return

        print(f"{'#':<4} │ {'Email':<40} │ {'Profile':<14} │ {'Stage':<8} │ {'Safe Cap':<10} │ {'Active Days':<12}")
        print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}")

        for idx, (gmail_addr, prof) in enumerate(accounts, start=1):
            cursor.execute(
                "SELECT warmup_stage, daily_safe_cap, days_active FROM account_warmup_profiles WHERE email = ?",
                (gmail_addr,)
            )
            w_row = cursor.fetchone()
            if not w_row:
                stage, cap, days = 1, 15, 1
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO account_warmup_profiles (email, profile_name, warmup_stage, daily_safe_cap, days_active)
                    VALUES (?, ?, 1, 15, 1)
                    """,
                    (gmail_addr, str(prof))
                )
                conn.commit()
            else:
                stage, cap, days = w_row

            stage_badge = f"{Colors.GREEN}Tier {stage}{Colors.RESET}" if stage >= 3 else f"{Colors.YELLOW}Tier {stage}{Colors.RESET}"
            print(f"{idx:<4} │ {str(gmail_addr):<40} │ {str(prof or 'Default'):<14} │ {stage_badge:<17} │ {cap}/day     │ {days} days")

        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}\n")
    finally:
        conn.close()
