"""
Campaign Automated Scheduler Daemon Worker
Monitors scheduled_campaigns table and triggers campaign_runner automatically.
"""

import time
from datetime import datetime
from config.database import get_connection
from campaign_engine.campaign_runner import run_campaign
from campaign_engine.ui_theme import Colors, print_banner, success, warning, info, error


def _ensure_schedules_table():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scheduled_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                scheduled_time TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def schedule_campaign(campaign_id, scheduled_time_str):
    _ensure_schedules_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO scheduled_campaigns (campaign_id, scheduled_time, status)
            VALUES (?, ?, 'Pending')
            """,
            (campaign_id, scheduled_time_str)
        )
        conn.commit()
        return True
    except Exception as e:
        print(error(f"Failed to schedule campaign: {e}"))
        return False
    finally:
        conn.close()


def get_all_schedules():
    _ensure_schedules_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT s.id, s.campaign_id, c.name, s.scheduled_time, s.status, s.created_at
            FROM scheduled_campaigns s
            LEFT JOIN campaigns c ON s.campaign_id = c.id
            ORDER BY s.id DESC
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


def cancel_scheduled_campaign(schedule_id):
    _ensure_schedules_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE scheduled_campaigns SET status = 'Cancelled' WHERE id = ?",
            (schedule_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_due_schedules():
    _ensure_schedules_table()
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            """
            SELECT id, campaign_id, scheduled_time
            FROM scheduled_campaigns
            WHERE status = 'Pending' AND scheduled_time <= ?
            ORDER BY scheduled_time ASC
            """,
            (now_str,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def mark_schedule_executed(schedule_id):
    _ensure_schedules_table()
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            "UPDATE scheduled_campaigns SET status = 'Executed', executed_at = ? WHERE id = ?",
            (now_str, schedule_id)
        )
        conn.commit()
    finally:
        conn.close()


def run_scheduler_daemon(poll_interval=15):
    """
    Background worker loop that automatically fires campaigns when scheduled time is reached.
    """
    print_banner("CAMPAIGN SCHEDULER DAEMON ACTIVE", "⏰")
    print(f" {Colors.GREEN}● Status        :{Colors.RESET} Running Background Listener")
    print(f" {Colors.CYAN}● Poll Frequency:{Colors.RESET} Checking every {poll_interval}s")
    print(f" {Colors.YELLOW}● Exit          :{Colors.RESET} Press Ctrl + C to return to menu\n")

    try:
        while True:
            due_jobs = get_due_schedules()
            if due_jobs:
                for job in due_jobs:
                    sched_id, camp_id, sched_time = job
                    print(f"\n{Colors.GOLD}⚡ [SCHEDULE TRIGGERED] Schedule #{sched_id} for Campaign #{camp_id} (Due: {sched_time}){Colors.RESET}")
                    mark_schedule_executed(sched_id)
                    run_campaign(camp_id)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print(f"\n{warning('Scheduler daemon stopped by user.')}\n")
