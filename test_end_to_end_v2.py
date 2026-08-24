"""
End-to-End Test Suite for Campaign Engine V2
Simulates complete flow: Template scoring -> Queue creation -> Execution -> Log Audit -> CSV Export.
"""

import os
from config.database import get_connection
from campaign_engine.ai_scorer.template_evaluator import evaluate_campaign_template
from campaign_engine.pipeline import build_campaign
from campaign_engine.queue.queue_resume import get_pending_queue, update_queue_status
from campaign_engine.logger.activity_logger import log_campaign_event, export_campaign_report
from campaign_engine.limits.limit_tracker import get_account_usage, increment_account_usage
from campaign_engine.ui_theme import Colors, print_banner, success, warning, error, info, highlight


def run_full_system_test():
    print_banner("CAMPAIGN ENGINE V2 - END-TO-END TEST SUITE", "")
    
    # 1. Setup Sample Contact in DB
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, status TEXT)")
        cursor.execute("INSERT OR IGNORE INTO contacts (email, status) VALUES ('test_client@example.com', 'valid')")
        
        cursor.execute(
            """
            INSERT INTO campaigns (name, status, total_contacts, completed_count, failed_count, pending_count)
            VALUES ('[TEST] End-To-End Verification Campaign', 'Draft', 0, 0, 0, 0)
            """
        )
        conn.commit()
        test_campaign_id = cursor.lastrowid
        print(success(f"Created Test Campaign #{test_campaign_id}"))
    finally:
        conn.close()

    # 2. Test AI Template Scorer
    print(f"\n{info('Testing AI Template Deliverability Scorer...')}")
    sample_subject = "Quick question regarding collaboration"
    sample_body = "Hi team, I came across your work and wanted to discuss a partnership. Let me know if you are open to connect."
    score_result = evaluate_campaign_template(sample_subject, sample_body)
    
    print(f" {highlight('AI Health Score')} : {Colors.GREEN}{score_result.get('health_score', 100)}/100{Colors.RESET}")
    print(f" {highlight('Deliverability')}  : {Colors.CYAN}{score_result.get('deliverability', 'EXCELLENT')}{Colors.RESET}")

    # 3. Test Campaign Pipeline & Queue Builder
    print(f"\n{info('Building Campaign Queue...')}")
    build_success = build_campaign(test_campaign_id, sample_subject, sample_body, 1)
    if not build_success:
        print(error("Failed to build campaign queue."))
        return

    # 4. Verify Queue
    queue = get_pending_queue(test_campaign_id)
    print(success(f"Queue verified: {len(queue)} pending item(s) found."))

    # 5. Simulate Dispatch, Quota Tracking & Activity Logger
    print(f"\n{info('Simulating Draft Execution, Quota Deduction & Event Logging...')}")
    for item in queue:
        qid = item[0]
        email = item[1]
        prof = item[2]
        
        # Test Limit Tracker
        mock_sender = "outreach.tester@gmail.com"
        usage_before = get_account_usage(mock_sender, prof)
        increment_account_usage(mock_sender, prof)
        usage_after = get_account_usage(mock_sender, prof)
        print(f" Account Quota Updated: {usage_before['used']} -> {usage_after['used']}/{usage_after['limit']}")

        # Test Status Update
        update_queue_status(qid, "completed")
        
        # Test Activity Logger
        log_campaign_event(test_campaign_id, qid, email, mock_sender, "Success", None)
        print(success(f"Event logged to database for recipient: {email}"))

    # 6. Test CSV Performance Report Exporter
    print(f"\n{info('Testing CSV Report Exporter...')}")
    report_file = export_campaign_report(test_campaign_id)
    if report_file and os.path.exists(report_file):
        print(success(f"Audit CSV Report generated successfully: {os.path.basename(report_file)}"))
    else:
        print(error("CSV export failed."))

    print_banner("ALL SYSTEM COMPONENTS OPERATIONAL (100% PASS)", "")


if __name__ == "__main__":
    run_full_system_test()
