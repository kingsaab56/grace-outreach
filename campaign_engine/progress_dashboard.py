"""
Campaign Engine V2 - Progress & Monitoring Dashboard
Provides real-time stats, delivery breakdown, and draft status.
"""

from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error

def display_campaign_dashboard(campaign_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, status, total_contacts, completed_count, failed_count, pending_count FROM campaigns WHERE id = ?", (campaign_id,))
        camp = cursor.fetchone()
        
        if not camp:
            print(error(f"Campaign #{campaign_id} not found."))
            return

        cid, name, stat, total, comp, fail, pend = camp
        
        cursor.execute("SELECT COUNT(*) FROM campaign_items WHERE campaign_id = ? AND status = 'Drafted'", (campaign_id,))
        drafted_cnt = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM campaign_items WHERE campaign_id = ? AND status = 'Pending'", (campaign_id,))
        pending_items_cnt = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM campaign_items WHERE campaign_id = ? AND status = 'Failed'", (campaign_id,))
        failed_items_cnt = cursor.fetchone()[0]

        print_banner(f"CAMPAIGN PROGRESS DASHBOARD: {name} (ID: #{cid})", "📊")
        print(f" {Colors.CYAN}Campaign Status     :{Colors.RESET} {stat}")
        print(f" {Colors.CYAN}Total Contacts      :{Colors.RESET} {total or 0}")
        print(f" {Colors.GREEN}Successfully Drafted:{Colors.RESET} {drafted_cnt}")
        print(f" {Colors.YELLOW}Pending in Queue    :{Colors.RESET} {pending_items_cnt}")
        print(f" {Colors.RED}Failed Items        :{Colors.RESET} {failed_items_cnt}\n")

        # Visual Progress Bar
        total_valid = total or (drafted_cnt + pending_items_cnt + failed_items_cnt)
        if total_valid > 0:
            pct = int((drafted_cnt / total_valid) * 100)
            bar_len = 30
            filled = int(bar_len * (pct / 100))
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f" {Colors.BOLD}Progress: [{bar}] {pct}%{Colors.RESET}\n")

        # Show Recent Items
        cursor.execute("""
            SELECT recipient_email, sender_email, status, created_at 
            FROM campaign_items 
            WHERE campaign_id = ? 
            ORDER BY id DESC LIMIT 10
        """, (campaign_id,))
        recent = cursor.fetchall()

        if recent:
            print(f"{Colors.BOLD}{'Recipient':<32} │ {'Sender Account':<32} │ {'Status'}{Colors.RESET}")
            print(f"{Colors.CYAN}{'─' * 78}{Colors.RESET}")
            for r in recent:
                to_e, from_e, item_stat, _ = r
                status_colored = f"{Colors.GREEN}{item_stat}{Colors.RESET}" if item_stat == 'Drafted' else (f"{Colors.RED}{item_stat}{Colors.RESET}" if item_stat == 'Failed' else f"{Colors.YELLOW}{item_stat}{Colors.RESET}")
                print(f"{str(to_e)[:30]:<32} │ {str(from_e or 'N/A')[:30]:<32} │ {status_colored}")
            print(f"{Colors.CYAN}{'─' * 78}{Colors.RESET}")
            
    finally:
        conn.close()
    input("\nPress Enter to return...")
