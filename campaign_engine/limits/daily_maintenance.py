"""
Daily Maintenance & Midnight Reset Engine
Auto-increments warm-up stages, resets daily sending counters, and audits account health.
"""

from datetime import datetime, date
from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, highlight


def run_daily_maintenance(force=False):
    """
    Executes daily warm-up tier evaluation and maintenance routines.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    
    print_banner("RUNNING DAILY ENGINE MAINTENANCE", "🛠️")
    
    try:
        # 1. Fetch all accounts from warmup table
        cursor.execute("SELECT email, profile_name, warmup_stage, daily_safe_cap, days_active, last_calculated FROM account_warmup_profiles")
        accounts = cursor.fetchall()
        
        upgraded_count = 0
        updated_days = 0
        
        for acc in accounts:
            email, prof, stage, cap, days, last_calc = acc
            last_date_str = str(last_calc)[:10] if last_calc else ""
            
            # Check if already updated today unless forced
            if last_date_str == today_str and not force:
                continue
                
            new_days = days + 1
            new_stage = stage
            new_cap = cap
            
            # Dynamic Tier Upgrade Logic:
            # 1-3 days   -> Tier 1 (15 drafts)
            # 4-7 days   -> Tier 2 (25 drafts)
            # 8-14 days  -> Tier 3 (40 drafts)
            # 15+ days   -> Tier 4 (50+ drafts)
            if new_days >= 15:
                new_stage = 4
                new_cap = 50
            elif new_days >= 8:
                new_stage = 3
                new_cap = 40
            elif new_days >= 4:
                new_stage = 2
                new_cap = 25
            else:
                new_stage = 1
                new_cap = 15
                
            if new_stage > stage:
                upgraded_count += 1
                
            cursor.execute(
                """
                UPDATE account_warmup_profiles
                SET warmup_stage = ?, daily_safe_cap = ?, days_active = ?, last_calculated = CURRENT_TIMESTAMP
                WHERE email = ?
                """,
                (new_stage, new_cap, new_days, email)
            )
            updated_days += 1
            
        conn.commit()
        
        print(f" {Colors.GREEN}✔ Accounts Audited & Maintained :{Colors.RESET} {updated_days}")
        if upgraded_count > 0:
            print(f" {Colors.GOLD}★ Warm-up Tiers Upgraded       :{Colors.RESET} {upgraded_count} account(s)")
        print(f" {Colors.CYAN}ℹ Daily Quotas Ready for Date  :{Colors.RESET} {today_str}\n")
        return True
    except Exception as e:
        print(warning(f"Maintenance warning: {e}"))
        return False
    finally:
        conn.close()
