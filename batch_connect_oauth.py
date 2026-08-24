"""
Multi-Account Batch OAuth Connector
Loops through pending accounts one by one automatically.
"""

from campaign_engine.oauth_vault.oauth_controller import get_pending_oauth_accounts, connect_oauth_flow_for_account
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning

def run_batch_connect():
    pending, connected = get_pending_oauth_accounts()
    print_banner("BATCH OAUTH ACCOUNT CONNECTOR", "⚡")
    print(f"Pending Accounts: {len(pending)}")
    
    for idx, acc in enumerate(pending, start=1):
        email = acc["email"]
        profs = acc["profiles"]
        print(f"\n{Colors.GOLD}==========================================")
        print(f"Connecting [{idx}/{len(pending)}]: {email}")
        print(f"=========================================={Colors.RESET}")
        
        ok = connect_oauth_flow_for_account(email, profs)
        if not ok:
            ans = input(f"{Colors.YELLOW}Do you want to continue to next account? (Y/N): {Colors.RESET}").strip().upper()
            if ans != "Y":
                break
                
    print(f"\n{success('Batch connection process completed!')}")

if __name__ == "__main__":
    run_batch_connect()
