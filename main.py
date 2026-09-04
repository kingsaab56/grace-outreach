import os
import json
import copy
import re
import subprocess
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

MODULES_DATA = {
    1: {
        "name": "Dashboard Hub & Real-time Telemetry",
        "category": "Core Analytics",
        "status": "Active",
        "lock": "Secured",
        "desc": "Enterprise real-time dispatch monitoring, response parsing, and velocity tracking.",
    },
    2: {
        "name": "Multi-Tenant Inboxes Manager",
        "category": "Connection Pool",
        "status": "Active (3 Inboxes)",
        "lock": "Secured",
        "desc": "Multi-channel Gmail rotation pool with automated quota preservation.",
    },
    3: {
        "name": "AI Warmup & Deliverability Engine",
        "category": "Reputation",
        "status": "Optimal (98%)",
        "lock": "Automated",
        "desc": "Autonomous peer thread engagement preserving IP and domain reputation.",
    },
    4: {
        "name": "Campaign Studio & Sequence Builder",
        "category": "Outreach",
        "status": "Active",
        "lock": "Armed",
        "desc": "Multi-stage automated outreach pipeline with conditional branching.",
    },
    5: {
        "name": "Spin-Syntax & Variant Generator",
        "category": "Copywriting",
        "status": "Active",
        "lock": "Ready",
        "desc": "Multi-tier dynamic Spintax processor eliminating spam trigger footprint.",
    },
    6: {
        "name": "Contractor Scraper & Enricher",
        "category": "Lead Gen",
        "status": "Standby",
        "lock": "Ready",
        "desc": "High-velocity data extraction and verification engine for verified decision-makers.",
    },
    7: {
        "name": "CRM Revenue Pipeline",
        "category": "Monetization",
        "status": "$64,800 Deal Value",
        "lock": "Active",
        "desc": "Visual deal-stage tracking converting inbound warm leads into revenue.",
    },
    8: {
        "name": "Colleague Management & RBAC",
        "category": "Access Control",
        "status": "Protected",
        "lock": "Restricted",
        "desc": "Granular role-based credential provisioning and access delegation.",
    },
    9: {
        "name": "System Doctor & Diagnostics",
        "category": "Diagnostics",
        "status": "100% Operational",
        "lock": "Monitored",
        "desc": "Automated latency checks, socket diagnostics, and worker thread watchdog.",
    },
    10: {
        "name": "Audio Studio & Broadcast Matrix",
        "category": "Alerts",
        "status": "Audio: ON",
        "lock": "Active",
        "desc": "Synthesized audio feedback triggers for real-time positive outreach classifications.",
    },
    11: {
        "name": "AI Knowledge & Context Agent",
        "category": "Intelligence",
        "status": "Online",
        "lock": "Ready",
        "desc": "Context-aware response classifier matching intent and sentiment scoring.",
    },
    12: {
        "name": "OAuth Token Vault & AES-256 Locker",
        "category": "Security Vault",
        "status": "AES-256 Locked",
        "lock": "Encrypted",
        "desc": "Hardware-level credential isolation with autonomous 24-hour token rotation daemon.",
    },
    13: {
        "name": "Blacklist & Spam Shield",
        "category": "Deliverability",
        "status": "Shield Active",
        "lock": "Secured",
        "desc": "Real-time DNSBL, SURBL, and MX record reputation monitoring.",
    },
    14: {
        "name": "Delivery Rate & Volume Throttler",
        "category": "Scheduler",
        "status": "Pacing Healthy",
        "lock": "Regulated",
        "desc": "Human-like jitter randomization preventing algorithmic mailbox flagging.",
    },
    15: {
        "name": "Domain Authenticator (SPF/DKIM/DMARC)",
        "category": "Compliance",
        "status": "Aligned (100%)",
        "lock": "Verified",
        "desc": "DNS alignment validation ensuring 100% deliverability inbox placement.",
    },
    16: {
        "name": "A/B Multivariate Testing Lab",
        "category": "Optimization",
        "status": "Testing",
        "lock": "Armed",
        "desc": "Split-variant subject and body copy optimization across active pools.",
    },
    17: {
        "name": "Template Forge & Asset Vault",
        "category": "Assets",
        "status": "Synced",
        "lock": "Protected",
        "desc": "Cloud template repository with tokenized personalized merge tags.",
    },
    18: {
        "name": "Bounce & Suppression Sentinel",
        "category": "Hygiene",
        "status": "Zero-Bounce",
        "lock": "Enforced",
        "desc": "Hard bounce suppression list automation maintaining sender score.",
    },
    19: {
        "name": "Compliance & Privacy Guard",
        "category": "Regulatory",
        "status": "CAN-SPAM Compliant",
        "lock": "Active",
        "desc": "Automated one-click opt-out header injection and compliance enforcement.",
    },
    20: {
        "name": "Billing Ledger & ROI Tracker",
        "category": "Accounting",
        "status": "Balanced",
        "lock": "Audited",
        "desc": "Enterprise invoice reconciliation and outreach ROI attribution reporting.",
    },
    21: {
        "name": "Audit Logs & Security Stream",
        "category": "Forensics",
        "status": "Recording",
        "lock": "Tamper-Proof",
        "desc": "Immutable append-only access and dispatch trail with timestamp forensics.",
    },
    22: {
        "name": "Enterprise Sync Engine",
        "category": "Integration",
        "status": "Connected",
        "lock": "Synchronized",
        "desc": "Bi-directional webhook synchronization with central hub and external CRMs.",
    },
}

REFERENCE_MODULE_LABELS = {
    1: ("Dashboard Overview", "Live analytics & telemetry", "◔"),
    2: ("Gmail Multi-Tenant Hub", "OAuth & 3-Tier Categorization", "✉"),
    3: ("AI Warmup Ramp", "Daily sender reputation guard", "♨"),
    4: ("Campaign Studio", "A/B Split + AI Scorer + Timezone", "➤"),
    5: ("Spin-Syntax AI Engine", "1-Click Auto-Spinner & Live Preview", "╱"),
    6: ("US Architect & Contractor Scraper", "All 50 US States + Live Ping & CSV/TXT", "⌕"),
    7: ("CRM Revenue Pipeline", "$64,800 Active deal monitor (Drag & Drop)", "$"),
    8: ("Colleague Access Controller", "Audit Logs, Presets & Force Logout", "♙"),
    9: ("System Doctor Daemon", "Live Gauges, Cache Flush & Telemetry", "♥"),
    10: ("Audio Studio & Extractor", "Soundscape, Visualizer & Alert Chimes", "♫"),
    11: ("Built-in AI Guide Agent", "King Saab AI Copilot & Email Drafter", "▣"),
    12: ("OAuth Token Vault", "AES-256 Locker, Auto-Renew & Backup", "⬟"),
    13: ("Timezone Scheduler", "US Live Clocks & Business Hour Dispatch", "◷"),
    14: ("Bounce Shield", "0.08% Bounce Ping & Queue Sanitizer", "◢"),
    15: ("Auto-Reply Detector", "AI Sentiment Classifier & CRM Push", "↶"),
    16: ("CSV / Excel Exporter", "Multi-Format Reports & Analytics Export", "⇥"),
    17: ("Broadcast Notification Node", "Targeted Recipient & Priority Banners", "⚑"),
    18: ("Brand Palette Studio", "Luxury Theme Presets & Color Picker", "✾"),
    19: ("Cloud Webhook Dispatcher", "Third-party JSON triggers", "⌘"),
    20: ("Daily Quota Guard", "50/50 safe account limits", "◉"),
    21: ("Security Audit Stream", "Immutable access logs & threat signals", "≋"),
    22: ("Enterprise Sync Engine", "Third-party JSON integrations", "⇄"),
}

for _module_id, (_name, _desc, _icon) in REFERENCE_MODULE_LABELS.items():
    MODULES_DATA[_module_id].update(name=_name, desc=_desc, icon=_icon)

PROFILES = {
    "king": {
        "name": "King Saab",
        "role": "Super Admin",
        "software_id": "GRA-ADM-001",
        "status": "Online",
        "initials": "KS",
        "tags": ["Manager", "Admin"],
        "allowed": list(range(1, 23)),
        "metrics": {"pipeline": "2,480", "inboxes": "3 Inboxes", "volume": "1,240", "deal": "$64,800"},
    },
    "abdullah": {
        "name": "Abdullah Khan",
        "role": "Strategic Lead",
        "software_id": "GRA-LEAD-002",
        "status": "Online",
        "initials": "AK",
        "tags": ["Manager", "Strategy"],
        "allowed": [1, 2, 3, 4, 5, 6, 7, 12],
        "metrics": {"pipeline": "1,860", "inboxes": "3 Inboxes", "volume": "920", "deal": "$48,200"},
    },
    "sarah": {
        "name": "Sarah Malik",
        "role": "Growth Marketer",
        "software_id": "GRA-MKT-003",
        "status": "Online",
        "initials": "SM",
        "tags": ["Marketer", "Growth"],
        "allowed": [1, 2, 4, 5, 11, 17, 18],
        "metrics": {"pipeline": "1,120", "inboxes": "2 Inboxes", "volume": "640", "deal": "$18,400"},
    },
    "hamza": {
        "name": "Hamza Ali",
        "role": "Lead Collector",
        "software_id": "GRA-COL-004",
        "status": "Offline",
        "initials": "HA",
        "tags": ["Collector", "Research"],
        "allowed": [1, 2, 6, 7, 13, 16],
        "metrics": {"pipeline": "740", "inboxes": "1 Inbox", "volume": "410", "deal": "$12,600"},
    },
}

MODULE_BLUEPRINTS = {
    1: {"eyebrow": "COMMAND CENTER", "title": "Dispatch velocity command", "metrics": [("Active threads", "2,480", "+14.2%"), ("Response velocity", "18m", "−3m vs target"), ("Telemetry health", "98%", "All nodes green")], "chart": [42, 55, 49, 68, 62, 78, 84, 92], "table_title": "Live dispatch lanes", "rows": [("Inbox #1", "45 messages", "Dispatching"), ("Inbox #2", "31 messages", "Classifying"), ("Inbox #3", "18 messages", "Cooling")], "controls": [("Recalculate telemetry", "Run a fresh node sweep"), ("Pause dispatch lanes", "Safety lock for active work"), ("Open response stream", "Review the latest classifications")]},
    2: {"eyebrow": "CONNECTION POOL", "title": "Gmail inbox orchestration", "metrics": [("Connected inboxes", "3", "Rotation healthy"), ("Quota remaining", "82%", "Safe operating band"), ("Unread priority", "19", "+4 since last sync")], "chart": [76, 62, 81, 58, 74, 69, 88, 82], "table_title": "Tenant rotation lanes", "rows": [("business.inbox1", "OAuth 2.0", "Healthy"), ("outreach.node2", "App password", "Healthy"), ("relay.personal", "App password", "Standby")], "controls": [("Sync all inboxes", "Refresh tenant state across the pool"), ("Rebalance rotation", "Apply quota-aware ordering"), ("Verify OAuth scopes", "Check the active Gmail grants")]},
    3: {"eyebrow": "REPUTATION", "title": "Sender reputation ramp", "metrics": [("Warmup day", "14 / 21", "Ramp on schedule"), ("Domain score", "98%", "+2.4% this week"), ("Peer threads", "126", "Healthy engagement")], "chart": [31, 38, 44, 51, 61, 67, 78, 86], "table_title": "Warmup cohorts", "rows": [("Cohort A", "42 threads", "Engaging"), ("Cohort B", "51 threads", "Queued"), ("Cohort C", "33 threads", "Reviewing")], "controls": [("Advance ramp", "Move the next cohort into warmup"), ("Run reputation check", "Scan sender and domain signals"), ("Adjust daily cap", "Tune the safe engagement ceiling")]},
    4: {"eyebrow": "OUTREACH", "title": "Campaign sequence control", "metrics": [("Active sequences", "18", "4 in experiment"), ("Next dispatch", "09:30", "Timezone aware"), ("AI quality score", "96%", "Above launch threshold")], "chart": [54, 63, 58, 72, 67, 81, 76, 90], "table_title": "Sequence lanes", "rows": [("Northstar launch", "Stage 3 / 5", "Running"), ("Partner pulse", "Stage 1 / 4", "A/B test"), ("Reactivation", "Stage 4 / 4", "Complete")], "controls": [("Create sequence", "Open a new conditional campaign"), ("Run AI score", "Evaluate copy and timing"), ("Pause selected lane", "Hold dispatch without deleting work")]},
    5: {"eyebrow": "COPYWRITING", "title": "Variant generation workbench", "metrics": [("Live variants", "128", "Across 18 sequences"), ("Spam risk", "0.7%", "Below 1% threshold"), ("Best lift", "+21.8%", "Subject line winner")], "chart": [36, 49, 62, 56, 71, 77, 83, 94], "table_title": "Variant experiments", "rows": [("Subject / A", "+21.8%", "Winner"), ("Opening / B", "+12.4%", "Testing"), ("CTA / C", "+8.6%", "Queued")], "controls": [("Generate variants", "Create a fresh safe-copy batch"), ("Preview spinner", "Render tokenized alternatives"), ("Promote winner", "Move the leading variant live")]},
    6: {"eyebrow": "LEAD GEN", "title": "Architect and contractor discovery", "metrics": [("Verified leads", "8,412", "+640 today"), ("States covered", "50 / 50", "National coverage"), ("Live pings", "38", "Awaiting enrichment")], "chart": [48, 52, 61, 66, 74, 69, 82, 89], "table_title": "Enrichment queue", "rows": [("Pacific region", "1,420 leads", "Enriching"), ("Mountain region", "884 leads", "Queued"), ("Northeast region", "1,092 leads", "Verified")], "controls": [("Start state scan", "Scan the next national segment"), ("Enrich live queue", "Verify decision-maker records"), ("Export lead batch", "Prepare a CSV or TXT handoff")]},
    7: {"eyebrow": "MONETIZATION", "title": "Revenue pipeline command", "metrics": [("Open deal value", "$64,800", "+21.4%"), ("Qualified opportunities", "34", "7 added today"), ("Conversion rate", "18.6%", "Above forecast")], "chart": [28, 42, 39, 55, 63, 59, 75, 88], "table_title": "Active deal stages", "rows": [("Discovery", "$18,400", "12 opportunities"), ("Proposal", "$27,600", "14 opportunities"), ("Negotiation", "$18,800", "8 opportunities")], "controls": [("Refresh pipeline", "Pull the latest CRM stages"), ("Score opportunities", "Rank deals by close signal"), ("Export ROI report", "Package the revenue attribution")]},
    8: {"eyebrow": "ACCESS CONTROL", "title": "Colleague access governance", "metrics": [("Managed identities", "4", "Presence monitored"), ("Permission changes", "12", "Last 24 hours"), ("Audit coverage", "100%", "No gaps detected")], "chart": [62, 62, 68, 65, 74, 79, 77, 91], "table_title": "Governance activity", "rows": [("Sarah Malik", "M17 enabled", "Approved"), ("Hamza Ali", "M13 reviewed", "Audited"), ("Abdullah Khan", "View-As session", "Recorded")], "controls": [("Open colleague manager", "Review profiles and RBAC"), ("Apply access preset", "Set a governed permission bundle"), ("Force logout", "End a selected colleague session")]},
    9: {"eyebrow": "DIAGNOSTICS", "title": "System health observatory", "metrics": [("Operational health", "100%", "All probes passing"), ("Median latency", "184ms", "−22ms today"), ("Worker threads", "12 / 12", "No stalled workers")], "chart": [91, 88, 94, 90, 97, 93, 99, 100], "table_title": "System probes", "rows": [("API response", "184ms", "Passing"), ("Queue worker", "42ms", "Passing"), ("Socket bridge", "99.99%", "Passing")], "controls": [("Run full diagnostic", "Probe every operational node"), ("Flush cache", "Clear safe transient state"), ("Open telemetry", "Inspect the latest health samples")]},
    10: {"eyebrow": "ALERTS", "title": "Audio broadcast matrix", "metrics": [("Audio state", "ON", "Chimes armed"), ("Alert channels", "4", "All reachable"), ("Last broadcast", "02m ago", "Acknowledged")], "chart": [44, 57, 51, 66, 61, 73, 69, 84], "table_title": "Alert channel status", "rows": [("Priority chime", "660 / 880Hz", "Armed"), ("Inbox alert", "3 targets", "Ready"), ("Full-screen node", "4 displays", "Ready")], "controls": [("Open soundscape", "Tune ambient tracks and clips"), ("Test alert chime", "Send a safe local test"), ("Open broadcast center", "Target a colleague display")]},
    11: {"eyebrow": "INTELLIGENCE", "title": "Context agent operations", "metrics": [("Intent accuracy", "96.4%", "+1.8%"), ("Classified replies", "1,824", "This week"), ("Guide availability", "24 / 7", "Online now")], "chart": [57, 61, 66, 71, 68, 79, 83, 96], "table_title": "AI signal feed", "rows": [("Positive intent", "62%", "Routing to CRM"), ("Needs follow-up", "24%", "Queued"), ("Not relevant", "14%", "Suppressed")], "controls": [("Open AI Guide", "Start a bilingual workflow session"), ("Run intent scan", "Classify the newest reply batch"), ("Draft follow-up", "Generate a review-ready response")]},
    12: {"eyebrow": "SECURITY VAULT", "title": "OAuth credential lifecycle", "metrics": [("Locker status", "AES-256", "Authenticated"), ("Tokens healthy", "3 / 3", "Auto-renew enabled"), ("Next rotation", "04h 12m", "No failures")], "chart": [98, 98, 99, 99, 100, 100, 100, 100], "table_title": "Vault activity", "rows": [("business.inbox1", "OAuth refresh", "Securely locked"), ("outreach.node2", "App password", "Securely locked"), ("relay.personal", "App password", "Securely locked")], "controls": [("Force vault sync", "Synchronize approved credentials"), ("Export encrypted backup", "Prepare a protected vault archive"), ("Rotate master key", "Re-wrap records with a new key")]},
    13: {"eyebrow": "SCHEDULER", "title": "Timezone dispatch command", "metrics": [("Active timezones", "9", "US business hours"), ("Queued sends", "384", "Jitter applied"), ("Next safe window", "08:00 ET", "In 17 minutes")], "chart": [34, 42, 56, 61, 68, 75, 73, 86], "table_title": "Regional clocks", "rows": [("Eastern", "08:00 – 18:00", "Open"), ("Central", "07:00 – 17:00", "Open"), ("Pacific", "05:00 – 15:00", "Queued")], "controls": [("Refresh live clocks", "Recalculate every dispatch window"), ("Preview schedule", "Review timezone-safe sends"), ("Pause queue", "Hold all timed dispatches")]},
    14: {"eyebrow": "DELIVERABILITY", "title": "Bounce protection shield", "metrics": [("Bounce rate", "0.08%", "−0.02% today"), ("Sanitized queue", "2,480", "No hard bounces"), ("Shield coverage", "100%", "All inboxes protected")], "chart": [88, 91, 89, 94, 96, 95, 98, 99], "table_title": "Suppression signals", "rows": [("Hard bounce", "0.04%", "Blocked"), ("Soft bounce", "0.04%", "Retry limited"), ("Risk domain", "0", "Clear")], "controls": [("Sanitize queue", "Remove risky recipients"), ("Run DNSBL scan", "Check active reputation lists"), ("Export suppressions", "Download the protected list")]},
    15: {"eyebrow": "CLASSIFICATION", "title": "Auto-reply intelligence desk", "metrics": [("Replies scanned", "1,824", "Since last sync"), ("Positive sentiment", "62%", "CRM push armed"), ("Confidence score", "94%", "High confidence")], "chart": [51, 58, 63, 67, 74, 72, 84, 92], "table_title": "Sentiment routing", "rows": [("Positive", "1,131 replies", "CRM push"), ("Neutral", "438 replies", "Needs review"), ("Negative", "255 replies", "Suppressed")], "controls": [("Classify inbox", "Run the sentiment model"), ("Review uncertain", "Open low-confidence replies"), ("Push to CRM", "Send approved classifications")]},
    16: {"eyebrow": "REPORTING", "title": "Multi-format analytics exporter", "metrics": [("Rows available", "18,420", "Across 22 modules"), ("Report freshness", "2m ago", "Current snapshot"), ("Export jobs", "3", "All completed")], "chart": [42, 54, 63, 59, 71, 76, 84, 90], "table_title": "Recent exports", "rows": [("Weekly outreach", "CSV", "Completed"), ("ROI attribution", "Excel", "Completed"), ("Access audit", "TXT", "Ready")], "controls": [("Build CSV report", "Export the current filtered view"), ("Build Excel report", "Package analytics with worksheets"), ("Download audit TXT", "Create a lightweight event export")]},
    17: {"eyebrow": "NOTIFICATIONS", "title": "Broadcast notification node", "metrics": [("Reachable displays", "4 / 4", "Presence confirmed"), ("Priority banners", "2", "Awaiting ack"), ("Delivery latency", "220ms", "Within target")], "chart": [44, 52, 48, 61, 65, 72, 78, 87], "table_title": "Recipient delivery", "rows": [("All colleagues", "4 displays", "Delivered"), ("Sarah Malik", "1 display", "Acknowledged"), ("Hamza Ali", "1 display", "Offline queue")], "controls": [("Compose broadcast", "Target a display or all colleagues"), ("Send test packet", "Verify the notification node"), ("Review acknowledgements", "Check delivery receipts")]},
    18: {"eyebrow": "BRAND SYSTEM", "title": "Palette and typography studio", "metrics": [("Theme presets", "6", "Ready to apply"), ("Typography profiles", "4", "Saved locally"), ("Brand consistency", "100%", "All surfaces aligned")], "chart": [72, 75, 78, 81, 84, 88, 91, 100], "table_title": "Brand tokens", "rows": [("Emerald signature", "#06352B", "Active"), ("Executive gold", "#D6A117", "Primary"), ("Cloud workspace", "#F1F5F9", "Available")], "controls": [("Open brand palette", "Apply a complete theme preset"), ("Tune typography", "Adjust the operating type system"), ("Preview light mode", "Review the accessible surface")]},
    19: {"eyebrow": "INTEGRATION", "title": "Cloud webhook dispatcher", "metrics": [("Connected hooks", "7", "All signatures valid"), ("Delivered today", "4,280", "+12.1%"), ("Retry queue", "3", "Backoff active")], "chart": [65, 59, 72, 68, 77, 82, 79, 94], "table_title": "Webhook endpoints", "rows": [("CRM revenue", "POST /deals", "200 OK"), ("Audit sink", "POST /events", "200 OK"), ("Partner hub", "POST /sync", "Retrying")], "controls": [("Dispatch test JSON", "Send a signed test payload"), ("Replay retry queue", "Reattempt safe failures"), ("Rotate webhook secret", "Refresh endpoint signing")]},
    20: {"eyebrow": "QUOTA SAFETY", "title": "Daily quota guardrail", "metrics": [("Safe accounts", "3 / 3", "Within policy"), ("Used today", "1,240", "50% of safe cap"), ("Blocked sends", "0", "No policy violations")], "chart": [24, 31, 38, 44, 51, 57, 63, 50], "table_title": "Account quota lanes", "rows": [("Inbox #1", "420 / 800", "Safe"), ("Inbox #2", "410 / 800", "Safe"), ("Inbox #3", "410 / 800", "Safe")], "controls": [("Recalculate quota", "Refresh account pacing limits"), ("Open safe-send plan", "Review the next dispatch window"), ("Lock overage", "Enforce the daily ceiling")]},
    21: {"eyebrow": "FORENSICS", "title": "Security audit stream", "metrics": [("Events recorded", "12,842", "Append-only"), ("Threat signals", "0", "No active threats"), ("Retention", "180 days", "Policy compliant")], "chart": [47, 51, 49, 58, 64, 69, 66, 82], "table_title": "Recent audit events", "rows": [("View-As session", "King Saab", "Recorded"), ("RBAC mutation", "M17 enabled", "Recorded"), ("Vault check", "AES-256", "Verified")], "controls": [("Open event stream", "Inspect immutable security events"), ("Run threat scan", "Check recent access signals"), ("Export audit record", "Prepare a signed evidence file")]},
    22: {"eyebrow": "SYNCHRONIZATION", "title": "Enterprise integration bridge", "metrics": [("Connected systems", "7", "Bi-directional"), ("Last sync", "02m ago", "No drift detected"), ("Records aligned", "99.9%", "Within tolerance")], "chart": [57, 63, 61, 71, 68, 79, 83, 95], "table_title": "Sync channels", "rows": [("CRM hub", "4,812 records", "Aligned"), ("Audit sink", "12,842 events", "Aligned"), ("Partner API", "3,204 records", "Monitoring")], "controls": [("Run full sync", "Reconcile all connected systems"), ("Review drift", "Inspect records outside tolerance"), ("Open connector map", "Review the integration topology")]},
}

ATTENDANCE_DAYS = [("mon", "Mon"), ("tue", "Tue"), ("wed", "Wed"), ("thu", "Thu"), ("fri", "Fri"), ("sat", "Sat")]
ATTENDANCE_PEOPLE = [
    ("king", "King Saab", "GRA-ADM-001"),
    ("abdullah", "Abdullah Khan", "GRA-LEAD-002"),
    ("sarah", "Sarah Malik", "GRA-MKT-003"),
    ("hamza", "Hamza Ali", "GRA-COL-004"),
]
ATTENDANCE_DEFAULTS = {
    "king": {"mon": "present", "tue": "present", "wed": "present", "thu": "present", "fri": "present", "sat": "present"},
    "abdullah": {"mon": "present", "tue": "present", "wed": "approved", "thu": "absent", "fri": "present", "sat": "present"},
    "sarah": {"mon": "present", "tue": "received", "wed": "present", "thu": "present", "fri": "absent", "sat": "present"},
    "hamza": {"mon": "absent", "tue": "present", "wed": "present", "thu": "absent", "fri": "present", "sat": "present"},
}
LEAVE_DEFAULTS = {
    "abdullah": {"start": "2026-09-07", "end": "2026-09-08", "state": "approved"},
    "sarah": {"start": "2026-09-12", "end": "2026-09-12", "state": "received"},
}
PROFILE_DEFAULTS = {
    "king": {"name": "King Saab", "role": "Super Admin", "state": "Pakistan", "presence": "Online", "contractorStates": []},
    "abdullah": {"name": "Abdullah Khan", "role": "Strategic Lead", "state": "Pakistan", "presence": "Online", "contractorStates": []},
    "sarah": {"name": "Sarah Malik", "role": "Growth Marketer", "state": "Pakistan", "presence": "Online", "contractorStates": []},
    "hamza": {"name": "Hamza Ali", "role": "Lead Collector", "state": "Pakistan", "presence": "Offline", "contractorStates": ["California", "Texas"]},
}
def _default_notifications():
    now = int(time.time())
    return [
        {
            "id": "n-001",
            "profile": "king",
            "inbox": "business.inbox1",
            "client": "Northstar Build Co.",
            "snippet": "The revised proposal looks good. Can we confirm the launch window?",
            "body": "The revised proposal looks good. Can we confirm the launch window for next week?",
            "category": "work",
            "createdAt": now - 180,
        },
        {
            "id": "n-002",
            "profile": "abdullah",
            "inbox": "outreach.node2",
            "client": "Atlas Contractors",
            "snippet": "Please send the scope notes before our 4 PM review.",
            "body": "Please send the scope notes before our 4 PM review. I have added the decision makers to the thread.",
            "category": "work",
            "createdAt": now - 540,
        },
        {
            "id": "n-003",
            "profile": "sarah",
            "inbox": "relay.personal",
            "client": "Mira Growth Studio",
            "snippet": "We are interested in the campaign test results.",
            "body": "We are interested in the campaign test results. Could you share the winning subject line?",
            "category": "work",
            "createdAt": now - 960,
        },
        {
            "id": "n-004",
            "profile": "hamza",
            "inbox": "business.inbox1",
            "client": "Pioneer Design Group",
            "snippet": "Can you verify the contractor contact list for Texas?",
            "body": "Can you verify the contractor contact list for Texas and flag any duplicate records?",
            "category": "work",
            "createdAt": now - 1560,
        },
        {
            "id": "n-noise",
            "profile": "king",
            "inbox": "relay.personal",
            "client": "Promotion Desk",
            "snippet": "Unsubscribe confirmation and promotional offer.",
            "body": "This automated promotional message is not part of an active outreach workflow.",
            "category": "spam",
            "createdAt": now - 240,
        },
    ]


SEEDED_NOTIFICATION_IDS = {"n-001", "n-002", "n-003", "n-004", "n-noise"}
SHARED_STATE_FILE = Path(__file__).resolve().parent / "data" / "grace_shared_state.json"
SHARED_STATE_LOCK = threading.Lock()


def _default_shared_state():
    return {
        "photos": {},
        "attendance": copy.deepcopy(ATTENDANCE_DEFAULTS),
        "leaves": copy.deepcopy(LEAVE_DEFAULTS),
        "clearedFines": {},
        "profiles": copy.deepcopy(PROFILE_DEFAULTS),
        "notifications": _default_notifications(),
        "gmailInboxes": {
            "business.inbox1": {"profile": "king", "address": "business.inbox1@gmail.com"},
            "outreach.node2": {"profile": "abdullah", "address": "outreach.node2@gmail.com"},
            "relay.personal": {"profile": "sarah", "address": "relay.personal@gmail.com"},
        },
    }


def _read_shared_state_unlocked():
    if not SHARED_STATE_FILE.exists():
        return _default_shared_state()
    try:
        saved = json.loads(SHARED_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("Shared Grace state is unreadable.") from exc
    state = _default_shared_state()
    if not isinstance(saved, dict):
        raise ValueError("Shared Grace state has an invalid shape.")
    for key in state:
        if key not in saved:
            continue
        if key == "notifications" and isinstance(saved[key], list):
            state[key] = saved[key]
        elif isinstance(saved[key], dict):
            state[key].update(saved[key])
    return state


def read_shared_state():
    gmail_sync = sync_gmail_notifications()
    with SHARED_STATE_LOCK:
        state = _read_shared_state_unlocked()
    state["gmailSync"] = gmail_sync
    return state


def _write_shared_state_unlocked(state):
    SHARED_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = SHARED_STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(SHARED_STATE_FILE)


def _validate_shared_update(payload):
    if not isinstance(payload, dict):
        raise ValueError("State update must be a JSON object.")
    resource = payload.get("resource")
    if resource not in {"photos", "attendance", "leaves", "clearedFines", "profiles", "notifications"}:
        raise ValueError("Unknown shared state resource.")
    value = payload.get("value")
    valid_profiles = {person[0] for person in ATTENDANCE_PEOPLE}
    if resource == "photos":
        key = payload.get("key")
        if key not in valid_profiles or not isinstance(value, str) or not value.startswith("data:image/") or len(value) > 3000000:
            raise ValueError("Invalid profile image update.")
        return resource, key, value
    if resource == "profiles":
        key = payload.get("key")
        if key not in valid_profiles or not isinstance(value, dict):
            raise ValueError("Invalid profile settings update.")
        name = value.get("name")
        state = value.get("state")
        presence = value.get("presence")
        contractor_states = value.get("contractorStates", [])
        if not isinstance(name, str) or not 2 <= len(name.strip()) <= 80:
            raise ValueError("Profile name must be between 2 and 80 characters.")
        if not isinstance(state, str) or not 2 <= len(state.strip()) <= 80:
            raise ValueError("Work state must be between 2 and 80 characters.")
        if presence not in {"Online", "Away", "Offline"}:
            raise ValueError("Invalid presence state.")
        if not isinstance(contractor_states, list) or len(contractor_states) > 2 or any(
            not isinstance(item, str) or not item.strip() for item in contractor_states
        ):
            raise ValueError("Contractor coverage is limited to two states.")
        return resource, key, {
            "name": name.strip(),
            "state": state.strip(),
            "presence": presence,
            "contractorStates": contractor_states[:2],
        }
    if resource == "notifications":
        if not isinstance(value, list) or len(value) > 100:
            raise ValueError("Notifications must be a list of at most 100 items.")
        valid_profiles = {person[0] for person in ATTENDANCE_PEOPLE}
        valid_categories = {"work", "system", "spam"}
        for item in value:
            if not isinstance(item, dict) or item.get("profile") not in valid_profiles:
                raise ValueError("Invalid notification profile.")
            if item.get("category") not in valid_categories:
                raise ValueError("Invalid notification category.")
            for field in ("id", "inbox", "client", "snippet", "body"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    raise ValueError("Invalid notification content.")
            if not isinstance(item.get("createdAt"), (int, float)):
                raise ValueError("Invalid notification timestamp.")
        return resource, payload.get("key"), value
    if not isinstance(value, dict):
        raise ValueError("State resource value must be an object.")
    if resource == "attendance":
        valid_days = {day for day, _ in ATTENDANCE_DAYS}
        valid_statuses = {"present", "absent", "received", "approved"}
        for key, days in value.items():
            if key not in valid_profiles or not isinstance(days, dict):
                raise ValueError("Invalid attendance profile.")
            if set(days) - valid_days or any(status not in valid_statuses for status in days.values()):
                raise ValueError("Invalid attendance entry.")
    elif resource == "leaves":
        valid_leave_profiles = {"abdullah", "sarah"}
        for key, leave in value.items():
            if key not in valid_leave_profiles or not isinstance(leave, dict):
                raise ValueError("Invalid leave profile.")
            if leave.get("state") not in {"received", "approved"}:
                raise ValueError("Invalid leave state.")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(leave.get("start", ""))) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(leave.get("end", ""))):
                raise ValueError("Leave dates must use YYYY-MM-DD.")
    else:
        if any(key not in valid_profiles or value[key] is not True for key in value):
            raise ValueError("Invalid fine-clearing update.")
    return resource, payload.get("key"), value


def update_shared_state(payload):
    resource, key, value = _validate_shared_update(payload)
    with SHARED_STATE_LOCK:
        state = _read_shared_state_unlocked()
        if resource == "photos":
            state["photos"][key] = value
        elif resource == "profiles":
            state["profiles"][key].update(value)
        elif resource == "notifications":
            state["notifications"] = value
        elif resource == "attendance":
            for profile, days in value.items():
                state["attendance"][profile] = days
        elif resource == "leaves":
            for profile, leave in value.items():
                state["leaves"][profile] = leave
        else:
            state["clearedFines"] = value
        _write_shared_state_unlocked(state)
        return state


GMAIL_SYNC_SCRIPT = Path(__file__).resolve().parent / "gmail_sync.mjs"
GMAIL_SYNC_LOCK = threading.Lock()
GMAIL_SYNC_CACHE = {"checked_at": 0.0, "messages": [], "account": None}
GMAIL_SYNC_STATUS = {
    "state": "waiting",
    "message": "Gmail sync has not run yet.",
    "added": 0,
    "checkedAt": None,
}
GMAIL_SYNC_INTERVAL_SECONDS = 5


def _gmail_inbox_routes(state):
    routes = state.get("gmailInboxes")
    if not isinstance(routes, dict):
        routes = {}
    return routes


def _message_recipients(message):
    recipients = []
    for field in ("toRecipients", "ccRecipients"):
        value = message.get(field, [])
        if isinstance(value, str):
            recipients.append(value)
        elif isinstance(value, list):
            recipients.extend(str(item) for item in value)
    return " ".join(recipients).lower()


def _route_gmail_message(message, state, account_email):
    routes = _gmail_inbox_routes(state)
    recipient_text = _message_recipients(message)
    for inbox, route in routes.items():
        if not isinstance(route, dict):
            continue
        address = str(route.get("address") or "").strip().lower()
        if address and address in recipient_text:
            profile = route.get("profile")
            if profile in {person[0] for person in ATTENDANCE_PEOPLE}:
                return inbox, profile

    # A Gmail connection represents the authenticated inbox. If its address is
    # not yet configured in the shared routing table, use the primary inbox
    # rather than dropping an otherwise valid client message.
    primary = next(iter(routes.items()), ("business.inbox1", {"profile": "king"}))
    profile = primary[1].get("profile", "king") if isinstance(primary[1], dict) else "king"
    return primary[0], profile


def _is_work_gmail_message(message):
    labels = {str(label).upper() for label in message.get("labelIds", []) if label}
    if labels.intersection({"SPAM", "TRASH", "CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL", "CATEGORY_FORUMS"}):
        return False
    sender = str(message.get("sender") or "").lower()
    subject = str(message.get("subject") or "").lower()
    snippet = str(message.get("snippet") or "").lower()
    noise_terms = (
        "unsubscribe",
        "newsletter",
        "promotional offer",
        "limited time offer",
        "sale ends",
        "marketing list",
        "this week's issue",
        "view this email in your browser",
        "new properties",
        "here's a summary",
    )
    if any(term in f"{sender} {subject} {snippet}" for term in noise_terms):
        return False
    if re.search(r"\b(?:no[-_.]?reply|notifications?|mailer[-_.]?daemon|newsletter|digest|updates)@", sender):
        return False
    if re.search(r"\bnews(?:letter)?[.@_-]", sender):
        return False
    return bool(sender or subject or snippet)


def _normalize_gmail_notification(message, state, account_email):
    if not isinstance(message, dict) or not _is_work_gmail_message(message):
        return None
    message_id = str(message.get("id") or "").strip()
    if not message_id:
        return None
    inbox, profile = _route_gmail_message(message, state, account_email)
    sender = str(message.get("sender") or "").strip()
    subject = str(message.get("subject") or "").strip()
    snippet = re.sub(r"\s+", " ", str(message.get("snippet") or "").strip())
    client = sender or "Gmail client"
    sender_match = re.match(r"^(.*?)\s*<[^>]+>$", sender)
    if sender_match and sender_match.group(1).strip():
        client = sender_match.group(1).strip().strip('"')
    display_snippet = f"{subject} · {snippet}" if subject and snippet else subject or snippet or "New client message"
    raw_date = str(message.get("date") or "").strip()
    try:
        created_at = int(float(message.get("createdAt") or 0))
    except (TypeError, ValueError):
        created_at = 0
    if created_at <= 0:
        created_at = int(time.time())
    return {
        "id": f"gmail-{message_id}",
        "profile": profile,
        "inbox": inbox,
        "client": client[:160],
        "snippet": display_snippet[:500],
        "body": (snippet or display_snippet)[:4000],
        "category": "work",
        "createdAt": created_at,
        "source": "gmail",
        "subject": subject[:300],
        "sender": sender[:300],
        "threadId": str(message.get("threadId") or ""),
        "receivedAt": raw_date[:80],
    }


def _run_gmail_sync():
    if not GMAIL_SYNC_SCRIPT.exists():
        raise RuntimeError("Gmail sync helper is missing.")
    completed = subprocess.run(
        ["node", str(GMAIL_SYNC_SCRIPT)],
        cwd=str(GMAIL_SYNC_SCRIPT.parent),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
        env=os.environ.copy(),
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "Unknown Gmail connector error.").strip()
        raise RuntimeError(detail[-600:])
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gmail connector returned invalid JSON.") from exc
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise RuntimeError(str((payload or {}).get("error") or "Gmail connector returned an unexpected response."))
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise RuntimeError("Gmail connector response did not include a message list.")
    return payload


def sync_gmail_notifications(force=False):
    now = time.time()
    if not force and now - GMAIL_SYNC_CACHE["checked_at"] < GMAIL_SYNC_INTERVAL_SECONDS:
        return copy.deepcopy(GMAIL_SYNC_STATUS)
    with GMAIL_SYNC_LOCK:
        now = time.time()
        if not force and now - GMAIL_SYNC_CACHE["checked_at"] < GMAIL_SYNC_INTERVAL_SECONDS:
            return copy.deepcopy(GMAIL_SYNC_STATUS)
        try:
            payload = _run_gmail_sync()
            with SHARED_STATE_LOCK:
                state = _read_shared_state_unlocked()
                existing = {
                    item.get("id"): item
                    for item in state["notifications"]
                    if isinstance(item, dict) and item.get("id") not in SEEDED_NOTIFICATION_IDS
                }
                added = 0
                current_gmail_ids = set()
                for message in payload["messages"]:
                    item = _normalize_gmail_notification(message, state, payload.get("account"))
                    if not item:
                        continue
                    current_gmail_ids.add(item["id"])
                    if item["id"] not in existing:
                        added += 1
                    existing[item["id"]] = item
                existing = {
                    item_id: item
                    for item_id, item in existing.items()
                    if item.get("source") != "gmail" or item_id in current_gmail_ids
                }
                merged = sorted(
                    existing.values(),
                    key=lambda item: float(item.get("createdAt") or 0),
                    reverse=True,
                )[:100]
                if merged != state["notifications"]:
                    state["notifications"] = merged
                    _write_shared_state_unlocked(state)
            GMAIL_SYNC_CACHE.update(
                checked_at=now,
                messages=payload["messages"],
                account=payload.get("account"),
            )
            GMAIL_SYNC_STATUS.update(
                state="connected",
                message="Gmail inbox synced.",
                added=added,
                checkedAt=int(now),
            )
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            GMAIL_SYNC_CACHE["checked_at"] = now
            GMAIL_SYNC_STATUS.update(
                state="error",
                message=f"Gmail sync failed: {str(exc)[:300]}",
                added=0,
                checkedAt=int(now),
            )
    return copy.deepcopy(GMAIL_SYNC_STATUS)

def _json_response(start_response, payload, status="200 OK"):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(data))),
            ("Cache-Control", "no-store"),
        ],
    )
    return [data]


LOGO_SVG = """<svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle; margin-right:8px;">
    <rect width="24" height="24" rx="6" fill="#10B981" fill-opacity="0.18"/>
    <path d="M12 3L3 7.5L12 12L21 7.5L12 3Z" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M3 12L12 16.5L21 12" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M3 16.5L12 21L21 16.5" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

LOGO_ASSET = Path(__file__).resolve().parents[2] / "attached_assets" / "Gemini_G_1788371414587.jfif"
ROBOT_ASSET = Path(__file__).resolve().parents[2] / "attached_assets" / "image_1788462208298.png"
ROBOT_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#a8c4c0"/></linearGradient></defs>
<rect width="160" height="160" rx="36" fill="#001713"/><circle cx="80" cy="18" r="7" fill="#d6a117"/>
<path d="M80 25v12" stroke="#d6a117" stroke-width="4"/><rect x="34" y="38" width="92" height="60" rx="22" fill="url(#g)"/>
<rect x="48" y="51" width="64" height="34" rx="12" fill="#08231f"/><circle cx="67" cy="68" r="6" fill="#8ffff0"/><circle cx="93" cy="68" r="6" fill="#8ffff0"/>
<rect x="52" y="102" width="56" height="32" rx="12" fill="url(#g)"/><path d="M45 108l-12 20M115 108l12 20" stroke="#dce7e5" stroke-width="8" stroke-linecap="round"/></svg>"""
FAVICON_DATA_URI = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='8' fill='%230B1120'/%3E"
    "%3Cpath d='M16 4L4 10L16 16L28 10L16 4Z' fill='none' stroke='%2310B981' stroke-width='2.5' stroke-linejoin='round'/%3E"
    "%3Cpath d='M4 14L16 20L28 14M4 20L16 26L28 20' fill='none' stroke='%2310B981' stroke-width='2.5' stroke-linejoin='round'/%3E"
    "%3C/svg%3E"
)


def render_header():
    return f"""
    <div class="card top-bar">
        <div style="display:flex; align-items:center;">
            <img src="/assets/grace-logo.jfif" class="brand-image" alt="Grace Outreach logo">
            <div>
                <h2 style="margin:0; font-size: 17px; font-weight:800; letter-spacing:0.5px;">GRACE OUTREACH ASSISTANT</h2>
                <span style="font-size: 12px; color: var(--text-muted);">Built by King Saab | Strategic Guidance by Abdullah Khan</span>
                <div class="active-profile-chip" id="active-profile-chip"><i class="presence-dot online"></i><span>Active workspace · <span id="active-profile-crown" class="verified-crown" title="Verified Super Admin">👑</span><b id="active-profile-name">King Saab · Super Admin</b></span></div>
            </div>
        </div>
        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
            <span class="btn btn-gray profile-session-badge"><span id="session-crown" class="verified-crown" title="Verified Super Admin">👑</span> <span id="active-profile-badge">King Saab · Super Admin</span></span>
            <button id="notification-button" class="btn btn-gray" onclick="openNotifications()" aria-haspopup="dialog" aria-controls="notification-panel">🔔 Notifications <b id="notification-count">4</b></button>
            <button class="btn btn-orange" onclick="openBroadcast()">📢 Broadcast Alert</button>
            <button class="btn btn-gray" onclick="openBrandPalette()">🎨 Brand Palette</button>
            <button id="audio-btn" class="btn btn-gray" onclick="toggleAudio()">🔊 Audio: ON</button>
            <button class="btn btn-gray" onclick="openSoundscape()">♫ Soundscape</button>
            <button id="theme-btn" class="btn btn-gray" onclick="toggleTheme()">🌓 Theme: DARK</button>
            <button class="btn btn-red" onclick="powerOff()">⏹ Power Off</button>
        </div>
    </div>
    <div id="toast-region" class="toast-region" aria-live="polite" aria-atomic="true"></div>
    <div id="action-dialog" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="dialog-title">
        <div class="modal-card dialog-card">
            <div class="modal-header"><h3 id="dialog-title">Confirm action</h3><button class="modal-close" onclick="closeActionDialog()" aria-label="Close confirmation dialog">×</button></div>
            <p id="dialog-message" class="modal-copy"></p>
            <div class="dialog-actions">
                <button class="btn btn-gray" onclick="closeActionDialog()">Cancel</button>
                <button id="dialog-confirm" class="btn btn-red" onclick="completeActionDialog()">Confirm</button>
            </div>
        </div>
    </div>
    <div id="brand-palette-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="palette-title">
        <div class="modal-card">
            <div class="modal-header"><h3 id="palette-title">Grace brand palette</h3><button class="modal-close" onclick="closeBrandPalette()" aria-label="Close brand palette">×</button></div>
            <p class="modal-copy">Instantly restyle the entire command center and tune typography for your operating style.</p>
            <span class="eyebrow">COLOR THEMES</span>
            <div class="palette-grid">
                <button class="palette-option" onclick="applyTheme('midnight')" style="--swatch:#0B1120"><i></i><b>Midnight</b><small>Executive dark</small></button>
                <button class="palette-option" onclick="applyTheme('emerald')" style="--swatch:#06352B"><i></i><b>Emerald</b><small>Grace signature</small></button>
                <button class="palette-option" onclick="applyTheme('royal')" style="--swatch:#16204A"><i></i><b>Royal Signal</b><small>High contrast</small></button>
                <button class="palette-option" onclick="applyTheme('sandstone')" style="--swatch:#3B2A1A"><i></i><b>Sandstone</b><small>Warm command</small></button>
                <button class="palette-option" onclick="applyTheme('slate')" style="--swatch:#1E293B"><i></i><b>Slate</b><small>Neutral ops</small></button>
                <button class="palette-option" onclick="applyTheme('cloud')" style="--swatch:#F1F5F9"><i></i><b>Cloud</b><small>Light workspace</small></button>
            </div>
            <span class="eyebrow palette-type-label">SURFACE COLOR CONTROLS</span>
            <div class="color-control-grid">
                <label>Ribbon / navbar<input id="nav-color-picker" type="color" value="#00110F" onchange="applyCustomColors()"><small>Top bar and command ribbon</small></label>
                <label>App background<input id="background-color-picker" type="color" value="#0B1120" onchange="applyCustomColors()"><small>Workspace canvas background</small></label>
            </div>
            <span class="eyebrow palette-type-label">TYPOGRAPHY CUSTOMIZER</span>
            <div class="typography-grid">
                <label>Web-safe font<select id="font-family" onchange="applyTypography()"><option value="system">System UI</option><option value="Arial">Arial</option><option value="Verdana">Verdana</option><option value="Tahoma">Tahoma</option><option value="Trebuchet MS">Trebuchet MS</option><option value="Georgia">Georgia</option><option value="Garamond">Garamond</option><option value="Courier New">Courier New</option><option value="Times New Roman">Times New Roman</option><option value="Segoe UI">Segoe UI</option><option value="Helvetica">Helvetica</option><option value="Impact">Impact</option></select></label>
                <label>Weight<select id="font-weight" onchange="applyTypography()"><option value="400">Regular</option><option value="500">Medium</option><option value="600" selected>Semibold</option><option value="700">Bold</option></select></label>
                <label>Tracking<select id="font-tracking" onchange="applyTypography()"><option value="0">Normal</option><option value="0.02em">Open</option><option value="0.06em">Wide</option></select></label>
                <label class="check-control"><input id="font-italic" type="checkbox" onchange="applyTypography()"> Italic UI</label>
            </div>
            <button class="btn btn-blue modal-action" onclick="closeBrandPalette()">Apply &amp; close</button>
        </div>
    </div>
    <div id="soundscape-panel" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="soundscape-title">
        <div class="modal-card wide-modal">
            <div class="modal-header"><h3 id="soundscape-title">Audio &amp; Background Soundscape Engine</h3><button class="modal-close" onclick="closeSoundscape()" aria-label="Close soundscape">×</button></div>
            <p class="modal-copy">Choose an ambient operating track or load a local audio/video file. Clip points apply to the active media session.</p>
            <div class="soundscape-options">
                <button class="soundscape-option active" data-track="focus" onclick="selectSoundscape('focus')"><b>Calm Focus</b><small>Soft executive pulse</small></button>
                <button class="soundscape-option" data-track="pulse" onclick="selectSoundscape('pulse')"><b>Emerald Pulse</b><small>High-velocity operations</small></button>
                <button class="soundscape-option" data-track="strategy" onclick="selectSoundscape('strategy')"><b>Strategic Flow</b><small>Measured planning ambience</small></button>
                <button class="soundscape-option" data-track="night" onclick="selectSoundscape('night')"><b>Night Shift</b><small>Low-light focus mode</small></button>
            </div>
            <div class="audio-player-shell">
                <div><span class="eyebrow">ACTIVE SOUNDscape</span><strong id="soundscape-status">Calm Focus · Ready</strong></div>
                <div class="audio-controls"><button class="btn btn-blue" onclick="toggleSoundscape()">▶ Start / Pause</button><span id="soundscape-time">00:00 / 00:00</span></div>
            </div>
            <label class="upload-zone"><span>＋ Load custom audio or video</span><small>Audio/video files are previewed locally; video soundtracks are routed through the same clip controls.</small><input id="custom-media-input" type="file" accept="audio/*,video/*" onchange="loadCustomMedia(event)"></label>
            <div class="clip-grid">
                <label>Start (seconds)<input id="clip-start" type="number" min="0" step="1" value="0"></label>
                <label>End (seconds)<input id="clip-end" type="number" min="0" step="1" placeholder="Track end"></label>
                <button class="btn btn-gray" onclick="applyClip()">Apply Clip</button>
            </div>
            <audio id="custom-media" controls hidden></audio>
        </div>
    </div>
    <div id="broadcast-panel" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="broadcast-title">
        <div class="modal-card wide-modal">
            <div class="modal-header"><h3 id="broadcast-title">Targeted Broadcast Center</h3><button class="modal-close" onclick="closeBroadcast()" aria-label="Close broadcast center">×</button></div>
            <p class="modal-copy">Send a targeted operational notice with optional chime and full-screen attention mode.</p>
            <div class="form-grid">
                <label>Target displays<select id="broadcast-target"><option value="all">All colleagues · 4 displays</option><option value="abdullah">Abdullah Khan · GRA-LEAD-002</option><option value="sarah">Sarah Malik · GRA-MKT-003</option><option value="hamza">Hamza Ali · GRA-COL-004</option></select></label>
                <label>Alert message<textarea id="broadcast-message" rows="3">Priority outreach window opens in 15 minutes.</textarea></label>
            </div>
            <div class="toggle-row"><label><input id="broadcast-chime" type="checkbox" checked> Play attention chime</label><label><input id="broadcast-fullscreen" type="checkbox"> Full-screen target modal</label></div>
            <div class="dialog-actions"><button class="btn btn-gray" onclick="closeBroadcast()">Cancel</button><button class="btn btn-orange" onclick="sendBroadcast()">Send targeted broadcast</button></div>
        </div>
    </div>
    <div id="broadcast-overlay" class="broadcast-overlay" hidden>
        <div class="broadcast-overlay-card"><span class="eyebrow">INCOMING PRIORITY BROADCAST</span><h2 id="broadcast-overlay-title">Grace Operations Notice</h2><p id="broadcast-overlay-message"></p><small id="broadcast-overlay-target"></small><button class="btn btn-orange" onclick="closeBroadcastOverlay()">Acknowledge notice</button></div>
    </div>
    <div id="notification-panel" class="modal-backdrop notification-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="notification-title">
        <div class="modal-card notification-modal">
            <div class="modal-header"><div><span class="eyebrow">LIVE INBOX SIGNALS</span><h3 id="notification-title">Multi-profile notification center</h3><small class="notification-sync-status" id="notification-sync-status">Shared state · syncing</small></div><button class="modal-close" onclick="closeNotifications()" aria-label="Close notification center">×</button></div>
            <div class="notification-toolbar">
                <label class="check-control"><input id="notification-auto-read" type="checkbox" checked onchange="toggleNotificationAutoRead()"> Auto-read non-work / spam</label>
                <label>Chime<select id="notification-chime" onchange="saveNotificationAudioSettings()"><option value="soft">Soft double ping</option><option value="bright">Bright signal</option><option value="urgent">Urgent pulse</option><option value="silent">Silent</option></select></label>
                <label>Volume<input id="notification-volume" type="range" min="0" max="100" value="35" oninput="saveNotificationAudioSettings(false)"></label>
                <button class="btn btn-gray" onclick="testNotificationChime()">Test chime</button>
            </div>
            <div class="notification-filters" id="notification-filters" role="tablist" aria-label="Filter notifications by profile"></div>
            <div id="notification-preview" class="notification-inline-preview" hidden></div>
            <div id="notification-list" class="notification-list" aria-live="polite"></div>
        </div>
    </div>
    <div id="ai-mascot" class="ai-mascot" onclick="toggleAIAssistant()" role="button" tabindex="0" aria-label="Open Grace AI Guide" onkeydown="if(event.key==='Enter' || event.key===' ') toggleAIAssistant()">
        <img class="robot-uploaded" src="/assets/grace-ai-robot.png" alt="Grace AI Guide robot"><span class="ai-ping"></span>
    </div>
    <aside id="ai-assistant" class="ai-drawer" aria-label="Grace AI Guide" aria-hidden="true">
        <div class="ai-drawer-head"><div><span class="eyebrow">MODULE 11 · ONLINE</span><h3>Grace AI Guide</h3><small style="display:block;color:var(--text-muted);margin-top:4px;">Drag the robot anywhere · workflow copilot</small></div><div style="display:grid;grid-template-columns:1fr auto;gap:6px;align-items:start;"><select id="ai-language" aria-label="Guide language" onchange="setAILanguage(this.value)"><option value="ur">Urdu · اردو</option><option value="en">English</option></select><select id="ai-voice" aria-label="AI guide voice" onchange="setAIVoice(this.value)"></select><button class="modal-close" onclick="closeAIAssistant()" aria-label="Close AI Guide">×</button></div></div>
        <div id="ai-messages" class="ai-messages">
            <div class="ai-response-block"><div class="ai-bubble ai-bubble-bot">خوش آمدید۔ نیچے سے کوئی module منتخب کریں، میں آپ کو پورا workflow قدم بہ قدم اردو میں سمجھاؤں گا۔ ہر module کا runbook یہاں موجود ہے۔</div><button class="ai-response-audio" onclick="speakText(this.previousElementSibling.innerText, this)">🔊 جواب سنیں</button></div>
        </div>
        <div class="ai-library-head"><span class="eyebrow">22-MODULE WORKFLOW LIBRARY</span><small>Choose any module for a guided runbook</small></div>
        <div id="ai-workflow-library" class="ai-workflow-library"></div>
        <div class="ai-suggestions"><button onclick="askAI('How do I use Module 12?', 12)">Module 12 walkthrough</button><button onclick="askAI('Show restricted modules')">Explain access</button></div>
        <div class="ai-compose"><input id="ai-input" placeholder="اردو میں سوال پوچھیں..." onkeydown="if(event.key==='Enter') sendAIMessage()"><button class="btn btn-blue" onclick="sendAIMessage()">Send</button></div>
        <button class="tts-button" onclick="speakGuide()">🔊 مکمل اردو رہنمائی سنیں</button>
    </aside>
    """


def render_navigation(active_tab):
    d_active = "btn-blue" if active_tab == "dashboard" else "btn-gray"
    m_active = "btn-blue" if active_tab == "matrix" else "btn-gray"
    c_active = "btn-blue" if active_tab == "colleagues" else "btn-gray"
    return f"""
    <div class="card" style="padding:10px 16px;">
        <div style="display:flex; gap:10px;">
            <a href="/?tab=dashboard" class="btn {d_active}">1. Dashboard Overview</a>
            <a href="/?tab=matrix" class="btn {m_active}">2. 22-Module Control Matrix</a>
            <a href="/?tab=colleagues" class="btn {c_active}">3. Colleague Management</a>
        </div>
    </div>
    <div class="view-as-bar">
        <div><span class="eyebrow">SUPER ADMIN VIEW-AS</span><strong>Preview colleague workspace instantly</strong><small id="active-scope-count">All 22 modules enabled</small></div>
        <div class="view-as-controls"><span id="view-as-label">King Saab · Super Admin</span><select id="view-as-picker" aria-label="Active profile workspace" onchange="changeViewAs(this.value)"><option value="king">King Saab · Super Admin · All 22</option><option value="abdullah">Abdullah Khan · Strategic Lead · 8 modules</option><option value="sarah">Sarah Malik · Marketer · 7 modules</option><option value="hamza">Hamza Ali · Collector · 6 modules</option></select></div>
    </div>
    """


BASE_CSS = """
    :root {
        --bg-main: #F1F5F9;
        --bg-card: #FFFFFF;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --border-color: #CBD5E1;
        --accent-blue: #0284C7;
        --accent-green: #10B981;
        --accent-orange: #EA580C;
        --accent-red: #EF4444;
        --accent-gold: #D97706;
    }
    body.dark {
        --bg-main: #0B1120;
        --bg-card: #001A17;
        --text-main: #F8FAFC;
        --text-muted: #9BB0AD;
        --border-color: #123B35;
        --accent-blue: #D6A117;
        --accent-green: #10B981;
        --accent-orange: #F59E0B;
        --accent-gold: #D6A117;
    }
    body { background-color: var(--bg-main); color: var(--text-main); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; }
    body.dark { background-image: radial-gradient(circle at 50% -20%, rgba(16, 185, 129, .08), transparent 38rem); }
    .card { background: var(--bg-card); padding: 18px 24px; border-radius: 14px; border: 1px solid var(--border-color); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .brand-image { width: 40px; height: 40px; object-fit: cover; border-radius: 10px; margin-right: 10px; border: 1px solid rgba(214, 161, 23, .75); box-shadow: 0 0 0 2px rgba(16, 185, 129, .2); }
    .top-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
    .view-as-bar { display:flex; justify-content:space-between; align-items:center; gap:16px; margin:-8px 0 20px; padding:12px 16px; border:1px solid var(--accent-gold); border-radius:11px; background:linear-gradient(100deg,rgba(16,185,129,.1),rgba(214,161,23,.06)); box-shadow:0 8px 24px rgba(0,0,0,.08); }
    .view-as-bar { background:linear-gradient(120deg,rgba(0,27,23,.92),rgba(5,52,43,.78)); backdrop-filter:blur(16px); box-shadow:0 16px 34px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.04); }
    body:not(.dark) .view-as-bar { background:linear-gradient(120deg,rgba(255,255,255,.82),rgba(226,247,239,.78)); }
    .view-as-bar strong { display:block; margin-top:4px; font-size:12px; }
    .view-as-bar small { display:block; margin-top:5px; color:var(--text-muted); font-size:10px; }
    .view-as-controls { display:flex; align-items:center; gap:10px; color:var(--accent-green); font-size:11px; font-weight:700; }
    .view-as-controls select { width:auto; min-width:280px; padding:8px 10px; }
    .active-profile-chip { display:flex; align-items:center; gap:6px; margin-top:8px; color:var(--accent-green); font-size:10px; font-weight:700; }
    .active-profile-chip b { color:var(--text-main); }
    .profile-session-badge { border-color:var(--accent-gold) !important; }
    .verified-crown { display:inline-block; color:#F6C453; filter:drop-shadow(0 0 5px rgba(246,196,83,.35)); font-size:13px; line-height:1; vertical-align:middle; }
    .notification-backdrop { align-items:start; justify-items:end; padding:78px 24px 24px; background:rgba(2,6,23,.48); }
    .notification-modal { width:min(920px, calc(100vw - 34px)); max-height:min(790px, calc(100vh - 102px)); overflow:hidden; padding:20px; background:linear-gradient(145deg,rgba(0,26,23,.98),rgba(4,43,36,.97)); border-color:rgba(214,161,23,.7); }
    .notification-modal .modal-header { padding-bottom:14px; border-bottom:1px solid rgba(148,163,184,.16); }
    .notification-modal .modal-header h3 { margin-top:4px; color:var(--text-main); }
    .notification-sync-status { display:block; margin-top:5px; color:var(--accent-green); font-size:10px; }
    .notification-toolbar { display:grid; grid-template-columns:1.4fr .9fr 1fr auto; gap:10px; align-items:end; padding:14px 0; }
    .notification-toolbar label { display:grid; gap:5px; color:var(--text-muted); font-size:10px; font-weight:700; }
    .notification-toolbar .check-control { display:flex; align-items:center; gap:7px; align-self:center; color:var(--text-main); }
    .notification-toolbar input[type="range"] { width:100%; accent-color:var(--accent-gold); }
    .notification-filters { display:flex; flex-wrap:wrap; gap:7px; padding:0 0 13px; }
    .notification-filter { border:1px solid var(--border-color); border-radius:999px; padding:7px 10px; color:var(--text-muted); background:rgba(0,0,0,.13); cursor:pointer; font-size:10px; font-weight:800; }
    .notification-filter.is-active { color:#061510; background:var(--accent-gold); border-color:var(--accent-gold); }
    .notification-inline-preview { margin:0 0 12px; padding:12px 14px; border-left:3px solid var(--accent-green); border-radius:9px; background:rgba(16,185,129,.08); color:var(--text-main); font-size:11px; line-height:1.5; }
    .notification-inline-preview strong { display:block; margin-bottom:4px; color:var(--accent-green); font-size:10px; text-transform:uppercase; letter-spacing:.07em; }
    .notification-list { display:grid; gap:9px; max-height:calc(100vh - 330px); overflow-y:auto; padding-right:3px; }
    .notification-item { display:grid; grid-template-columns:auto 1fr auto; gap:11px; align-items:start; padding:12px; border:1px solid rgba(148,163,184,.2); border-radius:11px; background:rgba(0,0,0,.16); }
    .notification-item:hover { border-color:rgba(214,161,23,.72); background:rgba(16,185,129,.07); }
    .notification-avatar { display:grid; place-items:center; width:34px; height:34px; border-radius:10px; color:#071510; background:linear-gradient(145deg,#35D39B,#D6A117); font-size:11px; font-weight:900; }
    .notification-main { min-width:0; }
    .notification-meta { display:flex; flex-wrap:wrap; align-items:center; gap:7px; margin-bottom:4px; color:var(--text-muted); font-size:9px; }
    .notification-meta strong { color:var(--text-main); font-size:11px; }
    .notification-meta .notification-profile { color:var(--accent-green); font-weight:800; }
    .notification-snippet { overflow:hidden; color:var(--text-main); font-size:11px; line-height:1.45; text-overflow:ellipsis; white-space:nowrap; }
    .notification-inbox { display:block; margin-top:5px; color:var(--text-muted); font-family:monospace; font-size:9px; }
    .notification-actions { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:6px; }
    .notification-actions .btn { padding:7px 9px; font-size:9px; white-space:nowrap; }
    .notification-empty { padding:30px 16px; border:1px dashed var(--border-color); border-radius:10px; color:var(--text-muted); text-align:center; font-size:11px; }
     .btn { border: none; border-radius: 8px; padding: 8px 14px; font-weight: 600; font-size: 12px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
    .btn-blue { background: #0284C7; color: white; }
    .btn-red { background: #DC2626; color: white; }
    .btn-orange { background: #EA580C; color: white; }
    .btn-gray { background: #E2E8F0; color: #1E293B; border: 1px solid #CBD5E1; }
    body.dark .btn-gray { background: #032824; color: #F8FAFC; border: 1px solid #80621B; }
    body.dark .btn-blue { background: #D6A117; color: #061510; }
    body.dark .btn-orange { background: #F59E0B; color: #061510; }
    body.dark .top-bar { background: var(--nav-color, #00110F); border-color: #80621B; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px; }
    .stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px 20px; }
    .stat-title { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 26px; font-weight: 800; margin: 8px 0 4px; }
    .stat-sub { font-size: 12px; font-weight: 600; color: var(--accent-green); }
    .grid-2 { display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; }
    .log-box { background: rgba(0,0,0,0.03); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; font-family: monospace; font-size: 12px; }
    [hidden] { display: none !important; }
    .modal-backdrop { position: fixed; inset: 0; z-index: 20; display: grid; place-items: center; padding: 20px; background: rgba(2, 6, 23, .64); backdrop-filter: blur(6px); }
    .modal-card { width: min(520px, 100%); padding: 22px; border: 1px solid var(--border-color); border-radius: 16px; background: var(--bg-card); box-shadow: 0 24px 70px rgba(2, 6, 23, .3); }
    .wide-modal { width: min(720px, 100%); max-height: min(760px, calc(100vh - 36px)); overflow-y: auto; }
    .dialog-card { width: min(430px, 100%); }
    .dialog-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:20px; }
    .toast-region { position:fixed; top:22px; right:22px; z-index:40; width:min(370px, calc(100vw - 44px)); display:grid; gap:10px; pointer-events:none; }
    .toast { display:flex; align-items:flex-start; gap:10px; padding:13px 15px; border:1px solid var(--border-color); border-left:3px solid var(--accent-green); border-radius:11px; background:var(--bg-card); color:var(--text-main); box-shadow:0 16px 36px rgba(2,6,23,.3); font-size:12px; line-height:1.4; animation:toast-in .22s ease-out; pointer-events:auto; }
    .toast-warning { border-left-color:var(--accent-orange); }
    .toast-info { border-left-color:var(--accent-blue); }
    .toast-label { display:block; margin-bottom:2px; color:var(--accent-green); font-size:10px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
    .toast-warning .toast-label { color:var(--accent-orange); }
    .toast-info .toast-label { color:var(--accent-blue); }
    @keyframes toast-in { from { opacity:0; transform:translateY(-8px) scale(.98); } to { opacity:1; transform:translateY(0) scale(1); } }
    .safety-locked .btn-red { opacity:.7; }
    .modal-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .modal-header h3 { margin: 0; font-size: 17px; }
    .modal-close { border: 0; color: var(--text-muted); background: transparent; font-size: 25px; line-height: 1; cursor: pointer; }
    .modal-copy { margin: 9px 0 18px; color: var(--text-muted); font-size: 12px; }
    .palette-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
    .palette-grid { grid-template-columns: repeat(3, 1fr); margin: 10px 0 20px; }
    .palette-option { display:grid; gap:6px; padding:10px; text-align:left; color:var(--text-main); background:transparent; border:1px solid var(--border-color); border-radius:10px; cursor:pointer; }
    .palette-option:hover { border-color:var(--accent-gold); transform:translateY(-1px); }
    .palette-option i { display:block; height:38px; background:var(--swatch); border:1px solid rgba(255,255,255,.22); border-radius:7px; }
    .palette-option small { color: var(--text-muted); font-size:10px; }
    .palette-type-label { display:block; margin-bottom:10px; }
    .typography-grid, .form-grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:12px; }
    .color-control-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin:10px 0 20px; }
    .color-control-grid label { padding:10px; border:1px solid var(--border-color); border-radius:9px; }
    .color-control-grid input[type="color"] { width:100%; height:38px; padding:3px; border:1px solid var(--border-color); border-radius:7px; background:transparent; cursor:pointer; }
    .color-control-grid small { color:var(--text-muted); font-size:10px; font-weight:400; }
    label { display:grid; gap:6px; color:var(--text-muted); font-size:11px; font-weight:700; }
    select, textarea, input[type="number"], input[type="text"] { width:100%; box-sizing:border-box; padding:10px 11px; color:var(--text-main); background:rgba(255,255,255,.04); border:1px solid var(--border-color); border-radius:8px; font:inherit; }
    select option { color:#0F172A; }
    textarea { resize:vertical; }
    .check-control { display:flex; align-items:center; align-content:center; grid-template-columns:auto 1fr; padding:10px 0; }
    .toggle-row { display:flex; flex-wrap:wrap; gap:18px; margin-top:16px; }
    .toggle-row label { display:flex; align-items:center; gap:7px; color:var(--text-main); }
    input[type="checkbox"] { accent-color:var(--accent-green); }
    .soundscape-options { display:grid; grid-template-columns:repeat(4, 1fr); gap:9px; }
    .soundscape-option { display:grid; gap:5px; padding:12px; text-align:left; color:var(--text-main); background:rgba(255,255,255,.03); border:1px solid var(--border-color); border-radius:10px; cursor:pointer; }
    .soundscape-option:hover, .soundscape-option.active { border-color:var(--accent-gold); background:rgba(214,161,23,.08); }
    .soundscape-option small { color:var(--text-muted); font-size:10px; }
    .audio-player-shell { display:flex; justify-content:space-between; align-items:center; gap:16px; margin:16px 0; padding:14px; border:1px solid var(--border-color); border-radius:10px; }
    .eyebrow { display:block; color:var(--accent-green); font-size:9px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
    .audio-player-shell strong { display:block; margin-top:5px; font-size:13px; }
    .audio-controls { display:flex; align-items:center; gap:12px; color:var(--text-muted); font-family:monospace; font-size:11px; }
    .upload-zone { display:grid; gap:5px; padding:15px; border:1px dashed var(--accent-gold); border-radius:10px; color:var(--text-main); cursor:pointer; }
    .upload-zone span { font-size:12px; font-weight:800; color:var(--accent-gold); }
    .upload-zone small { color:var(--text-muted); font-size:10px; font-weight:400; }
    .upload-zone input { margin-top:5px; }
    .clip-grid { display:grid; grid-template-columns:1fr 1fr auto; align-items:end; gap:10px; margin-top:12px; }
    .ai-mascot { position:fixed; right:24px; bottom:24px; z-index:25; width:72px; height:72px; display:grid; place-items:center; border:1px solid var(--accent-gold); border-radius:24px; background:radial-gradient(circle at 35% 25%,rgba(255,255,255,.18),transparent 35%),linear-gradient(145deg,#06483a,#001713); box-shadow:0 14px 35px rgba(0,0,0,.42); cursor:grab; touch-action:none; user-select:none; transition:transform .2s ease; }
    .ai-mascot:active { cursor:grabbing; }
    .ai-mascot:hover { transform:translateY(-4px) rotate(-2deg); }
     .robot-uploaded { width:58px; height:58px; object-fit:contain; border-radius:14px; display:block; filter:drop-shadow(4px 7px 4px rgba(0,0,0,.32)); mix-blend-mode:screen; }
     .robot-3d { position:relative; width:43px; height:48px; display:none; filter:drop-shadow(4px 7px 4px rgba(0,0,0,.32)); }
    .robot-antenna { position:absolute; left:20px; top:-5px; width:3px; height:9px; background:#DCE7E5; border-radius:3px; }
    .robot-antenna::before { content:''; position:absolute; top:-4px; left:-3px; width:9px; height:9px; border-radius:50%; background:#D6A117; box-shadow:0 0 8px #D6A117; }
    .robot-head { position:absolute; left:4px; top:5px; width:35px; height:27px; border-radius:10px 10px 8px 8px; background:linear-gradient(145deg,#fff,#C9D5D5); border:1px solid #fff; transform:perspective(90px) rotateX(-5deg); }
    .robot-head::after { content:''; position:absolute; inset:5px 5px 7px; border-radius:6px; background:linear-gradient(145deg,#163E39,#061613); }
    .robot-eye { position:absolute; z-index:1; top:14px; width:5px; height:7px; border-radius:50%; background:#8FFFF0; box-shadow:0 0 7px #35D39B; }
    .robot-eye.left { left:12px; } .robot-eye.right { right:12px; }
    .robot-body { position:absolute; left:8px; top:33px; width:27px; height:15px; border-radius:6px 6px 8px 8px; background:linear-gradient(145deg,#fff,#B6C5C3); border:1px solid #fff; }
    .robot-body::after { content:'✦'; position:absolute; left:9px; top:0px; color:#D6A117; font-size:11px; }
    .robot-arm { position:absolute; top:35px; width:6px; height:14px; border-radius:4px; background:#D4DFDE; } .robot-arm.left { left:2px; transform:rotate(12deg); } .robot-arm.right { right:2px; transform:rotate(-12deg); }
    .ai-ping { position:absolute; right:-3px; top:-3px; width:10px; height:10px; border:2px solid #001713; border-radius:50%; background:var(--accent-green); box-shadow:0 0 10px var(--accent-green); }
    .ai-drawer { position:fixed; top:0; right:0; z-index:24; width:min(390px, 100vw); height:100vh; box-sizing:border-box; display:flex; flex-direction:column; padding:20px; background:var(--bg-card); border-left:1px solid var(--accent-gold); box-shadow:-16px 0 45px rgba(0,0,0,.3); transform:translateX(105%); transition:transform .25s ease; }
    .ai-drawer.open { transform:translateX(0); }
    .ai-drawer-head { display:flex; justify-content:space-between; align-items:flex-start; padding-bottom:16px; border-bottom:1px solid var(--border-color); }
    .ai-drawer-head h3 { margin:5px 0 0; font-size:17px; }
    .ai-messages { flex:1; overflow:auto; display:grid; align-content:start; gap:10px; padding:18px 0; }
    .ai-response-block { display:grid; gap:5px; }
    .ai-bubble { padding:12px 13px; border-radius:11px; font-size:12px; line-height:1.55; white-space:pre-wrap; }
    .ai-bubble-bot { background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.25); }
    .ai-bubble-user { justify-self:end; max-width:85%; background:rgba(214,161,23,.13); border:1px solid rgba(214,161,23,.35); }
    .ai-suggestions { display:flex; gap:6px; overflow:auto; padding-bottom:10px; }
    .ai-suggestions button, .tts-button { border:1px solid var(--border-color); border-radius:7px; padding:7px 9px; color:var(--text-muted); background:transparent; font-size:10px; cursor:pointer; white-space:nowrap; }
    .ai-suggestions button:hover, .tts-button:hover { color:var(--text-main); border-color:var(--accent-gold); }
    .ai-library-head { display:flex; justify-content:space-between; align-items:end; gap:10px; margin-bottom:7px; }
    .ai-library-head small { color:var(--text-muted); font-size:9px; }
    .ai-workflow-library { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:5px; max-height:175px; overflow:auto; padding:2px 0 10px; }
    .ai-workflow-item { display:flex; align-items:center; gap:7px; min-width:0; padding:7px 8px; border:1px solid var(--border-color); border-radius:7px; background:rgba(16,185,129,.04); color:var(--text-main); text-align:left; cursor:pointer; }
    .ai-workflow-item:hover { border-color:var(--accent-gold); background:rgba(214,161,23,.09); }
    .ai-workflow-item b { color:var(--accent-gold); font-size:9px; }
    .ai-workflow-item span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--text-muted); font-size:9px; }
    .ai-compose { display:flex; gap:7px; }
    .ai-compose input { flex:1; min-width:0; }
    .ai-response-audio { justify-self:start; border:1px solid rgba(16,185,129,.35); border-radius:7px; padding:6px 9px; color:var(--accent-green); background:transparent; font-size:10px; cursor:pointer; }
    .ai-response-audio:hover { border-color:var(--accent-gold); color:var(--accent-gold); }
    .tts-button { width:100%; margin-top:10px; }
    .broadcast-overlay { position:fixed; inset:0; z-index:50; display:grid; place-items:center; padding:24px; background:rgba(0,8,7,.9); backdrop-filter:blur(10px); }
    .broadcast-overlay-card { width:min(560px, 100%); padding:34px; text-align:center; border:1px solid var(--accent-gold); border-radius:18px; background:linear-gradient(145deg,#062b24,#001713); box-shadow:0 30px 100px rgba(0,0,0,.5); }
    .broadcast-overlay-card h2 { margin:12px 0 10px; font-size:25px; }
    .broadcast-overlay-card p { margin:0 auto 14px; max-width:430px; color:var(--text-muted); line-height:1.5; }
    .broadcast-overlay-card small { display:block; margin-bottom:22px; color:var(--accent-green); }
    .colleague-grid { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:14px; }
    .colleague-card { padding:16px; border:1px solid var(--border-color); border-radius:12px; background:rgba(16,185,129,.04); }
     .colleague-head { display:flex; align-items:center; gap:11px; }
    .avatar { width:42px; height:42px; object-fit:cover; display:grid; place-items:center; flex:0 0 42px; border-radius:50%; background:linear-gradient(145deg,#075642,#D6A117); color:#fff; font-size:13px; font-weight:800; }
    .colleague-name { font-size:13px; font-weight:800; }
     .colleague-role { margin-top:3px; color:var(--text-muted); font-size:10px; }
     .colleague-state { margin-top:4px; color:var(--accent-green); font-size:10px; }
     .presence { display:inline-flex; align-items:center; gap:5px; margin-left:auto; color:var(--text-muted); font-size:10px; font-weight:700; white-space:nowrap; }
     .icon-button { width:30px; height:30px; display:grid; place-items:center; flex:0 0 30px; border:1px solid var(--border-color); border-radius:8px; color:var(--text-muted); background:transparent; cursor:pointer; font-size:15px; }
     .icon-button:hover, .icon-button:focus-visible { color:var(--accent-gold); border-color:var(--accent-gold); outline:none; }
    .presence-dot { width:8px; height:8px; border-radius:50%; background:#EF4444; box-shadow:0 0 8px rgba(239,68,68,.65); }
    .presence-dot.online { background:#10B981; box-shadow:0 0 8px rgba(16,185,129,.8); }
    .colleague-meta { display:grid; gap:7px; margin:15px 0; padding:11px 0; border-top:1px solid var(--border-color); border-bottom:1px solid var(--border-color); color:var(--text-muted); font-size:10px; }
    .colleague-meta b { color:var(--text-main); }
    .tag-list { display:flex; flex-wrap:wrap; gap:5px; }
    .tag { padding:4px 7px; border:1px solid rgba(214,161,23,.45); border-radius:999px; color:var(--accent-gold); font-size:9px; font-weight:800; }
    .colleague-actions { display:flex; gap:7px; flex-wrap:wrap; }
    .colleague-actions .btn { font-size:10px; padding:7px 9px; }
    .upload-mini { display:flex; align-items:center; gap:6px; margin-top:10px; color:var(--text-muted); font-size:10px; cursor:pointer; }
    .upload-mini input { width:130px; font-size:9px; }
    .rbac-section { margin-top:20px; }
    .permission-card { min-width:0; overflow:hidden; margin-top:10px; padding:14px; border:1px solid var(--border-color); border-radius:11px; background:rgba(0,0,0,.07); }
    .permission-card-head { display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:11px; }
    .permission-card-head strong { font-size:12px; }
    .permission-card-head small { color:var(--text-muted); font-size:10px; }
    .permission-grid { display:grid; grid-template-columns:repeat(6, minmax(0, 1fr)); gap:7px; width:100%; }
    .permission-item { min-width:0; display:grid; justify-items:center; gap:4px; padding:5px 2px; border:1px solid rgba(148,163,184,.16); border-radius:6px; color:var(--text-muted); font-size:9px; overflow:hidden; }
    .permission-item:hover { border-color:var(--accent-gold); color:var(--text-main); }
    .permission-item input { max-width:100%; }
    .attendance-card { margin-top:20px; }
    .section-heading { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; margin-bottom:14px; }
    .section-heading h3, .section-heading h4 { margin:6px 0 0; font-size:16px; }
    .section-heading.compact { align-items:end; margin-bottom:10px; }
    .section-heading.compact h4 { font-size:13px; }
    .section-heading small { color:var(--text-muted); font-size:10px; }
    .attendance-summary-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-bottom:16px; }
    .mini-stat { min-width:0; padding:11px; border:1px solid var(--border-color); border-radius:9px; background:rgba(16,185,129,.05); }
    .mini-stat span { display:block; color:var(--text-muted); font-size:10px; }
    .mini-stat strong { display:block; margin-top:6px; color:var(--accent-gold); font-size:16px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .attendance-scroll { overflow-x:auto; border:1px solid var(--border-color); border-radius:10px; }
    .attendance-table { min-width:980px; margin-top:0; }
    .attendance-table th, .attendance-table td { padding:9px 8px; font-size:10px; vertical-align:middle; }
    .attendance-table th { font-size:9px; }
    .attendance-table td:first-child { min-width:145px; }
    .attendance-table td:first-child small, .leave-row small { display:block; margin-top:3px; color:var(--text-muted); font-size:9px; }
    .attendance-table select { min-width:112px; padding:7px 6px; font-size:10px; }
    .fine-balance { color:var(--accent-orange); white-space:nowrap; }
    .leave-panel { margin-top:18px; padding-top:17px; border-top:1px solid var(--border-color); }
    .leave-list { display:grid; gap:8px; }
    .leave-row { display:grid; grid-template-columns:1.4fr .8fr .8fr .8fr auto; align-items:end; gap:9px; padding:11px; border:1px solid var(--border-color); border-radius:9px; background:rgba(0,0,0,.06); }
    .leave-row > div { align-self:center; }
    .leave-row label { font-size:9px; }
    .leave-row input, .leave-row select { padding:7px; font-size:10px; }
    .leave-row button { font-size:9px; padding:7px 9px; }
    .permission-item input { margin:0; }
    .profile-details { display:grid; grid-template-columns:120px 1fr; gap:18px; align-items:start; }
    .profile-photo { width:112px; height:112px; object-fit:cover; display:grid; place-items:center; border-radius:14px; background:linear-gradient(145deg,#075642,#D6A117); color:white; font-size:28px; font-weight:800; }
    .profile-summary { display:grid; gap:8px; }
    .profile-summary strong { font-size:18px; }
    .profile-summary small { color:var(--text-muted); }
     .profile-upload { margin-top:12px; }
     .profile-form-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin-top:14px; }
     .profile-form-grid .full { grid-column:1 / -1; }
     .profile-form-note { margin:4px 0 0; color:var(--text-muted); font-size:10px; line-height:1.45; }
     .crop-stage { display:grid; place-items:center; min-height:300px; padding:12px; border:1px solid var(--border-color); border-radius:12px; background:rgba(0,0,0,.22); }
     #crop-canvas { width:280px; height:280px; max-width:100%; border-radius:12px; background:#020617; }
     .crop-controls { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:14px; }
     .crop-controls input[type="range"] { width:100%; accent-color:var(--accent-gold); }
     .crop-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:16px; }
    .modal-action { margin-top: 20px; }
    .modules-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-top: 15px; }
     .module-card { min-height: 102px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px; text-decoration: none; display: flex; align-items: flex-start; gap: 11px; color: inherit; transition: 0.2s; }
    .module-card:hover { border-color: var(--accent-gold); transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,.22); }
    body.dark .module-card { background: #001713; border-color: #123D36; }
    .module-card.is-restricted { display:none; }
    .module-icon { width: 34px; height: 34px; flex: 0 0 34px; display: grid; place-items: center; color: #F59E0B; background: rgba(245, 158, 11, .1); border: 1px solid rgba(214, 161, 23, .55); border-radius: 8px; font-size: 18px; font-weight: 800; }
    .module-copy { min-width: 0; }
     .mod-title { font-size: 12px; font-weight: 800; color: var(--accent-gold); margin-bottom: 6px; line-height: 1.25; }
     .mod-name { font-size: 13px; font-weight: bold; line-height: 1.3; }
     .module-desc { margin-top: 5px; color: var(--text-muted); font-size: 10.5px; line-height: 1.35; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border-color); font-size: 13px; }
    th { font-size: 12px; color: var(--text-muted); text-transform: uppercase; }
    .module-hero { display:flex; justify-content:space-between; gap:18px; align-items:flex-start; }
    .module-hero h2 { margin:6px 0 7px; font-size:22px; color:var(--accent-gold); }
    .module-hero-copy { max-width:760px; }
    .module-status-pill { display:inline-flex; align-items:center; gap:7px; padding:8px 11px; border:1px solid rgba(16,185,129,.35); border-radius:999px; color:var(--accent-green); font-size:10px; font-weight:800; white-space:nowrap; }
    .telemetry-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:0 0 20px; }
    .telemetry-card { min-width:0; padding:15px; border:1px solid var(--border-color); border-radius:11px; background:linear-gradient(145deg,rgba(16,185,129,.08),rgba(214,161,23,.04)); }
    .telemetry-card strong { display:block; margin:7px 0 3px; font-size:22px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .telemetry-card small { color:var(--accent-green); font-size:10px; font-weight:700; }
    .module-workbench { display:grid; grid-template-columns:1.3fr .9fr; gap:20px; }
    .module-panel { min-width:0; padding:18px; border:1px solid var(--border-color); border-radius:13px; background:var(--bg-card); }
    .module-panel h3 { margin:0 0 14px; font-size:14px; }
    .panel-copy { margin:-5px 0 14px; color:var(--text-muted); font-size:11px; line-height:1.5; }
    .campaign-panel { margin-top:20px; border-color:rgba(214,161,23,.55); }
    .range-label { display:grid; grid-template-columns:1fr auto; gap:8px; align-items:center; margin-top:13px; color:var(--text-muted); }
    .range-label input { grid-column:1 / -1; width:100%; accent-color:var(--accent-gold); }
    .range-label span { color:var(--accent-gold); font-family:monospace; font-size:11px; }
    .dispatch-checks { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin:14px 0; }
    .dispatch-check { padding:9px; border:1px solid var(--border-color); border-radius:8px; color:var(--text-muted); font-size:10px; text-align:center; }
    .dispatch-check.is-ready { color:var(--accent-green); border-color:rgba(16,185,129,.45); background:rgba(16,185,129,.07); }
    .dispatch-check.is-warning { color:var(--accent-orange); border-color:rgba(234,88,12,.45); background:rgba(234,88,12,.07); }
    .dispatch-actions { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
    .dispatch-result { margin-top:12px; padding:10px; border-radius:8px; color:var(--text-muted); background:rgba(0,0,0,.1); font-size:10px; line-height:1.45; }
    .spintax-preview { min-height:78px; margin:13px 0 0; padding:11px; overflow:auto; border:1px solid var(--border-color); border-radius:8px; white-space:pre-wrap; color:var(--accent-green); background:rgba(0,0,0,.12); font:11px/1.55 monospace; }
    .bar-chart { display:flex; align-items:end; gap:9px; height:150px; padding:15px 8px 8px; border-bottom:1px solid var(--border-color); background:repeating-linear-gradient(to top,transparent 0,transparent 29px,rgba(148,163,184,.12) 30px); }
    .bar-chart span { flex:1; min-width:8px; border-radius:5px 5px 0 0; background:linear-gradient(180deg,var(--accent-green),var(--accent-gold)); box-shadow:0 0 12px rgba(16,185,129,.16); }
    .chart-caption { display:flex; justify-content:space-between; margin-top:9px; color:var(--text-muted); font-size:10px; }
    .control-list { display:grid; gap:9px; }
    .control-row { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px; border:1px solid var(--border-color); border-radius:9px; }
    .control-row span { color:var(--text-muted); font-size:10px; line-height:1.35; }
    .control-row b { display:block; color:var(--text-main); font-size:11px; margin-bottom:3px; }
    .control-row .btn { flex:0 0 auto; font-size:10px; padding:7px 9px; }
    .module-table-wrap { margin-top:20px; overflow-x:auto; }
    .module-table-wrap table { min-width:520px; margin-top:0; }
    .module-access-denied { padding:28px; text-align:center; border:1px dashed var(--accent-orange); border-radius:13px; background:rgba(234,88,12,.08); }
    .module-access-denied h3 { margin:0 0 8px; color:var(--accent-orange); }
    .module-access-denied p { color:var(--text-muted); font-size:12px; }
    .vault-panel { margin-top:20px; border-color:var(--accent-gold); }
    @media (max-width: 980px) { .modules-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
     @media (max-width: 700px) { body { padding: 10px; } .modules-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .palette-grid, .soundscape-options, .typography-grid, .form-grid, .color-control-grid, .profile-form-grid { grid-template-columns: repeat(2, 1fr); } .audio-player-shell, .clip-grid { grid-template-columns:1fr; flex-direction:column; align-items:stretch; } .attendance-summary-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .leave-row { grid-template-columns:1fr 1fr; } .leave-row > div { grid-column:1 / -1; } }
    @media (max-width: 980px) { .colleague-grid { grid-template-columns:repeat(2, minmax(0, 1fr)); } .permission-grid { grid-template-columns:repeat(5, minmax(0, 1fr)); } .module-workbench { grid-template-columns:1fr; } }
     @media (max-width: 700px) { .notification-backdrop { padding:64px 10px 10px; } .notification-modal { max-height:calc(100vh - 74px); padding:14px; } .notification-toolbar { grid-template-columns:1fr 1fr; } .notification-toolbar .check-control { grid-column:1 / -1; } .notification-list { max-height:calc(100vh - 365px); } .notification-item { grid-template-columns:auto 1fr; } .notification-actions { grid-column:1 / -1; justify-content:flex-start; } }
     @media (max-width: 480px) { .modules-grid { grid-template-columns: 1fr; } .top-bar { align-items: flex-start; } .view-as-bar { align-items:flex-start; flex-direction:column; } .view-as-controls { align-items:flex-start; flex-direction:column; width:100%; } .view-as-controls select { width:100%; min-width:0; } .colleague-grid { grid-template-columns:1fr; } .profile-details { grid-template-columns:1fr; } .profile-form-grid { grid-template-columns:1fr; } .profile-form-grid .full { grid-column:auto; } .permission-grid { grid-template-columns:repeat(3, minmax(0, 1fr)); } .telemetry-grid { grid-template-columns:1fr; } .module-hero { flex-direction:column; } .module-status-pill { align-self:flex-start; } .dispatch-checks { grid-template-columns:1fr; } .ai-mascot { right:14px; bottom:14px; } }
"""

COMMON_JS = """
<script>
const THEME_PRESETS = {
    midnight: {dark:true, bg:'#0B1120', card:'#001A17', text:'#F8FAFC', muted:'#9BB0AD', border:'#123B35', accent:'#D6A117', green:'#10B981'},
    emerald: {dark:true, bg:'#031C18', card:'#062B24', text:'#F4FFF9', muted:'#9BC7B9', border:'#1C5A4B', accent:'#E0AF32', green:'#35D39B'},
    royal: {dark:true, bg:'#11162D', card:'#182348', text:'#F5F7FF', muted:'#AEB8D6', border:'#34457C', accent:'#CBB5FF', green:'#64E6C0'},
    sandstone: {dark:true, bg:'#211A14', card:'#302319', text:'#FFF9F0', muted:'#C6B39D', border:'#60452B', accent:'#F0B55A', green:'#69D0A2'},
    slate: {dark:true, bg:'#111827', card:'#1E293B', text:'#F8FAFC', muted:'#A7B3C5', border:'#334155', accent:'#38BDF8', green:'#34D399'},
    cloud: {dark:false, bg:'#F1F5F9', card:'#FFFFFF', text:'#0F172A', muted:'#64748B', border:'#CBD5E1', accent:'#0284C7', green:'#10B981'}
};
const ACCESS_MAP = {
    king: Array.from({length:22}, (_, i) => i + 1),
    abdullah: [1,2,3,4,5,6,7,12],
    sarah: [1,2,4,5,11,17,18],
    hamza: [1,2,6,7,13,16]
};
const PROFILE_DATA = {
    king: {name:'King Saab', role:'Super Admin', status:'Online', state:'Pakistan', contractorStates:[], metrics:{pipeline:'2,480', inboxes:'3 Inboxes', volume:'1,240', deal:'$64,800'}},
    abdullah: {name:'Abdullah Khan', role:'Strategic Lead', status:'Online', state:'Pakistan', contractorStates:[], metrics:{pipeline:'1,860', inboxes:'3 Inboxes', volume:'920', deal:'$48,200'}},
    sarah: {name:'Sarah Malik', role:'Growth Marketer', status:'Online', state:'Pakistan', contractorStates:[], metrics:{pipeline:'1,120', inboxes:'2 Inboxes', volume:'640', deal:'$18,400'}},
    hamza: {name:'Hamza Ali', role:'Lead Collector', status:'Offline', state:'Pakistan', contractorStates:['California','Texas'], metrics:{pipeline:'740', inboxes:'1 Inbox', volume:'410', deal:'$12,600'}}
};
const PROFILE_META_SEED = {
    king:{name:'King Saab',role:'Super Admin',state:'Pakistan',presence:'Online',contractorStates:[]},
    abdullah:{name:'Abdullah Khan',role:'Strategic Lead',state:'Pakistan',presence:'Online',contractorStates:[]},
    sarah:{name:'Sarah Malik',role:'Growth Marketer',state:'Pakistan',presence:'Online',contractorStates:[]},
    hamza:{name:'Hamza Ali',role:'Lead Collector',state:'Pakistan',presence:'Offline',contractorStates:['California','Texas']}
};
const US_STATES = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'];
const ATTENDANCE_SEED = {
    king:{mon:'present',tue:'present',wed:'present',thu:'present',fri:'present',sat:'present'},
    abdullah:{mon:'present',tue:'present',wed:'approved',thu:'absent',fri:'present',sat:'present'},
    sarah:{mon:'present',tue:'received',wed:'present',thu:'present',fri:'absent',sat:'present'},
    hamza:{mon:'absent',tue:'present',wed:'present',thu:'absent',fri:'present',sat:'present'}
};
const LEAVE_SEED = {
    abdullah:{start:'2026-09-07',end:'2026-09-08',state:'approved'},
    sarah:{start:'2026-09-12',end:'2026-09-12',state:'received'}
};
const SHARED_STATE_ENDPOINT = '/state';
let sharedStateAvailable = false;
let notificationItems = [];
let notificationFilter = 'all';
let notificationInitialized = false;
let notificationCleaning = false;
let notificationPreviousIds = new Set();
function getProfileMeta() {
    try {
        const saved = JSON.parse(window.localStorage.getItem('grace-profile-meta') || '{}');
        return Object.assign({}, PROFILE_META_SEED, saved);
    } catch (error) {
        return Object.assign({}, PROFILE_META_SEED);
    }
}
async function syncSharedState() {
    try {
        const response = await fetch(SHARED_STATE_ENDPOINT, {headers:{Accept:'application/json'}});
        if (!response.ok) throw new Error('Shared state unavailable');
        const shared = await response.json();
        if (shared.photos) window.localStorage.setItem('grace-profile-photos', JSON.stringify(shared.photos));
        if (shared.attendance) window.localStorage.setItem('grace-attendance', JSON.stringify(shared.attendance));
        if (shared.leaves) window.localStorage.setItem('grace-leave-requests', JSON.stringify(shared.leaves));
        if (shared.clearedFines) window.localStorage.setItem('grace-cleared-fines', JSON.stringify(shared.clearedFines));
        if (shared.profiles) window.localStorage.setItem('grace-profile-meta', JSON.stringify(shared.profiles));
        sharedStateAvailable = true;
        if (shared.notifications) hydrateNotifications(shared.notifications);
        if (shared.gmailSync) {
            const syncStatus = document.getElementById('notification-sync-status');
            if (syncStatus && shared.gmailSync.state === 'error') syncStatus.innerText = shared.gmailSync.message;
        }
        hydrateProfilePhotos();
        hydrateProfileMeta();
        renderAttendanceLedger();
    } catch (error) {
        sharedStateAvailable = false;
    }
}
function publishSharedState(resource, value, key) {
    fetch(SHARED_STATE_ENDPOINT, {
        method:'POST',
        headers:{'Content-Type':'application/json', Accept:'application/json'},
        body:JSON.stringify({resource, value, key})
    }).then(function(response) {
    if (!response.ok) throw new Error('Shared state update rejected');
        sharedStateAvailable = true;
        syncSharedState();
    }).catch(function() {
        sharedStateAvailable = false;
    });
}
function notificationProfileName(key) {
    const meta = getProfileMeta()[key] || {};
    const fallback = PROFILE_DATA[key] || {};
    return meta.name || fallback.name || key;
}
function notificationInitials(name) {
    return String(name || '').split(/\\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'NA';
}
function notificationRelativeTime(createdAt) {
    const seconds = Math.max(0, Math.floor(Date.now() / 1000) - Number(createdAt || 0));
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return minutes + 'm ago';
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return hours + 'h ago';
    return Math.floor(hours / 24) + 'd ago';
}
function escapeNotificationText(value) {
    return String(value || '').replace(/[&<>"']/g, function(character) {
        return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character];
    });
}
function notificationAudioSettings() {
    try {
        return Object.assign({enabled:true, chime:'soft', volume:35}, JSON.parse(window.localStorage.getItem('grace-notification-audio') || '{}'));
    } catch (error) {
        return {enabled:true, chime:'soft', volume:35};
    }
}
function hydrateNotificationSettings() {
    const settings = notificationAudioSettings();
    const autoRead = document.getElementById('notification-auto-read');
    const chime = document.getElementById('notification-chime');
    const volume = document.getElementById('notification-volume');
    if (autoRead) autoRead.checked = window.localStorage.getItem('grace-notification-auto-read') !== 'false';
    if (chime) chime.value = settings.chime;
    if (volume) volume.value = settings.volume;
}
function saveNotificationAudioSettings(notify = true) {
    const settings = {
        enabled: true,
        chime: document.getElementById('notification-chime')?.value || 'soft',
        volume: Number(document.getElementById('notification-volume')?.value || 35)
    };
    window.localStorage.setItem('grace-notification-audio', JSON.stringify(settings));
    if (notify) showToast('Notification chime settings saved.', 'success');
}
function playNotificationChime() {
    const settings = notificationAudioSettings();
    if (settings.chime === 'silent' || settings.volume <= 0 || !settings.enabled) return;
    const patterns = {soft:[660,880], bright:[880,1175,1480], urgent:[440,660,440]};
    try {
        const context = new (window.AudioContext || window.webkitAudioContext)();
        const gain = context.createGain();
        gain.gain.value = Math.min(.12, Number(settings.volume) / 1000);
        gain.connect(context.destination);
        (patterns[settings.chime] || patterns.soft).forEach(function(frequency, index) {
            const oscillator = context.createOscillator();
            oscillator.type = settings.chime === 'urgent' ? 'square' : 'sine';
            oscillator.frequency.value = frequency;
            oscillator.connect(gain);
            oscillator.start(context.currentTime + index * .12);
            oscillator.stop(context.currentTime + index * .12 + .15);
        });
    } catch (error) {
        // Browsers may require one user gesture before allowing notification audio.
    }
}
function testNotificationChime() {
    saveNotificationAudioSettings(false);
    playNotificationChime();
    showToast('Notification chime preview played.', 'info');
}
function cleanNotificationNoise(items, persist = true) {
    const autoRead = window.localStorage.getItem('grace-notification-auto-read') !== 'false';
    const cleaned = autoRead ? items.filter((item) => item.category === 'work') : items;
    if (autoRead && persist && cleaned.length !== items.length && !notificationCleaning) {
        notificationCleaning = true;
        window.localStorage.setItem('grace-notifications', JSON.stringify(cleaned));
        publishSharedState('notifications', cleaned);
        window.setTimeout(function() { notificationCleaning = false; }, 700);
    }
    return cleaned;
}
function hydrateNotifications(items) {
    const raw = Array.isArray(items) ? items : [];
    const cleaned = cleanNotificationNoise(raw);
    const incoming = cleaned.filter((item) => notificationInitialized && !notificationPreviousIds.has(item.id));
    notificationItems = cleaned;
    notificationPreviousIds = new Set(cleaned.map((item) => item.id));
    window.localStorage.setItem('grace-notifications', JSON.stringify(cleaned));
    if (incoming.length) playNotificationChime();
    notificationInitialized = true;
    renderNotifications();
}
function notificationFilterLabel(filter) {
    return filter === 'all' ? 'All profiles' : notificationProfileName(filter);
}
function setNotificationFilter(filter) {
    notificationFilter = filter;
    renderNotifications();
}
function toggleNotificationAutoRead() {
    const enabled = document.getElementById('notification-auto-read')?.checked !== false;
    window.localStorage.setItem('grace-notification-auto-read', String(enabled));
    notificationItems = cleanNotificationNoise(notificationItems);
    renderNotifications();
    showToast(enabled ? 'Non-work and spam logs will be cleared automatically.' : 'Auto-read cleanup paused; all incoming logs remain visible.', 'info');
}
function toggleNotificationPreview(id) {
    const item = notificationItems.find((entry) => entry.id === id);
    const preview = document.getElementById('notification-preview');
    if (!item || !preview) return;
    preview.innerHTML = '<strong>' + escapeNotificationText(item.client) + ' · ' + escapeNotificationText(notificationProfileName(item.profile)) + '</strong><span>' + escapeNotificationText(item.body || item.snippet) + '</span>';
    preview.hidden = false;
}
function jumpToMailInbox(inbox) {
    window.open('https://mail.google.com/mail/u/0/#inbox', '_blank', 'noopener,noreferrer');
    showToast('Opening ' + inbox + ' in Gmail Inbox.', 'info');
}
function renderNotifications() {
    const filters = document.getElementById('notification-filters');
    const list = document.getElementById('notification-list');
    const count = document.getElementById('notification-count');
    const syncStatus = document.getElementById('notification-sync-status');
    if (count) count.innerText = notificationItems.length;
    if (syncStatus) syncStatus.innerText = sharedStateAvailable ? 'Shared state · live polling every 5 seconds' : 'Local preview · waiting for shared state';
    if (filters) {
        const profiles = ['all'].concat(Array.from(new Set(notificationItems.map((item) => item.profile))));
        filters.innerHTML = profiles.map(function(filter) {
            return '<button class="notification-filter ' + (notificationFilter === filter ? 'is-active' : '') + '" role="tab" aria-selected="' + (notificationFilter === filter ? 'true' : 'false') + '" onclick="setNotificationFilter(&quot;' + filter + '&quot;)">' + escapeNotificationText(notificationFilterLabel(filter)) + '</button>';
        }).join('');
    }
    if (!list) return;
    const visible = notificationItems.filter((item) => notificationFilter === 'all' || item.profile === notificationFilter);
    if (!visible.length) {
        list.innerHTML = '<div class="notification-empty">No work notifications in this profile view. Auto-read cleanup is active.</div>';
        return;
    }
    list.innerHTML = visible.map(function(item) {
        const profileName = notificationProfileName(item.profile);
        const profileRole = (getProfileMeta()[item.profile] || PROFILE_DATA[item.profile] || {}).role || 'Workspace';
        return '<article class="notification-item"><div class="notification-avatar">' + escapeNotificationText(notificationInitials(profileName)) + '</div><div class="notification-main"><div class="notification-meta"><strong>' + escapeNotificationText(item.client) + '</strong><span class="notification-profile">' + escapeNotificationText(profileName) + '</span><span>·</span><span>' + escapeNotificationText(profileRole) + '</span><span>·</span><span>' + escapeNotificationText(notificationRelativeTime(item.createdAt)) + '</span></div><div class="notification-snippet">' + escapeNotificationText(item.snippet) + '</div><span class="notification-inbox">Connected inbox · ' + escapeNotificationText(item.inbox) + '</span></div><div class="notification-actions"><button class="btn btn-gray" onclick="toggleNotificationPreview(&quot;' + escapeNotificationText(item.id) + '&quot;)">Preview</button><button class="btn btn-blue" onclick="jumpToMailInbox(&quot;' + escapeNotificationText(item.inbox) + '&quot;)">Jump to Mail Inbox</button></div></article>';
    }).join('');
}
function openNotifications() {
    const panel = document.getElementById('notification-panel');
    if (!panel) return;
    hydrateNotificationSettings();
    renderNotifications();
    panel.hidden = false;
}
function closeNotifications() {
    const panel = document.getElementById('notification-panel');
    if (panel) panel.hidden = true;
}
function addLiveNotification(item) {
    const next = [item].concat(notificationItems.filter((entry) => entry.id !== item.id)).slice(0, 100);
    notificationItems = cleanNotificationNoise(next, false);
    window.localStorage.setItem('grace-notifications', JSON.stringify(notificationItems));
    publishSharedState('notifications', notificationItems);
    renderNotifications();
    playNotificationChime();
}
const MODULE_GUIDES = {
    1:{name:'Dashboard Hub',en:'🧭 Step 1 ➔ Review pipeline and inbox health.\\nStep 2 ➔ Open the activity stream.\\nStep 3 ➔ Trigger a safe sync or pause outreach.',ur:'🧭 Step 1 ➔ Pipeline aur inbox health dekhein.\\nStep 2 ➔ Activity stream kholen.\\nStep 3 ➔ Safe sync chalayein ya outreach rok dein.'},
    2:{name:'Gmail Multi-Tenant Hub',en:'✉️ Step 1 ➔ Check each inbox quota.\\nStep 2 ➔ Verify OAuth and rotation health.\\nStep 3 ➔ Rebalance the tenant pool before dispatch.',ur:'✉️ Step 1 ➔ Har inbox ka quota check karein.\\nStep 2 ➔ OAuth aur rotation health verify karein.\\nStep 3 ➔ Dispatch se pehle tenant pool rebalance karein.'},
    3:{name:'AI Warmup Ramp',en:'♨️ Step 1 ➔ Review the sender reputation score.\\nStep 2 ➔ Inspect the active warmup cohort.\\nStep 3 ➔ Advance the next cohort only when engagement is healthy.',ur:'♨️ Step 1 ➔ Sender reputation score dekhein.\\nStep 2 ➔ Active warmup cohort inspect karein.\\nStep 3 ➔ Engagement healthy ho to agla cohort advance karein.'},
    4:{name:'Campaign Studio',en:'➤ Step 1 ➔ Select a sequence and timezone.\\nStep 2 ➔ Run the AI copy score and A/B split.\\nStep 3 ➔ Launch, pause, or review the next stage.',ur:'➤ Step 1 ➔ Sequence aur timezone select karein.\\nStep 2 ➔ AI copy score aur A/B split chalayein.\\nStep 3 ➔ Next stage launch, pause ya review karein.'},
    5:{name:'Spin-Syntax AI Engine',en:'╱ Step 1 ➔ Choose the source message.\\nStep 2 ➔ Generate safe variants and preview each spin.\\nStep 3 ➔ Promote the winning copy to a live sequence.',ur:'╱ Step 1 ➔ Source message choose karein.\\nStep 2 ➔ Safe variants generate karke preview karein.\\nStep 3 ➔ Winning copy ko live sequence mein promote karein.'},
    6:{name:'Architect & Contractor Scraper',en:'⌕ Step 1 ➔ Choose states or a regional segment.\\nStep 2 ➔ Run live pings and enrich decision-makers.\\nStep 3 ➔ Export the verified lead batch as CSV or TXT.',ur:'⌕ Step 1 ➔ States ya regional segment choose karein.\\nStep 2 ➔ Live pings aur decision-maker enrichment chalayein.\\nStep 3 ➔ Verified leads ko CSV ya TXT mein export karein.'},
    7:{name:'CRM Revenue Pipeline',en:'$ Step 1 ➔ Review discovery, proposal, and negotiation stages.\\nStep 2 ➔ Score opportunities by close signal.\\nStep 3 ➔ Refresh the pipeline and export ROI attribution.',ur:'$ Step 1 ➔ Discovery, proposal aur negotiation stages dekhein.\\nStep 2 ➔ Opportunities ko close signal ke mutabiq score karein.\\nStep 3 ➔ Pipeline refresh karke ROI export karein.'},
    8:{name:'Colleague Access Controller',en:'♙ Step 1 ➔ Open a colleague profile and confirm identity.\\nStep 2 ➔ Toggle the 22-module RBAC grid.\\nStep 3 ➔ Use View-As to verify the restricted workspace.',ur:'♙ Step 1 ➔ Colleague profile khol kar identity confirm karein.\\nStep 2 ➔ 22-module RBAC grid mein access toggle karein.\\nStep 3 ➔ Restricted workspace verify karne ke liye View-As use karein.'},
    9:{name:'System Doctor Daemon',en:'♥ Step 1 ➔ Read live latency and worker gauges.\\nStep 2 ➔ Run the full diagnostic probe.\\nStep 3 ➔ Flush safe cache state if telemetry recommends it.',ur:'♥ Step 1 ➔ Live latency aur worker gauges dekhein.\\nStep 2 ➔ Full diagnostic probe chalayein.\\nStep 3 ➔ Telemetry kahe to safe cache flush karein.'},
    10:{name:'Audio Studio & Extractor',en:'♫ Step 1 ➔ Choose an ambient track or upload media.\\nStep 2 ➔ Set clip start and end points.\\nStep 3 ➔ Test the alert chime or open Broadcast Center.',ur:'♫ Step 1 ➔ Ambient track choose ya media upload karein.\\nStep 2 ➔ Clip ka start aur end set karein.\\nStep 3 ➔ Alert chime test ya Broadcast Center kholen.'},
    11:{name:'Built-in AI Guide Agent',en:'▣ Step 1 ➔ Select English or Roman Urdu.\\nStep 2 ➔ Choose one of the 22 workflow runbooks.\\nStep 3 ➔ Play the response or ask a follow-up question.',ur:'▣ Step 1 ➔ English ya Roman Urdu select karein.\\nStep 2 ➔ 22 workflow runbooks mein se ek choose karein.\\nStep 3 ➔ Response play karein ya follow-up sawal poochein.'},
    12:{name:'OAuth Token Vault',en:'⬟ Step 1 ➔ Verify AES-256 locker and master-key telemetry.\\nStep 2 ➔ Check all token renewal states.\\nStep 3 ➔ Run a controlled sync or export an encrypted backup.',ur:'⬟ Step 1 ➔ AES-256 locker aur master-key telemetry verify karein.\\nStep 2 ➔ Sab tokens ki renewal state check karein.\\nStep 3 ➔ Controlled sync ya encrypted backup export karein.'},
    13:{name:'Timezone Scheduler',en:'◷ Step 1 ➔ Review live clocks for each region.\\nStep 2 ➔ Preview the business-hour dispatch queue.\\nStep 3 ➔ Apply jitter and release only the safe window.',ur:'◷ Step 1 ➔ Har region ki live clocks dekhein.\\nStep 2 ➔ Business-hour dispatch queue preview karein.\\nStep 3 ➔ Jitter apply karke sirf safe window release karein.'},
    14:{name:'Bounce Shield',en:'◢ Step 1 ➔ Inspect bounce and suppression signals.\\nStep 2 ➔ Sanitize the outgoing queue.\\nStep 3 ➔ Export the protected suppression list for audit.',ur:'◢ Step 1 ➔ Bounce aur suppression signals inspect karein.\\nStep 2 ➔ Outgoing queue sanitize karein.\\nStep 3 ➔ Protected suppression list audit ke liye export karein.'},
    15:{name:'Auto-Reply Detector',en:'↶ Step 1 ➔ Run the inbox sentiment classifier.\\nStep 2 ➔ Review uncertain replies.\\nStep 3 ➔ Push approved positive intent into the CRM.',ur:'↶ Step 1 ➔ Inbox sentiment classifier chalayein.\\nStep 2 ➔ Uncertain replies review karein.\\nStep 3 ➔ Approved positive intent CRM mein push karein.'},
    16:{name:'CSV / Excel Exporter',en:'⇥ Step 1 ➔ Select the report scope and time range.\\nStep 2 ➔ Build CSV, Excel, or TXT output.\\nStep 3 ➔ Confirm freshness before downloading the report.',ur:'⇥ Step 1 ➔ Report scope aur time range select karein.\\nStep 2 ➔ CSV, Excel ya TXT output banayein.\\nStep 3 ➔ Download se pehle freshness confirm karein.'},
    17:{name:'Broadcast Notification Node',en:'⚑ Step 1 ➔ Choose all displays or one recipient.\\nStep 2 ➔ Add a priority message and optional chime.\\nStep 3 ➔ Send, then review acknowledgement state.',ur:'⚑ Step 1 ➔ Sab displays ya ek recipient choose karein.\\nStep 2 ➔ Priority message aur optional chime add karein.\\nStep 3 ➔ Send karke acknowledgement state dekhein.'},
    18:{name:'Brand Palette Studio',en:'✾ Step 1 ➔ Choose an executive theme preset.\\nStep 2 ➔ Tune font, weight, tracking, and italic state.\\nStep 3 ➔ Apply the palette and review the full workspace.',ur:'✾ Step 1 ➔ Executive theme preset choose karein.\\nStep 2 ➔ Font, weight, tracking aur italic tune karein.\\nStep 3 ➔ Palette apply karke poora workspace review karein.'},
    19:{name:'Cloud Webhook Dispatcher',en:'⌘ Step 1 ➔ Inspect endpoint health and signatures.\\nStep 2 ➔ Send a signed test JSON payload.\\nStep 3 ➔ Replay safe retries and confirm a 200 response.',ur:'⌘ Step 1 ➔ Endpoint health aur signatures inspect karein.\\nStep 2 ➔ Signed test JSON payload bhejein.\\nStep 3 ➔ Safe retries replay karke 200 response confirm karein.'},
    20:{name:'Daily Quota Guard',en:'◉ Step 1 ➔ Review account caps and used volume.\\nStep 2 ➔ Recalculate safe-send pacing.\\nStep 3 ➔ Lock overage before the daily ceiling is reached.',ur:'◉ Step 1 ➔ Account caps aur used volume dekhein.\\nStep 2 ➔ Safe-send pacing recalculate karein.\\nStep 3 ➔ Daily ceiling se pehle overage lock karein.'},
    21:{name:'Security Audit Stream',en:'≋ Step 1 ➔ Open immutable access events.\\nStep 2 ➔ Run a threat-signal scan.\\nStep 3 ➔ Export a signed audit record for evidence.',ur:'≋ Step 1 ➔ Immutable access events kholen.\\nStep 2 ➔ Threat-signal scan chalayein.\\nStep 3 ➔ Evidence ke liye signed audit record export karein.'},
    22:{name:'Enterprise Sync Engine',en:'⇄ Step 1 ➔ Review connected systems and drift.\\nStep 2 ➔ Run a full bi-directional reconciliation.\\nStep 3 ➔ Inspect exceptions and confirm aligned records.',ur:'⇄ Step 1 ➔ Connected systems aur drift review karein.\\nStep 2 ➔ Full bi-directional reconciliation chalayein.\\nStep 3 ➔ Exceptions inspect karke aligned records confirm karein.'}
};
let selectedTheme = 'midnight';
let ambientContext = null;
let ambientNodes = [];
let soundscapePlaying = false;
let customMediaUrl = null;
const AI_VOICE_PRESETS = {
    hamza:{label:'Hamza · مردانہ', gender:'male', pitch:0.78, rate:0.88},
    ali:{label:'Ali Raza · مردانہ', gender:'male', pitch:0.86, rate:0.92},
    shahbaz:{label:'Shahbaz · مردانہ', gender:'male', pitch:0.72, rate:0.84},
    usman:{label:'Usman · مردانہ', gender:'male', pitch:0.94, rate:0.96},
    bilal:{label:'Bilal · مردانہ', gender:'male', pitch:0.82, rate:1.0},
    fahad:{label:'Fahad · مردانہ', gender:'male', pitch:0.68, rate:0.9},
    ayesha:{label:'Ayesha · زنانہ', gender:'female', pitch:1.22, rate:0.9},
    hira:{label:'Hira · زنانہ', gender:'female', pitch:1.34, rate:0.96},
    sana:{label:'Sana · زنانہ', gender:'female', pitch:1.12, rate:0.86},
    maham:{label:'Maham · زنانہ', gender:'female', pitch:1.42, rate:0.92},
    zoya:{label:'Zoya · زنانہ', gender:'female', pitch:1.28, rate:1.0},
    iqra:{label:'Iqra · زنانہ', gender:'female', pitch:1.08, rate:0.88}
};
let aiLanguage = window.localStorage.getItem('grace-ai-language') || 'ur';
let aiVoice = window.localStorage.getItem('grace-ai-voice') || 'ayesha';
let availableSpeechVoices = [];
let mascotDrag = {active:false, moved:false, startX:0, startY:0, left:0, top:0};
let cropSession = null;

function applyStoredTheme() {
    const stored = window.localStorage.getItem('grace-theme') || 'midnight';
    applyTheme(THEME_PRESETS[stored] ? stored : 'midnight', false);
    applyTypography(false);
    hydrateAccessMap();
    hydrateAILanguage();
    hydrateAIVoices();
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = hydrateAIVoices;
    }
    renderAIGuideLibrary();
    hydrateCustomColors();
    hydrateProfilePhotos();
    hydrateProfileMeta();
    renderAttendanceLedger();
    syncCampaignControls();
    try { notificationItems = JSON.parse(window.localStorage.getItem('grace-notifications') || '[]'); } catch (error) { notificationItems = []; }
    hydrateNotificationSettings();
    renderNotifications();
    initMascotDrag();
    updateViewAs();
    updateThemeButton();
    syncSharedState();
    window.setInterval(syncSharedState, 5000);
}
function applyTheme(name, notify = true) {
    const preset = THEME_PRESETS[name] || THEME_PRESETS.midnight;
    selectedTheme = name;
    document.body.classList.toggle('dark', preset.dark);
    Object.entries({
        '--bg-main': preset.bg, '--bg-card': preset.card, '--text-main': preset.text,
        '--text-muted': preset.muted, '--border-color': preset.border,
        '--accent-blue': preset.accent, '--accent-gold': preset.accent, '--accent-green': preset.green
    }).forEach(([key, value]) => document.body.style.setProperty(key, value));
    window.localStorage.setItem('grace-theme', name);
    updateThemeButton();
    if (notify) showToast(name.charAt(0).toUpperCase() + name.slice(1) + ' theme applied across the workspace.', 'success');
}
function updateThemeButton() {
    const btn = document.getElementById('theme-btn');
    if (btn) btn.innerText = document.body.classList.contains('dark') ? '🌓 Theme: DARK' : '☀️ Theme: LIGHT';
}
function applyTypography(notify = true) {
    const fontSelect = document.getElementById('font-family');
    const weightSelect = document.getElementById('font-weight');
    const trackingSelect = document.getElementById('font-tracking');
    const italicToggle = document.getElementById('font-italic');
    const saved = JSON.parse(window.localStorage.getItem('grace-typography') || '{}');
    const font = fontSelect ? fontSelect.value : (saved.font || 'system');
    const weight = weightSelect ? weightSelect.value : (saved.weight || '600');
    const tracking = trackingSelect ? trackingSelect.value : (saved.tracking || '0');
    const italic = italicToggle ? italicToggle.checked : !!saved.italic;
    const family = font === 'system' ? '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' : '"' + font + '", sans-serif';
    document.body.style.fontFamily = family;
    document.body.style.fontWeight = weight;
    document.body.style.fontStyle = italic ? 'italic' : 'normal';
    document.body.style.letterSpacing = tracking;
    window.localStorage.setItem('grace-typography', JSON.stringify({font, weight, tracking, italic}));
    if (notify) showToast('Typography settings applied to the executive interface.', 'success');
}
function hydrateTypographyControls() {
    const saved = JSON.parse(window.localStorage.getItem('grace-typography') || '{}');
    if (document.getElementById('font-family')) document.getElementById('font-family').value = saved.font || 'system';
    if (document.getElementById('font-weight')) document.getElementById('font-weight').value = saved.weight || '600';
    if (document.getElementById('font-tracking')) document.getElementById('font-tracking').value = saved.tracking || '0';
    if (document.getElementById('font-italic')) document.getElementById('font-italic').checked = !!saved.italic;
}
function showToast(message, tone = 'success') {
    const region = document.getElementById('toast-region');
    if (!region) return;
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + tone;
    const label = document.createElement('span');
    label.className = 'toast-label';
    label.innerText = tone === 'warning' ? 'Attention' : tone === 'info' ? 'System update' : 'Completed';
    const copy = document.createElement('span');
    copy.innerText = message;
    toast.append(label, copy);
    region.appendChild(toast);
    window.setTimeout(() => toast.remove(), 4200);
}
function toggleTheme() {
    applyTheme(document.body.classList.contains('dark') ? 'cloud' : 'midnight');
}
function toggleAudio() {
    const btn = document.getElementById('audio-btn');
    if (btn.innerText.includes('ON')) {
        btn.innerText = '🔇 Audio: OFF';
        stopAmbient();
        showToast('Audio feedback muted for this session.', 'info');
    } else {
        btn.innerText = '🔊 Audio: ON';
        showToast('Audio feedback enabled.', 'success');
    }
}
function openBrandPalette() {
    const modal = document.getElementById('brand-palette-modal');
    if (modal) {
        modal.hidden = false;
        hydrateTypographyControls();
    }
}
function closeBrandPalette() {
    const modal = document.getElementById('brand-palette-modal');
    if (modal) modal.hidden = true;
}
function openActionDialog(title, message, confirmLabel, callback) {
    const dialog = document.getElementById('action-dialog');
    if (!dialog) return;
    document.getElementById('dialog-title').innerText = title;
    document.getElementById('dialog-message').innerText = message;
    document.getElementById('dialog-confirm').innerText = confirmLabel || 'Confirm';
    window.graceDialogCallback = callback;
    dialog.hidden = false;
}
function closeActionDialog() {
    const dialog = document.getElementById('action-dialog');
    if (dialog) dialog.hidden = true;
    window.graceDialogCallback = null;
}
function completeActionDialog() {
    const callback = window.graceDialogCallback;
    closeActionDialog();
    if (callback) callback();
}
function powerOff() {
    openActionDialog('Activate safety lock?', 'This will pause background outreach services until they are explicitly resumed.', 'Activate lock', function() {
        document.body.classList.add('safety-locked');
        showToast('Services paused securely. Safety lock is active.', 'warning');
    });
}
async function manualSync() {
    try {
        const response = await fetch('/gmail-sync', {method:'POST', headers:{Accept:'application/json'}});
        const result = await response.json();
        if (!response.ok || result.state === 'error') throw new Error(result.message || 'Gmail sync failed.');
        await syncSharedState();
        showToast('Gmail inbox sync completed. ' + (result.added || 0) + ' new client message(s) received.', 'success');
    } catch (error) {
        showToast(error.message || 'Gmail sync failed.', 'warning');
    }
}
function pauseOutreach() {
    showToast('All active outreach threads paused across 3 inboxes.', 'warning');
}
function testBroadcast() {
    showToast('Test broadcast packet sent to the monitoring node.', 'success');
}
function openSoundscape() {
    const panel = document.getElementById('soundscape-panel');
    if (panel) panel.hidden = false;
}
function closeSoundscape() {
    const panel = document.getElementById('soundscape-panel');
    if (panel) panel.hidden = true;
}
function selectSoundscape(track) {
    document.querySelectorAll('.soundscape-option').forEach((button) => button.classList.toggle('active', button.dataset.track === track));
    const labels = {focus:'Calm Focus', pulse:'Emerald Pulse', strategy:'Strategic Flow', night:'Night Shift'};
    window.localStorage.setItem('grace-soundscape', track);
    const status = document.getElementById('soundscape-status');
    if (status) status.innerText = labels[track] + ' · Ready';
    if (soundscapePlaying) { stopAmbient(); startAmbient(track); }
    showToast(labels[track] + ' selected for the background soundscape.', 'info');
}
function startAmbient(track) {
    track = track || window.localStorage.getItem('grace-soundscape') || 'focus';
    const frequencies = {focus:[220,330], pulse:[146,220], strategy:[174,261], night:[110,165]};
    try {
        ambientContext = ambientContext || new (window.AudioContext || window.webkitAudioContext)();
        const gain = ambientContext.createGain();
        gain.gain.value = 0.018;
        gain.connect(ambientContext.destination);
        ambientNodes = (frequencies[track] || frequencies.focus).map((frequency, index) => {
            const oscillator = ambientContext.createOscillator();
            oscillator.type = index ? 'sine' : 'triangle';
            oscillator.frequency.value = frequency;
            oscillator.detune.value = index ? 7 : -5;
            oscillator.connect(gain);
            oscillator.start();
            return oscillator;
        });
        soundscapePlaying = true;
        const status = document.getElementById('soundscape-status');
        if (status) status.innerText = ({focus:'Calm Focus', pulse:'Emerald Pulse', strategy:'Strategic Flow', night:'Night Shift'}[track] || 'Calm Focus') + ' · Playing';
        showToast('Background soundscape started.', 'success');
    } catch (error) {
        showToast('Audio playback requires a browser interaction permission.', 'warning');
    }
}
function stopAmbient() {
    ambientNodes.forEach((node) => { try { node.stop(); } catch (error) {} });
    ambientNodes = [];
    soundscapePlaying = false;
    const status = document.getElementById('soundscape-status');
    if (status) status.innerText = 'Soundscape · Paused';
}
function toggleSoundscape() {
    if (soundscapePlaying) stopAmbient(); else startAmbient();
}
function formatSeconds(value) {
    if (!Number.isFinite(value)) return '00:00';
    return String(Math.floor(value / 60)).padStart(2, '0') + ':' + String(Math.floor(value % 60)).padStart(2, '0');
}
function updateMediaTime(media) {
    const start = Number(document.getElementById('clip-start')?.value || 0);
    const end = Number(document.getElementById('clip-end')?.value || media.duration);
    if (end > start && media.currentTime >= end) { media.pause(); media.currentTime = start; }
    const time = document.getElementById('soundscape-time');
    if (time) time.innerText = formatSeconds(media.currentTime) + ' / ' + formatSeconds(media.duration);
}
function loadCustomMedia(event) {
    const file = event.target.files && event.target.files[0];
    const media = document.getElementById('custom-media');
    if (!file || !media) return;
    if (customMediaUrl) URL.revokeObjectURL(customMediaUrl);
    customMediaUrl = URL.createObjectURL(file);
    media.src = customMediaUrl;
    media.hidden = false;
    media.onloadedmetadata = function() {
        document.getElementById('clip-end').value = Math.floor(media.duration || 0);
        document.getElementById('soundscape-status').innerText = file.name + ' · Audio track detected';
        showToast('Local ' + (file.type.startsWith('video') ? 'video soundtrack' : 'audio file') + ' loaded for preview and clipping.', 'success');
    };
    media.ontimeupdate = function() { updateMediaTime(media); };
}
function applyClip() {
    const media = document.getElementById('custom-media');
    if (!media || !media.src) { showToast('Load an audio or video file before applying clip points.', 'warning'); return; }
    const start = Number(document.getElementById('clip-start').value || 0);
    const end = Number(document.getElementById('clip-end').value || media.duration);
    if (end <= start || start < 0) { showToast('Clip end must be greater than clip start.', 'warning'); return; }
    media.currentTime = start;
    showToast('Custom clip applied: ' + formatSeconds(start) + ' to ' + formatSeconds(end) + '.', 'success');
}
function openBroadcast() {
    const panel = document.getElementById('broadcast-panel');
    if (panel) panel.hidden = false;
}
function closeBroadcast() {
    const panel = document.getElementById('broadcast-panel');
    if (panel) panel.hidden = true;
}
function playChime() {
    try {
        const context = new (window.AudioContext || window.webkitAudioContext)();
        [660, 880].forEach((frequency, index) => {
            const oscillator = context.createOscillator();
            const gain = context.createGain();
            oscillator.frequency.value = frequency;
            gain.gain.setValueAtTime(0.06, context.currentTime + index * .12);
            gain.gain.exponentialRampToValueAtTime(.001, context.currentTime + index * .12 + .18);
            oscillator.connect(gain).connect(context.destination);
            oscillator.start(context.currentTime + index * .12);
            oscillator.stop(context.currentTime + index * .12 + .2);
        });
    } catch (error) {}
}
function sendBroadcast() {
    const target = document.getElementById('broadcast-target');
    const message = document.getElementById('broadcast-message');
    const chime = document.getElementById('broadcast-chime');
    const fullscreen = document.getElementById('broadcast-fullscreen');
    const targetText = target.options[target.selectedIndex].text;
    const copy = (message.value || '').trim();
    if (!copy) { showToast('Add an alert message before sending.', 'warning'); return; }
    if (chime.checked) playChime();
    closeBroadcast();
    addLiveNotification({
        id: 'broadcast-' + Date.now(),
        profile: target.value === 'all' ? 'king' : target.value,
        inbox: 'internal.broadcast',
        client: 'Grace Operations',
        snippet: copy,
        body: copy,
        category: 'work',
        createdAt: Math.floor(Date.now() / 1000)
    });
    showToast('Broadcast sent to ' + targetText + '.', 'success');
    if (fullscreen.checked) showBroadcastOverlay(copy, targetText);
}
function showBroadcastOverlay(message, target) {
    document.getElementById('broadcast-overlay-message').innerText = message;
    document.getElementById('broadcast-overlay-target').innerText = 'Target: ' + target;
    document.getElementById('broadcast-overlay').hidden = false;
}
function closeBroadcastOverlay() {
    document.getElementById('broadcast-overlay').hidden = true;
}
function toggleAIAssistant() {
    if (mascotDrag.suppressClick) { mascotDrag.suppressClick = false; return; }
    const drawer = document.getElementById('ai-assistant');
    if (drawer) {
        drawer.classList.toggle('open');
        drawer.setAttribute('aria-hidden', drawer.classList.contains('open') ? 'false' : 'true');
    }
}
function closeAIAssistant() {
    const drawer = document.getElementById('ai-assistant');
    if (drawer) { drawer.classList.remove('open'); drawer.setAttribute('aria-hidden', 'true'); }
}
function appendAIMessage(text, user) {
    const messages = document.getElementById('ai-messages');
    if (!messages) return;
    const block = document.createElement('div');
    block.className = 'ai-response-block';
    const bubble = document.createElement('div');
    bubble.className = 'ai-bubble ' + (user ? 'ai-bubble-user' : 'ai-bubble-bot');
    bubble.innerText = text;
    block.appendChild(bubble);
    if (!user) {
        const audio = document.createElement('button');
        audio.className = 'ai-response-audio';
        audio.innerText = '🔊 Play response';
        audio.onclick = function() { speakText(bubble.innerText, audio); };
        block.appendChild(audio);
    }
    messages.appendChild(block);
    messages.scrollTop = messages.scrollHeight;
}
function askAI(question, forcedModule) {
    const input = document.getElementById('ai-input');
    if (input) input.value = question;
    sendAIMessage(forcedModule);
}
function sendAIMessage() {
    const input = document.getElementById('ai-input');
    const question = (input?.value || '').trim();
    if (!question) return;
    appendAIMessage(question, true);
    input.value = '';
    const lower = question.toLowerCase();
    let answer = 'English: Open the module from the matrix, review its live status, then use the execution toolbar for the next safe action.\\n\\nRoman Urdu: Matrix se module kholen, live status dekhen, phir execution toolbar se agla mehfooz action karein.';
    if (lower.includes('12') || lower.includes('oauth') || lower.includes('token')) answer = 'English: Module 12 keeps OAuth credentials in the AES-256-GCM locker. Check renewal health, verify the master-key telemetry, then run a controlled vault sync.\\n\\nRoman Urdu: Module 12 OAuth credentials ko AES-256-GCM locker mein mehfooz rakhta hai. Renewal health check karein, master-key telemetry dekhein, phir controlled vault sync chalayein.';
    else if (lower.includes('access') || lower.includes('restrict')) answer = 'English: Use View-As below the navigation to preview a colleague. Restricted modules remain visible with a lock treatment so the admin can explain access clearly.\\n\\nRoman Urdu: Navigation ke neeche View-As se colleague ka view dekhein. Restricted modules lock ke saath nazar aate hain taake access asani se samjhaya ja sake.';
    else if (lower.includes('audio') || lower.includes('sound')) answer = 'English: Open Soundscape, choose a track, or load a local audio/video file. Set start and end seconds, then apply the clip.\\n\\nRoman Urdu: Soundscape kholen, track select karein ya local audio/video load karein. Start aur end seconds set karke clip apply karein.';
    window.setTimeout(() => appendAIMessage(answer, false), 220);
}
function setAILanguage(value) {
    aiLanguage = value === 'ur' ? 'ur' : 'en';
    window.localStorage.setItem('grace-ai-language', aiLanguage);
    const input = document.getElementById('ai-input');
    if (input) input.placeholder = aiLanguage === 'ur' ? 'اردو میں سوال پوچھیں...' : 'Ask in English...';
    showToast(aiLanguage === 'ur' ? 'Urdu guidance selected.' : 'English guidance selected.', 'info');
}
function hydrateAILanguage() {
    const selector = document.getElementById('ai-language');
    if (selector) selector.value = aiLanguage;
}
function hydrateAIVoices() {
    if (!('speechSynthesis' in window)) return;
    availableSpeechVoices = window.speechSynthesis.getVoices() || [];
    const selector = document.getElementById('ai-voice');
    if (!selector) return;
    const current = AI_VOICE_PRESETS[aiVoice] ? aiVoice : 'ayesha';
    selector.innerHTML = '<option value="" disabled>Voice profile</option><optgroup label="مردانہ آوازیں">' +
        Object.entries(AI_VOICE_PRESETS).filter(([, voice]) => voice.gender === 'male').map(([key, voice]) => '<option value="' + key + '">' + voice.label + '</option>').join('') +
        '</optgroup><optgroup label="زنانہ آوازیں">' +
        Object.entries(AI_VOICE_PRESETS).filter(([, voice]) => voice.gender === 'female').map(([key, voice]) => '<option value="' + key + '">' + voice.label + '</option>').join('') +
        '</optgroup>';
    selector.value = current;
    aiVoice = current;
}
function setAIVoice(value) {
    if (!AI_VOICE_PRESETS[value]) return;
    aiVoice = value;
    window.localStorage.setItem('grace-ai-voice', aiVoice);
    showToast(AI_VOICE_PRESETS[aiVoice].label + ' selected for Urdu guidance.', 'info');
}
function renderAIGuideLibrary() {
    const library = document.getElementById('ai-workflow-library');
    if (!library) return;
    library.innerHTML = '';
    Object.entries(MODULE_GUIDES).forEach(([id, guide]) => {
        const button = document.createElement('button');
        button.className = 'ai-workflow-item';
        button.innerHTML = '<b>M' + id + '</b><span>' + guide.name + '</span>';
        button.onclick = function() { askAI('Module ' + id + ' workflow', Number(id)); };
        library.appendChild(button);
    });
}
function findGuideModule(question) {
    const direct = question.match(/(?:module|m)\\s*0*(\\d{1,2})/i);
    if (direct && MODULE_GUIDES[Number(direct[1])]) return Number(direct[1]);
    const lower = question.toLowerCase();
    const terms = {oauth:12, token:12, inbox:2, gmail:2, warmup:3, reputation:3, campaign:4, sequence:4, spinner:5, spintax:5, scraper:6, architect:6, crm:7, revenue:7, rbac:8, access:8, diagnostic:9, system:9, audio:10, soundscape:10, guide:11, timezone:13, scheduler:13, bounce:14, sentiment:15, reply:15, export:16, broadcast:17, palette:18, typography:18, webhook:19, quota:20, security:21, audit:21, sync:22, integration:22};
    for (const term of Object.keys(terms)) if (lower.includes(term)) return terms[term];
    return null;
}
function speakText(text, button) {
    if (!('speechSynthesis' in window)) { showToast('Voice playback is not supported in this browser.', 'warning'); return; }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const preset = AI_VOICE_PRESETS[aiVoice] || AI_VOICE_PRESETS.ayesha;
    utterance.lang = aiLanguage === 'ur' ? 'ur-PK' : 'en-US';
    utterance.rate = preset.rate;
    utterance.pitch = preset.pitch;
    const preferred = availableSpeechVoices.find((voice) => voice.lang.toLowerCase().startsWith('ur')) ||
        availableSpeechVoices.find((voice) => voice.lang.toLowerCase().startsWith('hi'));
    if (preferred) utterance.voice = preferred;
    utterance.onend = function() { if (button) button.innerText = '🔊 Play response'; };
    window.speechSynthesis.speak(utterance);
    if (button) button.innerText = '⏸ Playing response';
}
function sendAIMessage(forcedModule) {
    const input = document.getElementById('ai-input');
    const question = (input?.value || '').trim();
    if (!question) return;
    appendAIMessage(question, true);
    input.value = '';
    const lower = question.toLowerCase();
    const moduleId = forcedModule || findGuideModule(question);
    let answer = aiLanguage === 'ur'
        ? '🧭 Step 1 ➔ Matrix se module select karein.\\nStep 2 ➔ Live telemetry review karein.\\nStep 3 ➔ Execution toolbar se safe action karein.'
        : '🧭 Step 1 ➔ Select a module from the matrix.\\nStep 2 ➔ Review live telemetry.\\nStep 3 ➔ Use the execution toolbar for a safe action.';
    if (moduleId && MODULE_GUIDES[moduleId]) answer = MODULE_GUIDES[moduleId][aiLanguage];
    else if (lower.includes('restrict') || lower.includes('permission')) answer = aiLanguage === 'ur'
        ? '🔐 Step 1 ➔ Navigation ke neeche View-As picker kholen.\\nStep 2 ➔ Colleague workspace select karein.\\nStep 3 ➔ Sirf authorized modules aur adjusted dashboard metrics dekhein.'
        : '🔐 Step 1 ➔ Open the View-As picker below navigation.\\nStep 2 ➔ Select a colleague workspace.\\nStep 3 ➔ Review only authorized modules and adjusted dashboard metrics.';
    window.setTimeout(() => appendAIMessage(answer, false), 220);
}
function speakGuide() {
    if (!('speechSynthesis' in window)) { showToast('Voice playback is not supported in this browser.', 'warning'); return; }
    const text = document.getElementById('ai-messages')?.innerText || 'Grace AI Guide is ready.';
    speakText(text);
    showToast('Voice guidance started.', 'info');
}
function updateViewAs() {
    const picker = document.getElementById('view-as-picker');
    const value = window.localStorage.getItem('grace-view-as') || 'king';
    if (picker) picker.value = value;
    const label = document.getElementById('view-as-label');
    if (label) label.innerText = picker ? picker.options[picker.selectedIndex].text : 'King Saab · Super Admin';
    const allowed = ACCESS_MAP[value] || ACCESS_MAP.king;
    document.querySelectorAll('.module-card[data-module-id]').forEach((card) => {
        const id = Number(card.dataset.moduleId);
        const restricted = !allowed.includes(id);
        card.classList.toggle('is-restricted', restricted);
        card.setAttribute('aria-label', restricted ? 'Restricted module ' + id : 'Open module ' + id);
        card.onclick = function(event) {
            if (restricted) { event.preventDefault(); showToast('Module ' + id + ' is restricted in this colleague view.', 'warning'); }
        };
    });
}
function hydrateAccessMap() {
    try {
        const saved = JSON.parse(window.localStorage.getItem('grace-access-map') || '{}');
        Object.keys(saved).forEach((key) => { if (Array.isArray(saved[key])) ACCESS_MAP[key] = saved[key]; });
    } catch (error) {}
}
function updateViewAs() {
    const picker = document.getElementById('view-as-picker');
    const value = window.localStorage.getItem('grace-view-as') || 'king';
    if (picker) picker.value = value;
    const profile = PROFILE_DATA[value] || PROFILE_DATA.king;
    const label = document.getElementById('view-as-label');
    if (label) label.innerText = profile.name + ' · ' + profile.role;
    const activeName = document.getElementById('active-profile-name');
    const activeBadge = document.getElementById('active-profile-badge');
    if (activeName) activeName.innerText = profile.name + ' · ' + profile.role;
    if (activeBadge) activeBadge.innerText = profile.name + ' · ' + profile.role;
    const verified = value === 'king';
    document.getElementById('active-profile-crown')?.toggleAttribute('hidden', !verified);
    document.getElementById('session-crown')?.toggleAttribute('hidden', !verified);
    const activeChip = document.getElementById('active-profile-chip');
    if (activeChip) activeChip.querySelector('.presence-dot')?.classList.toggle('online', profile.status === 'Online');
    document.body.dataset.activeProfile = value;
    const allowed = ACCESS_MAP[value] || ACCESS_MAP.king;
    const scope = document.getElementById('active-scope-count');
    if (scope) scope.innerText = allowed.length === 22 ? 'All 22 modules enabled' : allowed.length + ' of 22 modules enabled';
    Object.entries(profile.metrics).forEach(([key, metric]) => {
        const target = document.querySelector('[data-metric-key="' + key + '"]');
        if (target) target.innerText = metric;
    });
    document.querySelectorAll('.module-card[data-module-id]').forEach((card) => {
        const id = Number(card.dataset.moduleId);
        const restricted = !allowed.includes(id);
        card.classList.toggle('is-restricted', restricted);
        card.setAttribute('aria-hidden', restricted ? 'true' : 'false');
        card.onclick = function(event) {
            if (restricted) { event.preventDefault(); showToast('Module ' + id + ' is restricted in this colleague view.', 'warning'); }
        };
    });
    document.querySelectorAll('[data-required-module]').forEach((control) => {
        control.hidden = !allowed.includes(Number(control.dataset.requiredModule));
    });
    const modulePage = document.querySelector('[data-module-page-id]');
    if (modulePage) {
        const moduleId = Number(modulePage.dataset.modulePageId);
        const restricted = !allowed.includes(moduleId);
        modulePage.querySelector('.module-authorized-content')?.toggleAttribute('hidden', restricted);
        modulePage.querySelector('.module-access-denied')?.toggleAttribute('hidden', !restricted);
    }
}
function changeViewAs(value) {
    window.localStorage.setItem('grace-view-as', value);
    updateViewAs();
    const picker = document.getElementById('view-as-picker');
    showToast('Previewing ' + picker.options[picker.selectedIndex].text + '.', 'info');
}
function previewColleaguePhoto(event, targetId) {
    const file = event.target.files && event.target.files[0];
    const target = document.getElementById(targetId);
    if (!file || !target) return;
    const reader = new FileReader();
    reader.onload = function() {
        if (target.tagName === 'IMG') target.src = reader.result;
        else {
            target.style.backgroundImage = 'url("' + reader.result + '")';
            target.style.backgroundSize = 'cover';
            target.style.backgroundPosition = 'center';
            target.innerText = '';
        }
        target.dataset.uploaded = 'true';
    };
    reader.readAsDataURL(file);
    showToast('Profile picture preview updated locally.', 'success');
}
function openColleagueProfile(name, softwareId, role, tags, initials) {
    const modal = document.getElementById('colleague-profile-modal');
    const body = document.getElementById('profile-modal-body');
    if (!modal || !body) return;
    document.getElementById('profile-title').innerText = name + ' · Profile & Access';
    body.innerHTML = '<div class="profile-details"><div><div id="profile-photo-preview" class="profile-photo">' + initials + '</div><label class="upload-zone profile-upload"><span>＋ Upload profile picture</span><small>Local preview only until connected storage is enabled.</small><input type="file" accept="image/*" onchange="previewProfilePhoto(event)"></label></div><div class="profile-summary"><strong>' + name + '</strong><small>' + role + '</small><small>Software ID · <b>' + softwareId + '</b></small><div class="tag-list">' + tags.split(',').map(function(tag) { return '<span class="tag">' + tag + '</span>'; }).join('') + '</div><div class="permission-card"><div class="permission-card-head"><strong>Access summary</strong><small>Managed by Super Admin</small></div><p style="margin:0;color:var(--text-muted);font-size:11px;line-height:1.5;">Permissions are controlled from the RBAC matrix on the colleague card. Use View-As to preview the exact restricted workspace.</p></div></div></div>';
    modal.hidden = false;
}
function closeColleagueProfile() {
    const modal = document.getElementById('colleague-profile-modal');
    if (modal) modal.hidden = true;
}
function previewProfilePhoto(event) {
    const file = event.target.files && event.target.files[0];
    const target = document.getElementById('profile-photo-preview');
    if (!file || !target) return;
    const reader = new FileReader();
    reader.onload = function() { target.innerHTML = '<img class="profile-photo" alt="Uploaded profile picture" src="' + reader.result + '">'; };
    reader.readAsDataURL(file);
    showToast('Profile picture preview updated locally.', 'success');
}
function savePermission(colleague, moduleId, enabled) {
    ACCESS_MAP[colleague] = ACCESS_MAP[colleague] || [];
    ACCESS_MAP[colleague] = enabled
        ? Array.from(new Set(ACCESS_MAP[colleague].concat(moduleId))).sort((a,b) => a-b)
        : ACCESS_MAP[colleague].filter((id) => id !== moduleId);
    window.localStorage.setItem('grace-access-map', JSON.stringify(ACCESS_MAP));
    if ((window.localStorage.getItem('grace-view-as') || 'king') === colleague) updateViewAs();
    showToast('Module ' + moduleId + ' ' + (enabled ? 'enabled for ' : 'restricted for ') + colleague + '.', enabled ? 'success' : 'warning');
}
function initMascotDrag() {
    const mascot = document.getElementById('ai-mascot');
    if (!mascot || mascot.dataset.dragReady) return;
    mascot.dataset.dragReady = 'true';
    mascot.addEventListener('pointerdown', function(event) {
        mascotDrag.active = true; mascotDrag.moved = false;
        mascotDrag.startX = event.clientX; mascotDrag.startY = event.clientY;
        const rect = mascot.getBoundingClientRect(); mascotDrag.left = rect.left; mascotDrag.top = rect.top;
        mascot.setPointerCapture?.(event.pointerId);
    });
    mascot.addEventListener('pointermove', function(event) {
        if (!mascotDrag.active) return;
        const dx = event.clientX - mascotDrag.startX; const dy = event.clientY - mascotDrag.startY;
        if (Math.abs(dx) + Math.abs(dy) > 5) mascotDrag.moved = true;
        if (!mascotDrag.moved) return;
        mascot.style.left = Math.max(8, Math.min(window.innerWidth - mascot.offsetWidth - 8, mascotDrag.left + dx)) + 'px';
        mascot.style.top = Math.max(8, Math.min(window.innerHeight - mascot.offsetHeight - 8, mascotDrag.top + dy)) + 'px';
        mascot.style.right = 'auto'; mascot.style.bottom = 'auto';
    });
    mascot.addEventListener('pointerup', function() {
        if (mascotDrag.moved) mascotDrag.suppressClick = true;
        mascotDrag.active = false;
    });
}
function hydrateCustomColors() {
    const saved = JSON.parse(window.localStorage.getItem('grace-custom-colors') || '{}');
    const nav = saved.nav || '#00110F';
    const background = saved.background || '#0B1120';
    document.body.style.setProperty('--nav-color', nav);
    document.body.style.setProperty('--bg-main', background);
    const navPicker = document.getElementById('nav-color-picker');
    const bgPicker = document.getElementById('background-color-picker');
    if (navPicker) navPicker.value = nav;
    if (bgPicker) bgPicker.value = background;
}
function applyCustomColors() {
    const nav = document.getElementById('nav-color-picker')?.value || '#00110F';
    const background = document.getElementById('background-color-picker')?.value || '#0B1120';
    document.body.style.setProperty('--nav-color', nav);
    document.body.style.setProperty('--bg-main', background);
    window.localStorage.setItem('grace-custom-colors', JSON.stringify({nav, background}));
    showToast('Navbar ribbon and app background colors applied.', 'success');
}
function setAvatarImage(key, data) {
    document.querySelectorAll('[data-profile-avatar="' + key + '"]').forEach((target) => {
        target.style.backgroundImage = 'url("' + data + '")';
        target.style.backgroundSize = 'cover';
        target.style.backgroundPosition = 'center';
        target.innerText = '';
        target.dataset.uploaded = 'true';
    });
}
function hydrateProfilePhotos() {
    try {
        const photos = JSON.parse(window.localStorage.getItem('grace-profile-photos') || '{}');
        Object.keys(photos).forEach((key) => setAvatarImage(key, photos[key]));
    } catch (error) {}
}
function hydrateProfileMeta() {
    const meta = getProfileMeta();
    Object.entries(meta).forEach(([key, profile]) => {
        PROFILE_DATA[key] = Object.assign(PROFILE_DATA[key] || {}, {
            name: profile.name || PROFILE_DATA[key]?.name,
            state: profile.state || PROFILE_DATA[key]?.state,
            status: profile.presence || PROFILE_DATA[key]?.status,
            contractorStates: profile.contractorStates || []
        });
        document.querySelectorAll('[data-profile-name="' + key + '"]').forEach((target) => { target.innerText = profile.name; });
        document.querySelectorAll('[data-profile-state="' + key + '"]').forEach((target) => { target.innerText = profile.state; });
        document.querySelectorAll('[data-profile-presence="' + key + '"]').forEach((target) => {
            const dot = target.querySelector('.presence-dot');
            const label = target.querySelector('.profile-presence-label');
            if (dot) dot.classList.toggle('online', profile.presence === 'Online');
            if (label) label.innerText = profile.presence;
        });
    });
    const picker = document.getElementById('view-as-picker');
    if (picker) Array.from(picker.options).forEach((option) => {
        const profile = meta[option.value];
        if (profile) option.innerText = profile.name + ' · ' + profile.role + (option.value === 'king' ? ' · All 22' : '');
    });
}
function openCropEditor(key, file) {
    if (!file || !file.type.startsWith('image/')) { showToast('Choose an image file for the profile picture.', 'warning'); return; }
    if (file.size > 10000000) { showToast('Choose an image smaller than 10 MB.', 'warning'); return; }
    const image = new Image();
    const sourceUrl = URL.createObjectURL(file);
    image.onload = function() {
        cropSession = {key, image, sourceUrl, zoom:1, x:50, y:50};
        const modal = document.getElementById('photo-crop-modal');
        if (modal) modal.hidden = false;
        updateCropPreview();
    };
    image.onerror = function() { URL.revokeObjectURL(sourceUrl); showToast('This image could not be opened for cropping.', 'warning'); };
    image.src = sourceUrl;
}
function updateCropPreview() {
    if (!cropSession) return;
    const canvas = document.getElementById('crop-canvas');
    if (!canvas) return;
    const context = canvas.getContext('2d');
    const image = cropSession.image;
    const cropSize = Math.min(image.naturalWidth, image.naturalHeight) / cropSession.zoom;
    const maxX = Math.max(0, image.naturalWidth - cropSize);
    const maxY = Math.max(0, image.naturalHeight - cropSize);
    const sx = maxX * (cropSession.x / 100);
    const sy = maxY * (cropSession.y / 100);
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, sx, sy, cropSize, cropSize, 0, 0, canvas.width, canvas.height);
    const zoom = document.getElementById('crop-zoom');
    const horizontal = document.getElementById('crop-horizontal');
    const vertical = document.getElementById('crop-vertical');
    if (zoom) zoom.value = cropSession.zoom;
    if (horizontal) horizontal.value = cropSession.x;
    if (vertical) vertical.value = cropSession.y;
}
function updateCropSetting(name, value) {
    if (!cropSession) return;
    cropSession[name] = Number(value);
    updateCropPreview();
}
function cancelCropEditor() {
    if (cropSession?.sourceUrl) URL.revokeObjectURL(cropSession.sourceUrl);
    cropSession = null;
    const modal = document.getElementById('photo-crop-modal');
    if (modal) modal.hidden = true;
}
function saveCroppedPhoto() {
    if (!cropSession) return;
    const canvas = document.getElementById('crop-canvas');
    if (!canvas) return;
    canvas.toBlob(function(blob) {
        if (!blob) { showToast('The cropped image could not be created.', 'warning'); return; }
        const key = cropSession.key;
        cancelCropEditor();
        persistProfilePhoto(key, blob);
    }, 'image/jpeg', 0.88);
}
function persistProfilePhoto(key, file, onDone) {
    if (!file || !file.type.startsWith('image/')) { showToast('Choose an image file for the profile picture.', 'warning'); return; }
    if (file.size > 3000000) { showToast('Profile images must be smaller than 3 MB.', 'warning'); return; }
    const reader = new FileReader();
    reader.onload = function() {
        try {
            const photos = JSON.parse(window.localStorage.getItem('grace-profile-photos') || '{}');
            photos[key] = reader.result;
            window.localStorage.setItem('grace-profile-photos', JSON.stringify(photos));
            setAvatarImage(key, reader.result);
            publishSharedState('photos', reader.result, key);
            if (onDone) onDone(reader.result);
            showToast('Profile picture cropped and saved for future visits.', 'success');
        } catch (error) {
            showToast('The image could not be saved. Try a smaller file.', 'warning');
        }
    };
    reader.readAsDataURL(file);
}
function previewColleaguePhoto(event, targetId) {
    const file = event.target.files && event.target.files[0];
    const target = document.getElementById(targetId);
    const key = targetId ? targetId.replace('avatar-', '') : '';
    if (!file || !target || !key) return;
    openCropEditor(key, file);
}
function openColleagueProfile(key, name, softwareId, role, tags, initials) {
    const modal = document.getElementById('colleague-profile-modal');
    const body = document.getElementById('profile-modal-body');
    if (!modal || !body) return;
    const meta = getProfileMeta()[key] || PROFILE_META_SEED[key];
    document.getElementById('profile-title').innerText = (meta.name || name) + ' · Profile & Settings';
    body.innerHTML = '<div class="profile-details"><div><div id="profile-photo-preview" class="profile-photo" data-profile-avatar="' + key + '">' + initials + '</div><label class="upload-zone profile-upload"><span>＋ Upload and crop profile picture</span><small>Saved to shared workspace state and restored after refresh.</small><input type="file" accept="image/*" onchange="previewProfilePhoto(event, &quot;' + key + '&quot;)"></label></div><div class="profile-summary"><strong data-modal-profile-name>' + (meta.name || name) + '</strong><small>' + role + ' · ' + softwareId + '</small><div class="profile-form-grid"><label>Display name<input id="profile-display-name" type="text" maxlength="80"></label><label>Presence<select id="profile-presence"><option>Online</option><option>Away</option><option>Offline</option></select></label><label class="full">Work state<input id="profile-work-state" type="text" maxlength="80" placeholder="Pakistan"></label><label class="full">Contractor coverage <small class="profile-form-note">Choose up to two active US states for this colleague or module. Changes sync live across workspaces.</small><select id="profile-contractor-states" multiple size="6">' + US_STATES.map(function(stateName) { return '<option value="' + stateName + '">' + stateName + '</option>'; }).join('') + '</select></label></div><div class="permission-card"><div class="permission-card-head"><strong>Access summary</strong><small>Managed by Super Admin</small></div><p style="margin:0;color:var(--text-muted);font-size:11px;line-height:1.5;">Use the RBAC matrix on the colleague card to control module access. This profile panel controls identity, presence, work state, and contractor coverage.</p></div><div class="dialog-actions"><button class="btn btn-gray" onclick="closeColleagueProfile()">Cancel</button><button class="btn btn-blue" onclick="saveProfileSettings(&quot;' + key + '&quot;)">Save profile settings</button></div></div></div>';
    document.getElementById('profile-display-name').value = meta.name || name;
    document.getElementById('profile-work-state').value = meta.state || 'Pakistan';
    document.getElementById('profile-presence').value = meta.presence || 'Online';
    Array.from(document.getElementById('profile-contractor-states').options).forEach(function(option) {
        option.selected = (meta.contractorStates || []).includes(option.value);
    });
    modal.hidden = false;
    hydrateProfilePhotos();
}
function previewProfilePhoto(event, key) {
    const file = event.target.files && event.target.files[0];
    if (!file || !key) return;
    openCropEditor(key, file);
}
function saveProfileSettings(key) {
    const meta = getProfileMeta();
    const name = (document.getElementById('profile-display-name')?.value || '').trim();
    const state = (document.getElementById('profile-work-state')?.value || '').trim();
    const presence = document.getElementById('profile-presence')?.value || 'Online';
    const contractorStates = Array.from(document.getElementById('profile-contractor-states')?.selectedOptions || []).map((option) => option.value);
    if (name.length < 2) { showToast('Add a display name before saving.', 'warning'); return; }
    if (state.length < 2) { showToast('Add the colleague work state before saving.', 'warning'); return; }
    if (contractorStates.length > 2) { showToast('Only two contractor states can be active at one time.', 'warning'); return; }
    meta[key] = Object.assign({}, meta[key] || PROFILE_META_SEED[key], {name, state, presence, contractorStates});
    window.localStorage.setItem('grace-profile-meta', JSON.stringify(meta));
    publishSharedState('profiles', meta[key], key);
    hydrateProfileMeta();
    updateViewAs();
    showToast('Profile and workspace settings saved for ' + name + '.', 'success');
    closeColleagueProfile();
}
function getAttendanceState() {
    let state;
    try { state = JSON.parse(window.localStorage.getItem('grace-attendance') || 'null'); } catch (error) { state = null; }
    if (!state) state = JSON.parse(JSON.stringify(ATTENDANCE_SEED));
    return state;
}
function getLeaveState() {
    let state;
    try { state = JSON.parse(window.localStorage.getItem('grace-leave-requests') || 'null'); } catch (error) { state = null; }
    return state || JSON.parse(JSON.stringify(LEAVE_SEED));
}
function updateAttendanceAccess() {
    const isAdmin = (window.localStorage.getItem('grace-view-as') || 'king') === 'king';
    document.querySelectorAll('[data-admin-only]').forEach((control) => {
        control.disabled = !isAdmin;
        control.title = isAdmin ? 'Super Admin control' : 'Restricted to Super Admin';
    });
}
function renderAttendanceLedger() {
    const ledger = document.querySelector('.attendance-card');
    if (!ledger) return;
    const state = getAttendanceState();
    const leaves = getLeaveState();
    const cleared = JSON.parse(window.localStorage.getItem('grace-cleared-fines') || '{}');
    let totalFine = 0;
    let totalAbsences = 0;
    let pendingLeaves = 0;
    Object.keys(state).forEach((key) => {
        const values = state[key] || {};
        const absences = Object.values(values).filter((status) => status === 'absent').length;
        totalAbsences += absences;
        const fine = cleared[key] ? 0 : absences * 150;
        totalFine += fine;
        const balance = document.querySelector('[data-fine-key="' + key + '"]');
        if (balance) balance.innerText = fine + ' PKR';
        Object.keys(values).forEach((day) => {
            const select = document.querySelector('[data-attendance-person="' + key + '"][data-attendance-day="' + day + '"]');
            if (select) select.value = values[day];
        });
    });
    Object.values(leaves).forEach((request) => { if (request.state === 'received') pendingLeaves += 1; });
    const total = document.getElementById('attendance-total-fines');
    const absences = document.getElementById('attendance-total-absences');
    const pending = document.getElementById('attendance-pending-leaves');
    if (total) total.innerText = totalFine + ' PKR';
    if (absences) absences.innerText = String(totalAbsences);
    if (pending) pending.innerText = pendingLeaves + ' pending';
    Object.keys(leaves).forEach((key) => {
        const request = leaves[key];
        const start = document.querySelector('[data-leave-date="' + key + '-start"]');
        const end = document.querySelector('[data-leave-date="' + key + '-end"]');
        const select = document.querySelector('[data-leave-state="' + key + '"]');
        if (start) start.value = request.start;
        if (end) end.value = request.end;
        if (select) select.value = request.state;
    });
    updateAttendanceAccess();
}
function updateAttendance(select) {
    if ((window.localStorage.getItem('grace-view-as') || 'king') !== 'king') { showToast('Attendance edits are restricted to Super Admin.', 'warning'); renderAttendanceLedger(); return; }
    const state = getAttendanceState();
    const key = select.dataset.attendancePerson;
    const day = select.dataset.attendanceDay;
    state[key] = state[key] || {};
    state[key][day] = select.value;
    if (select.value === 'absent') {
        const cleared = JSON.parse(window.localStorage.getItem('grace-cleared-fines') || '{}');
        delete cleared[key];
        window.localStorage.setItem('grace-cleared-fines', JSON.stringify(cleared));
        publishSharedState('clearedFines', cleared);
    }
    window.localStorage.setItem('grace-attendance', JSON.stringify(state));
    publishSharedState('attendance', {[key]: state[key]});
    renderAttendanceLedger();
    showToast('Attendance ledger updated and fine balance recalculated.', 'success');
}
function clearFine(key) {
    if ((window.localStorage.getItem('grace-view-as') || 'king') !== 'king') { showToast('Only Super Admin can clear fines.', 'warning'); return; }
    const cleared = JSON.parse(window.localStorage.getItem('grace-cleared-fines') || '{}');
    cleared[key] = true;
    window.localStorage.setItem('grace-cleared-fines', JSON.stringify(cleared));
    publishSharedState('clearedFines', cleared);
    renderAttendanceLedger();
    showToast('Fine balance cleared to zero for ' + key + '.', 'success');
}
function clearAllFines() {
    if ((window.localStorage.getItem('grace-view-as') || 'king') !== 'king') { showToast('Only Super Admin can clear fines.', 'warning'); return; }
    const cleared = {};
    Object.keys(ATTENDANCE_SEED).forEach((key) => { cleared[key] = true; });
    window.localStorage.setItem('grace-cleared-fines', JSON.stringify(cleared));
    publishSharedState('clearedFines', cleared);
    renderAttendanceLedger();
    showToast('All reviewed absence fines cleared to zero.', 'success');
}
function updateLeaveState(select) {
    if ((window.localStorage.getItem('grace-view-as') || 'king') !== 'king') { showToast('Leave approval is restricted to Super Admin.', 'warning'); renderAttendanceLedger(); return; }
    const leaves = getLeaveState();
    const key = select.dataset.leaveState;
    leaves[key] = leaves[key] || {};
    leaves[key].state = select.value;
    const start = document.querySelector('[data-leave-date="' + key + '-start"]');
    const end = document.querySelector('[data-leave-date="' + key + '-end"]');
    if (start) leaves[key].start = start.value;
    if (end) leaves[key].end = end.value;
    window.localStorage.setItem('grace-leave-requests', JSON.stringify(leaves));
    publishSharedState('leaves', {[key]: leaves[key]});
    renderAttendanceLedger();
    showToast('Leave request marked ' + (select.value === 'approved' ? 'Approved' : 'Received') + '.', 'success');
}
function requestLeave(key) {
    const leaves = getLeaveState();
    leaves[key] = leaves[key] || {start:'2026-09-07', end:'2026-09-07'};
    leaves[key].state = 'received';
    window.localStorage.setItem('grace-leave-requests', JSON.stringify(leaves));
    publishSharedState('leaves', {[key]: leaves[key]});
    renderAttendanceLedger();
    showToast('Leave request received for admin review.', 'info');
}
function changeViewAs(value) {
    window.localStorage.setItem('grace-view-as', value);
    updateViewAs();
    updateAttendanceAccess();
    const profile = PROFILE_DATA[value] || PROFILE_DATA.king;
    showToast('Active workspace switched to ' + profile.name + ' · ' + profile.role + '.', 'info');
}
let dispatchEvaluation = null;
function syncDispatchEnd(value) {
    const end = document.getElementById('dispatch-end');
    const label = document.getElementById('dispatch-range-label');
    if (end) end.value = value;
    if (label) label.innerText = (document.getElementById('dispatch-start')?.value || 1) + ' → ' + value;
}
function syncDispatchSlider(value) {
    const slider = document.getElementById('dispatch-range-slider');
    const label = document.getElementById('dispatch-range-label');
    if (slider) slider.value = value;
    if (label) label.innerText = (document.getElementById('dispatch-start')?.value || 1) + ' → ' + value;
}
function syncCampaignControls() {
    const end = document.getElementById('dispatch-end');
    if (end) syncDispatchSlider(end.value);
}
function setDispatchCheck(id, text, tone) {
    const target = document.getElementById(id);
    if (!target) return;
    target.innerText = text;
    target.classList.remove('is-ready', 'is-warning');
    if (tone) target.classList.add(tone);
}
function evaluateDispatch() {
    const start = Number(document.getElementById('dispatch-start')?.value || 0);
    const end = Number(document.getElementById('dispatch-end')?.value || 0);
    if (start < 1 || end < start || end > 1000) { showToast('Choose a valid dispatch range from 1 to 1000.', 'warning'); return false; }
    const count = end - start + 1;
    const risk = count > 750 ? '1.2% · Review recommended' : '0.7% · Passed';
    setDispatchCheck('dispatch-health', '✓ Sender profile · 98% healthy', 'is-ready');
    setDispatchCheck('dispatch-spam', '✓ Spam safety · ' + risk, count > 750 ? 'is-warning' : 'is-ready');
    setDispatchCheck('dispatch-jitter', '✓ Human jitter · 3–12s per send', 'is-ready');
    dispatchEvaluation = {start, end, count, risk};
    const result = document.getElementById('dispatch-result');
    if (result) result.innerText = count + ' records are staged. Sender health, safety checks, and randomized jitter are ready.';
    return true;
}
function executeCampaignDispatch() {
    if (!dispatchEvaluation && !evaluateDispatch()) return;
    const jitter = Math.floor(Math.random() * 10) + 3;
    const result = document.getElementById('dispatch-result');
    if (result) result.innerText = 'Dispatch queued for records ' + dispatchEvaluation.start + '–' + dispatchEvaluation.end + ' with ' + jitter + 's human-like jitter. Unique Spintax variants will be applied on every send.';
    showToast('Safe dispatch queued with ' + jitter + 's randomized jitter.', 'success');
}
function spinTemplate(template, index) {
    const options = template.replace(/\\{([^{}]+)\\}/g, function(_, choices) {
        const values = choices.split('|');
        return values[(index + values.length - 1) % values.length].trim();
    });
    const modifiers = ['Quick note: ', 'A brief update: ', 'Sharing a timely note: '];
    return modifiers[index % modifiers.length] + options.replace(/\\s+([.!?])/, '$1');
}
function generateSpintaxVariants() {
    const template = document.getElementById('spintax-template')?.value || '';
    return [0, 1, 2].map((index) => spinTemplate(template, index));
}
function previewSpintax() {
    const variants = generateSpintaxVariants();
    const preview = document.getElementById('spintax-preview');
    if (preview) preview.innerText = variants.map((variant, index) => 'Variant ' + (index + 1) + ' · ' + variant).join('\\n');
    const status = document.getElementById('spintax-status');
    if (status) status.innerText = 'Per-send variation engine · 3 fresh variants generated';
    showToast('Spintax variations and minor template modifications generated.', 'success');
}
function sendSpintaxBatch() {
    previewSpintax();
    showToast('Batch send simulation applied a unique variant to every recipient.', 'success');
}
document.addEventListener('DOMContentLoaded', applyStoredTheme);
</script>
"""


def render_dashboard():
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/jpeg">
    <title>Grace Outreach Assistant - Dashboard</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header()}
    {render_navigation("dashboard")}

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-title">ACTIVE OUTREACH PIPELINE</div>
            <div class="stat-value" data-metric-key="pipeline">2,480</div>
            <div class="stat-sub">+14.2% Velocity</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">CONNECTED GMAIL ACCOUNTS</div>
            <div class="stat-value" data-metric-key="inboxes">3 Inboxes</div>
            <div class="stat-sub">Rotation Healthy</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">WEEKLY SENT VOLUME</div>
            <div class="stat-value" data-metric-key="volume">1,240</div>
            <div class="stat-sub">+8.5% Speed</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">PIPELINE DEAL VALUE</div>
            <div class="stat-value" data-metric-key="deal">$64,800</div>
            <div class="stat-sub">+21.4% Revenue</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="card">
            <h4 style="margin:0 0 14px; font-size:14px;">⚡ Quick Action Toolbar</h4>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="btn btn-blue" data-required-module="2" onclick="manualSync()">Trigger Manual Sync</button>
                <button class="btn btn-red" data-required-module="4" onclick="pauseOutreach()">Pause All Outreaches</button>
                <button class="btn btn-orange" data-required-module="17" onclick="testBroadcast()">Test Broadcast</button>
            </div>
        </div>
        <div class="card">
            <h4 style="margin:0 0 10px; font-size:14px;">📊 Gmail API Quota & Health</h4>
            <div style="font-size:13px; font-weight:600; color:var(--accent-green); margin-bottom:8px;">Token Status: Healthy (98%)</div>
            <div style="width:100%; height:10px; background:#E2E8F0; border-radius:5px; overflow:hidden;">
                <div style="width:98%; height:100%; background:var(--accent-green);"></div>
            </div>
        </div>
    </div>

    <div class="card">
        <h4 style="margin:0 0 12px; font-size:14px;">📡 Real-Time Activity Stream</h4>
        <div class="log-box">
            <div>[10:50:02] [SYNC] Business Inbox #1 dispatched outreach batch (45 msgs).</div>
            <div>[10:48:15] [REPLY] Incoming positive response classified from client_id_884.</div>
            <div>[10:45:00] [VAULT] OAuth Token verified securely via AES-256-GCM locker.</div>
        </div>
    </div>
    {COMMON_JS}
</body>
</html>"""


def render_matrix():
    cards_html = ""
    for idx, info in MODULES_DATA.items():
        border_style = (
            'style="border: 2px solid var(--accent-gold);"' if idx == 12 else ""
        )
        cards_html += f"""
        <a href="/?tab=module&id={idx}" class="module-card" data-module-id="{idx}" {border_style}>
            <div class="module-icon" aria-hidden="true">{info.get("icon", "•")}</div>
            <div class="module-copy">
                <div class="mod-title">{idx}. {info["name"]}</div>
                <div class="module-desc">{info["desc"]}</div>
                <div style="font-size:9px; font-weight:bold; color:var(--accent-green); margin-top:5px;">● {info["status"]}</div>
            </div>
        </a>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/jpeg">
    <title>Grace Outreach Assistant - 22-Module Matrix</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header()}
    {render_navigation("matrix")}

    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3 style="margin:0;">Complete 22-Module Functional Matrix</h3>
            <span style="font-size:12px; color:var(--accent-green); font-weight:bold;">● Admin View (All Modules Unlocked)</span>
        </div>
        <div class="modules-grid">
            {cards_html}
        </div>
    </div>
    {COMMON_JS}
</body>
</html>"""


def render_module_detail(mod_id):
    try:
        m_id = int(mod_id)
    except (TypeError, ValueError):
        m_id = 1
    if m_id not in MODULES_DATA:
        m_id = 1
    mod_info = MODULES_DATA[m_id]
    blueprint = MODULE_BLUEPRINTS[m_id]
    metrics_html = "".join(
        f'<div class="telemetry-card"><span class="eyebrow">{label}</span><strong>{value}</strong><small>{delta}</small></div>'
        for label, value, delta in blueprint["metrics"]
    )
    bars_html = "".join(f'<span style="height:{height}%;" title="Telemetry sample {index + 1}"></span>' for index, height in enumerate(blueprint["chart"]))
    controls_html = "".join(
        f'<div class="control-row"><div><b>{label}</b><span>{description}</span></div><button class="btn btn-blue" data-required-module="{m_id}" onclick="showToast({json.dumps(description + " completed.").replace(chr(34), "&quot;")}, &quot;success&quot;)">Run</button></div>'
        for label, description in blueprint["controls"]
    )
    rows_html = "".join(
        f'<tr><td><b>{first}</b></td><td>{second}</td><td><span style="color:var(--accent-green);font-weight:800;">{third}</span></td></tr>'
        for first, second, third in blueprint["rows"]
    )
    vault_html = ""
    if m_id == 12:
        vault_html = """
        <div class="module-panel vault-panel">
            <h3>🔒 Credential protection matrix</h3>
            <table>
                <thead><tr><th>Connected inbox</th><th>Protocol</th><th>Locker</th><th>State</th></tr></thead>
                <tbody>
                    <tr><td><b>business.inbox1@gmail.com</b></td><td>OAuth 2.0 auto-refresh</td><td>AES-256-GCM</td><td><span style="color:var(--accent-green);font-weight:800;">Locked</span></td></tr>
                    <tr><td><b>outreach.node2@gmail.com</b></td><td>App password</td><td>AES-256-GCM</td><td><span style="color:var(--accent-green);font-weight:800;">Locked</span></td></tr>
                    <tr><td><b>relay.personal@gmail.com</b></td><td>App password</td><td>AES-256-GCM</td><td><span style="color:var(--accent-green);font-weight:800;">Locked</span></td></tr>
                </tbody>
            </table>
        </div>
        """
    campaign_html = ""
    if m_id == 4:
        campaign_html = """
        <div class="module-panel campaign-panel">
            <span class="eyebrow">PRE-DISPATCH GATE</span>
            <h3>Campaign range, health &amp; jitter controller</h3>
            <p class="panel-copy">Evaluate sender profile health and spam safety before any automated send. Human-like jitter is applied per dispatch batch.</p>
            <div class="form-grid">
                <label>Start record<input id="dispatch-start" type="number" min="1" max="1000" value="1"></label>
                <label>End record<input id="dispatch-end" type="number" min="1" max="1000" value="1000" oninput="syncDispatchSlider(this.value)"></label>
            </div>
            <label class="range-label">Dispatch range <input id="dispatch-range-slider" type="range" min="1" max="1000" value="1000" oninput="syncDispatchEnd(this.value)"><span id="dispatch-range-label">1 → 1000</span></label>
            <div class="dispatch-checks">
                <span id="dispatch-health" class="dispatch-check">◌ Sender profile · Pending</span>
                <span id="dispatch-spam" class="dispatch-check">◌ Spam safety · Pending</span>
                <span id="dispatch-jitter" class="dispatch-check">◌ Human jitter · 3–12s</span>
            </div>
            <div class="dispatch-actions"><button class="btn btn-blue" onclick="evaluateDispatch()">Evaluate pre-dispatch</button><button class="btn btn-orange" onclick="executeCampaignDispatch()">Run safe dispatch</button></div>
            <div id="dispatch-result" class="dispatch-result">Awaiting pre-dispatch evaluation.</div>
        </div>
        """
    elif m_id == 5:
        campaign_html = """
        <div class="module-panel campaign-panel">
            <span class="eyebrow">SEND VARIATION ENGINE</span>
            <h3>Spintax &amp; minor template modification preview</h3>
            <p class="panel-copy">Every send receives a safe variant and a small human-style template adjustment to reduce bulk repetition.</p>
            <label>Campaign template<textarea id="spintax-template" rows="4">{Hi|Hello|Greetings}, {first_name} — I wanted to share a quick update about {project|your project}.</textarea></label>
            <div class="dispatch-actions"><button class="btn btn-blue" onclick="previewSpintax()">Generate 3 variations</button><button class="btn btn-orange" onclick="sendSpintaxBatch()">Simulate send batch</button></div>
            <pre id="spintax-preview" class="spintax-preview">Your generated variants will appear here.</pre>
            <div id="spintax-status" class="dispatch-result">Per-send variation engine · Armed</div>
        </div>
        """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/jpeg">
    <title>Grace Outreach Assistant - Module {m_id}</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header()}
    {render_navigation("matrix")}
    <main id="module-workspace" data-module-page-id="{m_id}">
        <div class="module-authorized-content">
            <div class="card module-hero">
                <div class="module-hero-copy">
                    <span class="eyebrow">{blueprint["eyebrow"]} · MODULE {m_id:02d}</span>
                    <h2>{mod_info["name"]}</h2>
                    <span style="font-size:12px;color:var(--text-muted);">{mod_info["desc"]}</span>
                </div>
                <div style="display:grid;justify-items:end;gap:10px;"><span class="module-status-pill"><i class="presence-dot online"></i>{mod_info["status"]}</span><a href="/?tab=matrix" class="btn btn-blue module-back-button">← Back to Main Matrix</a></div>
            </div>
            <div class="telemetry-grid">{metrics_html}</div>
            <div class="module-workbench">
                <section class="module-panel">
                    <h3>📈 Live telemetry trend</h3>
                    <div class="bar-chart">{bars_html}</div>
                    <div class="chart-caption"><span>−24h</span><span>Current operating window</span><span>Now</span></div>
                </section>
                <section class="module-panel">
                    <h3>⚡ Execution controls</h3>
                    <div class="control-list">{controls_html}</div>
                </section>
            </div>
            <section class="module-panel module-table-wrap">
                <h3>{blueprint["table_title"]}</h3>
                <table><thead><tr><th>Lane / signal</th><th>Current reading</th><th>State</th></tr></thead><tbody>{rows_html}</tbody></table>
            </section>
            {campaign_html}
            {vault_html}
        </div>
        <div class="module-access-denied" hidden>
            <h3>🔐 Module {m_id} is restricted in this workspace</h3>
            <p>The active colleague profile does not have permission to open this operational node. Switch the profile from View-As to continue.</p>
            <a href="/?tab=matrix" class="btn btn-orange">Return to authorized matrix</a>
        </div>
    </main>
    {COMMON_JS}
</body>
</html>"""


def render_colleagues():
    colleagues = [
        {"key": "king", "name": "King Saab", "role": "Super Admin", "software_id": "GRA-ADM-001", "status": "Online", "initials": "KS", "tags": ["Manager", "Admin"], "allowed": list(range(1, 23))},
        {"key": "abdullah", "name": "Abdullah Khan", "role": "Strategic Lead", "software_id": "GRA-LEAD-002", "status": "Online", "initials": "AK", "tags": ["Manager", "Strategy"], "allowed": [1, 2, 3, 4, 5, 6, 7, 12]},
        {"key": "sarah", "name": "Sarah Malik", "role": "Growth Marketer", "software_id": "GRA-MKT-003", "status": "Online", "initials": "SM", "tags": ["Marketer", "Growth"], "allowed": [1, 2, 4, 5, 11, 17, 18]},
        {"key": "hamza", "name": "Hamza Ali", "role": "Lead Collector", "software_id": "GRA-COL-004", "status": "Offline", "initials": "HA", "tags": ["Collector", "Research"], "allowed": [1, 2, 6, 7, 13, 16]},
    ]
    cards_html = ""
    for colleague in colleagues:
        tags_html = "".join(f'<span class="tag">{tag}</span>' for tag in colleague["tags"])
        permission_html = "".join(
            f'<label class="permission-item" title="Module {module_id}"><input type="checkbox" {"checked" if module_id in colleague["allowed"] else ""} onchange="savePermission(\'{colleague["key"]}\', {module_id}, this.checked)">M{module_id}</label>'
            for module_id in range(1, 23)
        )
        online_class = "online" if colleague["status"] == "Online" else ""
        cards_html += f"""
        <article class="colleague-card" data-colleague-key="{colleague["key"]}">
            <div class="colleague-head">
                <div id="avatar-{colleague["key"]}" class="avatar" role="img" aria-label="{colleague["name"]} profile picture" data-profile-avatar="{colleague["key"]}" data-initials="{colleague["initials"]}">{colleague["initials"]}</div>
                <div><div class="colleague-name" data-profile-name="{colleague["key"]}">{colleague["name"]}</div><div class="colleague-role">{colleague["role"]}</div><div class="colleague-state">State: <span data-profile-state="{colleague["key"]}">Pakistan</span></div></div>
                <span class="presence" data-profile-presence="{colleague["key"]}"><i class="presence-dot {online_class}"></i><span class="profile-presence-label">{colleague["status"]}</span></span>
                <button class="icon-button" type="button" onclick="openColleagueProfile('{colleague["key"]}', '{colleague["name"]}', '{colleague["software_id"]}', '{colleague["role"]}', '{",".join(colleague["tags"])}', '{colleague["initials"]}')" aria-label="Open settings for {colleague["name"]}" title="Profile and settings">⚙</button>
            </div>
            <div class="colleague-meta"><span>Software ID <b>{colleague["software_id"]}</b></span><span>Access scope <b>{len(colleague["allowed"])} of 22 modules</b></span><div class="tag-list">{tags_html}</div></div>
            <div class="colleague-actions"><button class="btn btn-blue" onclick="openColleagueProfile('{colleague["key"]}', '{colleague["name"]}', '{colleague["software_id"]}', '{colleague["role"]}', '{",".join(colleague["tags"])}', '{colleague["initials"]}')">Profile</button><button class="btn btn-gray" onclick="changeViewAs('{colleague["key"]}')">View as</button></div>
            <label class="upload-mini">Profile picture <input type="file" accept="image/*" onchange="previewColleaguePhoto(event, 'avatar-{colleague["key"]}')"></label>
            <div class="permission-card"><div class="permission-card-head"><strong>RBAC permissions</strong><small>Toggle module access</small></div><div class="permission-grid">{permission_html}</div></div>
        </article>
        """

    status_options = '<option value="present">Present</option><option value="absent">Absent · 150 PKR</option><option value="received">Leave Received</option><option value="approved">Leave Approved</option>'
    attendance_rows_html = ""
    for key, name, software_id in ATTENDANCE_PEOPLE:
        day_cells = "".join(
            f'<td><select data-attendance-person="{key}" data-attendance-day="{day}" data-admin-only onchange="updateAttendance(this)" aria-label="{name} {label} attendance">{status_options}</select></td>'
            for day, label in ATTENDANCE_DAYS
        )
        attendance_rows_html += f'<tr data-attendance-row="{key}"><td><b>{name}</b><small>{software_id}</small></td>{day_cells}<td><strong class="fine-balance" data-fine-key="{key}">0 PKR</strong></td><td><button class="btn btn-gray" data-admin-only onclick="clearFine(\'{key}\')">Clear fine</button></td></tr>'

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/jpeg">
    <title>Grace Outreach Assistant - Colleague Management</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header()}
    {render_navigation("colleagues")}

    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:end; gap:16px; margin-bottom:16px;"><div><span class="eyebrow">ACCESS GOVERNANCE</span><h3 style="margin:6px 0 0;">Advanced Colleague Management</h3></div><span style="color:var(--accent-green); font-size:11px; font-weight:700;">4 identities · live presence</span></div>
        <div class="colleague-grid">{cards_html}</div>
    </div>
    <section class="card attendance-card">
        <div class="section-heading"><div><span class="eyebrow">ATTENDANCE &amp; PAYROLL</span><h3>Daily Attendance Ledger</h3><p class="panel-copy">Monday–Saturday · 6:00 PM to 2:30 AM PKT · absence fine: 150 PKR per missed shift</p></div><button class="btn btn-orange" data-admin-only onclick="clearAllFines()">Clear all fines</button></div>
        <div class="attendance-summary-grid">
            <div class="mini-stat"><span>Total running fines</span><strong id="attendance-total-fines">0 PKR</strong></div>
            <div class="mini-stat"><span>Absence flags</span><strong id="attendance-total-absences">0</strong></div>
            <div class="mini-stat"><span>Leave requests</span><strong id="attendance-pending-leaves">0 pending</strong></div>
            <div class="mini-stat"><span>Shift window</span><strong>6:00 PM → 2:30 AM</strong></div>
        </div>
        <div class="attendance-scroll"><table class="attendance-table"><thead><tr><th>Colleague</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Fine balance</th><th>Admin</th></tr></thead><tbody>{attendance_rows_html}</tbody></table></div>
        <div class="leave-panel">
            <div class="section-heading compact"><div><span class="eyebrow">LEAVE REQUEST QUEUE</span><h4>Received / Approved states</h4></div><small>Date edits are restricted to Super Admin</small></div>
            <div class="leave-list">
                <div class="leave-row" data-leave-row="abdullah"><div><b>Abdullah Khan</b><small>Strategic Lead · GRA-LEAD-002</small></div><label>Start<input type="date" data-leave-date="abdullah-start" value="2026-09-07" data-admin-only></label><label>End<input type="date" data-leave-date="abdullah-end" value="2026-09-08" data-admin-only></label><select data-leave-state="abdullah" data-admin-only onchange="updateLeaveState(this)"><option value="received">Received</option><option value="approved">Approved</option></select><button class="btn btn-gray" onclick="requestLeave('abdullah')">Request leave</button></div>
                <div class="leave-row" data-leave-row="sarah"><div><b>Sarah Malik</b><small>Growth Marketer · GRA-MKT-003</small></div><label>Start<input type="date" data-leave-date="sarah-start" value="2026-09-12" data-admin-only></label><label>End<input type="date" data-leave-date="sarah-end" value="2026-09-12" data-admin-only></label><select data-leave-state="sarah" data-admin-only onchange="updateLeaveState(this)"><option value="received" selected>Received</option><option value="approved">Approved</option></select><button class="btn btn-gray" onclick="requestLeave('sarah')">Request leave</button></div>
            </div>
        </div>
    </section>
    <div id="colleague-profile-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="profile-title">
        <div class="modal-card wide-modal">
            <div class="modal-header"><h3 id="profile-title">Colleague profile</h3><button class="modal-close" onclick="closeColleagueProfile()" aria-label="Close colleague profile">×</button></div>
            <div id="profile-modal-body"></div>
        </div>
    </div>
    <div id="photo-crop-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="crop-title">
        <div class="modal-card wide-modal">
            <div class="modal-header"><h3 id="crop-title">Crop profile picture</h3><button class="modal-close" onclick="cancelCropEditor()" aria-label="Close image cropper">×</button></div>
            <p class="modal-copy">Use the controls to frame a clean square avatar. The final crop is saved to shared workspace state.</p>
            <div class="crop-stage"><canvas id="crop-canvas" width="320" height="320"></canvas></div>
            <div class="crop-controls">
                <label>Zoom<input id="crop-zoom" type="range" min="1" max="3" step="0.05" value="1" oninput="updateCropSetting('zoom', this.value)"></label>
                <label>Horizontal<input id="crop-horizontal" type="range" min="0" max="100" step="1" value="50" oninput="updateCropSetting('x', this.value)"></label>
                <label>Vertical<input id="crop-vertical" type="range" min="0" max="100" step="1" value="50" oninput="updateCropSetting('y', this.value)"></label>
            </div>
            <div class="crop-actions"><button class="btn btn-gray" onclick="cancelCropEditor()">Cancel</button><button class="btn btn-blue" onclick="saveCroppedPhoto()">Save cropped image</button></div>
        </div>
    </div>
    {COMMON_JS}
</body>
</html>"""


def app(environ, start_response):
    path = environ.get("PATH_INFO", "")
    if path.rstrip("/") == "/assets/grace-ai-robot.png":
        try:
            robot_bytes = ROBOT_ASSET.read_bytes()
            content_type = "image/png"
        except OSError:
            robot_bytes = ROBOT_SVG.encode("utf-8")
            content_type = "image/svg+xml; charset=utf-8"
        start_response(
            "200 OK",
            [
                ("Content-Type", content_type),
                ("Content-Length", str(len(robot_bytes))),
                ("Cache-Control", "public, max-age=86400"),
            ],
        )
        return [robot_bytes]
    if path.rstrip("/") == "/assets/grace-logo.jfif":
        try:
            logo_bytes = LOGO_ASSET.read_bytes()
        except OSError:
            logo_bytes = LOGO_SVG.encode("utf-8")
            start_response(
                "200 OK",
                [
                    ("Content-Type", "image/svg+xml; charset=utf-8"),
                    ("Content-Length", str(len(logo_bytes))),
                    ("Cache-Control", "public, max-age=86400"),
                ],
            )
            return [logo_bytes]
        start_response(
            "200 OK",
            [
                ("Content-Type", "image/jpeg"),
                ("Content-Length", str(len(logo_bytes))),
                ("Cache-Control", "public, max-age=86400, immutable"),
            ],
        )
        return [logo_bytes]

    if path.rstrip("/") == "/gmail-sync":
        method = environ.get("REQUEST_METHOD", "GET").upper()
        if method not in {"GET", "POST"}:
            return _json_response(
                start_response,
                {"error": "Method not allowed."},
                "405 Method Not Allowed",
            )
        result = sync_gmail_notifications(force=True)
        return _json_response(
            start_response,
            result,
            "200 OK" if result["state"] == "connected" else "502 Bad Gateway",
        )

    if path.rstrip("/") == "/state":
        method = environ.get("REQUEST_METHOD", "GET").upper()
        if method == "GET":
            return _json_response(start_response, read_shared_state())
        if method == "POST":
            try:
                length = int(environ.get("CONTENT_LENGTH") or "0")
                if length <= 0 or length > 3500000:
                    raise ValueError("State update body is missing or too large.")
                raw_body = environ["wsgi.input"].read(length)
                payload = json.loads(raw_body.decode("utf-8"))
                return _json_response(start_response, update_shared_state(payload))
            except (ValueError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                return _json_response(
                    start_response,
                    {"error": str(exc)},
                    "400 Bad Request",
                )
        return _json_response(
            start_response,
            {"error": "Method not allowed."},
            "405 Method Not Allowed",
        )

    query_string = environ.get("QUERY_STRING", "")
    params = parse_qs(query_string)
    tab = params.get("tab", ["dashboard"])[0]
    mod_id = params.get("id", ["1"])[0]

    if tab == "matrix":
        body = render_matrix()
    elif tab == "module":
        body = render_module_detail(mod_id)
    elif tab == "colleagues":
        body = render_colleagues()
    else:
        body = render_dashboard()

    data = body.encode("utf-8")
    status = "200 OK"
    response_headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(data))),
    ]
    start_response(status, response_headers)
    return [data]


if __name__ == "__main__":
    with make_server(HOST, PORT, app) as httpd:
        print(f"Server running on {HOST}:{PORT}")
        httpd.serve_forever()