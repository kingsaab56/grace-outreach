"""
Campaign Engine Master Router - Direct Link to Safe Dynamic Pipeline
"""

import sys
import os
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error, highlight
from campaign_engine.campaign_creator import create_and_build_campaign_flow
from campaign_engine.runner import run_campaign_flow
from campaign_engine.progress_dashboard import display_campaign_dashboard
from campaign_engine.account_preflight import display_profile_accounts_categorized
from campaign_engine.limits.limit_tracker import display_account_limits_summary
from campaign_engine.limits.warmup_profiler import display_warmup_summary
from campaign_engine.limits.daily_maintenance import run_daily_maintenance
from campaign_engine.logger.activity_logger import export_campaign_report
from campaign_engine.replies.sync_replies import display_replies_matrix
from campaign_engine.scheduler.scheduler_menu import scheduler_menu
from campaign_engine.oauth_vault.oauth_controller import oauth_vault_manager_menu
from config.database import get_connection


def list_all_campaigns_overview():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, status, total_contacts, completed_count, failed_count, pending_count 
            FROM campaigns 
            ORDER BY id DESC
        """)
        camps = cursor.fetchall()
        print_banner("ALL CAMPAIGNS OVERVIEW", "📋")
        print(f"{'ID':<6} {'Name':<24} {'Status':<16} {'Total':<8} {'Done':<8} {'Fail':<8} {'Pend'}")
        print("─" * 84)
        for c in camps:
            cid, name, stat, tot, comp, fail, pend = c
            print(f"{cid:<6} {name[:22]:<24} {stat:<16} {tot or 0:<8} {comp or 0:<8} {fail or 0:<8} {pend or 0}")
        print("═" * 84)
    finally:
        conn.close()


def campaign_engine_menu():
    while True:
        print_banner("CAMPAIGN ENGINE V2 MASTER MENU", "🚀")
        print(f" {Colors.GREEN}[1]{Colors.RESET}  Create & Build Campaign (With AI Health Scorer)")
        print(f" {Colors.GREEN}[2]{Colors.RESET}  Run / Resume Campaign")
        print(f" {Colors.CYAN}[3]{Colors.RESET}  Campaign Progress Dashboard")
        print(f" {Colors.CYAN}[4]{Colors.RESET}  Campaign Scheduler (Automated Sending)")
        print(f" {Colors.GOLD}[5]{Colors.RESET}  Profile Login Accounts & Health (Categorized)")
        print(f" {Colors.GOLD}[6]{Colors.RESET}  Account Daily Quotas & Limits")
        print(f" {Colors.GOLD}[7]{Colors.RESET}  Account Warm-up & Throttle Matrix")
        print(f" {Colors.BLUE}[8]{Colors.RESET}  View All Campaigns List")
        print(f" {Colors.BLUE}[9]{Colors.RESET}  Export Campaign Audit Report (.TXT)")
        print(f" {Colors.MAGENTA}[10]{Colors.RESET} Inbound Replies & Suppression Hub")
        print(f" {Colors.YELLOW}[11]{Colors.RESET} 🛠️ Run Daily Maintenance & Warm-up Upgrade")
        print(f" {Colors.GREEN}[12]{Colors.RESET} 🔑 OAuth Connect Hub (Profile-Targeted & Vault Locked)")
        print(f" {Colors.RED}[0]{Colors.RESET}  Back to Main Menu")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")

        try:
            choice = input(f"{Colors.YELLOW}Select Option: {Colors.RESET}").strip()
        except KeyboardInterrupt:
            break

        if choice == "0":
            break
        elif choice == "1":
            create_and_build_campaign_flow()
        elif choice == "2":
            list_all_campaigns_overview()
            cid = input(f"\n{Colors.BOLD}Enter Campaign ID to Run/Resume: {Colors.RESET}").strip()
            if cid.isdigit():
                run_campaign_flow(int(cid))
        elif choice == "3":
            cid = input(f"{Colors.BOLD}Enter Campaign ID for Dashboard: {Colors.RESET}").strip()
            if cid.isdigit():
                display_campaign_dashboard(int(cid))
        elif choice == "4":
            scheduler_menu()
        elif choice == "5":
            display_profile_accounts_categorized()
        elif choice == "6":
            display_account_limits_summary()
        elif choice == "7":
            display_warmup_summary()
        elif choice == "8":
            list_all_campaigns_overview()
            input("\nPress Enter to continue...")
        elif choice == "9":
            cid = input(f"{Colors.BOLD}Enter Campaign ID to Export: {Colors.RESET}").strip()
            if cid.isdigit():
                export_campaign_report(int(cid))
        elif choice == "10":
            display_replies_matrix()
        elif choice == "11":
            run_daily_maintenance()
        elif choice == "12":
            oauth_vault_manager_menu()
