"""
Background Campaign Scheduler Worker
Polls scheduled campaigns and triggers execution when due.
"""

import time
from datetime import datetime
from config.database import get_connection
from campaign_engine.scheduler.campaign_scheduler import get_all_schedules, mark_schedule_executed
from campaign_engine.campaign_runner import run_campaign
from campaign_engine.ui_theme import Colors, print_banner, success, info, warning


def run_scheduler_daemon(poll_interval=15):
    """
    Continuous background loop checking for due schedules.
    """
    print_banner("CAMPAIGN SCHEDULER DAEMON ACTIVE", "⏰")
    print(f"{info('Polling database every')} {Colors.BOLD}{poll_interval}s{Colors.RESET} {info('for scheduled jobs.')}")
    print(f"{Colors.DIM}Press Ctrl + C to stop the scheduler daemon.{Colors.RESET}\n")

    try:
        while True:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    """
                    SELECT id, campaign_id, scheduled_time, repeat_interval
                    FROM campaign_schedules
                    WHERE is_active = 1 AND is_executed = 0 AND scheduled_time <= ?
                    ORDER BY scheduled_time ASC
                    """,
                    (now_str,)
                )
                due_jobs = cursor.fetchall()

                for job in due_jobs:
                    sched_id, camp_id, sched_time, repeat = job
                    print(f"\n{success(f'Triggering Scheduled Job #{sched_id}')} -> Campaign #{camp_id} (Due: {sched_time})")
                    
                    # Mark executed first to prevent double runs
                    mark_schedule_executed(sched_id)
                    
                    # Execute campaign
                    run_campaign(camp_id)

            finally:
                conn.close()

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print(f"\n{warning('Scheduler daemon stopped by user.')}")
