import os
import sys
import ctypes

# -------------------------------------------------------------------
# 1. Windows Console Setup: UTF-8 & Virtual Terminal ANSI Colors
# -------------------------------------------------------------------
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

if os.name == 'nt':
    try:
        kernel32 = ctypes.windll.kernel32
        hStdOut = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
        kernel32.SetConsoleMode(hStdOut, mode.value | 0x0004 | 0x0008)
    except Exception:
        pass
    os.system('')

# Ensure repository root is on sys.path and current working directory
APP_DIR = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists(os.path.join(APP_DIR, "campaign_engine")):
    FALLBACK = r"E:\Grace Outreach Assistant"
    if os.path.exists(FALLBACK):
        APP_DIR = FALLBACK

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from campaign_engine.ui_theme import Colors

# -------------------------------------------------------------------
# 2. Interactive Handlers for All 22 Modules
# -------------------------------------------------------------------

def handle_collector():
    from collector.collector import start_collector
    start_collector()
    input(f"\n{Colors.GREEN}Press Enter to return to main menu...{Colors.RESET}")

def handle_cleaner():
    from cleaner.service import run_cleaner
    run_cleaner()
    input(f"\n{Colors.GREEN}Press Enter to return to main menu...{Colors.RESET}")

def handle_campaign_manager():
    from campaign.campaign_manager import start_campaign_manager
    start_campaign_manager()

def handle_spam_checker():
    from spam_checker.spam_checker import start_spam_checker
    start_spam_checker()

def handle_crm():
    from crm.crm import start_crm
    start_crm()

def handle_lead_scoring():
    from crm.scoring import show_scoring
    show_scoring()

def handle_template_analyzer():
    from ai.template_analyzer import analyze_template
    from template_manager.manager import load_templates

    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}AI TEMPLATE ANALYZER{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
  [1] Enter Subject & Body Manually
  [2] Analyze a Saved Template from Database
  [0] Back to Main Menu
""")
        choice = input(f"{Colors.YELLOW}Select: {Colors.RESET}").strip()
        if choice == "1":
            print(f"\n{Colors.CYAN}--- Manual Template Analysis ---{Colors.RESET}")
            subj = input(f"{Colors.YELLOW}Subject: {Colors.RESET}").strip()
            print(f"{Colors.YELLOW}Body (type text and press Enter):{Colors.RESET}")
            body = input("> ").strip()
            if subj or body:
                analyze_template(subj, body)
            else:
                print(f"{Colors.RED}Subject or body cannot be empty.{Colors.RESET}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice == "2":
            templates = load_templates()
            if not templates:
                print(f"\n{Colors.YELLOW}No templates found in database.{Colors.RESET}")
                input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
                continue
            print(f"\n{Colors.CYAN}Available Templates:{Colors.RESET}")
            t_names = list(templates.keys())
            for i, name in enumerate(t_names, 1):
                print(f"  [{i}] {name}")
            sel = input(f"\n{Colors.YELLOW}Select Template (1-{len(t_names)}) or 0: {Colors.RESET}").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(t_names):
                    t = templates[t_names[idx]]
                    analyze_template(t.get("subject", ""), t.get("body", ""))
                else:
                    print(f"{Colors.RED}Invalid selection.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Please enter a number.{Colors.RESET}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice in ("0", ""):
            break

def handle_subject_analyzer():
    from ai.subject_analyzer import analyze_subject

    print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}AI SUBJECT ANALYZER{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
""")
    subj = input(f"{Colors.YELLOW}Enter Subject to analyze (or press Enter to cancel): {Colors.RESET}").strip()
    if subj:
        res = analyze_subject(subj)
        score = res.get("score", 0)
        rating = res.get("rating", "N/A")
        issues = res.get("issues", [])
        
        rating_color = Colors.GREEN if score >= 80 else (Colors.YELLOW if score >= 60 else Colors.RED)
        print(f"\nScore  : {rating_color}{score}/100{Colors.RESET}")
        print(f"Rating : {rating_color}{rating}{Colors.RESET}")
        print("\nIssues:")
        if issues:
            for iss in issues:
                print(f"  • {Colors.RED}{iss}{Colors.RESET}")
        else:
            print(f"  • {Colors.GREEN}None! Perfect Subject Line.{Colors.RESET}")
    input(f"\n{Colors.GREEN}Press Enter to return...{Colors.RESET}")

def handle_template_manager():
    from template_manager.manager import start_template_manager
    start_template_manager()

def handle_reports():
    from reports.report import show_reports
    show_reports()

def handle_activity_logs():
    from logger.activity_logger import show_logs
    show_logs()

def handle_personalized_campaign():
    from crm.crm import start_personalized_campaign
    start_personalized_campaign()
    input(f"\n{Colors.GREEN}Press Enter to return...{Colors.RESET}")

def handle_campaign_progress():
    from reports.campaign_progress import show_campaign_progress
    show_campaign_progress()

def handle_system_settings():
    from settings.campaign_settings import show_campaign_settings, edit_campaign_settings
    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}SYSTEM SETTINGS{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
  [1] View Current Settings
  [2] Edit Campaign Settings (Delays, Quotas)
  [0] Back to Main Menu
""")
        choice = input(f"{Colors.YELLOW}Select: {Colors.RESET}").strip()
        if choice == "1":
            show_campaign_settings()
        elif choice == "2":
            edit_campaign_settings()
        elif choice in ("0", ""):
            break

def handle_gmail_draft_assistant():
    from gmail.queue.queue_manager import show_queue
    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}GMAIL DRAFT ASSISTANT{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
  [1] View Pending Draft Queue
  [2] Create Manual Draft (Gmail OAuth)
  [0] Back to Main Menu
""")
        choice = input(f"{Colors.YELLOW}Select: {Colors.RESET}").strip()
        if choice == "1":
            show_queue()
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice == "2":
            to_email = input(f"{Colors.YELLOW}Recipient Email: {Colors.RESET}").strip()
            subject = input(f"{Colors.YELLOW}Subject: {Colors.RESET}").strip()
            body = input(f"{Colors.YELLOW}Body: {Colors.RESET}").strip()
            if not to_email:
                print(f"{Colors.RED}Recipient email is required.{Colors.RESET}")
                input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
                continue
            try:
                from automation.gmail_draft import create_draft
                res = create_draft(to_email, subject, body)
                print(f"\n{Colors.GREEN}✔ Draft successfully created in Gmail! ID: {res.get('id')}{Colors.RESET}")
            except Exception as e:
                print(f"\n{Colors.RED}✖ Error creating draft: {e}{Colors.RESET}")
                print(f"{Colors.YELLOW}Tip: Ensure Gmail credentials are configured or use Campaign Engine V2.{Colors.RESET}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice in ("0", ""):
            break

def handle_gmail_profile_manager():
    from gmail.profile_manager import start_profile_manager
    start_profile_manager()

def handle_followup_manager():
    from followup.manager import start_followup_manager
    start_followup_manager()

def handle_suppression_manager():
    from suppression.database import create_suppression_table, get_suppression_list, add_to_suppression, remove_from_suppression
    create_suppression_table()

    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}SUPPRESSION & DO-NOT-CONTACT MANAGER{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
  [1] View Suppression List
  [2] Add Email to Suppression
  [3] Remove Email from Suppression
  [0] Back to Main Menu
""")
        choice = input(f"{Colors.YELLOW}Select: {Colors.RESET}").strip()
        if choice == "1":
            rows = get_suppression_list()
            print(f"\n{Colors.CYAN}========== SUPPRESSION LIST ({len(rows)} entries) =========={Colors.RESET}\n")
            if not rows:
                print(f"{Colors.YELLOW}Suppression list is empty.{Colors.RESET}")
            else:
                for idx, r in enumerate(rows, 1):
                    email, reason, added_on = r
                    print(f"  {idx}. {Colors.RED}{email}{Colors.RESET} | Reason: {reason} | Date: {added_on}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice == "2":
            email = input(f"{Colors.YELLOW}Email to Suppress: {Colors.RESET}").strip().lower()
            reason = input(f"{Colors.YELLOW}Reason (e.g. Unsubscribe / Bounce): {Colors.RESET}").strip()
            if email:
                add_to_suppression(email, reason or "Manual Suppression")
                print(f"\n{Colors.GREEN}✔ Added {email} to suppression list.{Colors.RESET}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice == "3":
            email = input(f"{Colors.YELLOW}Email to Remove: {Colors.RESET}").strip().lower()
            if email:
                remove_from_suppression(email)
                print(f"\n{Colors.GREEN}✔ Removed {email} from suppression list.{Colors.RESET}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice in ("0", ""):
            break

def handle_reply_manager():
    from campaign_engine.replies.sync_replies import display_replies_matrix, classify_reply_intent, record_reply_event
    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}INBOUND REPLY MANAGER{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
  [1] View Inbound Replies Dashboard (Live Matrix)
  [2] AI Intent Classifier (Test an incoming email)
  [3] Record / Test an Inbound Reply Event
  [0] Back to Main Menu
""")
        choice = input(f"{Colors.YELLOW}Select: {Colors.RESET}").strip()
        if choice == "1":
            display_replies_matrix()
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice == "2":
            subj = input(f"{Colors.YELLOW}Email Subject: {Colors.RESET}").strip()
            body = input(f"{Colors.YELLOW}Email Body: {Colors.RESET}").strip()
            cat, act = classify_reply_intent(subj, body)
            print(f"\n{Colors.GREEN}Classified Category : {Colors.BOLD}{cat}{Colors.RESET}")
            print(f"{Colors.CYAN}Recommended Action  : {act}{Colors.RESET}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice == "3":
            email = input(f"{Colors.YELLOW}Lead Email: {Colors.RESET}").strip()
            subj = input(f"{Colors.YELLOW}Email Subject: {Colors.RESET}").strip()
            body = input(f"{Colors.YELLOW}Email Body: {Colors.RESET}").strip()
            if email:
                cat, act = record_reply_event(email, subj, body)
                print(f"\n{Colors.GREEN}✔ Recorded reply: {cat} -> {act}{Colors.RESET}")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice in ("0", ""):
            break

def handle_gmail_account_manager():
    from gmail.account_manager.account_manager import start_account_manager
    start_account_manager()

def handle_draft_queue_manager():
    from gmail.queue.queue_manager import show_queue, add_draft_to_queue
    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}DRAFT QUEUE MANAGER{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
  [1] View Draft Queue
  [2] Add Draft to Queue
  [0] Back to Main Menu
""")
        choice = input(f"{Colors.YELLOW}Select: {Colors.RESET}").strip()
        if choice == "1":
            show_queue()
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice == "2":
            email = input(f"{Colors.YELLOW}Recipient Email: {Colors.RESET}").strip()
            name = input(f"{Colors.YELLOW}Recipient Name: {Colors.RESET}").strip()
            company = input(f"{Colors.YELLOW}Company: {Colors.RESET}").strip()
            profile = input(f"{Colors.YELLOW}Gmail Profile Name: {Colors.RESET}").strip()
            subj = input(f"{Colors.YELLOW}Subject: {Colors.RESET}").strip()
            body = input(f"{Colors.YELLOW}Body: {Colors.RESET}").strip()
            if email:
                add_draft_to_queue(email, name, company, profile, subj, body)
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        elif choice in ("0", ""):
            break

def handle_campaign_engine_v2():
    from campaign_engine.campaign_menu import campaign_engine_menu
    campaign_engine_menu()


MODULE_DISPATCHER = {
    "1": ("Email Collector (DB)", handle_collector),
    "2": ("Email Cleaner (DB)", handle_cleaner),
    "3": ("Campaign Manager", handle_campaign_manager),
    "4": ("Spam Checker", handle_spam_checker),
    "5": ("CRM Dashboard", handle_crm),
    "6": ("Lead Scoring", handle_lead_scoring),
    "7": ("AI Template Analyzer", handle_template_analyzer),
    "8": ("Subject Analyzer", handle_subject_analyzer),
    "9": ("Template Manager", handle_template_manager),
    "10": ("Reports", handle_reports),
    "11": ("Activity Logs", handle_activity_logs),
    "12": ("Personalized Campaign", handle_personalized_campaign),
    "13": ("Campaign Progress", handle_campaign_progress),
    "14": ("System Settings", handle_system_settings),
    "15": ("Gmail Draft Assistant", handle_gmail_draft_assistant),
    "16": ("Gmail Profile Manager", handle_gmail_profile_manager),
    "17": ("Follow-up Manager", handle_followup_manager),
    "18": ("Suppression Manager", handle_suppression_manager),
    "19": ("Reply Manager", handle_reply_manager),
    "20": ("Gmail Account Manager", handle_gmail_account_manager),
    "21": ("Draft Queue Manager", handle_draft_queue_manager),
    "22": ("Campaign Engine V2", handle_campaign_engine_v2),
}

# -------------------------------------------------------------------
# 3. Main Master Loop
# -------------------------------------------------------------------

def main():
    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}Grace Outreach Assistant V1.0{Colors.RESET}
                {Colors.DIM}Developed by King Saab{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}

 {Colors.GREEN}[1]{Colors.RESET} Email Collector (DB)
 {Colors.GREEN}[2]{Colors.RESET} Email Cleaner (DB)
 {Colors.CYAN}[3]{Colors.RESET} Campaign Manager
 {Colors.YELLOW}[4]{Colors.RESET} Spam Checker
 {Colors.BLUE}[5]{Colors.RESET} CRM Dashboard
 {Colors.GOLD}[6]{Colors.RESET} Lead Scoring
 {Colors.MAGENTA}[7]{Colors.RESET} AI Template Analyzer
 {Colors.MAGENTA}[8]{Colors.RESET} Subject Analyzer
 {Colors.CYAN}[9]{Colors.RESET} Template Manager
 {Colors.WHITE}[10]{Colors.RESET} Reports
 {Colors.WHITE}[11]{Colors.RESET} Activity Logs
 {Colors.GOLD}[12]{Colors.RESET} Personalized Campaign
 {Colors.CYAN}[13]{Colors.RESET} Campaign Progress
 {Colors.DIM}[14]{Colors.RESET} System Settings
 {Colors.GREEN}[15]{Colors.RESET} Gmail Draft Assistant
 {Colors.BLUE}[16]{Colors.RESET} Gmail Profile Manager
 {Colors.YELLOW}[17]{Colors.RESET} Follow-up Manager
 {Colors.RED}[18]{Colors.RESET} Suppression Manager
 {Colors.GREEN}[19]{Colors.RESET} Reply Manager
 {Colors.BLUE}[20]{Colors.RESET} Gmail Account Manager
 {Colors.GOLD}[21]{Colors.RESET} Draft Queue Manager
 {Colors.CYAN}{Colors.BOLD}[22] Campaign Engine V2{Colors.RESET}
 {Colors.RED}[0] Exit{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
""")
        try:
            choice = input(f"{Colors.YELLOW}Select Option (0-22): {Colors.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.GREEN}Exiting Grace Outreach Assistant. Goodbye!{Colors.RESET}")
            sys.exit(0)

        if choice == "0":
            print(f"\n{Colors.GREEN}Exiting Grace Outreach Assistant. Goodbye King Saab!{Colors.RESET}\n")
            sys.exit(0)
        elif choice in MODULE_DISPATCHER:
            name, handler = MODULE_DISPATCHER[choice]
            try:
                handler()
            except Exception as e:
                print(f"\n{Colors.RED}[Error running {name}]: {e}{Colors.RESET}\n")
                input(f"{Colors.YELLOW}Press Enter to return to main menu...{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}Invalid selection [{choice}]. Please enter a number from 0 to 22.{Colors.RESET}")
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

if __name__ == "__main__":
    main()
