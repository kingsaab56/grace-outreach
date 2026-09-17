"""
Real-Time Draft & Campaign Engine for Grace Outreach Assistant
Developed for King Saab
"""

import os
from typing import Dict, Any, List, Optional
from config.database import get_connection
from gmail.drafts.draft_manager import create_draft


def get_available_contractor_contacts(
    limit: int = 50,
    state_filter: str = "",
    trade_filter: str = ""
) -> List[Dict[str, Any]]:
    """
    Fetches clean, verified contractor leads ready for outreach,
    optionally filtered by US State (e.g. GA, TX) and Trade (e.g. HVAC, Builders).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        query = "SELECT id, email, name, company, state, contractor_category FROM contacts WHERE status = 'valid'"
        params = []

        if state_filter and state_filter.upper() != "ALL":
            query += " AND UPPER(state) = ?"
            params.append(state_filter.strip().upper())

        if trade_filter and trade_filter != "ALL":
            query += " AND contractor_category LIKE ?"
            params.append(f"%{trade_filter.strip()}%")

        query += " ORDER BY id DESC LIMIT ?"
        params.append(int(limit))

        cur.execute(query, params)
        rows = cur.fetchall()

        contacts = []
        for r in rows:
            contacts.append({
                "id": r[0],
                "email": r[1],
                "name": r[2] or "Contractor",
                "company": r[3] or "Contractor Team",
                "state": r[4] or "US",
                "trade": r[5] or "Custom Home Builders"
            })
        return contacts
    finally:
        conn.close()


def generate_realtime_drafts(
    profile_name: str,
    account_email: str,
    subject_template: str,
    body_template: str,
    limit: int = 20,
    state_filter: str = "",
    trade_filter: str = ""
) -> Dict[str, Any]:
    """
    Generates real-time Gmail drafts for verified contractor contacts.
    Falls back gracefully to draft_queue if OAuth token is in renewal state.
    """
    contacts = get_available_contractor_contacts(limit, state_filter, trade_filter)
    if not contacts:
        return {
            "status": "warning",
            "created": 0,
            "message": "No verified contacts found matching the selected state/trade filter.",
            "drafts": []
        }

    created_drafts = []
    queued_drafts = []

    conn = get_connection()
    cur = conn.cursor()

    try:
        for c in contacts:
            # Personalize subject & body
            sub = subject_template.replace("{name}", c["name"]).replace("{company}", c["company"]).replace("{trade}", c["trade"]).replace("{state}", c["state"])
            body = body_template.replace("{name}", c["name"]).replace("{company}", c["company"]).replace("{trade}", c["trade"]).replace("{state}", c["state"])

            # Attempt live Gmail API draft creation if account given
            live_result = None
            if profile_name and account_email:
                try:
                    live_result = create_draft(
                        profile_name=profile_name,
                        account_email=account_email,
                        to_email=c["email"],
                        subject=sub,
                        body=body
                    )
                except Exception:
                    live_result = None

            # Record in draft_queue
            status_val = "created" if live_result else "queued"
            cur.execute("""
                INSERT INTO draft_queue 
                (contact_email, contact_name, company, profile_name, subject, body, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (c["email"], c["name"], c["company"], profile_name or "Default", sub, body, status_val))

            if live_result:
                created_drafts.append({"email": c["email"], "name": c["name"], "status": "Gmail Draft Created"})
            else:
                queued_drafts.append({"email": c["email"], "name": c["name"], "status": "Queued in Draft Manager"})

        conn.commit()
    finally:
        conn.close()

    total_handled = len(created_drafts) + len(queued_drafts)
    mode_note = f"{len(created_drafts)} synced to Gmail directly, {len(queued_drafts)} stored in Draft Queue" if queued_drafts else f"{len(created_drafts)} Gmail drafts created in real-time"
    return {
        "status": "ok",
        "created": total_handled,
        "gmail_created": len(created_drafts),
        "queued": len(queued_drafts),
        "message": f"Successfully generated {total_handled} contractor drafts! ({mode_note})",
        "drafts": (created_drafts + queued_drafts)[:30]
    }


def create_realtime_campaign(
    name: str,
    subject: str,
    body: str,
    limit: int = 50,
    state_filter: str = "",
    trade_filter: str = ""
) -> Dict[str, Any]:
    """
    Creates a campaign in campaigns table and dynamically builds campaign_queue.
    """
    contacts = get_available_contractor_contacts(limit, state_filter, trade_filter)
    if not contacts:
        return {
            "status": "warning",
            "message": "No verified contacts found for this campaign.",
            "campaign_id": None
        }

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO campaigns 
            (name, subject, body, status, total_contacts, created_at)
            VALUES (?, ?, ?, 'Draft', ?, CURRENT_TIMESTAMP)
        """, (name, subject, body, len(contacts)))
        campaign_id = cur.lastrowid

        for c in contacts:
            c_sub = subject.replace("{name}", c["name"]).replace("{company}", c["company"]).replace("{trade}", c["trade"]).replace("{state}", c["state"])
            c_body = body.replace("{name}", c["name"]).replace("{company}", c["company"]).replace("{trade}", c["trade"]).replace("{state}", c["state"])
            cur.execute("""
                INSERT INTO campaign_queue
                (campaign_id, contact_email, profile_name, subject, body, status, created_at)
                VALUES (?, ?, 'Auto-Rotate', ?, ?, 'queued', CURRENT_TIMESTAMP)
            """, (campaign_id, c["email"], c_sub, c_body))

        conn.commit()
        return {
            "status": "ok",
            "campaign_id": campaign_id,
            "name": name,
            "total_queued": len(contacts),
            "message": f"Campaign #{campaign_id} '{name}' created with {len(contacts)} verified {trade_filter or 'Contractor'} targets!"
        }
    finally:
        conn.close()
