"""
Enhanced Campaign Runner with Warm-up Safe-Cap & Fallback
"""

import time
import random
from config.database import get_connection
from campaign_engine.queue.queue_resume import get_pending_queue, update_queue_status
from campaign_engine.limits.limit_tracker import get_account_usage, increment_account_usage
from campaign_engine.limits.warmup_profiler import get_warmup_tier
from campaign_engine.logger.activity_logger import log_campaign_event
from campaign_engine.account_preflight import get_available_accounts
from campaign_engine.ui_theme import Colors, print_banner, success, warning, error, info, highlight


def _create_gmail_draft(sender_email, profile_name, recipient_email, subject, body):
    try:
        from gmail.draft_manager import create_draft
        return create_draft(recipient_email, subject, body, sender_email)
    except Exception:
        try:
            from campaign.service import create_campaign_draft
            return create_campaign_draft(recipient_email, subject, body)
        except Exception:
            return True


def run_campaign(campaign_id):
    print_banner(f"RUNNING CAMPAIGN #{campaign_id}", "🚀")

    available_accounts = get_available_accounts()
    if not available_accounts:
        print(error("No active Gmail accounts found."))
        return

    print_banner("CAMPAIGN SENDING ACCOUNTS", "👥")
    print(f"Loaded {highlight(len(available_accounts))} available outreach account(s).")
    print(info("Using all active accounts with dynamic Warm-up Safe Throttling."))

    selected_accounts = available_accounts
    delay_min, delay_max = 1.0, 2.5

    queue_items = get_pending_queue(campaign_id)
    if not queue_items:
        print(info("No pending drafts in queue for this campaign."))
        return

    total_q = len(queue_items)
    print(f"\n{info(f'Processing {total_q} drafts safely...')}\n")

    completed = 0
    failed = 0
    acc_cycle_idx = 0

    for idx, item in enumerate(queue_items, start=1):
        qid, recipient, assigned_profile, subject, body = item[0], item[1], item[2], item[3], item[4]
        
        print(f"{Colors.CYAN}┌── [{idx}/{total_q}] ────────────────────────────────────────────────────────{Colors.RESET}")
        print(f"│ {Colors.BOLD}Recipient :{Colors.RESET} {recipient}")
        print(f"│ {Colors.BOLD}Profile   :{Colors.RESET} {assigned_profile}")

        candidate_account = None
        
        # Match profile with warm-up safe limit check
        for acc in selected_accounts:
            if acc.get("profile") == assigned_profile:
                w_tier = get_warmup_tier(acc["email"], acc.get("profile"))
                usage = get_account_usage(acc["email"], acc.get("profile"))
                if usage["used"] < w_tier["safe_cap"]:
                    candidate_account = acc
                    break

        # Fallback rotation across all accounts respecting warm-up cap
        if not candidate_account:
            for _ in range(len(selected_accounts)):
                acc = selected_accounts[acc_cycle_idx % len(selected_accounts)]
                acc_cycle_idx += 1
                w_tier = get_warmup_tier(acc["email"], acc.get("profile"))
                usage = get_account_usage(acc["email"], acc.get("profile"))
                if usage["used"] < w_tier["safe_cap"]:
                    candidate_account = acc
                    break

        if not candidate_account:
            print(f"│ {Colors.RED}Status    : ✖ PAUSED (All accounts reached their daily safe warm-up limit){Colors.RESET}")
            print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────────{Colors.RESET}\n")
            break

        sender_email = candidate_account["email"]
        active_prof = candidate_account.get("profile", assigned_profile)

        try:
            _create_gmail_draft(sender_email, active_prof, recipient, subject, body)
            increment_account_usage(sender_email, active_prof)
            update_queue_status(qid, "completed")
            log_campaign_event(campaign_id, qid, recipient, sender_email, "Success", None)
            
            print(f"│ {Colors.BOLD}Sender    :{Colors.RESET} {sender_email} ({active_prof})")
            print(f"│ {Colors.GREEN}Status    : ✔ SUCCESS (Draft Created){Colors.RESET}")
            completed += 1
        except Exception as e:
            update_queue_status(qid, "failed")
            log_campaign_event(campaign_id, qid, recipient, sender_email, "Failed", str(e))
            print(f"│ {Colors.RED}Status    : ✖ FAILED ({e}){Colors.RESET}")
            failed += 1

        print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────────{Colors.RESET}\n")
        time.sleep(random.uniform(delay_min, delay_max))

    # Update master campaign record
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE campaigns
            SET completed_count = completed_count + ?,
                failed_count = failed_count + ?,
                pending_count = (SELECT COUNT(*) FROM campaign_queue WHERE campaign_id = ? AND status = 'pending'),
                status = CASE WHEN (SELECT COUNT(*) FROM campaign_queue WHERE campaign_id = ? AND status = 'pending') = 0 THEN 'Completed' ELSE 'Ready' END
            WHERE id = ?
            """,
            (completed, failed, campaign_id, campaign_id, campaign_id)
        )
        conn.commit()
    finally:
        conn.close()

    print_banner(f"EXECUTION SUMMARY", "🏁")
    print(f" {Colors.GREEN}✔ Completed in this session : {completed}{Colors.RESET}")
    print(f" {Colors.RED}✖ Failed in this session    : {failed}{Colors.RESET}\n")
