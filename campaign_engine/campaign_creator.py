"""
Hook Builder Pipeline into Campaign Creator
"""

from campaign_engine.ai_scorer.template_evaluator import evaluate_campaign_template
from campaign_engine.builder_pipeline import build_campaign_pipeline, get_contacts_pool_stats
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error
from config.database import get_connection


def create_and_build_campaign_flow():
    total, used, available, _ = get_contacts_pool_stats()
    
    print_banner("CREATE & BUILD CAMPAIGN (AI OPTIMIZED)", "📝")
    print(f" {Colors.CYAN}Total Contacts in DB     :{Colors.RESET} {total}")
    print(f" {Colors.YELLOW}Already Used / Sent      :{Colors.RESET} {used}")
    print(f" {Colors.GREEN}Fresh Contacts Available :{Colors.RESET} {available}\n")

    name = input(f"{Colors.BOLD}Enter Campaign Name: {Colors.RESET}").strip()
    if not name:
        print(error("Campaign Name is required."))
        return

    subject = input(f"{Colors.BOLD}Enter Email Subject: {Colors.RESET}").strip()
    if not subject:
        print(error("Subject is required."))
        return

    print(f"{Colors.BOLD}Enter Email Body (Type END on a new line to finish):{Colors.RESET}")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break
    body = "\n".join(lines).strip()

    if not body:
        print(error("Email Body cannot be empty."))
        return

    # Run AI Template & Health Scorer
    evaluate_campaign_template(subject, body)

    limit_input = input(f"\n{Colors.BOLD}Enter Contact Limit (Available {available}, Press Enter for ALL): {Colors.RESET}").strip()
    limit = int(limit_input) if limit_input.isdigit() else None

    # Insert into campaigns table
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO campaigns (name, subject, body, status, created_at)
        VALUES (?, ?, ?, 'Draft', CURRENT_TIMESTAMP)
    """, (name, subject, body))
    campaign_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"\n{success(f'Created Campaign #{campaign_id}: {name}')}\n")

    # Build queue dynamically
    queued = build_campaign_pipeline(campaign_id, name, subject, body, limit)
    if queued > 0:
        run_now = input(f"{Colors.YELLOW}Do you want to run this campaign now? (Y/N): {Colors.RESET}").strip().upper()
        if run_now == "Y":
            from campaign_engine.runner import run_campaign_flow
            run_campaign_flow(campaign_id)
