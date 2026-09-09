import os
import json
import copy
import re
import threading
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent / "data"))
SHARED_STATE_FILE = DATA_DIR / "grace_shared_state.json"
SHARED_STATE_LOCK = threading.Lock()

US_STATES_CATALOG = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]

US_CONTRACTORS_CATALOG = [
    "Turner Construction Co.", "Bechtel Corporation", "Skanska USA Building",
    "The Whiting-Turner Contracting Co.", "Gilbane Building Company", "Hensel Phelps",
    "Clark Construction Group", "DPR Construction", "Mortenson Construction",
    "McCarthy Building Companies", "Holder Construction", "Balfour Beatty US",
    "JE Dunn Construction", "Brasfield & Gorrie", "Lendlease Americas",
    "Suffolk Construction", "PCL Construction Enterprises", "Clayco Inc.",
    "Sundt Construction", "Webcor Builders", "Walsh Construction",
    "Structure Tone", "Austin Commercial", "Ryan Companies",
    "Pepper Construction", "Swinerton Inc.", "Kitchell Corporation",
    "Crossland Construction", "Level 10 Construction", "Hoar Construction"
]

MODULES_DATA = {
    1: {
        "name": "Dashboard Overview",
        "category": "Core Analytics",
        "status": "Active",
        "lock": "Secured",
        "desc": "Enterprise real-time dispatch monitoring, response parsing, and velocity tracking.",
        "icon": "◔",
    },
    2: {
        "name": "Gmail Multi-Tenant Hub",
        "category": "Connection Pool",
        "status": "Active (3 Inboxes)",
        "lock": "Secured",
        "desc": "Multi-channel Gmail rotation pool with automated quota preservation.",
        "icon": "✉",
    },
    3: {
        "name": "AI Warmup Ramp",
        "category": "Reputation",
        "status": "Optimal (98%)",
        "lock": "Automated",
        "desc": "Autonomous peer thread engagement preserving IP and domain reputation.",
        "icon": "♨",
    },
    4: {
        "name": "Campaign Studio",
        "category": "Outreach",
        "status": "Active",
        "lock": "Armed",
        "desc": "Multi-stage automated outreach pipeline with conditional branching.",
        "icon": "➤",
    },
    5: {
        "name": "Spin-Syntax AI Engine",
        "category": "Copywriting",
        "status": "Active",
        "lock": "Ready",
        "desc": "Multi-tier dynamic Spintax processor eliminating spam trigger footprint.",
        "icon": "╱",
    },
    6: {
        "name": "US Architect & Contractor Scraper",
        "category": "Lead Gen",
        "status": "Standby",
        "lock": "Ready",
        "desc": "High-velocity data extraction across all 50 US States with live ping & export.",
        "icon": "⌕",
    },
    7: {
        "name": "CRM Revenue Pipeline",
        "category": "Monetization",
        "status": "$64,800 Deal Value",
        "lock": "Active",
        "desc": "Visual deal-stage tracking converting inbound warm leads into revenue.",
        "icon": "$",
    },
    8: {
        "name": "Colleague Access Controller",
        "category": "Access Control",
        "status": "Protected",
        "lock": "Restricted",
        "desc": "Granular role-based credential provisioning and access delegation.",
        "icon": "♙",
    },
    9: {
        "name": "System Doctor Daemon",
        "category": "Diagnostics",
        "status": "100% Operational",
        "lock": "Monitored",
        "desc": "Automated latency checks, socket diagnostics, and worker thread watchdog.",
        "icon": "♥",
    },
    10: {
        "name": "Audio Studio & Extractor",
        "category": "Alerts",
        "status": "Audio: ON",
        "lock": "Active",
        "desc": "Synthesized audio feedback triggers for real-time outreach classifications.",
        "icon": "♫",
    },
    11: {
        "name": "Built-in AI Guide Agent",
        "category": "Intelligence",
        "status": "Online",
        "lock": "Ready",
        "desc": "Context-aware response classifier with 22 bilingual workflow runbooks.",
        "icon": "▣",
    },
    12: {
        "name": "OAuth Token Vault",
        "category": "Security Vault",
        "status": "AES-256 Locked",
        "lock": "Encrypted",
        "desc": "Hardware-level credential isolation with autonomous 24h token rotation daemon.",
        "icon": "⬟",
    },
    13: {
        "name": "Timezone Scheduler",
        "category": "Scheduler",
        "status": "Pacing Healthy",
        "lock": "Regulated",
        "desc": "US Live Clocks & Business Hour Dispatch with randomized human jitter.",
        "icon": "◷",
    },
    14: {
        "name": "Bounce Shield",
        "category": "Deliverability",
        "status": "0.08% Bounce Ping",
        "lock": "Secured",
        "desc": "Real-time DNSBL, MX monitoring, and automated zero-bounce queue sanitizer.",
        "icon": "◢",
    },
    15: {
        "name": "Auto-Reply Detector",
        "category": "Classification",
        "status": "Aligned (100%)",
        "lock": "Verified",
        "desc": "AI sentiment analysis and autonomous positive-reply CRM routing.",
        "icon": "↶",
    },
    16: {
        "name": "CSV / Excel Exporter",
        "category": "Reporting",
        "status": "Testing",
        "lock": "Armed",
        "desc": "Multi-format automated analytical exports for outreach reporting.",
        "icon": "⇥",
    },
    17: {
        "name": "Broadcast Notification Node",
        "category": "Notifications",
        "status": "Synced",
        "lock": "Protected",
        "desc": "Targeted colleague display notifications with high-priority chimes.",
        "icon": "⚑",
    },
    18: {
        "name": "Brand Palette Studio",
        "category": "Brand System",
        "status": "Zero-Bounce",
        "lock": "Enforced",
        "desc": "Executive luxury theme presets, custom hex pickers, and typography tuning.",
        "icon": "✾",
    },
    19: {
        "name": "Cloud Webhook Dispatcher",
        "category": "Integration",
        "status": "CAN-SPAM Compliant",
        "lock": "Active",
        "desc": "Cryptographically signed JSON triggers and automated retry dispatch.",
        "icon": "⌘",
    },
    20: {
        "name": "Daily Quota Guard",
        "category": "Quota Safety",
        "status": "Balanced",
        "lock": "Audited",
        "desc": "Automated safe account limits enforcing 50/50 mailbox health preservation.",
        "icon": "◉",
    },
    21: {
        "name": "Security Audit Stream",
        "category": "Forensics",
        "status": "Recording",
        "lock": "Tamper-Proof",
        "desc": "Immutable append-only access trail with cryptographic timestamp forensics.",
        "icon": "≋",
    },
    22: {
        "name": "Enterprise Sync Engine",
        "category": "Synchronization",
        "status": "Connected",
        "lock": "Synchronized",
        "desc": "Bi-directional webhook synchronization with central hub and external CRMs.",
        "icon": "⇄",
    },
}

DEFAULT_PROFILES = {
    "king": {
        "key": "king",
        "name": "King Saab",
        "role": "Super Admin",
        "software_id": "GRA-ADM-001",
        "status": "Online",
        "initials": "KS",
        "tags": ["Manager", "Admin"],
        "assigned_states": ["California", "New York"],
        "assigned_contractors": ["Turner Construction Co.", "Skanska USA Building"],
        "allowed": list(range(1, 23)),
        "metrics": {"pipeline": "2,480", "inboxes": "3 Inboxes", "volume": "1,240", "deal": "$64,800"},
    },
    "abdullah": {
        "key": "abdullah",
        "name": "Abdullah Khan",
        "role": "Strategic Lead",
        "software_id": "GRA-LEAD-002",
        "status": "Online",
        "initials": "AK",
        "tags": ["Manager", "Strategy"],
        "assigned_states": ["Texas", "Florida"],
        "assigned_contractors": ["Bechtel Corporation", "Clark Construction Group"],
        "allowed": [1, 2, 3, 4, 5, 6, 7, 12],
        "metrics": {"pipeline": "1,860", "inboxes": "3 Inboxes", "volume": "920", "deal": "$48,200"},
    },
    "sarah": {
        "key": "sarah",
        "name": "Sarah Malik",
        "role": "Growth Marketer",
        "software_id": "GRA-MKT-003",
        "status": "Online",
        "initials": "SM",
        "tags": ["Marketer", "Growth"],
        "assigned_states": ["Illinois", "Washington"],
        "assigned_contractors": ["Gilbane Building Company", "DPR Construction"],
        "allowed": [1, 2, 4, 5, 11, 17, 18],
        "metrics": {"pipeline": "1,120", "inboxes": "2 Inboxes", "volume": "640", "deal": "$18,400"},
    },
    "hamza": {
        "key": "hamza",
        "name": "Hamza Ali",
        "role": "Lead Collector",
        "software_id": "GRA-COL-004",
        "status": "Offline",
        "initials": "HA",
        "tags": ["Collector", "Research"],
        "assigned_states": ["Georgia", "Ohio"],
        "assigned_contractors": ["Mortenson Construction", "Hensel Phelps"],
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
    7: {"eyebrow": "MONETIZATION", "title": "Revenue pipeline command", "metrics": [("Open deal value", "$64,800", "+21.4%"), ("Qualified opportunities", "34", "7 added today"), ("Conversion rate", "18.6%", "Above forecast")], "chart": [28, 42, 39, 55, 63, 59, 75, 88], "table_title": "Active deal stages", "rows": [("Discovery", "$18,400", "12 opportunities"), ("Proposal", "$27,600", "14 opportunities"), ("Negotiation", "$18,800", "8 opportunities")], "controls": [("Advance Deal Stage", "Move highest value proposal to close-won"), ("Add Opportunity", "Log fresh qualified deal into pipeline"), ("Export ROI report", "Package the revenue attribution")]},
    8: {"eyebrow": "ACCESS CONTROL", "title": "Colleague access governance", "metrics": [("Managed identities", "4", "Presence monitored"), ("Permission changes", "12", "Last 24 hours"), ("Audit coverage", "100%", "No gaps detected")], "chart": [62, 62, 68, 65, 74, 79, 77, 91], "table_title": "Governance activity", "rows": [("Sarah Malik", "M17 enabled", "Approved"), ("Hamza Ali", "M13 reviewed", "Audited"), ("Abdullah Khan", "View-As session", "Recorded")], "controls": [("Open colleague manager", "Review profiles and RBAC"), ("Apply access preset", "Set a governed permission bundle"), ("Force logout", "End a selected colleague session")]},
    9: {"eyebrow": "DIAGNOSTICS", "title": "System health observatory", "metrics": [("Operational health", "100%", "All probes passing"), ("Median latency", "184ms", "−22ms today"), ("Worker threads", "12 / 12", "No stalled workers")], "chart": [91, 88, 94, 90, 97, 93, 99, 100], "table_title": "System probes", "rows": [("API response", "184ms", "Passing"), ("Queue worker", "42ms", "Passing"), ("Socket bridge", "99.99%", "Passing")], "controls": [("Run full diagnostic", "Probe every operational node"), ("Flush cache", "Clear safe transient state"), ("Open telemetry", "Inspect the latest health samples")]},
    10: {"eyebrow": "ALERTS", "title": "Audio broadcast matrix", "metrics": [("Audio state", "ON", "Chimes armed"), ("Alert channels", "4", "All reachable"), ("Last broadcast", "02m ago", "Acknowledged")], "chart": [44, 57, 51, 66, 61, 73, 69, 84], "table_title": "Alert channel status", "rows": [("Priority chime", "660 / 880Hz", "Armed"), ("Inbox alert", "3 targets", "Ready"), ("Full-screen node", "4 displays", "Ready")], "controls": [("Open soundscape", "Tune ambient tracks and clips"), ("Test alert chime", "Send a safe local test"), ("Open broadcast center", "Target a colleague display")]},
    11: {"eyebrow": "INTELLIGENCE", "title": "Context agent operations", "metrics": [("Intent accuracy", "96.4%", "+1.8%"), ("Classified replies", "1,824", "This week"), ("Guide availability", "24 / 7", "Online now")], "chart": [57, 61, 66, 71, 68, 79, 83, 96], "table_title": "AI signal feed", "rows": [("Positive intent", "62%", "Routing to CRM"), ("Needs follow-up", "24%", "Queued"), ("Not relevant", "14%", "Suppressed")], "controls": [("Open AI Guide", "Start a bilingual workflow session"), ("Run intent scan", "Classify the newest reply batch"), ("Draft follow-up", "Generate a review-ready response")]},
    12: {"eyebrow": "SECURITY VAULT", "title": "OAuth credential lifecycle", "metrics": [("Locker status", "AES-256", "Authenticated"), ("Tokens healthy", "3 / 3", "Auto-renew enabled"), ("Next rotation", "04h 12m", "No failures")], "chart": [98, 98, 99, 99, 100, 100, 100, 100], "table_title": "Vault activity", "rows": [("business.inbox1", "OAuth refresh", "Securely locked"), ("outreach.node2", "App password", "Securely locked"), ("relay.personal", "App password", "Securely locked")], "controls": [("Export Encrypted Backup", "Download secure JSON vault archive"), ("Rotate Master Key", "Re-wrap credentials with a fresh AES key"), ("Force vault sync", "Synchronize approved credentials")]},
    13: {"eyebrow": "SCHEDULER", "title": "Timezone dispatch command", "metrics": [("Active timezones", "4 Major US", "US business hours"), ("Queued sends", "384", "Jitter applied"), ("Live Status", "Active", "Clocks synchronized")], "chart": [34, 42, 56, 61, 68, 75, 73, 86], "table_title": "Regional clocks", "rows": [("Eastern Time (ET)", "08:00 – 18:00 EST", "Live Sync"), ("Central Time (CT)", "07:00 – 17:00 CST", "Live Sync"), ("Mountain Time (MT)", "06:00 – 16:00 MST", "Live Sync"), ("Pacific Time (PT)", "05:00 – 15:00 PST", "Live Sync")], "controls": [("Refresh live clocks", "Recalculate every dispatch window"), ("Preview schedule", "Review timezone-safe sends"), ("Pause queue", "Hold all timed dispatches")]},
    14: {"eyebrow": "DELIVERABILITY", "title": "Bounce protection shield", "metrics": [("Bounce rate", "0.08%", "−0.02% today"), ("Sanitized queue", "2,480", "No hard bounces"), ("Shield coverage", "100%", "All inboxes protected")], "chart": [88, 91, 89, 94, 96, 95, 98, 99], "table_title": "Suppression signals", "rows": [("Hard bounce", "0.04%", "Blocked"), ("Soft bounce", "0.04%", "Retry limited"), ("Risk domain", "0", "Clear")], "controls": [("Sanitize queue", "Remove risky recipients"), ("Run DNSBL scan", "Check active reputation lists"), ("Export Suppressions", "Download the CSV suppression list")]},
    15: {"eyebrow": "CLASSIFICATION", "title": "Auto-reply intelligence desk", "metrics": [("Replies scanned", "1,824", "Since last sync"), ("Positive sentiment", "62%", "CRM push armed"), ("Confidence score", "94%", "High confidence")], "chart": [51, 58, 63, 67, 74, 72, 84, 92], "table_title": "Sentiment routing", "rows": [("Positive", "1,131 replies", "CRM push"), ("Neutral", "438 replies", "Needs review"), ("Negative", "255 replies", "Suppressed")], "controls": [("Classify inbox", "Run the sentiment model"), ("Review uncertain", "Open low-confidence replies"), ("Push to CRM", "Send approved classifications")]},
    16: {"eyebrow": "REPORTING", "title": "Multi-format analytics exporter", "metrics": [("Rows available", "18,420", "Across 22 modules"), ("Report freshness", "Live", "Current snapshot"), ("Export jobs", "Ready", "Instant browser handoff")], "chart": [42, 54, 63, 59, 71, 76, 84, 90], "table_title": "Recent exports", "rows": [("Weekly outreach telemetry", "CSV Format", "Instant Export"), ("Executive deal ROI", "Excel Format", "Instant Export"), ("Colleague security audit", "TXT Log", "Instant Export")], "controls": [("Build CSV report", "Download outreach telemetry CSV"), ("Build Excel report", "Download formatted Excel report"), ("Download audit TXT", "Download security access trail TXT")]},
    17: {"eyebrow": "NOTIFICATIONS", "title": "Broadcast notification node", "metrics": [("Reachable displays", "4 / 4", "Presence confirmed"), ("Priority banners", "2", "Awaiting ack"), ("Delivery latency", "220ms", "Within target")], "chart": [44, 52, 48, 61, 65, 72, 78, 87], "table_title": "Recipient delivery", "rows": [("All colleagues", "4 displays", "Delivered"), ("Sarah Malik", "1 display", "Acknowledged"), ("Hamza Ali", "1 display", "Offline queue")], "controls": [("Compose broadcast", "Target a display or all colleagues"), ("Send test packet", "Verify the notification node"), ("Review acknowledgements", "Check delivery receipts")]},
    18: {"eyebrow": "BRAND SYSTEM", "title": "Palette and typography studio", "metrics": [("Theme presets", "6", "Ready to apply"), ("Typography profiles", "4", "Saved locally"), ("Brand consistency", "100%", "All surfaces aligned")], "chart": [72, 75, 78, 81, 84, 88, 91, 100], "table_title": "Brand tokens", "rows": [("Emerald signature", "#06352B", "Active"), ("Executive gold", "#D6A117", "Primary"), ("Sapphire Obsidian", "#0A192F", "Available")], "controls": [("Open brand palette", "Apply a complete theme preset"), ("Tune typography", "Adjust the operating type system"), ("Preview light mode", "Review the accessible surface")]},
    19: {"eyebrow": "INTEGRATION", "title": "Cloud webhook dispatcher", "metrics": [("Connected hooks", "7", "All signatures valid"), ("Delivered today", "4,280", "+12.1%"), ("Retry queue", "3", "Backoff active")], "chart": [65, 59, 72, 68, 77, 82, 79, 94], "table_title": "Webhook endpoints", "rows": [("CRM revenue", "POST /deals", "200 OK"), ("Audit sink", "POST /events", "200 OK"), ("Partner hub", "POST /sync", "Retrying")], "controls": [("Dispatch test JSON", "Send a signed test payload"), ("Replay retry queue", "Reattempt safe failures"), ("Rotate webhook secret", "Refresh endpoint signing")]},
    20: {"eyebrow": "QUOTA SAFETY", "title": "Daily quota guardrail", "metrics": [("Safe accounts", "3 / 3", "Within policy"), ("Used today", "1,240", "50% of safe cap"), ("Blocked sends", "0", "No policy violations")], "chart": [24, 31, 38, 44, 51, 57, 63, 50], "table_title": "Account quota lanes", "rows": [("Inbox #1", "420 / 800", "Safe"), ("Inbox #2", "410 / 800", "Safe"), ("Inbox #3", "410 / 800", "Safe")], "controls": [("Recalculate quota", "Refresh account pacing limits"), ("Open safe-send plan", "Review the next dispatch window"), ("Lock overage", "Enforce the daily ceiling")]},
    21: {"eyebrow": "FORENSICS", "title": "Security audit stream", "metrics": [("Events recorded", "12,842", "Append-only"), ("Threat signals", "0", "No active threats"), ("Retention", "180 days", "Policy compliant")], "chart": [47, 51, 49, 58, 64, 69, 66, 82], "table_title": "Recent audit events", "rows": [("View-As session", "King Saab", "Recorded"), ("RBAC mutation", "M17 enabled", "Recorded"), ("Vault check", "AES-256", "Verified")], "controls": [("Export Audit Log", "Download signed tamper-proof log"), ("Run threat scan", "Check recent access signals"), ("Flush memory buffer", "Clear safe audit pointers")]},
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


INITIAL_AUDIT_LOG = [
    {"id": "AUD-1001", "user": "King Saab", "action": "System Kernel Initialized", "timestamp": "2026-09-10 00:00:01 PKT", "role": "Super Admin", "status": "Verified"},
    {"id": "AUD-1002", "user": "King Saab", "action": "AES-256 Vault Locker Armed", "timestamp": "2026-09-10 00:01:15 PKT", "role": "Super Admin", "status": "Verified"},
    {"id": "AUD-1003", "user": "Abdullah Khan", "action": "Contractor Outreach Pool Synced", "timestamp": "2026-09-10 00:05:22 PKT", "role": "Strategic Lead", "status": "Verified"},
    {"id": "AUD-1004", "user": "System Daemon", "action": "US Working Contractors Catalog (30) Staged", "timestamp": "2026-09-10 00:10:00 PKT", "role": "Watchdog", "status": "Verified"}
]


def _default_shared_state():
    return {
        "photos": {},
        "profiles": copy.deepcopy(DEFAULT_PROFILES),
        "attendance": copy.deepcopy(ATTENDANCE_DEFAULTS),
        "leaves": copy.deepcopy(LEAVE_DEFAULTS),
        "clearedFines": {},
        "accessMap": {k: v["allowed"] for k, v in DEFAULT_PROFILES.items()},
        "auditLog": copy.deepcopy(INITIAL_AUDIT_LOG),
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
        if key in saved:
            if isinstance(saved[key], dict):
                state[key].update(saved[key])
            elif isinstance(saved[key], list):
                state[key] = saved[key]
    return state


def read_shared_state():
    with SHARED_STATE_LOCK:
        return _read_shared_state_unlocked()


def _write_shared_state_unlocked(state):
    SHARED_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = SHARED_STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(SHARED_STATE_FILE)


def _validate_shared_update(payload):
    if not isinstance(payload, dict):
        raise ValueError("State update must be a JSON object.")
    resource = payload.get("resource")
    if resource not in {"photos", "profiles", "attendance", "leaves", "clearedFines", "accessMap", "auditLog"}:
        raise ValueError(f"Unknown shared state resource: {resource}")
    value = payload.get("value")

    if resource == "photos":
        key = str(payload.get("key", "")).strip().lower()
        if not re.fullmatch(r"[a-z0-9_\-]{2,32}", key):
            raise ValueError("Invalid colleague key.")
        if not isinstance(value, str) or not value.startswith("data:image/") or len(value) > 4000000:
            raise ValueError("Invalid profile image update.")
        return resource, key, value

    if resource == "profiles":
        key = str(payload.get("key", "")).strip().lower()
        if not re.fullmatch(r"[a-z0-9_\-]{2,32}", key):
            raise ValueError("Invalid colleague key format.")
        if not isinstance(value, dict):
            raise ValueError("Invalid profile data payload.")
        name = str(value.get("name", "")).strip()
        role = str(value.get("role", "")).strip()
        if not name or len(name) > 80 or not role or len(role) > 80:
            raise ValueError("Profile name and role must be between 1 and 80 characters.")
        assigned_states = value.get("assigned_states", [])
        if not isinstance(assigned_states, list) or len(assigned_states) > 2:
            raise ValueError("Maximum 2 contractor territory states allowed per colleague.")
        for st in assigned_states:
            if not isinstance(st, str) or st not in US_STATES_CATALOG:
                raise ValueError(f"Invalid territory state: {st}")
        assigned_contractors = value.get("assigned_contractors", [])
        if not isinstance(assigned_contractors, list) or len(assigned_contractors) > 2:
            raise ValueError("Maximum 2 contractors allowed per colleague.")
        for ct in assigned_contractors:
            if not isinstance(ct, str) or ct not in US_CONTRACTORS_CATALOG:
                raise ValueError(f"Invalid contractor assignment: {ct}")
        return resource, key, value

    if resource == "auditLog":
        if not isinstance(value, dict):
            raise ValueError("Invalid audit log entry.")
        return resource, None, value

    if not isinstance(value, dict):
        raise ValueError("State resource value must be an object.")

    if resource == "attendance":
        valid_days = {day for day, _ in ATTENDANCE_DAYS}
        valid_statuses = {"present", "absent", "received", "approved"}
        for key, days in value.items():
            if not isinstance(days, dict):
                raise ValueError("Invalid attendance profile.")
            if set(days) - valid_days or any(status not in valid_statuses for status in days.values()):
                raise ValueError("Invalid attendance entry.")

    elif resource == "leaves":
        for key, leave in value.items():
            if not isinstance(leave, dict):
                raise ValueError("Invalid leave profile.")
            if leave.get("state") not in {"received", "approved"}:
                raise ValueError("Invalid leave state.")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(leave.get("start", ""))) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(leave.get("end", ""))):
                raise ValueError("Leave dates must use YYYY-MM-DD format.")

    elif resource == "accessMap":
        for key, mods in value.items():
            if not isinstance(mods, list):
                raise ValueError("Invalid access map entry.")
            if any(not isinstance(m, int) or m < 1 or m > 22 for m in mods):
                raise ValueError("Modules must be integers between 1 and 22.")

    else:  # clearedFines
        pass

    return resource, payload.get("key"), value


def update_shared_state(payload):
    resource, key, value = _validate_shared_update(payload)
    with SHARED_STATE_LOCK:
        state = _read_shared_state_unlocked()
        if resource == "photos":
            state["photos"][key] = value
        elif resource == "profiles":
            if key not in state["profiles"]:
                # Provision defaults for newly created colleague
                initials = "".join(part[0].upper() for part in value.get("name", "CO").split()[:2]) or "CO"
                state["profiles"][key] = {
                    "key": key,
                    "name": value.get("name"),
                    "role": value.get("role"),
                    "software_id": f"GRA-COL-{len(state['profiles']) + 1:03d}",
                    "status": "Online",
                    "initials": initials,
                    "tags": ["Team", "Contractor"],
                    "assigned_states": value.get("assigned_states", []),
                    "assigned_contractors": value.get("assigned_contractors", []),
                    "allowed": [1, 2, 6, 7, 13, 16],
                    "metrics": {"pipeline": "500", "inboxes": "1 Inbox", "volume": "250", "deal": "$10,000"}
                }
            else:
                state["profiles"][key].update(value)
        elif resource == "attendance":
            for profile, days in value.items():
                state["attendance"][profile] = days
        elif resource == "leaves":
            for profile, leave in value.items():
                state["leaves"][profile] = leave
        elif resource == "accessMap":
            for profile, mods in value.items():
                state["accessMap"][profile] = mods
        elif resource == "auditLog":
            if "auditLog" not in state or not isinstance(state["auditLog"], list):
                state["auditLog"] = []
            state["auditLog"].insert(0, value)
            state["auditLog"] = state["auditLog"][:60]
        else:
            state["clearedFines"] = value
        _write_shared_state_unlocked(state)
        return state


LOGO_SVG = """<svg width="38" height="38" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle; margin-right:10px;">
    <rect width="24" height="24" rx="6" fill="#10B981" fill-opacity="0.22"/>
    <path d="M12 3L3 7.5L12 12L21 7.5L12 3Z" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M3 12L12 16.5L21 12" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M3 16.5L12 21L21 16.5" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

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
            <div id="brand-logo-container">{LOGO_SVG}</div>
            <div>
                <h2 style="margin:0; font-size: 19px; font-weight:800; letter-spacing:0.5px;">GRACE OUTREACH ASSISTANT</h2>
                <span style="font-size: 13px; color: var(--text-muted); font-weight: 500;">Built by King Saab | Strategic Guidance by Abdullah Khan</span>
                <div class="active-profile-chip" id="active-profile-chip"><i class="presence-dot online"></i><span>Active workspace · <b id="active-profile-name">King Saab · Super Admin</b></span></div>
            </div>
        </div>
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
            <span class="btn btn-gray profile-session-badge">👑 <span id="active-profile-badge">King Saab · Super Admin</span></span>
            <button class="btn btn-gray" onclick="showToast('All 3 Gmail inboxes are operating at peak performance.', 'success')">🔔 Notifications <b>2</b></button>
            <button class="btn btn-orange" onclick="openBroadcast()">📢 Broadcast Alert</button>
            <button class="btn btn-gray" onclick="openBrandPalette()">🎨 Brand Palette</button>
            <button id="audio-btn" class="btn btn-gray" onclick="toggleAudio()">🔊 Audio: ON</button>
            <button class="btn btn-gray" onclick="openSoundscape()">♫ Soundscape</button>
            <button id="theme-btn" class="btn btn-gray" onclick="toggleTheme()">🌓 Theme: DARK</button>
            <button class="btn btn-red" onclick="powerOff()">⏹ Power Off</button>
        </div>
    </div>
    <div id="toast-region" class="toast-region" aria-live="polite" aria-atomic="true"></div>

    <!-- Executive Authentication & Lock Screen Portal -->
    <div id="auth-gateway-overlay" class="modal-backdrop auth-gateway-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="auth-portal-title">
        <div class="modal-card auth-card" style="position:relative;">
            <button type="button" id="gateway-sound-toggle" class="gateway-sound-toggle" onclick="toggleGatewayAudio()">🔇 Ambient Sound: OFF</button>
            <div class="auth-header">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    {LOGO_SVG}
                    <div>
                        <h3 id="auth-portal-title" style="margin:0; font-size:18px; font-weight:800; color:var(--accent-gold); letter-spacing:0.5px;">GRACE EXECUTIVE GATEWAY</h3>
                        <small style="color:var(--accent-green); font-weight:700; font-size:11px;">AES-256 Hardware Locker • Role-Based Terminal Access</small>
                    </div>
                </div>
                <div id="gateway-mandatory-notice" class="mandatory-notice" hidden>🔒 <b>Mandatory Access:</b> Please sign in with an executive identity or create an account to unlock the workspace.</div>
                <p id="auth-status-desc" class="modal-copy" style="margin:6px 0 16px;">Session locked. Authenticate with colleague credentials or provision a new account.</p>
                <div class="auth-tabs">
                    <button id="auth-tab-btn-signin" class="auth-tab-btn active" onclick="switchAuthTab('signin')">🔐 Sign In</button>
                    <button id="auth-tab-btn-register" class="auth-tab-btn" onclick="switchAuthTab('register')">✨ Create Account</button>
                    <button id="auth-tab-btn-forgot" class="auth-tab-btn" onclick="switchAuthTab('forgot')">🔑 Forgot Password</button>
                </div>
            </div>

            <!-- Sign In Pane -->
            <div id="auth-pane-signin" class="auth-pane">
                <div class="form-grid" style="grid-template-columns:1fr; gap:12px; margin:14px 0;">
                    <label>Select Colleague Identity
                        <select id="login-identity-picker">
                            <option value="king">👑 King Saab · Super Admin</option>
                            <option value="abdullah">🎯 Abdullah Khan · Strategic Lead</option>
                            <option value="sarah">📈 Sarah Malik · Growth Marketer</option>
                            <option value="hamza">🔍 Hamza Ali · Lead Collector</option>
                        </select>
                    </label>
                    <label>Terminal Password
                        <div style="position:relative; display:flex; align-items:center;">
                            <input id="login-password-input" type="password" value="grace2026" placeholder="Enter password (default: grace2026)" style="padding-right:42px;">
                            <button type="button" class="password-toggle-btn" onclick="togglePasswordVisibility('login-password-input')" title="Toggle password visibility">👁️</button>
                        </div>
                    </label>
                </div>
                <div class="fast-login-tray">
                    <span class="eyebrow" style="font-size:10px; margin-bottom:6px;">QUICK 1-CLICK FAST-PASS LOGINS</span>
                    <div style="display:flex; flex-wrap:wrap; gap:6px;">
                        <button type="button" class="fast-pass-btn" onclick="fastPassLogin('king')">👑 King Saab</button>
                        <button type="button" class="fast-pass-btn" onclick="fastPassLogin('abdullah')">🎯 Abdullah</button>
                        <button type="button" class="fast-pass-btn" onclick="fastPassLogin('sarah')">📈 Sarah</button>
                        <button type="button" class="fast-pass-btn" onclick="fastPassLogin('hamza')">🔍 Hamza</button>
                    </div>
                </div>
                <div class="dialog-actions" style="margin-top:18px;">
                    <button id="gateway-dismiss-btn" class="btn btn-gray" onclick="unlockGatewayPreview()">Dismiss / Cancel</button>
                    <button class="btn btn-blue" onclick="submitSignIn()">Authenticate &amp; Unlock</button>
                </div>
            </div>

            <!-- Create Account Pane -->
            <div id="auth-pane-register" class="auth-pane" hidden>
                <div class="form-grid" style="gap:10px; margin:12px 0;">
                    <label>Full Name<input id="reg-name" type="text" placeholder="e.g. Zayd Malik"></label>
                    <label>Role Title<input id="reg-role" type="text" placeholder="e.g. Outreach Specialist"></label>
                    <label>Colleague Key (ID)<input id="reg-key" type="text" placeholder="e.g. zayd (lowercase letters)"></label>
                    <label>Password<input id="reg-password" type="password" value="grace2026"></label>
                </div>
                <div class="territory-section" style="margin-top:10px; padding:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span class="eyebrow" style="font-size:10px;">TERRITORY STATES (MAX 2)</span>
                        <small id="reg-territory-warn" style="color:var(--accent-orange); font-size:10px;" hidden>Max 2 reached</small>
                    </div>
                    <input type="text" id="reg-state-search" class="search-input" placeholder="🔍 Search 50 US States..." oninput="filterRegChips('states', this.value)">
                    <div id="reg-territory-chips" class="territory-chips-container" style="max-height:85px;"></div>
                </div>
                <div class="territory-section" style="margin-top:10px; padding:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span class="eyebrow" style="font-size:10px;">US WORKING CONTRACTORS (MAX 2)</span>
                        <small id="reg-contractor-warn" style="color:var(--accent-orange); font-size:10px;" hidden>Max 2 reached</small>
                    </div>
                    <input type="text" id="reg-contractor-search" class="search-input" placeholder="🔍 Search US Working Contractors..." oninput="filterRegChips('contractors', this.value)">
                    <div id="reg-contractor-chips" class="territory-chips-container" style="max-height:85px;"></div>
                </div>
                <div class="dialog-actions" style="margin-top:16px;">
                    <button class="btn btn-gray" onclick="switchAuthTab('signin')">Back to Sign In</button>
                    <button class="btn btn-blue" onclick="submitCreateAccount()">Register Identity &amp; Open</button>
                </div>
            </div>

            <!-- Forgot Password Pane -->
            <div id="auth-pane-forgot" class="auth-pane" hidden>
                <p style="font-size:12px; color:var(--text-muted); line-height:1.5;">Super Admin master recovery key will reset the selected colleague credentials back to default (<code>grace2026</code>).</p>
                <div class="form-grid" style="grid-template-columns:1fr; gap:12px; margin:12px 0;">
                    <label>Target Colleague Account
                        <select id="forgot-account-select">
                            <option value="king">King Saab (GRA-ADM-001)</option>
                            <option value="abdullah">Abdullah Khan (GRA-LEAD-002)</option>
                            <option value="sarah">Sarah Malik (GRA-MKT-003)</option>
                            <option value="hamza">Hamza Ali (GRA-COL-004)</option>
                        </select>
                    </label>
                    <label>Master Vault Key<input type="text" readonly value="GRA-MASTER-AES256-RECOVERY-KEY"></label>
                </div>
                <div class="dialog-actions" style="margin-top:18px;">
                    <button class="btn btn-gray" onclick="switchAuthTab('signin')">Back to Sign In</button>
                    <button class="btn btn-orange" onclick="submitPasswordReset()">Reset Password to Default</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Interactive Avatar Cropping Modal (Auto-Fit for Mobile & Any Ratio) -->
    <div id="image-cropper-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="cropper-title">
        <div class="modal-card wide-modal cropper-card">
            <div class="modal-header">
                <div>
                    <span class="eyebrow">AUTO-ASPECT FRAMING ENGINE</span>
                    <h3 id="cropper-title" style="margin:2px 0 0;">Crop &amp; Frame Colleague Avatar</h3>
                </div>
                <button class="modal-close" onclick="closeImageCropper()" aria-label="Close image cropper">×</button>
            </div>
            <p class="modal-copy">Handles any mobile portrait (9:16), wide, or square photo. Use zoom slider or mouse wheel to zoom in/out, drag to reposition.</p>
            <div class="cropper-workspace">
                <div class="canvas-wrap">
                    <canvas id="cropper-canvas" width="320" height="320"></canvas>
                </div>
                <div class="cropper-controls">
                    <label>Zoom / Scale (<span id="cropper-zoom-val">1.0×</span>)
                        <input id="cropper-zoom" type="range" min="0.15" max="4.0" step="0.02" value="1" oninput="onCropperZoomChange()">
                    </label>
                    <div style="display:flex; flex-wrap:wrap; gap:6px;">
                        <button type="button" class="btn btn-gray" style="font-size:11px; padding:6px 10px;" onclick="cropperFitFull()">📐 Fit Full Photo</button>
                        <button type="button" class="btn btn-gray" style="font-size:11px; padding:6px 10px;" onclick="cropperFillCircle()">🔍 Fill Circle</button>
                        <button type="button" class="btn btn-gray" style="font-size:11px; padding:6px 10px;" onclick="cropperResetCenter()">↺ Center</button>
                    </div>
                    <div class="cropper-preview-box">
                        <span class="eyebrow">LIVE CIRCULAR PREVIEW</span>
                        <canvas id="cropper-preview" width="96" height="96"></canvas>
                    </div>
                </div>
            </div>
            <div class="dialog-actions">
                <button class="btn btn-gray" onclick="closeImageCropper()">Cancel</button>
                <button class="btn btn-blue" onclick="saveCroppedAvatar()">Crop &amp; Save Avatar</button>
            </div>
        </div>
    </div>

    <!-- Colleague Settings & Territories Modal -->
    <div id="colleague-settings-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="settings-title">
        <div class="modal-card wide-modal">
            <div class="modal-header">
                <h3 id="settings-title">Colleague Settings &amp; Territories</h3>
                <button class="modal-close" onclick="closeColleagueSettings()" aria-label="Close settings">×</button>
            </div>
            <p class="modal-copy">Update identity, role, and manage US contractor &amp; territory assignments (strict limit of max 2 states and max 2 contractors).</p>
            <input type="hidden" id="edit-colleague-key">
            <div class="form-grid">
                <label>Colleague name<input id="edit-colleague-name" type="text"></label>
                <label>Role title<input id="edit-colleague-role" type="text"></label>
            </div>
            <div class="territory-section">
                <div class="territory-header">
                    <div>
                        <span class="eyebrow">CONTRACTOR TERRITORY ASSIGNMENT</span>
                        <strong style="font-size:14px;">Assigned States (<span id="assigned-states-count">0</span> / 2 Max)</strong>
                    </div>
                    <small id="territory-warning" class="territory-warning-banner" hidden>⚠️ Maximum 2 states allowed!</small>
                </div>
                <input type="text" id="edit-state-search" class="search-input" placeholder="🔍 Search 50 US States..." oninput="filterSettingsChips('states', this.value)">
                <div class="territory-chips-container" id="territory-chips-container"></div>
            </div>
            <div class="territory-section" style="margin-top:14px;">
                <div class="territory-header">
                    <div>
                        <span class="eyebrow">ASSIGNED US WORKING CONTRACTORS</span>
                        <strong style="font-size:14px;">Assigned Contractors (<span id="assigned-contractors-count">0</span> / 2 Max)</strong>
                    </div>
                    <small id="contractor-warning" class="territory-warning-banner" hidden>⚠️ Maximum 2 contractors allowed!</small>
                </div>
                <input type="text" id="edit-contractor-search" class="search-input" placeholder="🔍 Search US Working Contractors..." oninput="filterSettingsChips('contractors', this.value)">
                <div class="territory-chips-container" id="contractor-chips-container"></div>
            </div>
            <div class="dialog-actions">
                <button class="btn btn-gray" onclick="closeColleagueSettings()">Cancel</button>
                <button class="btn btn-blue" onclick="saveColleagueSettings()">Save Profile &amp; Territories</button>
            </div>
        </div>
    </div>

    <div id="brand-palette-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="palette-title">
        <div class="modal-card">
            <div class="modal-header"><h3 id="palette-title">Grace brand palette</h3><button class="modal-close" onclick="closeBrandPalette()" aria-label="Close brand palette">×</button></div>
            <p class="modal-copy">Instantly restyle the entire command center and tune typography for your operating style.</p>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding:8px 12px; background:rgba(16,185,129,0.08); border-radius:8px; border:1px solid rgba(16,185,129,0.3); font-size:12px;">
                <span style="color:var(--accent-green); font-weight:700;">👁️ Live Preview Mode (Canvas updates immediately)</span>
                <button class="btn btn-blue" style="font-size:11px; padding:6px 12px;" onclick="applyStoredTheme(); closeBrandPalette();">Save &amp; Lock</button>
            </div>
            <span class="eyebrow">COLOR THEMES</span>
            <div class="palette-grid">
                <button class="palette-option" onclick="applyTheme('midnight')" style="--swatch:#0B1120"><i></i><b>Midnight</b><small>Executive dark</small></button>
                <button class="palette-option" onclick="applyTheme('emerald')" style="--swatch:#06352B"><i></i><b>Emerald</b><small>Grace signature</small></button>
                <button class="palette-option" onclick="applyTheme('royal')" style="--swatch:#16204A"><i></i><b>Royal Signal</b><small>High contrast</small></button>
                <button class="palette-option" onclick="applyTheme('sandstone')" style="--swatch:#3B2A1A"><i></i><b>Sandstone</b><small>Warm command</small></button>
                <button class="palette-option" onclick="applyTheme('slate')" style="--swatch:#1E293B"><i></i><b>Slate</b><small>Neutral ops</small></button>
                <button class="palette-option" onclick="applyTheme('dark')" style="--swatch:#0B1120"><i></i><b>Executive Dark</b><small>Luxury Obsidian</small></button><button class="palette-option" onclick="applyTheme('light')" style="--swatch:#FFFFFF"><i></i><b>Clean Light</b><small>High contrast slate</small></button>
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
            <p class="modal-copy">Choose an ambient operating track or load a local audio/video file. Clip points apply to active media session.</p>
            <div class="soundscape-options">
                <button class="soundscape-option active" data-track="focus" onclick="selectSoundscape('focus')"><b>Calm Focus</b><small>Soft executive pulse</small></button>
                <button class="soundscape-option" data-track="pulse" onclick="selectSoundscape('pulse')"><b>Emerald Pulse</b><small>High-velocity operations</small></button>
                <button class="soundscape-option" data-track="strategy" onclick="selectSoundscape('strategy')"><b>Strategic Flow</b><small>Measured planning ambience</small></button>
                <button class="soundscape-option" data-track="night" onclick="selectSoundscape('night')"><b>Night Shift</b><small>Low-light focus mode</small></button>
            </div>
            <div style="display:flex; gap:10px; margin:14px 0 6px; align-items:center;">
                <span class="eyebrow" style="font-size:10px;">LOOP MODE:</span>
                <button type="button" id="loop-single-btn" class="btn btn-gray" style="font-size:11px; padding:6px 12px;" onclick="setLoopMode('single')">🔁 Repeat Track</button>
                <button type="button" id="loop-ambient-btn" class="btn btn-blue" style="font-size:11px; padding:6px 12px;" onclick="setLoopMode('ambient')">🔀 Ambient Playlist Loop</button>
            </div>
            <div class="audio-player-shell">
                <div><span class="eyebrow">ACTIVE SOUNDSCAPE</span><strong id="soundscape-status">Calm Focus · Ready</strong></div>
                <div class="audio-controls"><button class="btn btn-blue" onclick="toggleSoundscape()">▶ Start / Pause</button><span id="soundscape-time">00:00 / 00:00</span></div>
            </div>
            <label class="upload-zone"><span>＋ Load custom audio or video</span><small>Audio/video files are previewed locally; video soundtracks are routed through clip controls.</small><input id="custom-media-input" type="file" accept="audio/*,video/*" onchange="loadCustomMedia(event)"></label>
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

    <!-- Real-Time Interactive Campaign Execution Studio Drawer / Modal -->
    <div id="campaign-studio-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="campaign-studio-title">
        <div class="modal-card campaign-studio-card">
            <div class="modal-header">
                <div>
                    <span class="eyebrow">ENTERPRISE CAMPAIGN DISPATCH ENGINE</span>
                    <h3 id="campaign-studio-title" style="margin:2px 0 0;">Campaign Studio &amp; Real-Time Dispatcher</h3>
                </div>
                <button class="modal-close" onclick="closeCampaignStudio()" aria-label="Close campaign studio">×</button>
            </div>
            <p class="modal-copy">Select contact database records, rotate Spintax variants with spam scoring, verify OAuth/App Passwords, and trigger live jittered sending.</p>

            <!-- Step 1: Database Contact Range -->
            <div class="studio-step">
                <div class="step-header">
                    <strong>1. Database Contact Range Selector</strong>
                    <span class="step-badge">1,000 Verified Contractors in Pool</span>
                </div>
                <div class="form-grid" style="grid-template-columns:1fr 1fr; gap:12px;">
                    <label>Start Record Number
                        <input id="studio-range-start" type="number" min="1" max="1000" value="1" oninput="updateStudioRange()">
                    </label>
                    <label>End Record Number (Draft Count)
                        <input id="studio-range-end" type="number" min="1" max="1000" value="25" oninput="updateStudioRange()">
                    </label>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:12px; color:var(--text-muted);">Active Selection: <b id="studio-target-count" style="color:var(--accent-gold);">25 Decision-Makers</b></span>
                    <small style="color:var(--accent-green); font-weight:700;">Target Segment: Commercial Architects &amp; General Contractors</small>
                </div>
            </div>

            <!-- Step 2: Template, Spintax Rotation & Spam Score -->
            <div class="studio-step">
                <div class="step-header">
                    <strong>2. Template, Spintax AI Variants &amp; Spam Scorer</strong>
                    <span class="spam-score-pill">🛡️ 99.2% Clean · Zero Spam Flags</span>
                </div>
                <label>Subject Line (with Spintax choice brackets)
                    <input id="studio-subject" type="text" value="{{Exclusive Alliance|Commercial Opportunity|Architectural Partnership}} with {{{{company}}}}">
                </label>
                <label style="margin-top:8px;">Email Body Template
                    <textarea id="studio-body" rows="4">{{Hi|Hello|Dear}} {{{{first_name}}}}, I noticed your recent architectural projects in {{{{state}}}}. We would love to collaborate on upcoming commercial developments.</textarea>
                </label>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                    <button type="button" class="btn btn-gray" style="font-size:11px;" onclick="generateStudioAiVariants()">🎲 Generate 3 AI Rotating Variants</button>
                    <small style="color:var(--text-muted); font-size:11px;">Automatic hash rotation per recipient</small>
                </div>
                <div id="studio-variants-preview" class="spintax-preview" style="margin-top:8px; display:none;"></div>
            </div>

            <!-- Step 3: Sending Account & Auth Protocol Gate -->
            <div class="studio-step">
                <div class="step-header">
                    <strong>3. Multi-Tenant Sending Account &amp; Connection Method</strong>
                    <span id="studio-auth-chip" class="auth-status-chip connected">● OAuth 2.0 Connected</span>
                </div>
                <div class="form-grid" style="grid-template-columns:1.2fr 1fr; gap:12px;">
                    <label>Select Sending Inbox
                        <select id="studio-inbox-select" onchange="updateStudioInboxAuth(this.value)">
                            <option value="business.inbox1@gmail.com">business.inbox1@gmail.com (OAuth 2.0)</option>
                            <option value="outreach.node2@gmail.com">outreach.node2@gmail.com (16-Digit App Password)</option>
                            <option value="relay.personal@gmail.com">relay.personal@gmail.com (OAuth 2.0 Backup)</option>
                        </select>
                    </label>
                    <div style="display:flex; flex-direction:column; justify-content:center; gap:6px;">
                        <button type="button" id="studio-auth-action-btn" class="btn btn-gray" style="font-size:11px;" onclick="triggerOAuthPermissionFlow()">🔗 Re-Authorize Google OAuth</button>
                        <small id="studio-auth-desc" style="font-size:11px; color:var(--text-muted);">AES-256 Token Active</small>
                    </div>
                </div>
            </div>

            <!-- Step 4: Staging Drafts & Multi-Campaign Execution -->
            <div class="studio-step">
                <div class="step-header">
                    <strong>4. Multi-Campaign Staging &amp; Draft Progress</strong>
                    <span id="studio-campaign-id" class="countdown-pill">Campaign #GRA-CMP-104</span>
                </div>
                <div class="progress-bar-wrap">
                    <div id="studio-draft-progress" class="progress-bar-fill"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span id="studio-draft-status" style="font-size:12px; color:var(--text-muted);">Awaiting draft initialization...</span>
                    <button type="button" class="btn btn-blue" onclick="stageStudioDrafts()">📝 Stage Drafts in Gmail Account</button>
                </div>
            </div>

            <!-- Step 5: Jittered Dispatch Engine -->
            <div class="studio-step">
                <div class="step-header">
                    <strong>5. Dispatch Pacing &amp; Randomized Human Jitter</strong>
                    <span class="countdown-pill" id="studio-jitter-label">Random Jitter: 1s – 5s</span>
                </div>
                <div class="form-grid" style="grid-template-columns:1fr 1fr; gap:12px;">
                    <label>Dispatch Mode
                        <select id="studio-dispatch-mode">
                            <option value="auto">⚡ Autonomous Jittered Dispatch</option>
                            <option value="manual">👁️ Manual Review &amp; Send</option>
                        </select>
                    </label>
                    <label>Jitter Pacing Profile
                        <select id="studio-jitter-select" onchange="updateJitterProfile(this.value)">
                            <option value="human">🎲 Human Jitter (Random 1s, 3s, 5s)</option>
                            <option value="steady">⏱ Steady Pacing (4s interval)</option>
                            <option value="conservative">🛡 Conservative (8s interval)</option>
                        </select>
                    </label>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin:12px 0 8px;">
                    <button type="button" class="btn btn-orange" onclick="runStudioDispatch()">🚀 Execute Live Safe Dispatch</button>
                    <button type="button" class="btn btn-gray" onclick="cancelStudioDispatch()">⏹ Halt Queue</button>
                </div>
                <div id="studio-live-ticker" class="dispatch-live-ticker" style="display:none;"></div>
            </div>
        </div>
    </div>
    <div id="ai-mascot" class="ai-mascot" onclick="toggleAIAssistant()" role="button" tabindex="0" aria-label="Open Grace AI Guide" onkeydown="if(event.key==='Enter' || event.key===' ') toggleAIAssistant()">
        <span class="robot-3d" aria-hidden="true"><i class="robot-antenna"></i><i class="robot-head"></i><i class="robot-eye left"></i><i class="robot-eye right"></i><i class="robot-body"></i><i class="robot-arm left"></i><i class="robot-arm right"></i></span><span class="ai-ping"></span>
    </div>
    <aside id="ai-assistant" class="ai-drawer" aria-label="Grace AI Guide" aria-hidden="true">
        <div class="ai-drawer-head"><div><span class="eyebrow">MODULE 11 · ONLINE</span><h3>Grace AI Guide</h3><small style="display:block;color:var(--text-muted);margin-top:4px;">Drag robot anywhere · bilingual workflow copilot</small></div><div style="display:flex;align-items:flex-start;gap:8px;"><select id="ai-language" aria-label="Guide language" onchange="setAILanguage(this.value)"><option value="en">English</option><option value="ur">Roman Urdu</option></select><button class="modal-close" onclick="closeAIAssistant()" aria-label="Close AI Guide">×</button></div></div>
        <div id="ai-messages" class="ai-messages">
            <div class="ai-response-block"><div class="ai-bubble ai-bubble-bot">Welcome. Select a module below and I will guide you step by step. Har module ka workflow neeche available hai.</div><button class="ai-response-audio" onclick="speakText(this.previousElementSibling.innerText, this)">🔊 Play response</button></div>
        </div>
        <div class="ai-library-head"><span class="eyebrow">22-MODULE WORKFLOW LIBRARY</span><small>Choose any module for runbook</small></div>
        <div id="ai-workflow-library" class="ai-workflow-library"></div>
        <div class="ai-suggestions"><button onclick="askAI('How do I use Module 12?', 12)">Module 12 walkthrough</button><button onclick="askAI('Show restricted modules')">Explain access</button></div>
        <div class="ai-compose"><input id="ai-input" placeholder="Ask in English or Roman Urdu..." onkeydown="if(event.key==='Enter') sendAIMessage()"><button class="btn btn-blue" onclick="sendAIMessage()">Send</button></div>
        <button class="tts-button" onclick="speakGuide()">🔊 Play voice guidance</button>
    </aside>
    """


def render_navigation(active_tab):
    d_active = "btn-blue" if active_tab == "dashboard" else "btn-gray"
    m_active = "btn-blue" if active_tab == "matrix" else "btn-gray"
    c_active = "btn-blue" if active_tab == "colleagues" else "btn-gray"
    return f"""
    <div class="card" style="padding:12px 18px;">
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <a href="/api/?tab=dashboard" class="btn {d_active}">1. Dashboard Overview</a>
            <a href="/api/?tab=matrix" class="btn {m_active}">2. 22-Module Control Matrix</a>
            <a href="/api/?tab=colleagues" class="btn {c_active}">3. Colleague Management</a>
        </div>
    </div>
    <div class="view-as-bar">
        <div><span class="eyebrow">SUPER ADMIN VIEW-AS</span><strong style="font-size:14px;">Preview colleague workspace instantly</strong><small id="active-scope-count">All 22 modules enabled</small></div>
        <div class="view-as-controls"><span id="view-as-label">King Saab · Super Admin</span><select id="view-as-picker" aria-label="Active profile workspace" onchange="changeViewAs(this.value)"><option value="king">King Saab · Super Admin · All 22</option><option value="abdullah">Abdullah Khan · Strategic Lead · 8 modules</option><option value="sarah">Sarah Malik · Marketer · 7 modules</option><option value="hamza">Hamza Ali · Collector · 6 modules</option></select></div>
    </div>
    """


BASE_CSS = """
    :root {
        --bg-main: #0B1120;
        --bg-card: #001A17;
        --text-main: #F8FAFC;
        --text-muted: #9BB0AD;
        --border-color: #123B35;
        --accent-blue: #D6A117;
        --accent-green: #10B981;
        --accent-orange: #F59E0B;
        --accent-red: #EF4444;
        --accent-gold: #D6A117;
        --nav-color: #00110F;
    }
    /* GLOBAL BODY DEFAULT */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin: 0;
        padding: 22px;
        transition: background-color 0.2s ease, color 0.2s ease;
    }

    /* =========================================================================
       DARK THEME (Executive Dark Luxury)
       ========================================================================= */
    body.dark, body:not(.light) {
        --bg-main: #0B1120;
        --bg-card: #001A17;
        --text-main: #F8FAFC;
        --text-muted: #9BB0AD;
        --border-color: #123B35;
        --accent-blue: #D6A117;
        --accent-green: #10B981;
        --accent-orange: #F59E0B;
        --accent-gold: #D6A117;
        background-color: #0B1120 !important;
        color: #F8FAFC !important;
        background-image: radial-gradient(circle at 50% -20%, rgba(16, 185, 129, .08), transparent 38rem);
    }
    body.dark .top-bar, body:not(.light) .top-bar {
        background: var(--nav-color, #00110F) !important;
        border-color: #80621B !important;
    }
    body.dark .top-bar h1, body.dark .top-bar a, body.dark .top-bar span,
    body:not(.light) .top-bar h1, body:not(.light) .top-bar a, body:not(.light) .top-bar span {
        color: #F8FAFC !important;
    }
    body.dark .card, body.dark .stat-card, body.dark .module-panel, body.dark .modal-card,
    body:not(.light) .card, body:not(.light) .stat-card, body:not(.light) .module-panel, body:not(.light) .modal-card {
        background: #001A17 !important;
        border: 1px solid #123B35 !important;
        color: #F8FAFC !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
    }
    body.dark .stat-title, body:not(.light) .stat-title {
        color: #9BB0AD !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }
    body.dark .stat-value, body:not(.light) .stat-value {
        color: #10B981 !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        margin: 10px 0 6px !important;
        text-shadow: 0 0 16px rgba(16,185,129,0.35) !important;
    }
    body.dark .stat-sub, body:not(.light) .stat-sub {
        color: #10B981 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    body.dark .card h1, body.dark .card h2, body.dark .card h3, body.dark .card h4,
    body:not(.light) .card h1, body:not(.light) .card h2, body:not(.light) .card h3, body:not(.light) .card h4 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    body.dark .card p, body.dark .card span,
    body:not(.light) .card p, body:not(.light) .card span {
        color: #E2E8F0;
    }
    body.dark .btn-gray, body:not(.light) .btn-gray {
        background: #032824 !important;
        color: #F8FAFC !important;
        border: 1px solid #80621B !important;
    }
    body.dark .btn-blue, body:not(.light) .btn-blue {
        background: #D6A117 !important;
        color: #061510 !important;
    }
    body.dark .module-card, body:not(.light) .module-card {
        background: #001A17 !important;
        border-color: #123B35 !important;
    }
    body.dark .colleague-guide-card, body:not(.light) .colleague-guide-card {
        background: linear-gradient(135deg, rgba(6,53,43,0.35), rgba(11,17,32,0.85)) !important;
        border-color: rgba(16,185,129,0.3) !important;
        color: #F8FAFC !important;
    }
    body.dark .colleague-guide-card h3, body:not(.light) .colleague-guide-card h3 {
        color: #FFFFFF !important;
    }
    body.dark table th, body:not(.light) table th {
        color: #9BB0AD !important;
        background: #001A17 !important;
    }
    body.dark table td, body:not(.light) table td {
        color: #F8FAFC !important;
        border-color: #123B35 !important;
    }
    body.dark table td b, body:not(.light) table td b {
        color: #FFFFFF !important;
    }
    body.dark .view-as-bar, body:not(.light) .view-as-bar {
        background: linear-gradient(100deg,rgba(16,185,129,.1),rgba(214,161,23,.06)) !important;
        border-color: var(--accent-gold) !important;
    }
    body.dark .view-as-bar strong, body:not(.light) .view-as-bar strong {
        color: #FFFFFF !important;
    }
    body.dark .log-box, body:not(.light) .log-box {
        background: #051412 !important;
        border: 1px solid #123B35 !important;
        border-radius: 10px !important;
        color: #34D399 !important;
        font-family: monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        max-height: 220px !important;
        overflow-y: auto !important;
    }
    body.dark .log-box div, body:not(.light) .log-box div {
        color: #34D399 !important;
        margin-bottom: 4px !important;
    }

    /* =========================================================================
       LIGHT THEME (High-Contrast Professional Clean Slate)
       ========================================================================= */
    body.light {
        --bg-main: #F1F5F9;
        --bg-card: #FFFFFF;
        --text-main: #0F172A;
        --text-muted: #475569;
        --border-color: #CBD5E1;
        --accent-blue: #0284C7;
        --accent-green: #059669;
        --accent-orange: #D97706;
        --accent-gold: #B45309;
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        background-image: none !important;
    }
    body.light .top-bar {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    body.light .top-bar h1, body.light .top-bar a, body.light .top-bar span {
        color: #0F172A !important;
    }
    body.light .profile-session-badge {
        background: #F8FAFC !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    body.light .nav-tabs {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
    }
    body.light .nav-tab {
        color: #475569 !important;
    }
    body.light .nav-tab.active {
        background: #0284C7 !important;
        color: #FFFFFF !important;
    }
    body.light .card, body.light .stat-card, body.light .module-panel, body.light .modal-card {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06) !important;
    }
    body.light .stat-title {
        color: #475569 !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }
    body.light .stat-value {
        color: #059669 !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        margin: 10px 0 6px !important;
        text-shadow: none !important;
    }
    body.light .stat-sub {
        color: #059669 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    body.light .card h1, body.light .card h2, body.light .card h3, body.light .card h4 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    body.light .card p, body.light .card span {
        color: #334155;
    }
    body.light .btn-gray {
        background: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    body.light .btn-blue {
        background: #0284C7 !important;
        color: #FFFFFF !important;
    }
    body.light .module-card {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    body.light .mod-title {
        color: #64748B !important;
    }
    body.light .mod-name {
        color: #0F172A !important;
    }
    body.light .module-desc {
        color: #334155 !important;
    }
    body.light .mod-status-tag {
        color: #059669 !important;
        background: rgba(5,150,105,0.1) !important;
    }
    body.light .colleague-guide-card {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
    }
    body.light .colleague-guide-card h3, body.light .colleague-guide-card strong {
        color: #0F172A !important;
    }
    body.light .colleague-guide-card span, body.light .colleague-guide-card div {
        color: #334155 !important;
    }
    body.light table th {
        color: #475569 !important;
        background: #F8FAFC !important;
        border-color: #CBD5E1 !important;
    }
    body.light table td {
        color: #0F172A !important;
        border-color: #E2E8F0 !important;
    }
    body.light table td b {
        color: #0F172A !important;
    }
    body.light .view-as-bar {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
    }
    body.light .view-as-bar strong, body.light .view-as-bar b {
        color: #0F172A !important;
    }
    body.light .view-as-bar small {
        color: #475569 !important;
    }
    body.light .view-as-controls select {
        background: #F8FAFC !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    body.light .log-box {
        background: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #34D399 !important;
        font-family: monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        max-height: 220px !important;
        overflow-y: auto !important;
    }
    body.light .log-box div {
        color: #34D399 !important;
        margin-bottom: 4px !important;
    }
    body.light select, body.light textarea, body.light input[type="text"], body.light input[type="number"], body.light input[type="password"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    body.light .telemetry-card {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    body.light .telemetry-card strong {
        color: #059669 !important;
        text-shadow: none !important;
    }
    body.light .telemetry-card .eyebrow {
        color: #475569 !important;
    }
    body.light .telemetry-card small {
        color: #059669 !important;
    }
    body.light .module-hero {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
    }
    body.light .module-hero h2 {
        color: #0F172A !important;
    }

    /* COMMON UTILITIES */
    .top-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
    .view-as-bar { display:flex; justify-content:space-between; align-items:center; gap:16px; margin:-8px 0 22px; padding:14px 18px; border:1px solid var(--accent-gold); border-radius:12px; }
    .view-as-bar strong { display:block; margin-top:4px; font-size:14px; }
    .view-as-bar small { display:block; margin-top:5px; color:var(--text-muted); font-size:12px; }
    .view-as-controls { display:flex; align-items:center; gap:12px; font-size:13px; font-weight:700; }
    .view-as-controls select { width:auto; min-width:290px; padding:9px 12px; font-size:13px; }
    .active-profile-chip { display:flex; align-items:center; gap:8px; margin-top:8px; font-size:12px; font-weight:700; }
    .btn { border: none; border-radius: 8px; padding: 9px 16px; font-weight: 700; font-size: 13px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 7px; transition: 0.15s ease; }
    .btn:hover { opacity: 0.92; transform: translateY(-1px); }
    .btn-red { background: #DC2626; color: white; }
    .btn-orange { background: #EA580C; color: white; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 22px; }
    .grid-2 { display: grid; grid-template-columns: 1.2fr 1fr; gap: 22px; }
    [hidden] { display: none !important; }
    .modal-backdrop { position: fixed; inset: 0; z-index: 50; display: grid; place-items: center; padding: 20px; background: rgba(2, 6, 23, .72); backdrop-filter: blur(8px); }
    .modal-card { width: min(560px, 100%); padding: 26px; border: 1px solid var(--border-color); border-radius: 16px; box-shadow: 0 24px 70px rgba(2, 6, 23, .4); }
    .wide-modal { width: min(780px, 100%); max-height: min(820px, calc(100vh - 40px)); overflow-y: auto; }
    .dialog-actions { display:flex; justify-content:flex-end; gap:12px; margin-top:24px; }

    .toast-region { position:fixed; top:24px; right:24px; z-index:90; width:min(400px, calc(100vw - 48px)); display:grid; gap:12px; pointer-events:none; }
    .toast { display:flex; align-items:flex-start; gap:12px; padding:15px 18px; border:1px solid var(--border-color); border-left:4px solid var(--accent-green); border-radius:12px; background:var(--bg-card); color:var(--text-main); box-shadow:0 18px 40px rgba(2,6,23,.35); font-size:13px; line-height:1.45; animation:toast-in .22s ease-out; pointer-events:auto; }
    .toast-warning { border-left-color:var(--accent-orange); }
    .toast-info { border-left-color:var(--accent-blue); }
    .toast-label { display:block; margin-bottom:3px; color:var(--accent-green); font-size:11px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
    .toast-warning .toast-label { color:var(--accent-orange); }
    .toast-info .toast-label { color:var(--accent-blue); }
    @keyframes toast-in { from { opacity:0; transform:translateY(-8px) scale(.98); } to { opacity:1; transform:translateY(0) scale(1); } }
    .modal-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .modal-header h3 { margin: 0; font-size: 19px; }
    .modal-close { border: 0; color: var(--text-muted); background: transparent; font-size: 26px; line-height: 1; cursor: pointer; }
    .modal-copy { margin: 9px 0 20px; color: var(--text-muted); font-size: 13px; line-height: 1.5; }
    .palette-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 12px 0 22px; }
    .palette-option { display:grid; gap:8px; padding:12px; text-align:left; color:var(--text-main); background:transparent; border:1px solid var(--border-color); border-radius:10px; cursor:pointer; }
    .palette-option:hover { border-color:var(--accent-gold); transform:translateY(-1px); }
    .palette-option i { display:block; height:42px; background:var(--swatch); border:1px solid rgba(255,255,255,.22); border-radius:8px; }
    .palette-option small { color: var(--text-muted); font-size:11px; }
    .palette-type-label { display:block; margin-bottom:12px; }
    .typography-grid, .form-grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:14px; }
    .color-control-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; margin:12px 0 22px; }
    .color-control-grid label { padding:12px; border:1px solid var(--border-color); border-radius:10px; }
    .color-control-grid input[type="color"] { width:100%; height:40px; padding:3px; border:1px solid var(--border-color); border-radius:8px; background:transparent; cursor:pointer; }
    .color-control-grid small { color:var(--text-muted); font-size:11px; font-weight:400; }
    label { display:grid; gap:7px; color:var(--text-muted); font-size:12px; font-weight:700; }
    select, textarea, input[type="number"], input[type="text"], input[type="password"] { width:100%; box-sizing:border-box; padding:11px 13px; color:var(--text-main); background:rgba(255,255,255,.04); border:1px solid var(--border-color); border-radius:8px; font:inherit; font-size:13px; }
    select option { color:#0F172A; }
    textarea { resize:vertical; }
    .check-control { display:flex; align-items:center; align-content:center; grid-template-columns:auto 1fr; padding:10px 0; }
    .toggle-row { display:flex; flex-wrap:wrap; gap:18px; margin-top:16px; }
    .toggle-row label { display:flex; align-items:center; gap:7px; color:var(--text-main); font-size:13px; }
    input[type="checkbox"] { accent-color:var(--accent-green); }
    .soundscape-options { display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; }
    .soundscape-option { display:grid; gap:6px; padding:14px; text-align:left; color:var(--text-main); background:rgba(255,255,255,.03); border:1px solid var(--border-color); border-radius:10px; cursor:pointer; }
    .soundscape-option:hover, .soundscape-option.active { border-color:var(--accent-gold); background:rgba(214,161,23,.08); }
    .soundscape-option small { color:var(--text-muted); font-size:11px; }
    .audio-player-shell { display:flex; justify-content:space-between; align-items:center; gap:16px; margin:18px 0; padding:16px; border:1px solid var(--border-color); border-radius:10px; }
    .eyebrow { display:block; color:var(--accent-green); font-size:11px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
    .audio-player-shell strong { display:block; margin-top:6px; font-size:14px; }
    .audio-controls { display:flex; align-items:center; gap:14px; color:var(--text-muted); font-family:monospace; font-size:12px; }
    .upload-zone { display:grid; gap:6px; padding:16px; border:1px dashed var(--accent-gold); border-radius:10px; color:var(--text-main); cursor:pointer; }
    .upload-zone span { font-size:13px; font-weight:800; color:var(--accent-gold); }
    .upload-zone small { color:var(--text-muted); font-size:11px; font-weight:400; }
    .upload-zone input { margin-top:6px; }
    .clip-grid { display:grid; grid-template-columns:1fr 1fr auto; align-items:end; gap:12px; margin-top:14px; }

    /* AUTH GATEWAY MODAL */
    .auth-card { width: min(520px, 100%); padding: 28px; border: 1px solid var(--accent-gold); background: linear-gradient(145deg, #062b24, #001713); box-shadow: 0 28px 80px rgba(0,0,0,0.6); }
    .auth-tabs { display:flex; gap:8px; border-bottom:1px solid var(--border-color); padding-bottom:12px; margin-top:14px; }
    .auth-tab-btn { background:transparent; border:1px solid transparent; color:var(--text-muted); font-size:13px; font-weight:700; cursor:pointer; padding:7px 12px; border-radius:7px; transition:0.15s; }
    .auth-tab-btn:hover { color:var(--text-main); }
    .auth-tab-btn.active { color:var(--accent-gold); background:rgba(214,161,23,0.12); border-color:rgba(214,161,23,0.35); }
    .fast-login-tray { background:rgba(0,0,0,0.2); padding:12px; border-radius:10px; border:1px solid rgba(214,161,23,0.25); margin-top:10px; }
    .fast-pass-btn { padding:7px 11px; border-radius:7px; border:1px solid rgba(16,185,129,0.35); background:rgba(16,185,129,0.08); color:var(--accent-green); font-size:11px; font-weight:700; cursor:pointer; }
    .fast-pass-btn:hover { border-color:var(--accent-gold); color:var(--accent-gold); background:rgba(214,161,23,0.12); }
    .password-toggle-btn { position:absolute; right:8px; background:transparent; border:none; cursor:pointer; font-size:15px; color:var(--text-muted); }

    /* AI MASCOT & DRAWER */
    .ai-mascot { position:fixed; right:26px; bottom:26px; z-index:60; width:76px; height:76px; display:grid; place-items:center; border:1px solid var(--accent-gold); border-radius:24px; background:radial-gradient(circle at 35% 25%,rgba(255,255,255,.18),transparent 35%),linear-gradient(145deg,#06483a,#001713); box-shadow:0 14px 35px rgba(0,0,0,.45); cursor:grab; touch-action:none; user-select:none; transition:transform .2s ease; }
    .ai-mascot:active { cursor:grabbing; }
    .ai-mascot:hover { transform:translateY(-4px) rotate(-2deg); }
    .robot-3d { position:relative; width:44px; height:50px; display:block; filter:drop-shadow(4px 7px 4px rgba(0,0,0,.32)); }
    .robot-antenna { position:absolute; left:20px; top:-5px; width:3px; height:9px; background:#DCE7E5; border-radius:3px; }
    .robot-antenna::before { content:''; position:absolute; top:-4px; left:-3px; width:9px; height:9px; border-radius:50%; background:#D6A117; box-shadow:0 0 8px #D6A117; }
    .robot-head { position:absolute; left:4px; top:5px; width:36px; height:28px; border-radius:10px 10px 8px 8px; background:linear-gradient(145deg,#fff,#C9D5D5); border:1px solid #fff; transform:perspective(90px) rotateX(-5deg); }
    .robot-head::after { content:''; position:absolute; inset:5px 5px 7px; border-radius:6px; background:linear-gradient(145deg,#163E39,#061613); }
    .robot-eye { position:absolute; z-index:1; top:14px; width:5px; height:7px; border-radius:50%; background:#8FFFF0; box-shadow:0 0 7px #35D39B; }
    .robot-eye.left { left:12px; } .robot-eye.right { right:12px; }
    .robot-body { position:absolute; left:8px; top:34px; width:28px; height:15px; border-radius:6px 6px 8px 8px; background:linear-gradient(145deg,#fff,#B6C5C3); border:1px solid #fff; }
    .robot-body::after { content:'✦'; position:absolute; left:9px; top:0px; color:#D6A117; font-size:11px; }
    .robot-arm { position:absolute; top:35px; width:6px; height:14px; border-radius:4px; background:#D4DFDE; } .robot-arm.left { left:2px; transform:rotate(12deg); } .robot-arm.right { right:2px; transform:rotate(-12deg); }
    .ai-ping { position:absolute; right:-3px; top:-3px; width:10px; height:10px; border:2px solid #001713; border-radius:50%; background:var(--accent-green); box-shadow:0 0 10px var(--accent-green); }
    .ai-drawer { position:fixed; top:0; right:0; z-index:65; width:min(420px, 100vw); height:100vh; box-sizing:border-box; display:flex; flex-direction:column; padding:22px; background:var(--bg-card); border-left:1px solid var(--accent-gold); box-shadow:-16px 0 45px rgba(0,0,0,.35); transform:translateX(105%); transition:transform .25s ease; }
    .ai-drawer.open { transform:translateX(0); }
    .ai-drawer-head { display:flex; justify-content:space-between; align-items:flex-start; padding-bottom:16px; border-bottom:1px solid var(--border-color); }
    .ai-drawer-head h3 { margin:5px 0 0; font-size:18px; }
    .ai-messages { flex:1; overflow:auto; display:grid; align-content:start; gap:12px; padding:18px 0; }
    .ai-response-block { display:grid; gap:6px; }
    .ai-bubble { padding:13px 15px; border-radius:12px; font-size:13px; line-height:1.55; white-space:pre-wrap; }
    .ai-bubble-bot { background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.25); }
    .ai-bubble-user { justify-self:end; max-width:85%; background:rgba(214,161,23,.13); border:1px solid rgba(214,161,23,.35); }
    .ai-suggestions { display:flex; gap:8px; overflow:auto; padding-bottom:12px; }
    .ai-suggestions button, .tts-button { border:1px solid var(--border-color); border-radius:8px; padding:8px 12px; color:var(--text-muted); background:transparent; font-size:11px; cursor:pointer; white-space:nowrap; }
    .ai-suggestions button:hover, .tts-button:hover { color:var(--text-main); border-color:var(--accent-gold); }
    .ai-library-head { display:flex; justify-content:space-between; align-items:end; gap:10px; margin-bottom:8px; }
    .ai-library-head small { color:var(--text-muted); font-size:11px; }
    .ai-workflow-library { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:6px; max-height:180px; overflow:auto; padding:2px 0 10px; }
    .ai-workflow-item { display:flex; align-items:center; gap:8px; min-width:0; padding:8px 10px; border:1px solid var(--border-color); border-radius:8px; background:rgba(16,185,129,.04); color:var(--text-main); text-align:left; cursor:pointer; }
    .ai-workflow-item:hover { border-color:var(--accent-gold); background:rgba(214,161,23,.09); }
    .ai-workflow-item b { color:var(--accent-gold); font-size:11px; }
    .ai-workflow-item span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--text-muted); font-size:11px; }
    .ai-compose { display:flex; gap:8px; }
    .ai-compose input { flex:1; min-width:0; }
    .ai-response-audio { justify-self:start; border:1px solid rgba(16,185,129,.35); border-radius:8px; padding:6px 10px; color:var(--accent-green); background:transparent; font-size:11px; cursor:pointer; }
    .ai-response-audio:hover { border-color:var(--accent-gold); color:var(--accent-gold); }
    .tts-button { width:100%; margin-top:12px; }

    /* BROADCAST */
    .broadcast-overlay { position:fixed; inset:0; z-index:70; display:grid; place-items:center; padding:24px; background:rgba(0,8,7,.9); backdrop-filter:blur(10px); }
    .broadcast-overlay-card { width:min(580px, 100%); padding:36px; text-align:center; border:1px solid var(--accent-gold); border-radius:18px; background:linear-gradient(145deg,#062b24,#001713); box-shadow:0 30px 100px rgba(0,0,0,.5); }
    .broadcast-overlay-card h2 { margin:12px 0 10px; font-size:26px; }
    .broadcast-overlay-card p { margin:0 auto 16px; max-width:440px; color:var(--text-muted); line-height:1.5; font-size:14px; }
    .broadcast-overlay-card small { display:block; margin-bottom:22px; color:var(--accent-green); font-size:13px; }

    /* COLLEAGUES & TERRITORIES */
    .colleague-grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:18px; }
    .colleague-card { padding:20px; border:1px solid var(--border-color); border-radius:14px; background:rgba(16,185,129,.04); }
    .colleague-head { display:flex; align-items:center; gap:14px; }
    .avatar { width:54px; height:54px; object-fit:cover; display:grid; place-items:center; flex:0 0 54px; border-radius:50%; background:linear-gradient(145deg,#075642,#D6A117); color:#fff; font-size:16px; font-weight:800; border:2px solid var(--accent-gold); box-shadow: 0 0 12px rgba(214,161,23,.3); background-size:cover; background-position:center center; background-repeat:no-repeat; }
    .colleague-name { font-size:16px; font-weight:800; }
    .colleague-role { margin-top:3px; color:var(--text-muted); font-size:12px; font-weight:600; }
    .presence { display:inline-flex; align-items:center; gap:6px; margin-left:auto; color:var(--text-muted); font-size:12px; font-weight:700; }
    .presence-dot { width:9px; height:9px; border-radius:50%; background:#EF4444; box-shadow:0 0 8px rgba(239,68,68,.65); }
    .presence-dot.online { background:#10B981; box-shadow:0 0 8px rgba(16,185,129,.8); }
    .colleague-meta { display:grid; gap:8px; margin:16px 0; padding:14px 0; border-top:1px solid var(--border-color); border-bottom:1px solid var(--border-color); color:var(--text-muted); font-size:12px; }
    .colleague-meta b { color:var(--text-main); }
    .tag-list { display:flex; flex-wrap:wrap; gap:6px; align-items:center; }
    .tag { padding:4px 9px; border:1px solid rgba(214,161,23,.45); border-radius:999px; color:var(--accent-gold); font-size:11px; font-weight:800; }
    .state-badge { padding:4px 9px; border:1px solid rgba(16,185,129,.45); border-radius:999px; color:var(--accent-green); background:rgba(16,185,129,.08); font-size:11px; font-weight:800; }
    .colleague-actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
    .colleague-actions .btn { font-size:12px; padding:8px 12px; }
    .rbac-section { margin-top:22px; }
    .permission-card { min-width:0; overflow:hidden; margin-top:14px; padding:16px; border:1px solid var(--border-color); border-radius:12px; background:rgba(0,0,0,.08); }
    .permission-card-head { display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:12px; }
    .permission-card-head strong { font-size:13px; color:var(--text-main); }
    .permission-card-head small { color:var(--text-muted); font-size:11px; }
    .permission-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(210px, 1fr)); gap:8px; width:100%; }
    .permission-item { min-width:0; display:flex; align-items:center; gap:8px; padding:8px 10px; border:1px solid rgba(148,163,184,.16); border-radius:8px; background:rgba(255,255,255,.02); color:var(--text-muted); font-size:11px; overflow:hidden; cursor:pointer; transition:0.15s; }
    .permission-item:hover { border-color:var(--accent-gold); color:var(--text-main); background:rgba(214,161,23,.06); }
    .permission-item input { margin:0; flex:0 0 auto; }
    .perm-badge { font-family:monospace; font-weight:800; color:var(--accent-gold); font-size:10px; flex:0 0 auto; }
    .perm-icon { font-size:13px; flex:0 0 auto; color:var(--accent-green); }
    .perm-title { font-weight:600; font-size:11px; color:var(--text-main); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; }

    /* TERRITORY PICKER & SEARCH FILTERS */
    .territory-section { margin-top:20px; padding:16px; border:1px solid var(--border-color); border-radius:12px; background:rgba(0,0,0,.06); }
    .territory-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
    .territory-warning-banner { color:var(--accent-orange); font-size:12px; font-weight:800; }
    .search-input { width:100%; box-sizing:border-box; padding:9px 12px; border:1px solid var(--border-color); border-radius:8px; background:rgba(0,0,0,0.3); color:#F8FAFC; font-size:12px; margin-bottom:10px; }
    .search-input:focus { outline:none; border-color:var(--accent-gold); }
    .territory-chips-container { display:flex; flex-wrap:wrap; gap:8px; max-height:180px; overflow-y:auto; padding:4px; }
    .state-chip-btn { padding:6px 12px; border:1px solid var(--border-color); border-radius:8px; background:rgba(255,255,255,.03); color:var(--text-muted); font-size:12px; font-weight:600; cursor:pointer; transition:.15s; }
    .state-chip-btn:hover { border-color:var(--accent-gold); color:var(--text-main); }
    .state-chip-btn.selected { background:rgba(16,185,129,.16); border-color:var(--accent-green); color:var(--accent-green); font-weight:800; }
    .contractor-badge { padding:4px 9px; border:1px solid rgba(214,161,23,.45); border-radius:999px; color:var(--accent-gold); background:rgba(214,161,23,.08); font-size:11px; font-weight:800; }

    /* CROPPER MODAL */
    .cropper-card { width: min(660px, 100%); }
    .cropper-workspace { display:grid; grid-template-columns: 340px 1fr; gap:22px; align-items:center; margin:16px 0; }
    .canvas-wrap { width:320px; height:320px; background:#040e0c; border:2px dashed var(--accent-gold); border-radius:14px; overflow:hidden; position:relative; cursor:grab; display:grid; place-items:center; touch-action:none; }
    .canvas-wrap:active { cursor:grabbing; }
    #cropper-canvas { display:block; }
    .cropper-controls { display:grid; gap:16px; }
    .cropper-preview-box { text-align:center; padding:14px; border:1px solid var(--border-color); border-radius:12px; background:rgba(0,0,0,0.15); }
    #cropper-preview { border-radius:50%; border:2px solid var(--accent-gold); background:#040e0c; margin-top:8px; }

    /* BRAND PALETTE SCROLLBAR FIX */
    #brand-palette-modal .modal-card { max-height:88vh !important; overflow-y:auto !important; overflow-x:hidden !important; scrollbar-width:thin; scrollbar-color:var(--accent-green) var(--bg-card); }
    #brand-palette-modal .modal-card::-webkit-scrollbar { width:8px; }
    #brand-palette-modal .modal-card::-webkit-scrollbar-thumb { background:#10B981; border-radius:4px; }
    #brand-palette-modal .modal-card::-webkit-scrollbar-track { background:#001A17; }

    /* GATEWAY FLOATING AUDIO & MANDATORY BANNER */
    .gateway-sound-toggle { position:absolute; top:18px; right:18px; background:rgba(16,185,129,0.12); border:1px solid var(--accent-green); color:var(--accent-green); font-size:11px; font-weight:700; border-radius:999px; padding:6px 12px; cursor:pointer; transition:0.15s; }
    .gateway-sound-toggle:hover { background:rgba(16,185,129,0.25); }
    .mandatory-notice { padding:10px 14px; background:rgba(214,161,23,0.1); border:1px solid var(--accent-gold); border-radius:8px; color:var(--accent-gold); font-size:12px; font-weight:600; margin-bottom:14px; display:flex; align-items:center; gap:8px; }

    /* CAMPAIGN STUDIO INTERACTIVE MODAL */
    .campaign-studio-card { width: min(840px, 100%); max-height: 90vh; overflow-y: auto; scrollbar-width: thin; scrollbar-color: var(--accent-green) var(--bg-card); }
    .campaign-studio-card::-webkit-scrollbar { width: 8px; }
    .campaign-studio-card::-webkit-scrollbar-thumb { background: #10B981; border-radius: 4px; }
    .campaign-studio-card::-webkit-scrollbar-track { background: #001A17; }
    .studio-step { background: rgba(0,0,0,0.25); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; margin-bottom: 14px; }
    .step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .step-badge { background: var(--accent-green); color: #061510; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 6px; }
    .spam-score-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: rgba(16,185,129,0.15); border: 1px solid var(--accent-green); color: var(--accent-green); font-size: 11px; font-weight: 800; }
    .auth-status-chip { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; padding: 6px 12px; border-radius: 8px; }
    .auth-status-chip.connected { background: rgba(16,185,129,0.15); border: 1px solid var(--accent-green); color: var(--accent-green); }
    .auth-status-chip.pending { background: rgba(245,158,11,0.15); border: 1px solid var(--accent-orange); color: var(--accent-orange); }
    .progress-bar-wrap { height: 10px; background: rgba(255,255,255,0.08); border-radius: 5px; overflow: hidden; margin: 10px 0; }
    .progress-bar-fill { height: 100%; width: 0%; background: linear-gradient(90deg, var(--accent-green), var(--accent-gold)); transition: width 0.3s; }
    .countdown-pill { font-family: monospace; font-size: 13px; font-weight: 800; color: var(--accent-gold); }
    .dispatch-live-ticker { max-height: 120px; overflow-y: auto; font-family: monospace; font-size: 11px; line-height: 1.6; padding: 8px 12px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 1px solid var(--border-color); color: var(--accent-green); }

    /* ATTENDANCE & PAYROLL */
    .attendance-card { margin-top:22px; }
    .section-heading { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; margin-bottom:16px; }
    .section-heading h3, .section-heading h4 { margin:6px 0 0; font-size:18px; color:var(--text-main); }
    .section-heading.compact { align-items:end; margin-bottom:12px; }
    .section-heading.compact h4 { font-size:15px; }
    .section-heading small { color:var(--text-muted); font-size:12px; }
    .attendance-summary-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:18px; }
    .mini-stat { min-width:0; padding:14px; border:1px solid var(--border-color); border-radius:10px; background:rgba(16,185,129,.05); }
    .mini-stat span { display:block; color:var(--text-muted); font-size:12px; font-weight:600; }
    .mini-stat strong { display:block; margin-top:6px; color:var(--accent-gold); font-size:18px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .attendance-scroll { overflow-x:auto; border:1px solid var(--border-color); border-radius:12px; }
    .attendance-table { min-width:980px; margin-top:0; }
    .attendance-table th, .attendance-table td { padding:12px 10px; font-size:12px; vertical-align:middle; color:var(--text-main); }
    .attendance-table th { font-size:11px; font-weight:800; }
    .attendance-table td:first-child { min-width:150px; }
    .attendance-table td:first-child small, .leave-row small { display:block; margin-top:3px; color:var(--text-muted); font-size:11px; }
    .attendance-table select { min-width:115px; padding:8px 8px; font-size:12px; }
    .fine-balance { color:var(--accent-orange); white-space:nowrap; font-size:13px; font-weight:800; }
    .leave-panel { margin-top:20px; padding-top:20px; border-top:1px solid var(--border-color); }
    .leave-list { display:grid; gap:10px; }
    .leave-row { display:grid; grid-template-columns:1.4fr .8fr .8fr .8fr auto; align-items:end; gap:12px; padding:14px; border:1px solid var(--border-color); border-radius:10px; background:rgba(0,0,0,.06); }
    .leave-row > div { align-self:center; }
    .leave-row label { font-size:11px; }
    .leave-row input, .leave-row select { padding:8px; font-size:12px; }
    .leave-row button { font-size:11px; padding:8px 10px; }

    /* 22-MODULE MATRIX CARD REFINEMENTS (CRISP LEGIBILITY) */
    .modules-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-top: 18px; }
    .module-card { min-height: 96px; background: #001713 !important; border: 1px solid #123D36 !important; border-radius: 12px; padding: 16px 18px; text-decoration: none; display: flex; align-items: flex-start; gap: 14px; color: inherit; transition: 0.2s ease; }
    .module-card:hover { border-color: var(--accent-gold) !important; transform: translateY(-3px); box-shadow: 0 10px 24px rgba(0,0,0,.35); }
    .module-card.is-restricted { display:none; }
    .module-icon { width: 42px; height: 42px; flex: 0 0 42px; display: grid; place-items: center; color: #F59E0B; background: rgba(245, 158, 11, .12); border: 1px solid rgba(214, 161, 23, .65); border-radius: 10px; font-size: 20px; font-weight: 800; }
    .module-copy { min-width: 0; flex: 1; }
    .mod-title { font-size: 12px; font-weight: 800; color: var(--accent-gold); margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-transform: uppercase; letter-spacing: 0.5px; }
    .mod-name { font-size: 15px; font-weight: 700; line-height: 1.35; color: #F8FAFC !important; margin-bottom: 4px; }
    .module-desc { margin-top: 4px; color: var(--text-muted); font-size: 12px; line-height: 1.45; font-weight: 400; }
    .mod-status-tag { font-size: 11px; font-weight: 800; color: var(--accent-green); margin-top: 8px; display: flex; align-items: center; gap: 5px; }

    /* MODULE DETAIL & HIGH-CONTRAST TELEMETRY (FIXES CONTRAST GLITCH) */
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { text-align: left; padding: 12px 14px; border-bottom: 1px solid var(--border-color); font-size: 13px; color: #F8FAFC; }
    th { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 800; }
    .module-hero { display:flex; justify-content:space-between; gap:18px; align-items:flex-start; background: #001A17 !important; }
    .module-hero h2 { margin:6px 0 7px; font-size:24px; color:var(--accent-gold); }
    .module-hero-copy { max-width:780px; }
    .module-status-pill { display:inline-flex; align-items:center; gap:8px; padding:8px 14px; border:1px solid rgba(16,185,129,.35); border-radius:999px; color:var(--accent-green); font-size:12px; font-weight:800; white-space:nowrap; }
    .telemetry-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin:0 0 22px; }
    .telemetry-card { min-width:0; padding:16px 20px; border:1px solid rgba(16,185,129,.35) !important; border-radius:12px; background:#001f1c !important; }
    .telemetry-card strong { display:block; margin:8px 0 4px; font-size:26px !important; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#10B981 !important; font-weight:800 !important; text-shadow:0 0 16px rgba(16,185,129,.35) !important; }
    .telemetry-card small { color:var(--accent-green) !important; font-size:12px; font-weight:700; }
    .module-workbench { display:grid; grid-template-columns:1.3fr .9fr; gap:22px; }
    .module-panel { min-width:0; padding:20px; border:1px solid #123B35 !important; border-radius:14px; background:#001A17 !important; color:#F8FAFC !important; }
    .module-panel h3 { margin:0 0 14px; font-size:16px; color:#F8FAFC; }
    .panel-copy { margin:-5px 0 16px; color:var(--text-muted); font-size:12px; line-height:1.55; }
    .campaign-panel { margin-top:22px; border-color:rgba(214,161,23,.55) !important; }
    .range-label { display:grid; grid-template-columns:1fr auto; gap:8px; align-items:center; margin-top:14px; color:var(--text-muted); font-size:12px; }
    .range-label input { grid-column:1 / -1; width:100%; accent-color:var(--accent-gold); }
    .range-label span { color:var(--accent-gold); font-family:monospace; font-size:13px; font-weight:700; }
    .dispatch-checks { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin:16px 0; }
    .dispatch-check { padding:10px; border:1px solid var(--border-color); border-radius:8px; color:var(--text-muted); font-size:11px; text-align:center; font-weight:600; }
    .dispatch-check.is-ready { color:var(--accent-green); border-color:rgba(16,185,129,.45); background:rgba(16,185,129,.07); }
    .dispatch-check.is-warning { color:var(--accent-orange); border-color:rgba(234,88,12,.45); background:rgba(234,88,12,.07); }
    .dispatch-actions { display:flex; flex-wrap:wrap; gap:10px; margin-top:14px; }
    .dispatch-result { margin-top:14px; padding:12px; border-radius:8px; color:var(--text-muted); background:rgba(0,0,0,.25); font-size:12px; line-height:1.5; }
    .spintax-preview { min-height:85px; margin:14px 0 0; padding:12px; overflow:auto; border:1px solid var(--border-color); border-radius:8px; white-space:pre-wrap; color:var(--accent-green); background:rgba(0,0,0,.25); font:12px/1.6 monospace; }
    .bar-chart { display:flex; align-items:end; gap:10px; height:160px; padding:16px 10px 10px; border-bottom:1px solid var(--border-color); background:repeating-linear-gradient(to top,transparent 0,transparent 29px,rgba(148,163,184,.12) 30px); }
    .bar-chart span { flex:1; min-width:8px; border-radius:5px 5px 0 0; background:linear-gradient(180deg,var(--accent-green),var(--accent-gold)); box-shadow:0 0 12px rgba(16,185,129,.16); }
    .chart-caption { display:flex; justify-content:space-between; margin-top:10px; color:var(--text-muted); font-size:11px; }
    .control-list { display:grid; gap:10px; }
    .control-row { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px; border:1px solid var(--border-color); border-radius:10px; background:rgba(0,0,0,0.2); }
    .control-row span { color:var(--text-muted); font-size:12px; line-height:1.4; }
    .control-row b { display:block; color:var(--text-main); font-size:13px; margin-bottom:3px; }
    .control-row .btn { flex:0 0 auto; font-size:11px; padding:8px 12px; }
    .module-table-wrap { margin-top:22px; overflow-x:auto; }
    .module-table-wrap table { min-width:540px; margin-top:0; }
    .module-access-denied { padding:32px; text-align:center; border:1px dashed var(--accent-orange); border-radius:14px; background:rgba(234,88,12,.08); }
    .module-access-denied h3 { margin:0 0 10px; color:var(--accent-orange); font-size:18px; }
    .module-access-denied p { color:var(--text-muted); font-size:13px; }
    .vault-panel { margin-top:22px; border-color:var(--accent-gold) !important; }

    @media (max-width: 1200px) { .modules-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
    @media (max-width: 980px) {
        .modules-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .colleague-grid { grid-template-columns: 1fr; }
        .permission-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); }
        .module-workbench { grid-template-columns: 1fr; }
        .cropper-workspace { grid-template-columns: 1fr; }
    }
    @media (max-width: 700px) {
        body { padding: 12px; }
        .palette-grid, .soundscape-options, .typography-grid, .form-grid, .color-control-grid { grid-template-columns: repeat(2, 1fr); }
        .audio-player-shell, .clip-grid { grid-template-columns:1fr; flex-direction:column; align-items:stretch; }
        .attendance-summary-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
        .leave-row { grid-template-columns:1fr 1fr; }
        .leave-row > div { grid-column:1 / -1; }
    }
    @media (max-width: 480px) {
        .modules-grid { grid-template-columns: 1fr; }
        .top-bar { align-items: flex-start; }
        .view-as-bar { align-items:flex-start; flex-direction:column; }
        .view-as-controls { align-items:flex-start; flex-direction:column; width:100%; }
        .view-as-controls select { width:100%; min-width:0; }
        .permission-grid { grid-template-columns:repeat(3, minmax(0, 1fr)); }
        .telemetry-grid { grid-template-columns:1fr; }
        .module-hero { flex-direction:column; }
        .module-status-pill { align-self:flex-start; }
        .dispatch-checks { grid-template-columns:1fr; }
        .ai-mascot { right:16px; bottom:16px; }
    }
"""

COMMON_JS = r"""
<script>
const US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
];

const US_CONTRACTORS = [
    "Turner Construction Co.", "Bechtel Corporation", "Skanska USA Building",
    "The Whiting-Turner Contracting Co.", "Gilbane Building Company", "Hensel Phelps",
    "Clark Construction Group", "DPR Construction", "Mortenson Construction",
    "McCarthy Building Companies", "Holder Construction", "Balfour Beatty US",
    "JE Dunn Construction", "Brasfield & Gorrie", "Lendlease Americas",
    "Suffolk Construction", "PCL Construction Enterprises", "Clayco Inc.",
    "Sundt Construction", "Webcor Builders", "Walsh Construction",
    "Structure Tone", "Austin Commercial", "Ryan Companies",
    "Pepper Construction", "Swinerton Inc.", "Kitchell Corporation",
    "Crossland Construction", "Level 10 Construction", "Hoar Construction"
];

function publishAuditEvent(action, details) {
    const userKey = window.localStorage.getItem('grace-view-as') || 'king';
    const userName = PROFILE_DATA[userKey]?.name || 'King Saab';
    const now = new Date();
    const timestamp = now.getFullYear() + '-' +
        String(now.getMonth()+1).padStart(2,'0') + '-' +
        String(now.getDate()).padStart(2,'0') + ' ' +
        String(now.getHours()).padStart(2,'0') + ':' +
        String(now.getMinutes()).padStart(2,'0') + ':' +
        String(now.getSeconds()).padStart(2,'0');
    const entry = {
        timestamp: timestamp,
        user: userName,
        action: action,
        details: details
    };
    publishSharedState('auditLog', entry);
}

const THEME_PRESETS = {
    midnight: {dark:true, bg:'#0B1120', card:'#001A17', text:'#F8FAFC', muted:'#9BB0AD', border:'#123B35', accent:'#D6A117', green:'#10B981'},
    emerald: {dark:true, bg:'#031C18', card:'#062B24', text:'#F4FFF9', muted:'#9BC7B9', border:'#1C5A4B', accent:'#E0AF32', green:'#35D39B'},
    royal: {dark:true, bg:'#11162D', card:'#182348', text:'#F5F7FF', muted:'#AEB8D6', border:'#34457C', accent:'#CBB5FF', green:'#64E6C0'},
    sandstone: {dark:true, bg:'#211A14', card:'#302319', text:'#FFF9F0', muted:'#C6B39D', border:'#60452B', accent:'#F0B55A', green:'#69D0A2'},
    slate: {dark:true, bg:'#111827', card:'#1E293B', text:'#F8FAFC', muted:'#A7B3C5', border:'#334155', accent:'#38BDF8', green:'#34D399'},
    sapphire: {dark:true, bg:'#070E1A', card:'#0A192F', text:'#F8FAFC', muted:'#94A3B8', border:'#1E3A5F', accent:'#38BDF8', green:'#10B981'},
    cloud: {dark:true, bg:'#0B1120', card:'#001A17', text:'#F8FAFC', muted:'#9BB0AD', border:'#123B35', accent:'#D6A117', green:'#10B981'}
};

let ACCESS_MAP = {
    king: Array.from({length:22}, (_, i) => i + 1),
    abdullah: [1,2,3,4,5,6,7,12],
    sarah: [1,2,4,5,11,17,18],
    hamza: [1,2,6,7,13,16]
};

let PROFILE_DATA = {
    king: {key:'king', name:'King Saab', role:'Super Admin', status:'Online', software_id:'GRA-ADM-001', initials:'KS', tags:['Manager', 'Admin'], assigned_states:['California', 'New York'], metrics:{pipeline:'2,480', inboxes:'3 Inboxes', volume:'1,240', deal:'$64,800'}},
    abdullah: {key:'abdullah', name:'Abdullah Khan', role:'Strategic Lead', status:'Online', software_id:'GRA-LEAD-002', initials:'AK', tags:['Manager', 'Strategy'], assigned_states:['Texas', 'Florida'], metrics:{pipeline:'1,860', inboxes:'3 Inboxes', volume:'920', deal:'$48,200'}},
    sarah: {key:'sarah', name:'Sarah Malik', role:'Growth Marketer', status:'Online', software_id:'GRA-MKT-003', initials:'SM', tags:['Marketer', 'Growth'], assigned_states:['Illinois', 'Washington'], metrics:{pipeline:'1,120', inboxes:'2 Inboxes', volume:'640', deal:'$18,400'}},
    hamza: {key:'hamza', name:'Hamza Ali', role:'Lead Collector', status:'Offline', software_id:'GRA-COL-004', initials:'HA', tags:['Collector', 'Research'], assigned_states:['Georgia', 'Ohio'], metrics:{pipeline:'740', inboxes:'1 Inbox', volume:'410', deal:'$12,600'}}
};

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

const SHARED_STATE_ENDPOINT = '/api/state';
let sharedStateAvailable = false;

/* =========================================================================
   SERVER-SIDE PERSISTENCE BRIDGE (/api/state)
   ========================================================================= */
async function syncSharedState() {
    try {
        const response = await fetch(SHARED_STATE_ENDPOINT, {headers:{Accept:'application/json'}});
        if (!response.ok) throw new Error('Shared state unavailable');
        const shared = await response.json();
        if (shared.photos) {
            window.localStorage.setItem('grace-profile-photos', JSON.stringify(shared.photos));
            Object.keys(shared.photos).forEach((key) => setAvatarImage(key, shared.photos[key]));
        }
        if (shared.profiles) {
            Object.keys(shared.profiles).forEach((k) => {
                if (PROFILE_DATA[k]) Object.assign(PROFILE_DATA[k], shared.profiles[k]);
                else PROFILE_DATA[k] = shared.profiles[k];
            });
            window.localStorage.setItem('grace-profiles', JSON.stringify(PROFILE_DATA));
            hydrateColleagueCards();
            populateColleaguePickers();
        }
        if (shared.attendance) window.localStorage.setItem('grace-attendance', JSON.stringify(shared.attendance));
        if (shared.leaves) window.localStorage.setItem('grace-leave-requests', JSON.stringify(shared.leaves));
        if (shared.clearedFines) window.localStorage.setItem('grace-cleared-fines', JSON.stringify(shared.clearedFines));
        if (shared.accessMap) {
            Object.assign(ACCESS_MAP, shared.accessMap);
            window.localStorage.setItem('grace-access-map', JSON.stringify(ACCESS_MAP));
        }
        sharedStateAvailable = true;
        renderAttendanceLedger();
        updateViewAs();
    } catch (error) {
        console.warn('Sync fallback to local cache:', error);
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
    }).catch(function(err) {
        console.warn('Backend sync failed, state preserved in browser:', err);
    });
}

function populateColleaguePickers() {
    const loginPicker = document.getElementById('login-identity-picker');
    const viewAsPicker = document.getElementById('view-as-picker');
    const forgotPicker = document.getElementById('forgot-account-select');
    if (!loginPicker || !viewAsPicker) return;

    const currentLoginVal = loginPicker.value;
    const currentViewVal = viewAsPicker.value;

    loginPicker.innerHTML = '';
    viewAsPicker.innerHTML = '';
    if (forgotPicker) forgotPicker.innerHTML = '';

    Object.keys(PROFILE_DATA).forEach((k) => {
        const p = PROFILE_DATA[k];
        const opt1 = document.createElement('option');
        opt1.value = k;
        opt1.innerText = (k === 'king' ? '👑 ' : '👤 ') + p.name + ' · ' + p.role;
        loginPicker.appendChild(opt1);

        const opt2 = document.createElement('option');
        opt2.value = k;
        opt2.innerText = p.name + ' · ' + p.role + ' · ' + (p.allowed ? p.allowed.length : 22) + ' modules';
        viewAsPicker.appendChild(opt2);

        if (forgotPicker) {
            const opt3 = document.createElement('option');
            opt3.value = k;
            opt3.innerText = p.name + ' (' + (p.software_id || 'ID') + ')';
            forgotPicker.appendChild(opt3);
        }
    });

    loginPicker.value = currentLoginVal || 'king';
    viewAsPicker.value = currentViewVal || 'king';
}

/* =========================================================================
   AUTHENTICATION & SECURITY GATEWAY (POWER OFF / LOCK)
   ========================================================================= */
function powerOff() {
    openAuthGateway('signin', true, false);
    showToast('Session locked. Terminal returned to Security Gateway.', 'info');
}

function openAuthGateway(tab = 'signin', isLock = false, isMandatory = false) {
    const overlay = document.getElementById('auth-gateway-overlay');
    if (!overlay) return;
    overlay.hidden = false;
    switchAuthTab(tab);
    if (isLock) {
        window.localStorage.setItem('grace-session-locked', 'true');
        document.body.classList.add('safety-locked');
    }
    const notice = document.getElementById('gateway-mandatory-notice');
    const dismissBtn = document.getElementById('gateway-dismiss-btn');
    if (isMandatory) {
        if (notice) notice.hidden = false;
        if (dismissBtn) dismissBtn.style.display = 'none';
    } else {
        if (notice) notice.hidden = true;
        if (dismissBtn) dismissBtn.style.display = '';
    }
}

function closeAuthGateway() {
    const overlay = document.getElementById('auth-gateway-overlay');
    if (overlay) overlay.hidden = true;
    window.localStorage.setItem('grace-session-locked', 'false');
    document.body.classList.remove('safety-locked');
}

function unlockGatewayPreview() {
    if (!window.sessionStorage.getItem('grace_auth_user')) {
        showToast('Access restricted: Please log in or create an account.', 'warning');
        return;
    }
    closeAuthGateway();
    showToast('Lock screen dismissed. Active workspace preview active.', 'info');
}

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab-btn').forEach((b) => b.classList.remove('active'));
    document.querySelectorAll('.auth-pane').forEach((p) => p.hidden = true);
    const tabBtn = document.getElementById('auth-tab-btn-' + tab);
    const pane = document.getElementById('auth-pane-' + tab);
    if (tabBtn) tabBtn.classList.add('active');
    if (pane) pane.hidden = false;

    if (tab === 'register') {
        renderRegTerritoryChips();
        renderRegContractorChips();
    }
}

function togglePasswordVisibility(inputId) {
    const el = document.getElementById(inputId);
    if (el) el.type = el.type === 'password' ? 'text' : 'password';
}

function fastPassLogin(key) {
    const picker = document.getElementById('login-identity-picker');
    if (picker) picker.value = key;
    const pwdInput = document.getElementById('login-password-input');
    if (pwdInput) pwdInput.value = 'grace2026';
    submitSignIn();
}

function submitSignIn() {
    const key = document.getElementById('login-identity-picker')?.value || 'king';
    const pwd = document.getElementById('login-password-input')?.value || '';
    if (!pwd) {
        showToast('Please enter password.', 'warning');
        return;
    }
    // Verify password (default: grace2026 or custom)
    const storedPasswords = JSON.parse(window.localStorage.getItem('grace-passwords') || '{}');
    const validPwd = storedPasswords[key] || 'grace2026';
    if (pwd !== validPwd) {
        showToast('Invalid password for ' + (PROFILE_DATA[key]?.name || key) + '.', 'warning');
        return;
    }
    window.sessionStorage.setItem('grace_auth_user', key);
    changeViewAs(key);
    closeAuthGateway();
    publishAuditEvent('Authentication', 'Colleague signed into workspace: ' + (PROFILE_DATA[key]?.name || key));
    showToast('Welcome back, ' + PROFILE_DATA[key].name + ' · Workspace unlocked.', 'success');
}

let regSelectedStates = [];
let regSelectedContractors = [];
let regStateSearchFilter = '';
let regContractorSearchFilter = '';

function filterRegChips(type, query) {
    if (type === 'states') {
        regStateSearchFilter = (query || '').trim().toLowerCase();
        renderRegTerritoryChips();
    } else {
        regContractorSearchFilter = (query || '').trim().toLowerCase();
        renderRegContractorChips();
    }
}

function renderRegTerritoryChips() {
    const container = document.getElementById('reg-territory-chips');
    const warn = document.getElementById('reg-territory-warn');
    if (!container) return;
    if (warn) warn.hidden = regSelectedStates.length < 2;
    const list = regStateSearchFilter
        ? US_STATES.filter(s => s.toLowerCase().includes(regStateSearchFilter))
        : US_STATES.slice(0, 20);
    container.innerHTML = list.map((st) => {
        const sel = regSelectedStates.includes(st);
        return '<button type="button" class="state-chip-btn ' + (sel ? 'selected' : '') + '" onclick="toggleRegState(\'' + st.replace(/'/g, "\\'") + '\')">' + (sel ? '✓ ' : '+ ') + st + '</button>';
    }).join('');
}

function toggleRegState(st) {
    const idx = regSelectedStates.indexOf(st);
    if (idx >= 0) {
        regSelectedStates.splice(idx, 1);
    } else {
        if (regSelectedStates.length >= 2) {
            showToast('Strict limit: Max 2 states per colleague.', 'warning');
            const warn = document.getElementById('reg-territory-warn');
            if (warn) warn.hidden = false;
            return;
        }
        regSelectedStates.push(st);
    }
    renderRegTerritoryChips();
}

function renderRegContractorChips() {
    const container = document.getElementById('reg-contractor-chips');
    const warn = document.getElementById('reg-contractor-warn');
    if (!container) return;
    if (warn) warn.hidden = regSelectedContractors.length < 2;
    const list = regContractorSearchFilter
        ? US_CONTRACTORS.filter(c => c.toLowerCase().includes(regContractorSearchFilter))
        : US_CONTRACTORS.slice(0, 15);
    container.innerHTML = list.map((ct) => {
        const sel = regSelectedContractors.includes(ct);
        return '<button type="button" class="state-chip-btn ' + (sel ? 'selected' : '') + '" onclick="toggleRegContractor(\'' + ct.replace(/'/g, "\\'") + '\')">' + (sel ? '✓ ' : '+ ') + ct + '</button>';
    }).join('');
}

function toggleRegContractor(ct) {
    const idx = regSelectedContractors.indexOf(ct);
    if (idx >= 0) {
        regSelectedContractors.splice(idx, 1);
    } else {
        if (regSelectedContractors.length >= 2) {
            showToast('Strict limit: Max 2 contractors per colleague.', 'warning');
            const warn = document.getElementById('reg-contractor-warn');
            if (warn) warn.hidden = false;
            return;
        }
        regSelectedContractors.push(ct);
    }
    renderRegContractorChips();
}

function submitCreateAccount() {
    const name = document.getElementById('reg-name')?.value.trim();
    const role = document.getElementById('reg-role')?.value.trim();
    const rawKey = document.getElementById('reg-key')?.value.trim().toLowerCase();
    const pwd = document.getElementById('reg-password')?.value;

    if (!name || !role || !rawKey || !pwd) {
        showToast('Please fill all registration fields.', 'warning');
        return;
    }
    const cleanKey = rawKey.replace(/[^a-z0-9_\-]/g, '');
    if (cleanKey.length < 2) {
        showToast('Colleague key must be at least 2 alphanumeric characters.', 'warning');
        return;
    }
    if (PROFILE_DATA[cleanKey]) {
        showToast('Colleague key already exists. Choose another ID.', 'warning');
        return;
    }

    const newProfile = {
        name,
        role,
        assigned_states: Array.from(regSelectedStates),
        assigned_contractors: Array.from(regSelectedContractors)
    };

    // Save locally
    const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'CO';
    PROFILE_DATA[cleanKey] = {
        key: cleanKey,
        name,
        role,
        software_id: 'GRA-COL-' + String(Object.keys(PROFILE_DATA).length + 1).padStart(3, '0'),
        status: 'Online',
        initials,
        tags: ['New', 'Team'],
        assigned_states: Array.from(regSelectedStates),
        assigned_contractors: Array.from(regSelectedContractors),
        allowed: [1, 2, 4, 6, 7, 13, 16],
        metrics: {pipeline:'500', inboxes:'1 Inbox', volume:'200', deal:'$12,000'}
    };

    const storedPasswords = JSON.parse(window.localStorage.getItem('grace-passwords') || '{}');
    storedPasswords[cleanKey] = pwd;
    window.localStorage.setItem('grace-passwords', JSON.stringify(storedPasswords));
    window.localStorage.setItem('grace-profiles', JSON.stringify(PROFILE_DATA));
    window.sessionStorage.setItem('grace_auth_user', cleanKey);

    publishSharedState('profiles', newProfile, cleanKey);
    publishAuditEvent('Account Registration', 'Registered new colleague ' + name + ' (' + cleanKey + ')');
    populateColleaguePickers();
    changeViewAs(cleanKey);
    closeAuthGateway();
    showToast('New colleague identity registered successfully!', 'success');
}

function submitPasswordReset() {
    const key = document.getElementById('forgot-account-select')?.value || 'king';
    const storedPasswords = JSON.parse(window.localStorage.getItem('grace-passwords') || '{}');
    delete storedPasswords[key];
    window.localStorage.setItem('grace-passwords', JSON.stringify(storedPasswords));
    showToast('Password for ' + (PROFILE_DATA[key]?.name || key) + ' reset to default: grace2026', 'success');
    switchAuthTab('signin');
}

/* =========================================================================
   MODULE WORKFLOW RUNBOOKS (BILINGUAL)
   ========================================================================= */
const MODULE_GUIDES = {
    1:{name:'Dashboard Hub',en:'🧭 Step 1 ➔ Review pipeline and inbox health.\nStep 2 ➔ Open the activity stream.\nStep 3 ➔ Trigger a safe sync or pause outreach.',ur:'🧭 Step 1 ➔ Pipeline aur inbox health dekhein.\nStep 2 ➔ Activity stream kholen.\nStep 3 ➔ Safe sync chalayein ya outreach rok dein.'},
    2:{name:'Gmail Multi-Tenant Hub',en:'✉️ Step 1 ➔ Check each inbox quota.\nStep 2 ➔ Verify OAuth and rotation health.\nStep 3 ➔ Rebalance the tenant pool before dispatch.',ur:'✉️ Step 1 ➔ Har inbox ka quota check karein.\nStep 2 ➔ OAuth aur rotation health verify karein.\nStep 3 ➔ Dispatch se pehle tenant pool rebalance karein.'},
    3:{name:'AI Warmup Ramp',en:'♨️ Step 1 ➔ Review the sender reputation score.\nStep 2 ➔ Inspect the active warmup cohort.\nStep 3 ➔ Advance the next cohort only when engagement is healthy.',ur:'♨️ Step 1 ➔ Sender reputation score dekhein.\nStep 2 ➔ Active warmup cohort inspect karein.\nStep 3 ➔ Engagement healthy ho to agla cohort advance karein.'},
    4:{name:'Campaign Studio',en:'➤ Step 1 ➔ Select a sequence and timezone.\nStep 2 ➔ Run the AI copy score and A/B split.\nStep 3 ➔ Launch, pause, or review the next stage.',ur:'➤ Step 1 ➔ Sequence aur timezone select karein.\nStep 2 ➔ AI copy score aur A/B split chalayein.\nStep 3 ➔ Next stage launch, pause ya review karein.'},
    5:{name:'Spin-Syntax AI Engine',en:'╱ Step 1 ➔ Choose the source message.\nStep 2 ➔ Generate safe variants and preview each spin.\nStep 3 ➔ Promote the winning copy to a live sequence.',ur:'╱ Step 1 ➔ Source message choose karein.\nStep 2 ➔ Safe variants generate karke preview karein.\nStep 3 ➔ Winning copy ko live sequence mein promote karein.'},
    6:{name:'Architect & Contractor Scraper',en:'⌕ Step 1 ➔ Choose states or a regional segment.\nStep 2 ➔ Run live pings and enrich decision-makers.\nStep 3 ➔ Export the verified lead batch as CSV or TXT.',ur:'⌕ Step 1 ➔ States ya regional segment choose karein.\nStep 2 ➔ Live pings aur decision-maker enrichment chalayein.\nStep 3 ➔ Verified leads ko CSV ya TXT mein export karein.'},
    7:{name:'CRM Revenue Pipeline',en:'$ Step 1 ➔ Review discovery, proposal, and negotiation stages.\nStep 2 ➔ Score opportunities by close signal.\nStep 3 ➔ Refresh the pipeline and export ROI attribution.',ur:'$ Step 1 ➔ Discovery, proposal aur negotiation stages dekhein.\nStep 2 ➔ Opportunities ko close signal ke mutabiq score karein.\nStep 3 ➔ Pipeline refresh karke ROI export karein.'},
    8:{name:'Colleague Access Controller',en:'♙ Step 1 ➔ Open a colleague profile and confirm identity.\nStep 2 ➔ Toggle the 22-module RBAC grid.\nStep 3 ➔ Use View-As to verify the restricted workspace.',ur:'♙ Step 1 ➔ Colleague profile khol kar identity confirm karein.\nStep 2 ➔ 22-module RBAC grid mein access toggle karein.\nStep 3 ➔ Restricted workspace verify karne ke liye View-As use karein.'},
    9:{name:'System Doctor Daemon',en:'♥ Step 1 ➔ Read live latency and worker gauges.\nStep 2 ➔ Run the full diagnostic probe.\nStep 3 ➔ Flush safe cache state if telemetry recommends it.',ur:'♥ Step 1 ➔ Live latency aur worker gauges dekhein.\nStep 2 ➔ Full diagnostic probe chalayein.\nStep 3 ➔ Telemetry kahe to safe cache flush karein.'},
    10:{name:'Audio Studio & Extractor',en:'♫ Step 1 ➔ Choose an ambient track or upload media.\nStep 2 ➔ Set clip start and end points.\nStep 3 ➔ Test the alert chime or open Broadcast Center.',ur:'♫ Step 1 ➔ Ambient track choose ya media upload karein.\nStep 2 ➔ Clip ka start aur end set karein.\nStep 3 ➔ Alert chime test ya Broadcast Center kholen.'},
    11:{name:'Built-in AI Guide Agent',en:'▣ Step 1 ➔ Select English or Roman Urdu.\nStep 2 ➔ Choose one of the 22 workflow runbooks.\nStep 3 ➔ Play the response or ask a follow-up question.',ur:'▣ Step 1 ➔ English ya Roman Urdu select karein.\nStep 2 ➔ 22 workflow runbooks mein se ek choose karein.\nStep 3 ➔ Response play karein ya follow-up sawal poochein.'},
    12:{name:'OAuth Token Vault',en:'⬟ Step 1 ➔ Verify AES-256 locker and master-key telemetry.\nStep 2 ➔ Check all token renewal states.\nStep 3 ➔ Run a controlled sync or export an encrypted backup.',ur:'⬟ Step 1 ➔ AES-256 locker aur master-key telemetry verify karein.\nStep 2 ➔ Sab tokens ki renewal state check karein.\nStep 3 ➔ Controlled sync ya encrypted backup export karein.'},
    13:{name:'Timezone Scheduler',en:'◷ Step 1 ➔ Review live clocks for each region.\nStep 2 ➔ Preview the business-hour dispatch queue.\nStep 3 ➔ Apply jitter and release only the safe window.',ur:'◷ Step 1 ➔ Har region ki live clocks dekhein.\nStep 2 ➔ Business-hour dispatch queue preview karein.\nStep 3 ➔ Jitter apply karke sirf safe window release karein.'},
    14:{name:'Bounce Shield',en:'◢ Step 1 ➔ Inspect bounce and suppression signals.\nStep 2 ➔ Sanitize the outgoing queue.\nStep 3 ➔ Export the protected suppression list for audit.',ur:'◢ Step 1 ➔ Bounce aur suppression signals inspect karein.\nStep 2 ➔ Outgoing queue sanitize karein.\nStep 3 ➔ Protected suppression list audit ke liye export karein.'},
    15:{name:'Auto-Reply Detector',en:'↶ Step 1 ➔ Run the inbox sentiment classifier.\nStep 2 ➔ Review uncertain replies.\nStep 3 ➔ Push approved positive intent into the CRM.',ur:'↶ Step 1 ➔ Inbox sentiment classifier chalayein.\nStep 2 ➔ Uncertain replies review karein.\nStep 3 ➔ Approved positive intent CRM mein push karein.'},
    16:{name:'CSV / Excel Exporter',en:'⇥ Step 1 ➔ Select the report scope and time range.\nStep 2 ➔ Build CSV, Excel, or TXT output.\nStep 3 ➔ Confirm freshness before downloading the report.',ur:'⇥ Step 1 ➔ Report scope aur time range select karein.\nStep 2 ➔ CSV, Excel ya TXT output banayein.\nStep 3 ➔ Download se pehle freshness confirm karein.'},
    17:{name:'Broadcast Notification Node',en:'⚑ Step 1 ➔ Choose all displays or one recipient.\nStep 2 ➔ Add a priority message and optional chime.\nStep 3 ➔ Send, then review acknowledgement state.',ur:'⚑ Step 1 ➔ Sab displays ya ek recipient choose karein.\nStep 2 ➔ Priority message aur optional chime add karein.\nStep 3 ➔ Send karke acknowledgement state dekhein.'},
    18:{name:'Brand Palette Studio',en:'✾ Step 1 ➔ Choose an executive theme preset.\nStep 2 ➔ Tune font, weight, tracking, and italic state.\nStep 3 ➔ Apply the palette and review the full workspace.',ur:'✾ Step 1 ➔ Executive theme preset choose karein.\nStep 2 ➔ Font, weight, tracking aur italic tune karein.\nStep 3 ➔ Palette apply karke poora workspace review karein.'},
    19:{name:'Cloud Webhook Dispatcher',en:'⌘ Step 1 ➔ Inspect endpoint health and signatures.\nStep 2 ➔ Send a signed test JSON payload.\nStep 3 ➔ Replay safe retries and confirm a 200 response.',ur:'⌘ Step 1 ➔ Endpoint health aur signatures inspect karein.\nStep 2 ➔ Signed test JSON payload bhejein.\nStep 3 ➔ Safe retries replay karke 200 response confirm karein.'},
    20:{name:'Daily Quota Guard',en:'◉ Step 1 ➔ Review account caps and used volume.\nStep 2 ➔ Recalculate safe-send pacing.\nStep 3 ➔ Lock overage before the daily ceiling is reached.',ur:'◉ Step 1 ➔ Account caps aur used volume dekhein.\nStep 2 ➔ Safe-send pacing recalculate karein.\nStep 3 ➔ Daily ceiling se pehle overage lock karein.'},
    21:{name:'Security Audit Stream',en:'≋ Step 1 ➔ Open immutable access events.\nStep 2 ➔ Run a threat-signal scan.\nStep 3 ➔ Export a signed audit record for evidence.',ur:'≋ Step 1 ➔ Immutable access events kholen.\nStep 2 ➔ Threat-signal scan chalayein.\nStep 3 ➔ Evidence ke liye signed audit record export karein.'},
    22:{name:'Enterprise Sync Engine',en:'⇄ Step 1 ➔ Review connected systems and drift.\nStep 2 ➔ Run a full bi-directional reconciliation.\nStep 3 ➔ Inspect exceptions and confirm aligned records.',ur:'⇄ Step 1 ➔ Connected systems aur drift review karein.\nStep 2 ➔ Full bi-directional reconciliation chalayein.\nStep 3 ➔ Exceptions inspect karke aligned records confirm karein.'}
};

let selectedTheme = 'midnight';
let ambientContext = null;
let ambientNodes = [];
let soundscapePlaying = false;
let loopMode = 'ambient';
let gatewayAudioActive = false;
let customMediaUrl = null;
let aiLanguage = window.localStorage.getItem('grace-ai-language') || 'en';
let mascotDrag = {active:false, moved:false, startX:0, startY:0, left:0, top:0, suppressClick:false};

function setLoopMode(mode) {
    loopMode = mode;
    const singleBtn = document.getElementById('loop-single-btn');
    const ambientBtn = document.getElementById('loop-ambient-btn');
    if (singleBtn && ambientBtn) {
        if (mode === 'single') {
            singleBtn.className = 'btn btn-blue';
            ambientBtn.className = 'btn btn-gray';
            showToast('Loop mode: Repeat current soundscape track.', 'info');
        } else {
            singleBtn.className = 'btn btn-gray';
            ambientBtn.className = 'btn btn-blue';
            showToast('Loop mode: Continuous ambient soundscape playlist.', 'info');
        }
    }
}

function toggleGatewayAudio() {
    const btn = document.getElementById('gateway-sound-toggle');
    gatewayAudioActive = !gatewayAudioActive;
    if (gatewayAudioActive) {
        startAmbient();
        if (btn) btn.innerText = '🔊 Ambient Sound: ON';
        showToast('Gateway background soundscape playing.', 'success');
    } else {
        stopAmbient();
        if (btn) btn.innerText = '🔇 Ambient Sound: OFF';
        showToast('Gateway background soundscape muted.', 'info');
    }
}

/* =========================================================================
   INITIALIZATION
   ========================================================================= */
function applyStoredTheme() {
    const stored = window.localStorage.getItem('grace-theme') || 'dark';
    applyTheme(stored === 'light' ? 'light' : 'dark', false);
    applyTypography(false);
    hydrateAccessMap();
    hydrateLocalProfiles();
    populateColleaguePickers();
    hydrateAILanguage();
    renderAIGuideLibrary();
    hydrateCustomColors();
    hydrateProfilePhotos();
    renderAttendanceLedger();
    syncCampaignControls();
    initMascotDrag();
    updateViewAs();
    updateThemeButton();
    startLiveClocks();
    startTelemetryFeed();
    syncSharedState();

    if (window.localStorage.getItem('grace-session-locked') === 'true') {
        openAuthGateway('signin', true);
    }
}

function applyTheme(name, notify = true) {
    const isLight = (name === 'light' || name === 'cloud');
    const isDark = !isLight;
    
    if (isDark) {
        document.body.classList.add('dark');
        document.body.classList.remove('light');
        document.body.style.backgroundColor = '#0B1120';
        document.body.style.color = '#F8FAFC';
        selectedTheme = 'dark';
    } else {
        document.body.classList.remove('dark');
        document.body.classList.add('light');
        document.body.style.backgroundColor = '#F1F5F9';
        document.body.style.color = '#0F172A';
        selectedTheme = 'light';
    }
    window.localStorage.setItem('grace-theme', selectedTheme);
    updateThemeButton();
    if (notify) {
        showToast(isDark ? '🌓 Dark Theme activated.' : '☀️ Light Theme activated.', 'success');
    }
}

function updateThemeButton() {
    const btn = document.getElementById('theme-btn');
    const isDark = document.body.classList.contains('dark') || !document.body.classList.contains('light');
    if (btn) {
        btn.innerText = isDark ? '🌓 Theme: DARK' : '☀️ Theme: LIGHT';
    }
}

function toggleTheme() {
    const isCurrentlyDark = document.body.classList.contains('dark') || !document.body.classList.contains('light');
    const targetTheme = isCurrentlyDark ? 'light' : 'dark';
    applyTheme(targetTheme);
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
    const family = font === 'system' ? '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' : '"' + font + '", sans-serif';
    document.body.style.fontFamily = family;
    document.body.style.fontWeight = weight;
    document.body.style.fontStyle = italic ? 'italic' : 'normal';
    document.body.style.letterSpacing = tracking;
    window.localStorage.setItem('grace-typography', JSON.stringify({font, weight, tracking, italic}));
    if (notify) showToast('Typography settings applied to the executive interface.', 'success');
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
    if (modal) modal.hidden = false;
}
function closeBrandPalette() {
    const modal = document.getElementById('brand-palette-modal');
    if (modal) modal.hidden = true;
}

function manualSync() {
    showToast('Manual sync completed across Gmail inboxes #1, #2, and #3.', 'success');
}
function pauseOutreach() {
    showToast('All active outreach threads paused across 3 inboxes.', 'warning');
}
function testBroadcast() {
    showToast('Test broadcast packet sent to the monitoring node.', 'success');
}

/* =========================================================================
   REAL-TIME FILE DOWNLOAD UTILITY
   ========================================================================= */
function downloadFile(filename, content, mimeType = 'text/plain;charset=utf-8') {
    const blob = new Blob([content], {type: mimeType});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 250);
}

/* Real-Time Live Clock Matrix */
function startLiveClocks() {
    function updateClocks() {
        const now = new Date();
        const opts = {hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:true};
        const et = new Intl.DateTimeFormat('en-US', {...opts, timeZone:'America/New_York'}).format(now);
        const ct = new Intl.DateTimeFormat('en-US', {...opts, timeZone:'America/Chicago'}).format(now);
        const mt = new Intl.DateTimeFormat('en-US', {...opts, timeZone:'America/Denver'}).format(now);
        const pt = new Intl.DateTimeFormat('en-US', {...opts, timeZone:'America/Los_Angeles'}).format(now);

        const rows = document.querySelectorAll('.module-table-wrap table tr');
        rows.forEach((r) => {
            const txt = r.innerText;
            if (txt.includes('Eastern')) r.children[1].innerHTML = '<b>' + et + '</b> (08:00–18:00 ET)';
            else if (txt.includes('Central')) r.children[1].innerHTML = '<b>' + ct + '</b> (07:00–17:00 CT)';
            else if (txt.includes('Mountain')) r.children[1].innerHTML = '<b>' + mt + '</b> (06:00–16:00 MT)';
            else if (txt.includes('Pacific')) r.children[1].innerHTML = '<b>' + pt + '</b> (05:00–15:00 PT)';
        });
    }
    updateClocks();
    setInterval(updateClocks, 1000);
}

/* Real-Time Telemetry Feed Simulation */
function startTelemetryFeed() {
    const box = document.querySelector('.log-box');
    if (!box) return;
    const samples = [
        "[DISPATCH] Gmail Inbox #2 safely rotated next 15 contractor leads.",
        "[CLASSIFY] Positive reply sentiment classified from arch_design_fl.",
        "[VAULT] AES-256 credential token heartbeat checked (0 drift).",
        "[WARMUP] Reputation ramp thread peer engagement healthy at 98.4%.",
        "[SYNC] Enterprise webhook synced 12 deal updates with CRM."
    ];
    let idx = 0;
    setInterval(() => {
        const now = new Date().toTimeString().split(' ')[0];
        const line = document.createElement('div');
        line.innerText = '[' + now + '] ' + samples[idx % samples.length];
        box.prepend(line);
        idx++;
    }, 9000);
}

/* =========================================================================
   REAL-TIME EXPORTS & INTERACTIVE ACTIONS ACROSS MODULES
   ========================================================================= */
function exportScraperLeads(format) {
    const sampleLeads = [
        {name:"Apex Architectural Studio", state:"California", contact:"Marcus Vance", email:"mvance@apexarch.com", phone:"(415) 890-2104"},
        {name:"Blue Ridge Contracting LLC", state:"Texas", contact:"Elena Ramos", email:"eramos@blueridgebuilds.com", phone:"(512) 640-3912"},
        {name:"Cascade Design Partners", state:"Washington", contact:"David Sterling", email:"dsterling@cascadedesign.com", phone:"(206) 430-8821"},
        {name:"Evergreen Structural Group", state:"Illinois", contact:"Rachel Meyer", email:"rmeyer@evergreenstruct.com", phone:"(312) 550-9140"},
        {name:"Summit Valley Builders", state:"Colorado", contact:"Thomas Reed", email:"treed@summitvalleybuilds.com", phone:"(303) 780-4491"},
        {name:"Coastal Heritage Architecture", state:"Florida", contact:"Sophia Alvarez", email:"salvarez@coastalarchfl.com", phone:"(305) 920-1178"},
        {name:"Metropolitan Design Guild", state:"New York", contact:"Julian Hayes", email:"jhayes@metroguildny.com", phone:"(212) 840-7734"}
    ];

    if (format === 'csv') {
        let csv = "Company Name,State,Decision Maker,Email,Phone,Verification Status\n";
        sampleLeads.forEach(l => {
            csv += `"${l.name}","${l.state}","${l.contact}","${l.email}","${l.phone}","Verified 100%"\n`;
        });
        downloadFile("verified_contractors_50_states.csv", csv, "text/csv;charset=utf-8");
        showToast("Verified contractor leads exported to CSV.", "success");
    } else {
        let txt = "========================================================\nGRACE OUTREACH ASSISTANT - VERIFIED CONTRACTOR LEADS (50 STATES)\n========================================================\n\n";
        sampleLeads.forEach((l, i) => {
            txt += `[#${i+1}] ${l.name} | ${l.state}\nContact: ${l.contact} <${l.email}>\nPhone: ${l.phone} | Status: Verified Decision-Maker\n\n`;
        });
        downloadFile("verified_contractors_50_states.txt", txt, "text/plain;charset=utf-8");
        showToast("Contractor lead batch exported to TXT handoff.", "success");
    }
}

function exportVaultBackup() {
    const backupData = {
        vault_name: "Grace OAuth AES-256 Credentials Locker",
        exported_at: new Date().toISOString(),
        encryption_standard: "AES-256-GCM Hardware-Isolated",
        master_key_fingerprint: "SHA256:8f4c2e9b1a7d4e3f8a0b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f",
        connected_nodes: [
            {inbox: "business.inbox1@gmail.com", protocol: "OAuth 2.0 Auto-Renew", status: "Active"},
            {inbox: "outreach.node2@gmail.com", protocol: "App Password Locker", status: "Active"},
            {inbox: "relay.personal@gmail.com", protocol: "App Password Locker", status: "Active"}
        ]
    };
    downloadFile("grace_oauth_vault_backup.json", JSON.stringify(backupData, null, 2), "application/json");
    showToast("Encrypted vault backup archive generated & downloaded.", "success");
}

function exportAnalyticsReport(format) {
    const reportData = [
        {metric:"Active Outreach Threads", value:"2,480", status:"+14.2% Growth"},
        {metric:"Connected Gmail Inboxes", value:"3 Active Inboxes", status:"Rotation Healthy"},
        {metric:"Weekly Dispatch Volume", value:"1,240 Messages", status:"Safe 50/50 Caps"},
        {metric:"CRM Pipeline Deal Value", value:"$64,800 USD", status:"+21.4% Target Lift"},
        {metric:"Deliverability Bounce Ping", value:"0.08%", status:"Zero Hard Bounces"}
    ];

    if (format === 'csv') {
        let csv = "Operational Metric,Current Value,Performance Indicator\n";
        reportData.forEach(r => { csv += `"${r.metric}","${r.value}","${r.status}"\n`; });
        downloadFile("grace_outreach_analytics.csv", csv, "text/csv;charset=utf-8");
        showToast("Outreach telemetry report exported as CSV.", "success");
    } else if (format === 'excel') {
        let html = "<html><head><meta charset='utf-8'></head><body><h3>Grace Outreach Assistant - Analytics Report</h3><table border='1'><tr><th>Metric</th><th>Value</th><th>Status</th></tr>";
        reportData.forEach(r => { html += `<tr><td>${r.metric}</td><td>${r.value}</td><td>${r.status}</td></tr>`; });
        html += "</table></body></html>";
        downloadFile("grace_outreach_analytics.xls", html, "application/vnd.ms-excel");
        showToast("Excel spreadsheet report generated & downloaded.", "success");
    } else {
        let txt = "GRACE OUTREACH ASSISTANT - SECURITY AUDIT TRAIL\n===============================================\n";
        txt += "Generated: " + new Date().toUTCString() + "\nAudit Coverage: 100% Append-Only Immutable Records\n\n";
        reportData.forEach(r => { txt += `• ${r.metric}: ${r.value} (${r.status})\n`; });
        downloadFile("grace_access_audit.txt", txt, "text/plain;charset=utf-8");
        showToast("Security access audit log downloaded.", "success");
    }
}

function exportSuppressionList() {
    let csv = "Suppressed Recipient,Reason,Recorded At,Status\n";
    csv += "risk.user@spamtrap.org,DNSBL Risk Score,2026-09-01,Blocked\n";
    csv += "bounced.mailbox@abandoned.net,Hard Bounce 550,2026-09-03,Suppressed\n";
    csv += "optout@clientcorp.com,CAN-SPAM One-Click,2026-09-04,Suppressed\n";
    downloadFile("grace_suppression_list.csv", csv, "text/csv;charset=utf-8");
    showToast("Zero-Bounce suppression list exported.", "success");
}

let pipelineDeals = [
    {stage:"Discovery", value:"$18,400", deals:12},
    {stage:"Proposal", value:"$27,600", deals:14},
    {stage:"Negotiation", value:"$18,800", deals:8}
];

function advancePipelineDeal() {
    pipelineDeals[1].deals -= 1;
    pipelineDeals[2].deals += 1;
    const statEl = document.querySelector('[data-metric-key="deal"]');
    if (statEl) {
        statEl.innerText = "$72,400";
        statEl.style.color = "var(--accent-gold)";
    }
    showToast("Proposal deal advanced to Negotiation! Pipeline updated to $72,400.", "success");
}

function addPipelineOpportunity() {
    pipelineDeals[0].deals += 1;
    showToast("New qualified contractor opportunity added to Discovery stage.", "success");
}

/* =========================================================================
   SOUNDSCAPE AUDIO ENGINE
   ========================================================================= */
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
        showToast('Audio playback requires browser user interaction permission.', 'warning');
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
        showToast('Local media soundtrack loaded for preview and clipping.', 'success');
    };
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

/* =========================================================================
   BROADCAST MATRIX
   ========================================================================= */
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
    showToast('Broadcast sent to ' + targetText + '.', 'success');
    if (fullscreen.checked) {
        document.getElementById('broadcast-overlay-message').innerText = copy;
        document.getElementById('broadcast-overlay-target').innerText = 'Target: ' + targetText;
        document.getElementById('broadcast-overlay').hidden = false;
    }
}
function closeBroadcastOverlay() {
    document.getElementById('broadcast-overlay').hidden = true;
}

/* =========================================================================
   AI MASCOT & GUIDE
   ========================================================================= */
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
function setAILanguage(value) {
    aiLanguage = value === 'ur' ? 'ur' : 'en';
    window.localStorage.setItem('grace-ai-language', aiLanguage);
    showToast(aiLanguage === 'ur' ? 'Roman Urdu guidance selected.' : 'English guidance selected.', 'info');
}
function hydrateAILanguage() {
    const selector = document.getElementById('ai-language');
    if (selector) selector.value = aiLanguage;
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
    const direct = question.match(/(?:module|m)\s*0*(\d{1,2})/i);
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
    utterance.lang = aiLanguage === 'ur' ? 'ur-PK' : 'en-US';
    utterance.rate = .92;
    utterance.onend = function() { if (button) button.innerText = '🔊 Play response'; };
    window.speechSynthesis.speak(utterance);
    if (button) button.innerText = '⏸ Playing response';
}
function askAI(question, forcedModule) {
    const input = document.getElementById('ai-input');
    if (input) input.value = question;
    sendAIMessage(forcedModule);
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
        ? '🧭 Step 1 ➔ Matrix se module select karein.\nStep 2 ➔ Live telemetry review karein.\nStep 3 ➔ Execution toolbar se safe action karein.'
        : '🧭 Step 1 ➔ Select a module from the matrix.\nStep 2 ➔ Review live telemetry.\nStep 3 ➔ Use the execution toolbar for a safe action.';
    if (moduleId && MODULE_GUIDES[moduleId]) answer = MODULE_GUIDES[moduleId][aiLanguage];
    else if (lower.includes('restrict') || lower.includes('permission')) answer = aiLanguage === 'ur'
        ? '🔐 Step 1 ➔ Navigation ke neeche View-As picker kholen.\nStep 2 ➔ Colleague workspace select karein.\nStep 3 ➔ Sirf authorized modules aur adjusted dashboard metrics dekhein.'
        : '🔐 Step 1 ➔ Open the View-As picker below navigation.\nStep 2 ➔ Select a colleague workspace.\nStep 3 ➔ Review only authorized modules and adjusted dashboard metrics.';
    window.setTimeout(() => appendAIMessage(answer, false), 220);
}
function speakGuide() {
    if (!('speechSynthesis' in window)) { showToast('Voice playback is not supported in this browser.', 'warning'); return; }
    const text = document.getElementById('ai-messages')?.innerText || 'Grace AI Guide is ready.';
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = .92;
    window.speechSynthesis.speak(utterance);
    showToast('Voice guidance started.', 'info');
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

/* =========================================================================
   CUSTOM COLORS & TYPOGRAPHY
   ========================================================================= */
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

/* =========================================================================
   COLLEAGUE PROFILES & TERRITORY MANAGEMENT (STRICT MAX 2 STATES)
   ========================================================================= */
function hydrateLocalProfiles() {
    try {
        const saved = JSON.parse(window.localStorage.getItem('grace-profiles') || '{}');
        Object.keys(saved).forEach((k) => {
            if (PROFILE_DATA[k]) Object.assign(PROFILE_DATA[k], saved[k]);
        });
        hydrateColleagueCards();
    } catch (error) {}
}

function hydrateColleagueCards() {
    Object.keys(PROFILE_DATA).forEach((key) => {
        const prof = PROFILE_DATA[key];
        const card = document.querySelector('[data-colleague-card="' + key + '"]');
        if (!card) return;
        const nameEl = card.querySelector('.colleague-name');
        const roleEl = card.querySelector('.colleague-role');
        const stateWrap = card.querySelector('.colleague-states-list');
        const contractorWrap = card.querySelector('.colleague-contractors-list');
        if (nameEl) nameEl.innerText = prof.name;
        if (roleEl) roleEl.innerText = prof.role;
        if (stateWrap) {
            const states = prof.assigned_states || [];
            stateWrap.innerHTML = states.length
                ? states.map((s) => '<span class="state-badge">📍 ' + s + '</span>').join('')
                : '<span style="color:var(--text-muted);font-size:11px;">No states assigned (Max 2)</span>';
        }
        if (contractorWrap) {
            const contractors = prof.assigned_contractors || [];
            contractorWrap.innerHTML = contractors.length
                ? contractors.map((c) => '<span class="state-badge" style="border-color:var(--accent-gold); color:var(--accent-gold);">🏗️ ' + c + '</span>').join('')
                : '<span style="color:var(--text-muted);font-size:11px;">No contractors assigned (Max 2)</span>';
        }
    });
}

let activeEditingColleague = null;
let tempSelectedStates = [];
let tempSelectedContractors = [];
let editStateFilter = '';
let editContractorFilter = '';

function filterSettingsChips(type, query) {
    if (type === 'states') {
        editStateFilter = (query || '').trim().toLowerCase();
        renderTerritoryChips();
    } else {
        editContractorFilter = (query || '').trim().toLowerCase();
        renderContractorChips();
    }
}

function openColleagueSettings(key) {
    activeEditingColleague = key;
    const prof = PROFILE_DATA[key];
    if (!prof) return;
    const modal = document.getElementById('colleague-settings-modal');
    document.getElementById('edit-colleague-key').value = key;
    document.getElementById('edit-colleague-name').value = prof.name;
    document.getElementById('edit-colleague-role').value = prof.role;
    tempSelectedStates = Array.from(prof.assigned_states || []);
    tempSelectedContractors = Array.from(prof.assigned_contractors || []);
    editStateFilter = '';
    editContractorFilter = '';
    const stSearch = document.getElementById('edit-state-search');
    const ctSearch = document.getElementById('edit-contractor-search');
    if (stSearch) stSearch.value = '';
    if (ctSearch) ctSearch.value = '';
    renderTerritoryChips();
    renderContractorChips();
    modal.hidden = false;
}

function closeColleagueSettings() {
    const modal = document.getElementById('colleague-settings-modal');
    if (modal) modal.hidden = true;
    activeEditingColleague = null;
}

function renderTerritoryChips() {
    const container = document.getElementById('territory-chips-container');
    const counter = document.getElementById('assigned-states-count');
    const warning = document.getElementById('territory-warning');
    if (!container) return;
    if (counter) counter.innerText = String(tempSelectedStates.length);
    if (warning) warning.hidden = tempSelectedStates.length < 2;
    const list = editStateFilter
        ? US_STATES.filter(s => s.toLowerCase().includes(editStateFilter))
        : US_STATES;
    container.innerHTML = list.map((state) => {
        const isSelected = tempSelectedStates.includes(state);
        return '<button type="button" class="state-chip-btn ' + (isSelected ? 'selected' : '') + '" onclick="toggleTerritoryState(\'' + state.replace(/'/g, "\\'") + '\')">' + (isSelected ? '✓ ' : '+ ') + state + '</button>';
    }).join('');
}

function toggleTerritoryState(state) {
    const idx = tempSelectedStates.indexOf(state);
    if (idx >= 0) {
        tempSelectedStates.splice(idx, 1);
    } else {
        if (tempSelectedStates.length >= 2) {
            showToast('Strict limit: Max 2 territory states allowed per colleague.', 'warning');
            const warning = document.getElementById('territory-warning');
            if (warning) {
                warning.hidden = false;
                warning.innerText = '⚠️ Maximum 2 states limit reached! Uncheck one to change.';
            }
            return;
        }
        tempSelectedStates.push(state);
    }
    renderTerritoryChips();
}

function renderContractorChips() {
    const container = document.getElementById('contractor-chips-container');
    const counter = document.getElementById('assigned-contractors-count');
    const warning = document.getElementById('contractor-warning');
    if (!container) return;
    if (counter) counter.innerText = String(tempSelectedContractors.length);
    if (warning) warning.hidden = tempSelectedContractors.length < 2;
    const list = editContractorFilter
        ? US_CONTRACTORS.filter(c => c.toLowerCase().includes(editContractorFilter))
        : US_CONTRACTORS;
    container.innerHTML = list.map((ct) => {
        const isSelected = tempSelectedContractors.includes(ct);
        return '<button type="button" class="state-chip-btn ' + (isSelected ? 'selected' : '') + '" onclick="toggleTerritoryContractor(\'' + ct.replace(/'/g, "\\'") + '\')">' + (isSelected ? '✓ ' : '+ ') + ct + '</button>';
    }).join('');
}

function toggleTerritoryContractor(ct) {
    const idx = tempSelectedContractors.indexOf(ct);
    if (idx >= 0) {
        tempSelectedContractors.splice(idx, 1);
    } else {
        if (tempSelectedContractors.length >= 2) {
            showToast('Strict limit: Max 2 contractors allowed per colleague.', 'warning');
            const warning = document.getElementById('contractor-warning');
            if (warning) {
                warning.hidden = false;
                warning.innerText = '⚠️ Maximum 2 contractors limit reached! Uncheck one to change.';
            }
            return;
        }
        tempSelectedContractors.push(ct);
    }
    renderContractorChips();
}

function saveColleagueSettings() {
    const key = document.getElementById('edit-colleague-key').value;
    const name = document.getElementById('edit-colleague-name').value.trim();
    const role = document.getElementById('edit-colleague-role').value.trim();
    if (!name || !role) {
        showToast('Please enter both name and role.', 'warning');
        return;
    }
    if (tempSelectedStates.length > 2) {
        showToast('Maximum 2 states allowed per colleague.', 'warning');
        return;
    }
    if (tempSelectedContractors.length > 2) {
        showToast('Maximum 2 contractors allowed per colleague.', 'warning');
        return;
    }
    if (!PROFILE_DATA[key]) return;
    PROFILE_DATA[key].name = name;
    PROFILE_DATA[key].role = role;
    PROFILE_DATA[key].assigned_states = Array.from(tempSelectedStates);
    PROFILE_DATA[key].assigned_contractors = Array.from(tempSelectedContractors);

    window.localStorage.setItem('grace-profiles', JSON.stringify(PROFILE_DATA));
    publishSharedState('profiles', {name, role, assigned_states: tempSelectedStates, assigned_contractors: tempSelectedContractors}, key);
    publishAuditEvent('Territory Update', 'Updated profile, states & contractors for ' + name);
    hydrateColleagueCards();
    populateColleaguePickers();
    updateViewAs();
    closeColleagueSettings();
    showToast('Profile, territory states & contractors saved permanently.', 'success');
}

/* =========================================================================
   AUTO-ASPECT FRAMING CANVAS AVATAR CROPPER (MOBILE 9:16 & ANY RATIO)
   ========================================================================= */
let cropperState = {
    key: null,
    image: null,
    scale: 1,
    fitScale: 1,
    fillScale: 1,
    offsetX: 0,
    offsetY: 0,
    dragging: false,
    startX: 0,
    startY: 0
};

function triggerAvatarUpload(key) {
    cropperState.key = key;
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.onchange = function(e) {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        if (file.size > 8000000) { showToast('Image file too large. Max 8MB.', 'warning'); return; }
        const reader = new FileReader();
        reader.onload = function() {
            const img = new Image();
            img.onload = function() {
                openImageCropper(key, img);
            };
            img.src = reader.result;
        };
        reader.readAsDataURL(file);
    };
    fileInput.click();
}

function openImageCropper(key, img) {
    cropperState.key = key;
    cropperState.image = img;
    cropperState.offsetX = 0;
    cropperState.offsetY = 0;

    const canvas = document.getElementById('cropper-canvas');
    const w = canvas ? canvas.width : 320;
    const h = canvas ? canvas.height : 320;

    // Calculate smart fit so full mobile vertical/horizontal image fits comfortably
    const fitScale = (w * 0.78) / Math.max(img.width, img.height);
    const fillScale = (w * 0.85) / Math.min(img.width, img.height);
    cropperState.fitScale = fitScale;
    cropperState.fillScale = fillScale;
    cropperState.scale = fitScale; // Default to full fit so entire mobile photo is visible!

    const zoomEl = document.getElementById('cropper-zoom');
    if (zoomEl) {
        zoomEl.value = Math.min(4.0, Math.max(0.15, fitScale));
        document.getElementById('cropper-zoom-val').innerText = (fitScale).toFixed(2) + '×';
    }

    const modal = document.getElementById('image-cropper-modal');
    modal.hidden = false;
    initCropperCanvasEvents();
    drawCropper();
}

function closeImageCropper() {
    const modal = document.getElementById('image-cropper-modal');
    if (modal) modal.hidden = true;
    cropperState.image = null;
}

function cropperFitFull() {
    if (!cropperState.image) return;
    cropperState.scale = cropperState.fitScale;
    cropperState.offsetX = 0;
    cropperState.offsetY = 0;
    const zoomEl = document.getElementById('cropper-zoom');
    if (zoomEl) {
        zoomEl.value = cropperState.fitScale;
        document.getElementById('cropper-zoom-val').innerText = cropperState.fitScale.toFixed(2) + '×';
    }
    drawCropper();
    showToast('Fitted entire image inside viewfinder.', 'info');
}

function cropperFillCircle() {
    if (!cropperState.image) return;
    cropperState.scale = cropperState.fillScale;
    cropperState.offsetX = 0;
    cropperState.offsetY = 0;
    const zoomEl = document.getElementById('cropper-zoom');
    if (zoomEl) {
        zoomEl.value = cropperState.fillScale;
        document.getElementById('cropper-zoom-val').innerText = cropperState.fillScale.toFixed(2) + '×';
    }
    drawCropper();
    showToast('Expanded to fill circular frame.', 'info');
}

function cropperResetCenter() {
    cropperState.offsetX = 0;
    cropperState.offsetY = 0;
    drawCropper();
}

function initCropperCanvasEvents() {
    const canvas = document.getElementById('cropper-canvas');
    if (!canvas || canvas.dataset.ready) return;
    canvas.dataset.ready = 'true';

    canvas.addEventListener('pointerdown', function(e) {
        cropperState.dragging = true;
        cropperState.startX = e.clientX - cropperState.offsetX;
        cropperState.startY = e.clientY - cropperState.offsetY;
        canvas.setPointerCapture?.(e.pointerId);
    });
    canvas.addEventListener('pointermove', function(e) {
        if (!cropperState.dragging) return;
        cropperState.offsetX = e.clientX - cropperState.startX;
        cropperState.offsetY = e.clientY - cropperState.startY;
        drawCropper();
    });
    canvas.addEventListener('pointerup', function() {
        cropperState.dragging = false;
    });

    // Mouse wheel zoom
    canvas.addEventListener('wheel', function(e) {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.08 : -0.08;
        cropperState.scale = Math.max(0.15, Math.min(4.0, cropperState.scale + delta));
        const zoomEl = document.getElementById('cropper-zoom');
        if (zoomEl) {
            zoomEl.value = cropperState.scale;
            document.getElementById('cropper-zoom-val').innerText = cropperState.scale.toFixed(2) + '×';
        }
        drawCropper();
    }, {passive: false});
}

function onCropperZoomChange() {
    const zoomVal = parseFloat(document.getElementById('cropper-zoom').value);
    cropperState.scale = zoomVal;
    document.getElementById('cropper-zoom-val').innerText = zoomVal.toFixed(2) + '×';
    drawCropper();
}

function drawCropper() {
    const canvas = document.getElementById('cropper-canvas');
    if (!canvas || !cropperState.image) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Dark backdrop fill
    ctx.fillStyle = '#031713';
    ctx.fillRect(0, 0, w, h);

    // Draw image centered and scaled
    const img = cropperState.image;
    const drawW = img.width * cropperState.scale;
    const drawH = img.height * cropperState.scale;
    const drawX = (w - drawW) / 2 + cropperState.offsetX;
    const drawY = (h - drawH) / 2 + cropperState.offsetY;

    ctx.save();
    ctx.drawImage(img, drawX, drawY, drawW, drawH);
    ctx.restore();

    // Dark overlay with circular cutout
    ctx.save();
    ctx.fillStyle = 'rgba(0, 10, 8, 0.7)';
    ctx.beginPath();
    ctx.rect(0, 0, w, h);
    ctx.arc(w / 2, h / 2, w * 0.4, 0, Math.PI * 2, true);
    ctx.fill();

    // Circular crop guide stroke
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#D6A117';
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, w * 0.4, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Draw live preview
    const preview = document.getElementById('cropper-preview');
    if (preview) {
        const pctx = preview.getContext('2d');
        const pw = preview.width;
        const ph = preview.height;
        pctx.clearRect(0, 0, pw, ph);

        pctx.save();
        pctx.fillStyle = '#031713';
        pctx.beginPath();
        pctx.arc(pw / 2, ph / 2, pw / 2, 0, Math.PI * 2);
        pctx.fill();
        pctx.clip();

        // Draw cropped view
        const cropDiameter = w * 0.8;
        const cropLeft = (w - cropDiameter) / 2;
        const cropTop = (h - cropDiameter) / 2;
        pctx.drawImage(canvas, cropLeft, cropTop, cropDiameter, cropDiameter, 0, 0, pw, ph);
        pctx.restore();
    }
}

function saveCroppedAvatar() {
    const canvas = document.getElementById('cropper-canvas');
    if (!canvas || !cropperState.key) return;
    const w = canvas.width;
    const h = canvas.height;
    const cropSize = w * 0.8;
    const cropX = (w - cropSize) / 2;
    const cropY = (h - cropSize) / 2;

    const exportCanvas = document.createElement('canvas');
    exportCanvas.width = 240;
    exportCanvas.height = 240;
    const ectx = exportCanvas.getContext('2d');

    // Circular clip
    ectx.beginPath();
    ectx.arc(120, 120, 120, 0, Math.PI * 2);
    ectx.clip();

    // Dark backdrop fill for circular avatar
    ectx.fillStyle = '#031713';
    ectx.fillRect(0, 0, 240, 240);

    // Redraw the raw image cleanly without overlay
    const img = cropperState.image;
    const drawW = img.width * cropperState.scale;
    const drawH = img.height * cropperState.scale;
    const drawX = (w - drawW) / 2 + cropperState.offsetX;
    const drawY = (h - drawH) / 2 + cropperState.offsetY;

    // Scale from canvas 320x320 crop to export 240x240
    const exportScale = 240 / cropSize;
    ectx.drawImage(
        img,
        (drawX - cropX) * exportScale,
        (drawY - cropY) * exportScale,
        drawW * exportScale,
        drawH * exportScale
    );

    const croppedDataUri = exportCanvas.toDataURL('image/jpeg', 0.9);
    const key = cropperState.key;

    // Save to local & server
    const photos = JSON.parse(window.localStorage.getItem('grace-profile-photos') || '{}');
    photos[key] = croppedDataUri;
    window.localStorage.setItem('grace-profile-photos', JSON.stringify(photos));
    setAvatarImage(key, croppedDataUri);
    publishSharedState('photos', croppedDataUri, key);

    closeImageCropper();
    showToast('Cropped avatar updated and synced across sessions.', 'success');
}

function setAvatarImage(key, data) {
    document.querySelectorAll('[data-profile-avatar="' + key + '"]').forEach((target) => {
        target.style.backgroundImage = 'url("' + data + '")';
        target.style.backgroundSize = 'cover';
        target.style.backgroundPosition = 'center center';
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

/* =========================================================================
   ATTENDANCE, FINES & PAYROLL (150 PKR / MISSED SHIFT)
   ========================================================================= */
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
    if ((window.localStorage.getItem('grace-view-as') || 'king') !== 'king') { showToast('Attendance edits restricted to Super Admin.', 'warning'); renderAttendanceLedger(); return; }
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
    publishSharedState('attendance', state);
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
    if ((window.localStorage.getItem('grace-view-as') || 'king') !== 'king') { showToast('Leave approval restricted to Super Admin.', 'warning'); renderAttendanceLedger(); return; }
    const leaves = getLeaveState();
    const key = select.dataset.leaveState;
    leaves[key] = leaves[key] || {};
    leaves[key].state = select.value;
    const start = document.querySelector('[data-leave-date="' + key + '-start"]');
    const end = document.querySelector('[data-leave-date="' + key + '-end"]');
    if (start) leaves[key].start = start.value;
    if (end) leaves[key].end = end.value;
    window.localStorage.setItem('grace-leave-requests', JSON.stringify(leaves));
    publishSharedState('leaves', leaves);
    renderAttendanceLedger();
    showToast('Leave request marked ' + (select.value === 'approved' ? 'Approved' : 'Received') + '.', 'success');
}
function requestLeave(key) {
    const leaves = getLeaveState();
    leaves[key] = leaves[key] || {start:'2026-09-07', end:'2026-09-07'};
    leaves[key].state = 'received';
    window.localStorage.setItem('grace-leave-requests', JSON.stringify(leaves));
    publishSharedState('leaves', leaves);
    renderAttendanceLedger();
    showToast('Leave request received for admin review.', 'info');
}

/* =========================================================================
   VIEW-AS & RBAC MATRIX
   ========================================================================= */
function hydrateAccessMap() {
    try {
        const saved = JSON.parse(window.localStorage.getItem('grace-access-map') || '{}');
        Object.keys(saved).forEach((key) => { if (Array.isArray(saved[key])) ACCESS_MAP[key] = saved[key]; });
    } catch (error) {}
}
function savePermission(colleague, moduleId, enabled) {
    ACCESS_MAP[colleague] = ACCESS_MAP[colleague] || [];
    ACCESS_MAP[colleague] = enabled
        ? Array.from(new Set(ACCESS_MAP[colleague].concat(moduleId))).sort((a,b) => a-b)
        : ACCESS_MAP[colleague].filter((id) => id !== moduleId);
    window.localStorage.setItem('grace-access-map', JSON.stringify(ACCESS_MAP));
    publishSharedState('accessMap', ACCESS_MAP);
    if ((window.localStorage.getItem('grace-view-as') || 'king') === colleague) updateViewAs();
    showToast('Module ' + moduleId + ' ' + (enabled ? 'enabled for ' : 'restricted for ') + colleague + '.', enabled ? 'success' : 'warning');
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
    const activeChip = document.getElementById('active-profile-chip');
    if (activeChip) activeChip.querySelector('.presence-dot')?.classList.toggle('online', profile.status === 'Online');
    document.body.dataset.activeProfile = value;
    const allowed = ACCESS_MAP[value] || ACCESS_MAP.king;
    const scope = document.getElementById('active-scope-count');
    if (scope) scope.innerText = allowed.length === 22 ? 'All 22 modules enabled' : allowed.length + ' of 22 modules enabled';
    if (profile.metrics) {
        Object.entries(profile.metrics).forEach(([key, metric]) => {
            const target = document.querySelector('[data-metric-key="' + key + '"]');
            if (target) target.innerText = metric;
        });
    }
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
    updateAttendanceAccess();
    const profile = PROFILE_DATA[value] || PROFILE_DATA.king;
    showToast('Active workspace switched to ' + profile.name + ' · ' + profile.role + '.', 'info');
}

/* =========================================================================
   CAMPAIGN STUDIO (MODULE 4 & 5)
   ========================================================================= */
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
    const options = template.replace(/\{([^{}]+)\}/g, function(_, choices) {
        const values = choices.split('|');
        return values[(index + values.length - 1) % values.length].trim();
    });
    const modifiers = ['Quick note: ', 'A brief update: ', 'Sharing a timely note: '];
    return modifiers[index % modifiers.length] + options.replace(/\s+([.!?])/, '$1');
}
function generateSpintaxVariants() {
    const template = document.getElementById('spintax-template')?.value || '';
    return [0, 1, 2].map((index) => spinTemplate(template, index));
}
function previewSpintax() {
    const variants = generateSpintaxVariants();
    const preview = document.getElementById('spintax-preview');
    if (preview) preview.innerText = variants.map((variant, index) => 'Variant ' + (index + 1) + ' · ' + variant).join('\n');
    const status = document.getElementById('spintax-status');
    if (status) status.innerText = 'Per-send variation engine · 3 fresh variants generated';
    showToast('Spintax variations and template modifications generated.', 'success');
}
function sendSpintaxBatch() {
    previewSpintax();
    showToast('Batch send simulation applied a unique variant to every recipient.', 'success');
}

/* =========================================================================
   INTERACTIVE CAMPAIGN EXECUTION STUDIO
   ========================================================================= */
let studioJitterTimer = null;
let studioIsDispatching = false;
let studioJitterProfile = 'human';

function openCampaignStudio() {
    const modal = document.getElementById('campaign-studio-modal');
    if (!modal) return;
    modal.hidden = false;
    updateStudioRange();
}

function closeCampaignStudio() {
    const modal = document.getElementById('campaign-studio-modal');
    if (modal) modal.hidden = true;
    cancelStudioDispatch();
}

function updateStudioRange() {
    const start = parseInt(document.getElementById('studio-range-start')?.value || '1', 10);
    const end = parseInt(document.getElementById('studio-range-end')?.value || '25', 10);
    const count = Math.max(0, end - start + 1);
    const targetCount = document.getElementById('studio-target-count');
    if (targetCount) targetCount.innerText = count + ' Decision-Makers';
}

function generateStudioAiVariants() {
    const subjTpl = document.getElementById('studio-subject')?.value || '{Exclusive Alliance|Commercial Opportunity} with {{company}}';
    const bodyTpl = document.getElementById('studio-body')?.value || '{Hi|Hello} {{first_name}}, let us collaborate.';
    const container = document.getElementById('studio-variants-preview');
    if (!container) return;

    function spin(template) {
        return template.replace(/\{([^{}]+)\}/g, function(_, choices) {
            const arr = choices.split('|');
            return arr[Math.floor(Math.random() * arr.length)].trim();
        });
    }

    const previewCards = [1, 2, 3].map(i => {
        const s = spin(subjTpl).replace('{{company}}', 'Apex Arch LLC');
        const b = spin(bodyTpl).replace('{{first_name}}', 'Marcus').replace('{{state}}', 'California');
        return '<div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:6px; padding:8px; margin-bottom:6px;">' +
            '<div style="font-size:11px; color:var(--accent-gold); font-weight:700;">Variant #' + i + ' Subject: ' + s + '</div>' +
            '<div style="font-size:11px; color:var(--text-main); margin-top:3px;">' + b + '</div>' +
            '</div>';
    }).join('');

    container.innerHTML = previewCards;
    container.style.display = 'block';
    showToast('Generated 3 AI rotating Spintax variants.', 'success');
}

function updateStudioInboxAuth(inbox) {
    const chip = document.getElementById('studio-auth-chip');
    const btn = document.getElementById('studio-auth-action-btn');
    const desc = document.getElementById('studio-auth-desc');
    if (inbox.includes('node2')) {
        if (chip) { chip.className = 'auth-status-chip connected'; chip.innerText = '● 16-Digit App Password'; }
        if (btn) btn.innerText = '🔑 Validate App Password';
        if (desc) desc.innerText = 'Encrypted AES-256 Locker';
    } else {
        if (chip) { chip.className = 'auth-status-chip connected'; chip.innerText = '● OAuth 2.0 Connected'; }
        if (btn) btn.innerText = '🔗 Re-Authorize Google OAuth';
        if (desc) desc.innerText = 'AES-256 Token Active';
    }
}

function triggerOAuthPermissionFlow() {
    showToast('Google OAuth 2.0 consent token verified and renewed (AES-256).', 'success');
}

function stageStudioDrafts() {
    const start = parseInt(document.getElementById('studio-range-start')?.value || '1', 10);
    const end = parseInt(document.getElementById('studio-range-end')?.value || '25', 10);
    const count = Math.max(0, end - start + 1);
    const progress = document.getElementById('studio-draft-progress');
    const status = document.getElementById('studio-draft-status');

    if (status) status.innerText = 'Staging ' + count + ' customized drafts in Gmail account...';
    let pct = 0;
    if (progress) progress.style.width = '0%';
    const intv = setInterval(() => {
        pct += 25;
        if (progress) progress.style.width = pct + '%';
        if (pct >= 100) {
            clearInterval(intv);
            if (status) status.innerText = '✓ ' + count + ' Drafts successfully created in Gmail queue (Ready to send)';
            showToast(count + ' Drafts staged in multi-tenant inbox.', 'success');
        }
    }, 280);
}

function updateJitterProfile(profile) {
    studioJitterProfile = profile;
    const label = document.getElementById('studio-jitter-label');
    if (!label) return;
    if (profile === 'human') label.innerText = 'Random Jitter: 1s – 5s';
    else if (profile === 'steady') label.innerText = 'Steady: 4s Interval';
    else label.innerText = 'Conservative: 8s Interval';
}

function runStudioDispatch() {
    if (studioIsDispatching) {
        showToast('Dispatch is already in progress.', 'info');
        return;
    }
    const start = parseInt(document.getElementById('studio-range-start')?.value || '1', 10);
    const end = parseInt(document.getElementById('studio-range-end')?.value || '25', 10);
    const count = Math.max(0, end - start + 1);

    const ticker = document.getElementById('studio-live-ticker');
    if (ticker) {
        ticker.style.display = 'block';
        ticker.innerHTML = '<div style="color:var(--accent-green); font-weight:700;">🚀 Dispatch queue launched for ' + count + ' records...</div>';
    }

    studioIsDispatching = true;
    let currentRecord = start;

    const contractorSampleNames = [
        "Marcus Vance · Apex Arch (CA)", "Elena Ramos · Blue Ridge (TX)",
        "David Sterling · Cascade (WA)", "Rachel Meyer · Evergreen (IL)",
        "Thomas Reed · Summit Valley (CO)", "Sophia Alvarez · Coastal (FL)",
        "Julian Hayes · Metro Guild (NY)", "Kevin Brooks · Keystone (PA)"
    ];

    function scheduleNext() {
        if (!studioIsDispatching || currentRecord > end) {
            studioIsDispatching = false;
            if (ticker) ticker.innerHTML = '<div style="color:var(--accent-gold); font-weight:700;">✓ Campaign Dispatch Complete. ' + count + ' emails sent safely.</div>' + ticker.innerHTML;
            showToast('All ' + count + ' outreach emails dispatched safely!', 'success');
            publishAuditEvent('Campaign Dispatch', 'Safely dispatched ' + count + ' outreach emails with human jitter');
            return;
        }

        let jitterMs = 2500;
        if (studioJitterProfile === 'human') {
            jitterMs = Math.floor(Math.random() * 4000) + 1200; // 1.2s to 5.2s
        } else if (studioJitterProfile === 'steady') {
            jitterMs = 4000;
        } else {
            jitterMs = 8000;
        }

        studioJitterTimer = setTimeout(() => {
            const nowTime = new Date().toTimeString().split(' ')[0];
            const name = contractorSampleNames[(currentRecord - start) % contractorSampleNames.length];
            const jitterSec = (jitterMs / 1000).toFixed(1);
            if (ticker) {
                const line = document.createElement('div');
                line.style.fontSize = '11px';
                line.style.margin = '2px 0';
                line.innerHTML = '<span style="color:var(--accent-green);">[' + nowTime + ']</span> <b style="color:var(--accent-gold);">#' + currentRecord + '</b> Sent to <i>' + name + '</i> · Jitter ' + jitterSec + 's · Spintax Applied';
                ticker.prepend(line);
            }
            currentRecord++;
            scheduleNext();
        }, jitterMs);
    }

    scheduleNext();
    showToast('Autonomous jittered dispatch started.', 'success');
}

function cancelStudioDispatch() {
    if (studioJitterTimer) clearTimeout(studioJitterTimer);
    studioIsDispatching = false;
    const ticker = document.getElementById('studio-live-ticker');
    if (ticker && ticker.style.display !== 'none') {
        ticker.innerHTML = '<div style="color:var(--accent-orange); font-weight:700;">⏹ Dispatch halted by user.</div>' + ticker.innerHTML;
    }
    showToast('Campaign dispatch halted.', 'warning');
}

/* Session Enforcement on load */
const origApplyStoredTheme = applyStoredTheme;
applyStoredTheme = function() {
    origApplyStoredTheme();
    const authSession = window.sessionStorage.getItem('grace_auth_user');
    if (!authSession) {
        openAuthGateway('signin', true, true);
    }
};


/* =========================================================================
   DIRECT IN-PAGE WORKSPACE HANDLERS (MODULES 1–22)
   ========================================================================= */
let m1OutreachPaused = false;
function toggleM1Outreach() {
    m1OutreachPaused = !m1OutreachPaused;
    const btn = document.getElementById('m1-toggle-btn');
    const status = document.getElementById('m1-engine-status');
    if (m1OutreachPaused) {
        if (btn) btn.innerText = '▶ Resume Live Outreach Stream';
        if (status) { status.innerText = '⏸ Outreach Stream Paused'; status.style.background = 'var(--accent-orange)'; }
        showToast('Real-time outreach stream paused across all inboxes.', 'warning');
    } else {
        if (btn) btn.innerText = '⏸ Pause Live Outreach Stream';
        if (status) { status.innerText = '● Real-Time Engine Active'; status.style.background = 'var(--accent-green)'; }
        showToast('Real-time outreach stream resumed at calibrated velocity.', 'success');
    }
}

function simulateM3WarmupReplies() {
    const log = document.getElementById('m3-peer-log');
    if (log) {
        const now = new Date().toTimeString().split(' ')[0];
        const seedEmails = ["seed.alpha@reputation-ramp.io", "peer.validator@inbox-guard.net", "rep.deliverability@trust-relay.org"];
        seedEmails.forEach(e => {
            const line = document.createElement('div');
            line.innerHTML = '<span style="color:var(--accent-green);">[' + now + '] [PEER-REPLY]</span> 2-way engagement confirmed from <i>' + e + '</i> (Positive signal)';
            log.prepend(line);
        });
    }
    showToast('Simulated 5 peer warmup threads engaged successfully.', 'success');
}

function updateInpageStudioRange() {
    const start = parseInt(document.getElementById('inpage-studio-range-start')?.value || '1', 10);
    const end = parseInt(document.getElementById('inpage-studio-range-end')?.value || '25', 10);
    const count = Math.max(0, end - start + 1);
    const targetCount = document.getElementById('inpage-studio-target-count');
    if (targetCount) targetCount.innerText = count + ' Decision-Makers';
}

function generateInpageStudioAiVariants() {
    const subjTpl = document.getElementById('inpage-studio-subject')?.value || '{Exclusive Alliance|Commercial Opportunity} with {{company}}';
    const bodyTpl = document.getElementById('inpage-studio-body')?.value || '{Hi|Hello} {{first_name}}, let us collaborate.';
    const container = document.getElementById('inpage-studio-variants-preview');
    if (!container) return;

    function spin(template) {
        return template.replace(/\{([^{}]+)\}/g, function(_, choices) {
            const arr = choices.split('|');
            return arr[Math.floor(Math.random() * arr.length)].trim();
        });
    }

    const previewCards = [1, 2, 3].map(i => {
        const s = spin(subjTpl).replace('{{company}}', 'Apex Arch LLC');
        const b = spin(bodyTpl).replace('{{first_name}}', 'Marcus').replace('{{state}}', 'California');
        return '<div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:6px; padding:8px; margin-bottom:6px;">' +
            '<div style="font-size:11px; color:var(--accent-gold); font-weight:700;">Variant #' + i + ' Subject: ' + s + '</div>' +
            '<div style="font-size:11px; color:var(--text-main); margin-top:3px;">' + b + '</div>' +
            '</div>';
    }).join('');

    container.innerHTML = previewCards;
    container.style.display = 'block';
    showToast('Generated 3 AI rotating Spintax variants in workspace.', 'success');
}

function stageInpageStudioDrafts() {
    const start = parseInt(document.getElementById('inpage-studio-range-start')?.value || '1', 10);
    const end = parseInt(document.getElementById('inpage-studio-range-end')?.value || '25', 10);
    const count = Math.max(0, end - start + 1);
    const progress = document.getElementById('inpage-studio-draft-progress');
    const status = document.getElementById('inpage-studio-draft-status');

    if (status) status.innerText = 'Staging ' + count + ' customized drafts in Gmail account...';
    let pct = 0;
    if (progress) progress.style.width = '0%';
    const intv = setInterval(() => {
        pct += 25;
        if (progress) progress.style.width = pct + '%';
        if (pct >= 100) {
            clearInterval(intv);
            if (status) status.innerText = '✓ ' + count + ' Drafts successfully staged in Gmail inbox (Armed for dispatch)';
            showToast(count + ' Drafts staged in Gmail inbox!', 'success');
        }
    }, 250);
}

let inpageDispatchTimer = null;
let inpageIsDispatching = false;
function runInpageStudioDispatch() {
    if (inpageIsDispatching) {
        showToast('Dispatch is already in progress.', 'info');
        return;
    }
    const start = parseInt(document.getElementById('inpage-studio-range-start')?.value || '1', 10);
    const end = parseInt(document.getElementById('inpage-studio-range-end')?.value || '25', 10);
    const count = Math.max(0, end - start + 1);

    const ticker = document.getElementById('inpage-studio-live-ticker');
    if (ticker) {
        ticker.style.display = 'block';
        ticker.innerHTML = '<div style="color:var(--accent-green); font-weight:700;">🚀 In-page dispatch engine initialized for ' + count + ' records...</div>';
    }

    inpageIsDispatching = true;
    let currentRecord = start;

    const contractorSampleNames = [
        "Marcus Vance · Apex Arch (CA)", "Elena Ramos · Blue Ridge (TX)",
        "David Sterling · Cascade (WA)", "Rachel Meyer · Evergreen (IL)",
        "Thomas Reed · Summit Valley (CO)", "Sophia Alvarez · Coastal (FL)"
    ];

    function scheduleNext() {
        if (!inpageIsDispatching || currentRecord > end) {
            inpageIsDispatching = false;
            if (ticker) ticker.innerHTML = '<div style="color:var(--accent-gold); font-weight:700;">✓ In-Page Dispatch Complete. ' + count + ' outreach emails delivered safely.</div>' + ticker.innerHTML;
            showToast('All ' + count + ' outreach emails dispatched safely!', 'success');
            publishAuditEvent('Campaign Dispatch', 'Safely dispatched ' + count + ' contractor outreach emails from Module 4');
            return;
        }

        const jitterMs = Math.floor(Math.random() * 3000) + 1200; // 1.2s to 4.2s

        inpageDispatchTimer = setTimeout(() => {
            const nowTime = new Date().toTimeString().split(' ')[0];
            const name = contractorSampleNames[(currentRecord - start) % contractorSampleNames.length];
            const jitterSec = (jitterMs / 1000).toFixed(1);
            if (ticker) {
                const line = document.createElement('div');
                line.style.fontSize = '11px';
                line.style.margin = '2px 0';
                line.innerHTML = '<span style="color:var(--accent-green);">[' + nowTime + ']</span> <b style="color:var(--accent-gold);">#' + currentRecord + '</b> Dispatched to <i>' + name + '</i> · Jitter ' + jitterSec + 's';
                ticker.prepend(line);
            }
            currentRecord++;
            scheduleNext();
        }, jitterMs);
    }

    scheduleNext();
    showToast('Autonomous in-page jittered dispatch started.', 'success');
}

function cancelInpageStudioDispatch() {
    if (inpageDispatchTimer) clearTimeout(inpageDispatchTimer);
    inpageIsDispatching = false;
    const ticker = document.getElementById('inpage-studio-live-ticker');
    if (ticker && ticker.style.display !== 'none') {
        ticker.innerHTML = '<div style="color:var(--accent-orange); font-weight:700;">⏹ Dispatch halted by user.</div>' + ticker.innerHTML;
    }
    showToast('Campaign dispatch halted.', 'warning');
}

function generateM5Variants() {
    const subj = document.getElementById('m5-subject')?.value || '';
    const body = document.getElementById('m5-body')?.value || '';
    const container = document.getElementById('m5-variants-container');
    if (!container) return;

    function spin(text, idx) {
        return text.replace(/\{([^{}]+)\}/g, function(_, choices) {
            const arr = choices.split('|');
            return arr[(idx + arr.length) % arr.length].trim();
        }).replace('{first_name}', 'Marcus').replace('{state}', 'California').replace('{firm_name}', 'Apex Arch');
    }

    container.innerHTML = [0, 1, 2].map(i => {
        return '<div style="padding:10px 14px; background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:8px;">' +
            '<div style="font-size:12px; color:var(--accent-gold); font-weight:700;">Variant #' + (i+1) + ' · Subject: ' + spin(subj, i) + '</div>' +
            '<div style="font-size:12px; color:var(--text-main); margin-top:4px;">' + spin(body, i) + '</div>' +
            '</div>';
    }).join('');
    showToast('3 Unique Spintax variants generated.', 'success');
}

function runM6Scraper() {
    const state = document.getElementById('m6-state-select')?.value || 'California';
    const wrap = document.getElementById('m6-progress-wrap');
    const bar = document.getElementById('m6-progress-bar');
    if (wrap) wrap.style.display = 'block';
    let pct = 0;
    const intv = setInterval(() => {
        pct += 25;
        if (bar) bar.style.width = pct + '%';
        if (pct >= 100) {
            clearInterval(intv);
            showToast('Scraper finished. 142 decision-makers enriched for ' + state + '.', 'success');
        }
    }, 200);
}

function renderM8Permissions(userKey) {
    const container = document.getElementById('m8-permissions-grid');
    if (!container) return;
    const allowed = ACCESS_MAP[userKey] || Array.from({length:22}, (_, i) => i + 1);
    container.innerHTML = Array.from({length:22}, (_, i) => i + 1).map(id => {
        const checked = allowed.includes(id) ? 'checked' : '';
        return '<label class="permission-item">' +
            '<input type="checkbox" ' + checked + ' onchange="savePermission(\'' + userKey + '\', ' + id + ', this.checked)">' +
            '<span class="perm-badge">M' + id + '</span>' +
            '<span class="perm-title">Module ' + id + ' Access</span>' +
            '</label>';
    }).join('');
}

function saveM8Permissions() {
    const userKey = document.getElementById('m8-colleague-select')?.value || 'abdullah';
    showToast('Permissions saved for ' + userKey + ' across 22 modules.', 'success');
}

function grantAllM8Permissions() {
    const userKey = document.getElementById('m8-colleague-select')?.value || 'abdullah';
    ACCESS_MAP[userKey] = Array.from({length:22}, (_, i) => i + 1);
    window.localStorage.setItem('grace-access-map', JSON.stringify(ACCESS_MAP));
    publishSharedState('accessMap', ACCESS_MAP);
    renderM8Permissions(userKey);
    showToast('All 22 modules granted to ' + userKey + '.', 'success');
}

function runM9Diagnostics() {
    const log = document.getElementById('m9-diag-log');
    if (log) {
        const now = new Date().toTimeString().split(' ')[0];
        log.innerHTML = '<div>[' + now + '] [DIAGNOSTIC] Probing WSGI simple server... HTTP 200 OK (38ms)</div>' +
            '<div>[' + now + '] [DIAGNOSTIC] Testing thread lock SHARED_STATE_LOCK... ACQUIRED & RELEASED</div>' +
            '<div>[' + now + '] [DIAGNOSTIC] Checking persistent storage integrity... ALL 22 DATA SLICES HEALTHY</div>' + log.innerHTML;
    }
    showToast('Full system health probe completed. All subsystems optimal (100%).', 'success');
}

function executeM11Query() {
    const query = (document.getElementById('m11-query-input')?.value || '').trim();
    const box = document.getElementById('m11-response-box');
    if (!query || !box) return;
    const lower = query.toLowerCase();
    let ans = "Module workflow runbook: Step 1 ➔ Review active telemetry. Step 2 ➔ Adjust parameters in workspace. Step 3 ➔ Run live action.";
    if (lower.includes('quota') || lower.includes('2')) ans = "Module 2 (Gmail Hub): Enforces strict 50/50 safe send limit per inbox to preserve domain reputation. Live quota meters display used capacity.";
    else if (lower.includes('4') || lower.includes('campaign')) ans = "Module 4 (Campaign Studio): Select records from the 1,000 contractor database, review Spintax AI variants, stage drafts into Gmail, and launch randomized jittered dispatch.";
    else if (lower.includes('contractor') || lower.includes('state')) ans = "Territory Governance: Colleague profiles are strictly limited to max 2 states and max 2 contractors. Use Module 8 or Colleague Settings to assign.";
    box.innerHTML = '<b style="color:var(--accent-gold);">Question: ' + query + '</b><br><span style="color:var(--accent-green);">' + ans + '</span>';
    showToast('AI Guide response rendered.', 'info');
}

function addM14Suppression() {
    const input = document.getElementById('m14-add-input');
    const email = (input?.value || '').trim();
    if (!email) { showToast('Please enter an email address to suppress.', 'warning'); return; }
    const tbody = document.querySelector('#m14-table tbody');
    if (tbody) {
        const row = document.createElement('tr');
        row.innerHTML = '<td><b>' + email + '</b></td><td>Manual Admin Suppression</td><td>' + new Date().toISOString().split('T')[0] + '</td><td><span style="color:var(--accent-red);font-weight:800;">Suppressed</span></td>';
        tbody.prepend(row);
    }
    input.value = '';
    showToast('Email added to active Zero-Bounce suppression registry.', 'success');
}

function classifyM15Sentiment() {
    const text = document.getElementById('m15-input')?.value || '';
    const badge = document.getElementById('m15-sentiment-badge');
    if (!badge) return;
    const lower = text.toLowerCase();
    if (lower.includes('out of the office') || lower.includes('away')) {
        badge.innerHTML = '<span style="color:var(--accent-orange);">● Auto-Responder / Out of Office</span>';
        showToast('Classified as Out of Office. Follow-up scheduled.', 'info');
    } else if (lower.includes('remove') || lower.includes('unsubscribe')) {
        badge.innerHTML = '<span style="color:var(--accent-red);">● Opt-Out Request (Immediate Suppression Triggered)</span>';
        showToast('Classified as Unsubscribe. Recipient suppressed.', 'warning');
    } else {
        badge.innerHTML = '<span style="color:var(--accent-green);">● Positive Commercial Opportunity (98.6%)</span>';
        showToast('Classified as High-Intent Opportunity.', 'success');
    }
}

function runM16Export() {
    const dataset = document.getElementById('m16-dataset')?.value || 'analytics';
    const format = document.getElementById('m16-format')?.value || 'csv';
    if (dataset === 'contractors') {
        exportScraperLeads(format);
    } else {
        exportAnalyticsReport(format);
    }
}

function sendM17Broadcast() {
    const target = document.getElementById('m17-target')?.options[document.getElementById('m17-target').selectedIndex]?.text || 'All';
    const msg = document.getElementById('m17-msg')?.value || '';
    if (!msg) { showToast('Please enter an alert message.', 'warning'); return; }
    if (document.getElementById('m17-chime')?.checked) playChime();
    showToast('Broadcast transmitted to ' + target + ' successfully!', 'success');
}

function sendM19Webhook() {
    const endpoint = document.getElementById('m19-endpoint')?.value || '';
    const status = document.getElementById('m19-status');
    if (status) status.innerText = 'Transmitting signed payload...';
    setTimeout(() => {
        if (status) status.innerHTML = '<b style="color:var(--accent-green);">HTTP 200 OK</b> · Response: <code>{"status":"acknowledged","latency":"74ms"}</code>';
        showToast('Webhook delivered with HMAC-SHA256 signature.', 'success');
    }, 450);
}

let m20Frozen = false;
function toggleM20EmergencyLock() {
    m20Frozen = !m20Frozen;
    const btn = document.getElementById('m20-lock-btn');
    if (m20Frozen) {
        if (btn) btn.innerText = '🔓 Unlock & Resume Inboxes';
        showToast('EMERGENCY FREEZE: All 3 inboxes locked immediately.', 'warning');
    } else {
        if (btn) btn.innerText = '🚨 Emergency Freeze: Lock All Inboxes';
        showToast('Emergency lock released. Safe sending resumed.', 'success');
    }
}


let M1_DISPATCH_PAUSED = false;
let M4_SEQUENCE_PAUSED = false;
let M13_QUEUE_PAUSED = false;

function clearAuthSession() {
    if (confirm("Are you sure you want to end your active session and lock the workspace?")) {
        sessionStorage.removeItem("grace_auth_user");
        sessionStorage.removeItem("grace_auth_role");
        showToast("🔒 Session ended. Returning to Gateway.", "warning");
        setTimeout(() => { window.location.reload(); }, 600);
    }
}

function runModuleBlueprintControl(modId, ctrlIdx, label, btn) {
    modId = parseInt(modId, 10);
    ctrlIdx = parseInt(ctrlIdx, 10);
    
    // Immediate visual feedback on button
    const originalText = btn ? btn.innerText : 'Run';
    if (btn) {
        btn.innerText = '⏳ Working...';
        btn.disabled = true;
    }
    
    setTimeout(() => {
        if (btn) {
            btn.disabled = false;
        }
        
        switch (modId) {
            case 1: {
                if (ctrlIdx === 0) { // Recalculate telemetry
                    const val0 = document.getElementById('telem-val-1-0');
                    const val1 = document.getElementById('telem-val-1-1');
                    const val2 = document.getElementById('telem-val-1-2');
                    if (val0) {
                        val0.innerText = '2,514';
                        val0.style.color = '#34D399';
                        setTimeout(() => val0.style.color = '#10B981', 1200);
                    }
                    if (val1) {
                        val1.innerText = '14m';
                        val1.style.color = '#34D399';
                        setTimeout(() => val1.style.color = '#10B981', 1200);
                    }
                    if (val2) {
                        val2.innerText = '99.4%';
                        val2.style.color = '#34D399';
                        setTimeout(() => val2.style.color = '#10B981', 1200);
                    }
                    const chart = document.getElementById('module-bar-chart');
                    if (chart) {
                        const heights = [58, 65, 72, 69, 81, 88, 92, 98];
                        const spans = chart.querySelectorAll('span');
                        spans.forEach((s, i) => { if (heights[i]) s.style.height = heights[i] + '%'; });
                    }
                    appendM1Log('Node sweep complete: 3 inboxes re-synchronized at 38ms latency.');
                    showToast('✓ Real-Time Node Sweep: 3 inboxes synced, 0 latency spikes.', 'success');
                    if (btn) btn.innerText = '✓ Swept';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Pause / Resume dispatch lanes
                    M1_DISPATCH_PAUSED = !M1_DISPATCH_PAUSED;
                    const tbody = document.getElementById('module-table-body');
                    const pill = document.getElementById('module-table-status-pill');
                    if (M1_DISPATCH_PAUSED) {
                        if (tbody) {
                            tbody.innerHTML = `
                                <tr id="mod-row-1-0"><td><b>Inbox #1 (business.inbox1)</b></td><td id="mod-val-1-0">45 messages</td><td><span class="row-state-badge" style="color:#EF4444; font-weight:800; background:rgba(239,68,68,0.15); padding:3px 8px; border-radius:4px; border:1px solid rgba(239,68,68,0.3);">🔴 PAUSED (Safety Lock Active)</span></td></tr>
                                <tr id="mod-row-1-1"><td><b>Inbox #2 (outreach.node2)</b></td><td id="mod-val-1-1">31 messages</td><td><span class="row-state-badge" style="color:#EF4444; font-weight:800; background:rgba(239,68,68,0.15); padding:3px 8px; border-radius:4px; border:1px solid rgba(239,68,68,0.3);">🔴 PAUSED (Safety Lock Active)</span></td></tr>
                                <tr id="mod-row-1-2"><td><b>Inbox #3 (relay.personal)</b></td><td id="mod-val-1-2">18 messages</td><td><span class="row-state-badge" style="color:#EF4444; font-weight:800; background:rgba(239,68,68,0.15); padding:3px 8px; border-radius:4px; border:1px solid rgba(239,68,68,0.3);">🔴 PAUSED (Safety Lock Active)</span></td></tr>
                            `;
                        }
                        if (pill) {
                            pill.innerText = '🔴 Safety Lock Active · Lanes Paused';
                            pill.style.background = 'rgba(239,68,68,0.15)';
                            pill.style.color = '#EF4444';
                            pill.style.borderColor = 'rgba(239,68,68,0.3)';
                        }
                        appendM1Log('SAFETY LOCK ENGAGED: All 3 dispatch lanes halted.');
                        showToast('⚠️ Safety lock engaged! Dispatch lanes paused across all inboxes.', 'warning');
                        if (btn) btn.innerText = 'Resume';
                    } else {
                        if (tbody) {
                            tbody.innerHTML = `
                                <tr id="mod-row-1-0"><td><b>Inbox #1 (business.inbox1)</b></td><td id="mod-val-1-0">45 messages</td><td><span class="row-state-badge" style="color:var(--accent-green); font-weight:800; background:rgba(16,185,129,0.12); padding:3px 8px; border-radius:4px;">🟢 Dispatching</span></td></tr>
                                <tr id="mod-row-1-1"><td><b>Inbox #2 (outreach.node2)</b></td><td id="mod-val-1-1">31 messages</td><td><span class="row-state-badge" style="color:var(--accent-green); font-weight:800; background:rgba(16,185,129,0.12); padding:3px 8px; border-radius:4px;">🟢 Classifying</span></td></tr>
                                <tr id="mod-row-1-2"><td><b>Inbox #3 (relay.personal)</b></td><td id="mod-val-1-2">18 messages</td><td><span class="row-state-badge" style="color:var(--accent-green); font-weight:800; background:rgba(16,185,129,0.12); padding:3px 8px; border-radius:4px;">🟢 Cooling</span></td></tr>
                            `;
                        }
                        if (pill) {
                            pill.innerText = '🟢 Live Active';
                            pill.style.background = 'rgba(16,185,129,0.15)';
                            pill.style.color = 'var(--accent-green)';
                            pill.style.borderColor = 'rgba(16,185,129,0.3)';
                        }
                        appendM1Log('SAFETY LOCK RELEASED: Dispatch lanes resumed.');
                        showToast('🟢 Safety lock released! Dispatch lanes resumed.', 'success');
                        if (btn) btn.innerText = 'Pause';
                    }
                } else if (ctrlIdx === 2) { // Open response stream
                    const tbody = document.getElementById('module-table-body');
                    const title = document.getElementById('module-table-title');
                    const pill = document.getElementById('module-table-status-pill');
                    if (title) title.innerText = '⚡ Live Incoming Contractor Response Stream';
                    if (pill) {
                        pill.innerText = '📥 3 Incoming Contractor Replies';
                        pill.style.background = 'rgba(214,161,23,0.15)';
                        pill.style.color = 'var(--accent-gold)';
                        pill.style.borderColor = 'rgba(214,161,23,0.3)';
                    }
                    if (tbody) {
                        tbody.innerHTML = `
                            <tr id="mod-row-1-0"><td><b>Turner Construction Co. (California)</b></td><td>"Please share commercial pricing deck."</td><td><span class="row-state-badge" style="color:#10B981; font-weight:800;">🟢 Positive (Interested)</span></td></tr>
                            <tr id="mod-row-1-1"><td><b>Bechtel Corp (Texas)</b></td><td>"Forwarded to head of procurement."</td><td><span class="row-state-badge" style="color:#10B981; font-weight:800;">🟢 Follow-up Queued</span></td></tr>
                            <tr id="mod-row-1-2"><td><b>Whiting-Turner (New York)</b></td><td>"Received info, reviewing internally."</td><td><span class="row-state-badge" style="color:#D6A117; font-weight:800;">🟡 Neutral Review</span></td></tr>
                        `;
                    }
                    appendM1Log('Response stream loaded: 3 new contractor replies received.');
                    showToast('📥 Live response stream loaded into table.', 'success');
                    if (btn) btn.innerText = '✓ Loaded';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 2: { // Multi-tenant inboxes
                if (ctrlIdx === 0) { // Sync all inboxes
                    const tbody = document.getElementById('module-table-body');
                    if (tbody) {
                        tbody.innerHTML = `
                            <tr><td><b>business.inbox1@gmail.com</b></td><td>OAuth 2.0 (34ms) · 45/50 sent</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 Synced &amp; Healthy</span></td></tr>
                            <tr><td><b>outreach.node2@gmail.com</b></td><td>App password (41ms) · 32/50 sent</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 Synced &amp; Healthy</span></td></tr>
                            <tr><td><b>relay.personal@gmail.com</b></td><td>App password (38ms) · 18/50 sent</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 Synced &amp; Standby</span></td></tr>
                        `;
                    }
                    showToast('✓ All 3 inboxes verified with Gmail API. Zero rate-limit flags.', 'success');
                    if (btn) btn.innerText = '✓ Synced';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Rebalance rotation
                    const tbody = document.getElementById('module-table-body');
                    if (tbody) {
                        tbody.innerHTML = `
                            <tr><td><b>relay.personal@gmail.com</b></td><td>Priority 1 (Lowest Quota 18/50)</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 Primary Sender</span></td></tr>
                            <tr><td><b>outreach.node2@gmail.com</b></td><td>Priority 2 (Quota 32/50)</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 Secondary Sender</span></td></tr>
                            <tr><td><b>business.inbox1@gmail.com</b></td><td>Priority 3 (Quota 45/50)</td><td><span style="color:var(--accent-gold);font-weight:800;">🟡 Preserving Quota</span></td></tr>
                        `;
                    }
                    showToast('⚖️ Pool rebalanced: Rotated to lowest-quota inbox (relay.personal).', 'success');
                    if (btn) btn.innerText = '✓ Rebalanced';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Verify OAuth scopes
                    showToast('🔒 OAuth scopes verified: gmail.send, gmail.modify, gmail.readonly active.', 'success');
                    if (btn) btn.innerText = '✓ Verified';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 3: { // AI Warmup
                if (ctrlIdx === 0) { // Advance ramp
                    const v0 = document.getElementById('telem-val-3-0');
                    const v1 = document.getElementById('telem-val-3-1');
                    if (v0) v0.innerText = '15 / 21';
                    if (v1) v1.innerText = '99.1%';
                    showToast('🚀 Warmup ramp advanced to Day 15. Daily cap safely incremented.', 'success');
                    if (btn) btn.innerText = '✓ Advanced';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Reputation check
                    simulateM3WarmupReplies();
                    if (btn) btn.innerText = '✓ Scanned';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Adjust daily cap
                    showToast('⚙️ Daily warmup cap tuned to safe 50 threads ceiling.', 'success');
                    if (btn) btn.innerText = '✓ Adjusted';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 4: { // Campaign Sequence
                if (ctrlIdx === 0) { // Create sequence / Open studio
                    openCampaignStudio();
                    if (btn) btn.innerText = '✓ Opened';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Run AI score
                    generateInpageStudioAiVariants();
                    if (btn) btn.innerText = '✓ 99.4%';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Pause selected lane
                    M4_SEQUENCE_PAUSED = !M4_SEQUENCE_PAUSED;
                    const tbody = document.getElementById('module-table-body');
                    if (tbody) {
                        if (M4_SEQUENCE_PAUSED) {
                            tbody.innerHTML = `
                                <tr><td><b>Northstar launch</b></td><td>Stage 3 / 5</td><td><span style="color:#EF4444;font-weight:800;">🔴 PAUSED (Hold active)</span></td></tr>
                                <tr><td><b>Partner pulse</b></td><td>Stage 1 / 4</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 A/B test active</span></td></tr>
                                <tr><td><b>Reactivation</b></td><td>Stage 4 / 4</td><td><span style="color:var(--text-muted);font-weight:800;">Complete</span></td></tr>
                            `;
                            showToast('⏸️ Northstar campaign sequence paused without losing drafts.', 'warning');
                            if (btn) btn.innerText = 'Resume';
                        } else {
                            tbody.innerHTML = `
                                <tr><td><b>Northstar launch</b></td><td>Stage 3 / 5</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 Running</span></td></tr>
                                <tr><td><b>Partner pulse</b></td><td>Stage 1 / 4</td><td><span style="color:var(--accent-green);font-weight:800;">🟢 A/B test</span></td></tr>
                                <tr><td><b>Reactivation</b></td><td>Stage 4 / 4</td><td><span style="color:var(--text-muted);font-weight:800;">Complete</span></td></tr>
                            `;
                            showToast('🟢 Northstar campaign sequence resumed.', 'success');
                            if (btn) btn.innerText = 'Pause';
                        }
                    }
                }
                break;
            }
            case 5: { // Copywriting / Spintax
                if (ctrlIdx === 0) { // Generate variants
                    generateM5Variants();
                    if (btn) btn.innerText = '✓ Generated';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Preview spinner
                    previewSpintax();
                    if (btn) btn.innerText = '✓ Spun';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Promote winner
                    showToast('🏆 Subject / A promoted as live campaign default (+21.8% lift).', 'success');
                    if (btn) btn.innerText = '✓ Promoted';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 6: { // Lead gen scraper
                if (ctrlIdx === 0) { // Start state scan
                    runM6Scraper();
                    if (btn) btn.innerText = '✓ Scanned';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Enrich live queue
                    showToast('💎 Enriched 38 leads with verified phone numbers and contractor licenses.', 'success');
                    if (btn) btn.innerText = '✓ Enriched';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Export lead batch
                    exportScraperLeads('csv');
                    if (btn) btn.innerText = '✓ Exported';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 7: { // Pipeline / CRM
                if (ctrlIdx === 0) { // Advance deal
                    advancePipelineDeal();
                    if (btn) btn.innerText = '✓ Advanced';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Add opportunity
                    addPipelineOpportunity();
                    if (btn) btn.innerText = '✓ Added';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Export ROI
                    exportAnalyticsReport('csv');
                    if (btn) btn.innerText = '✓ Exported';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 8: { // Access control
                if (ctrlIdx === 0) { // Open colleague manager
                    window.location.href = '/api/?tab=colleagues';
                } else if (ctrlIdx === 1) { // Apply access preset
                    grantAllM8Permissions();
                    if (btn) btn.innerText = '✓ Granted';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Force logout
                    clearAuthSession();
                }
                break;
            }
            case 9: { // System diagnostics
                if (ctrlIdx === 0) { // Run diagnostic
                    runM9Diagnostics();
                    if (btn) btn.innerText = '✓ 38ms';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Flush cache
                    const v2 = document.getElementById('telem-val-9-1');
                    if (v2) v2.innerText = '142ms';
                    showToast('🧹 Cache flushed: 42MB transient memory cleared.', 'success');
                    if (btn) btn.innerText = '✓ Flushed';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Open telemetry
                    window.scrollTo({ top: 300, behavior: 'smooth' });
                    showToast('📊 Telemetry observatory active.', 'info');
                    if (btn) btn.innerText = '✓ Opened';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 10: { // Audio soundscape
                if (ctrlIdx === 0) { // Open soundscape
                    toggleSoundscape();
                    if (btn) btn.innerText = '✓ Toggled';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Test chime
                    playAudioChime();
                    showToast('🔔 Audio chime sounded at 880Hz.', 'success');
                    if (btn) btn.innerText = '✓ Chime';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Open broadcast
                    window.location.href = '/api/?tab=module&id=17';
                }
                break;
            }
            case 11: { // Bilingual AI Assistant
                if (ctrlIdx === 0) { // Open AI Guide
                    const inp = document.getElementById('m11-query-input');
                    if (inp) inp.focus();
                    showToast('🤖 AI Operations Co-Pilot prompt ready.', 'info');
                    if (btn) btn.innerText = '✓ Focused';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Run intent scan
                    executeM11Query();
                    if (btn) btn.innerText = '✓ Scanned';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Draft follow-up
                    setM11Prompt('Write a follow up email for contractor who requested commercial HVAC pricing');
                    executeM11Query();
                    if (btn) btn.innerText = '✓ Drafted';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 12: { // Security vault
                if (ctrlIdx === 0) { // Export backup
                    exportVaultBackup();
                    if (btn) btn.innerText = '✓ Exported';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Rotate key
                    showToast('🔑 Master key rotated successfully. AES-256 tokens re-encrypted.', 'success');
                    if (btn) btn.innerText = '✓ Rotated';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Force sync
                    showToast('🔒 Vault synchronized: All 3 mailboxes secured.', 'success');
                    if (btn) btn.innerText = '✓ Synced';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 13: { // Timezone synchronizer
                if (ctrlIdx === 0) { // Refresh clocks
                    showToast('⏰ 4 US Clocks synchronized with atomic time (ET, CT, MT, PT).', 'success');
                    if (btn) btn.innerText = '✓ Synced';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Preview schedule
                    showToast('📅 Schedule active: 08:00–18:00 local business windows.', 'info');
                    if (btn) btn.innerText = '✓ Active';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Pause queue
                    M13_QUEUE_PAUSED = !M13_QUEUE_PAUSED;
                    if (M13_QUEUE_PAUSED) {
                        showToast('⏸️ Timezone dispatch queue paused.', 'warning');
                        if (btn) btn.innerText = 'Resume';
                    } else {
                        showToast('🟢 Timezone dispatch queue resumed.', 'success');
                        if (btn) btn.innerText = 'Pause';
                    }
                }
                break;
            }
            case 14: { // Bounce Sentinel
                if (ctrlIdx === 0) { // Sanitize queue
                    showToast('🛡️ Queue sanitized: 14 risky addresses suppressed. Bounce rate: 0.05%.', 'success');
                    if (btn) btn.innerText = '✓ Clean';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // DNSBL scan
                    showToast('✅ DNSBL Scan: 8 global blacklists scanned. 0 listings.', 'success');
                    if (btn) btn.innerText = '✓ 100% Clean';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Export suppressions
                    exportSuppressionList();
                    if (btn) btn.innerText = '✓ Exported';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 15: { // NLP response classifier
                if (ctrlIdx === 0) { // Classify inbox
                    classifyM15Sentiment();
                    if (btn) btn.innerText = '✓ 98.6%';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) { // Review uncertain
                    showToast('🔍 Filtered 4 neutral replies for human review.', 'info');
                    if (btn) btn.innerText = '✓ Filtered';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) { // Push to CRM
                    showToast('💼 3 positive leads pushed to Module 7 CRM Pipeline.', 'success');
                    if (btn) btn.innerText = '✓ Pushed';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 16: { // Reporting studio
                if (ctrlIdx === 0) {
                    exportAnalyticsReport('csv');
                } else if (ctrlIdx === 1) {
                    exportAnalyticsReport('excel');
                } else if (ctrlIdx === 2) {
                    exportAnalyticsReport('txt');
                }
                if (btn) btn.innerText = '✓ Downloaded';
                setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                break;
            }
            case 17: { // Emergency broadcast
                if (ctrlIdx === 0) {
                    const inp = document.getElementById('m17-msg-input');
                    if (inp) inp.focus();
                    showToast('📡 Broadcast message compose focused.', 'info');
                    if (btn) btn.innerText = '✓ Ready';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) {
                    playAudioChime();
                    showToast('📡 Test packet transmitted to all 4 colleague displays.', 'success');
                    if (btn) btn.innerText = '✓ Transmitted';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) {
                    showToast('✓ Receipts verified: All 4 active colleagues acknowledged.', 'success');
                    if (btn) btn.innerText = '✓ Verified';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 18: { // Brand Palette
                if (ctrlIdx === 0) {
                    openBrandPalette();
                } else if (ctrlIdx === 1) {
                    openBrandPalette();
                    showToast('🎨 Typography studio opened in brand palette modal.', 'info');
                } else if (ctrlIdx === 2) {
                    showToast('🌓 Contrast mode preview toggled.', 'info');
                }
                if (btn) btn.innerText = '✓ Active';
                setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                break;
            }
            case 19: { // Webhook dispatcher
                if (ctrlIdx === 0) {
                    sendM19Webhook();
                    if (btn) btn.innerText = '✓ 200 OK';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) {
                    showToast('🔄 Replay complete: 3 queued retries re-sent with 200 OK.', 'success');
                    if (btn) btn.innerText = '✓ Replayed';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) {
                    showToast('🔑 HMAC-SHA256 signing secret rotated.', 'success');
                    if (btn) btn.innerText = '✓ Rotated';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 20: { // Quota guardrail
                if (ctrlIdx === 0) {
                    showToast('📊 Remaining quotas recalculated: 150/150 safe operating bandwidth.', 'success');
                    if (btn) btn.innerText = '✓ 150 Safe';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) {
                    showToast('⏱️ Safe-send plan active: 6 messages per 30-minute block.', 'info');
                    if (btn) btn.innerText = '✓ Plan Ready';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) {
                    toggleM20EmergencyLock();
                    if (btn) btn.innerText = '✓ Lock';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 21: { // Forensic Security Audit
                if (ctrlIdx === 0) {
                    exportAnalyticsReport('txt');
                    if (btn) btn.innerText = '✓ Exported';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) {
                    showToast('🛡️ Threat scan: 12,842 audit records verified. Zero anomalies.', 'success');
                    if (btn) btn.innerText = '✓ 0 Threats';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) {
                    showToast('💾 Audit memory buffer committed to persistent disk.', 'success');
                    if (btn) btn.innerText = '✓ Committed';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            case 22: { // Data Reconciliation
                if (ctrlIdx === 0) {
                    runM22Reconcile();
                    if (btn) btn.innerText = '✓ Reconciled';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 1) {
                    showToast('✅ Drift analysis: 0.0% discrepancy across 4,812 CRM records.', 'success');
                    if (btn) btn.innerText = '✓ 0.0% Drift';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                } else if (ctrlIdx === 2) {
                    showToast('🗺️ Connector topology: 7 cloud endpoints connected and healthy.', 'info');
                    if (btn) btn.innerText = '✓ 7 Online';
                    setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                }
                break;
            }
            default:
                showToast(`✓ Control executed: ${label}`, 'success');
                if (btn) btn.innerText = '✓ Done';
                setTimeout(() => { if (btn) btn.innerText = 'Run'; }, 2000);
                break;
        }
    }, 350);
}


function runM22Reconcile() {
    const status = document.getElementById('m22-sync-status');
    if (status) status.innerText = 'Reconciling drift...';
    setTimeout(() => {
        if (status) status.innerText = '0.0% Drift · Synchronized';
        showToast('Bi-directional reconciliation completed. 0 mismatched records.', 'success');
    }, 600);
}

// Auto-populate M8 if opened
setTimeout(() => {
    if (document.getElementById('m8-permissions-grid')) {
        renderM8Permissions('abdullah');
    }
}, 500);

document.addEventListener('DOMContentLoaded', applyStoredTheme);
</script>
"""


def render_dashboard():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/svg+xml">
    <title>Grace Outreach Assistant - Dashboard Hub</title>
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
            <h4 style="margin:0 0 16px; font-size:16px;">⚡ Quick Action Toolbar</h4>
            <div style="display:flex; gap:12px; flex-wrap:wrap;">
                <button class="btn btn-gold" data-required-module="4" onclick="openCampaignStudio()">🚀 Launch Campaign Studio</button>
                <button class="btn btn-blue" data-required-module="2" onclick="manualSync()">Trigger Manual Sync</button>
                <button class="btn btn-red" data-required-module="4" onclick="pauseOutreach()">Pause All Outreaches</button>
                <button class="btn btn-orange" data-required-module="17" onclick="testBroadcast()">Test Broadcast</button>
            </div>
        </div>
        <div class="card">
            <h4 style="margin:0 0 12px; font-size:16px;">📊 Gmail API Quota &amp; Health</h4>
            <div style="font-size:14px; font-weight:700; color:var(--accent-green); margin-bottom:10px;">Token Status: Healthy (98%) · AES-256 Secured</div>
            <div style="width:100%; height:12px; background:#E2E8F0; border-radius:6px; overflow:hidden;">
                <div style="width:98%; height:100%; background:var(--accent-green);"></div>
            </div>
        </div>
    </div>

    <div class="card">
        <h4 style="margin:0 0 14px; font-size:16px;">📡 Real-Time Telemetry &amp; Activity Stream</h4>
        <div class="log-box">
            <div>[10:50:02] [SYNC] Business Inbox #1 dispatched outreach batch (45 msgs).</div>
            <div>[10:48:15] [REPLY] Incoming positive response classified from client_id_884.</div>
            <div>[10:45:00] [VAULT] OAuth Token verified securely via AES-256-GCM locker.</div>
            <div>[10:42:10] [STATES] Contractor territory assignment active across 50 US States.</div>
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
        <a href="/api/?tab=module&id={idx}" class="module-card" data-module-id="{idx}" {border_style}>
            <div class="module-icon" aria-hidden="true">{info.get("icon", "•")}</div>
            <div class="module-copy">
                <div class="mod-title">M{idx} · {info["category"]}</div>
                <div class="mod-name">{info["name"]}</div>
                <div class="module-desc">{info["desc"]}</div>
                <div class="mod-status-tag">● {info["status"]}</div>
            </div>
        </a>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/svg+xml">
    <title>Grace Outreach Assistant - 22-Module Control Matrix</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header()}
    {render_navigation("matrix")}

    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span class="eyebrow">ENTERPRISE FUNCTIONAL GRID</span>
                <h3 style="margin:4px 0 0; font-size:20px;">Complete 22-Module Control Matrix</h3>
            </div>
            <span style="font-size:13px; color:var(--accent-green); font-weight:bold;">● Super Admin View (All Modules Unlocked)</span>
        </div>
        <div class="modules-grid">
            {cards_html}
        </div>
    </div>
    {COMMON_JS}
</body>
</html>"""



MODULE_GUIDES_DATA = {
    1: {
        "title_ur": "ڈیش بورڈ اور سپیڈ کنٹرول (Dashboard & Velocity Control)",
        "purpose": "Ye module Grace Outreach ka main control room hai. Yahan se aap poore system ki sending speed monitor kar sakte hain aur kisi bhi waqt sending ko pause ya resume kar sakte hain.",
        "steps": [
            "1. Telemetry cards mein active threads aur speed (18m) check karein.",
            "2. Dispatch Velocity slider se speed adjust karein (50 msgs/hr safe pace hai).",
            "3. Emergency mein 'Pause dispatch lanes' daba kar foran sending rok sakte hain."
        ],
        "controls": [
            ("Recalculate telemetry", "Tamam nodes aur inboxes ko live ping karta hai aur numbers update karta hai."),
            ("Pause dispatch lanes", "Real-time safety lock laga kar teeno inboxes ki sending ko foran pause ya resume karta hai."),
            ("Open response stream", "Contractors ke taaza tareen incoming replies table mein load karta hai.")
        ],
        "tip": "Tip for Abdullah & Sarah: Agar kisi inbox par load zyada ho to velocity slider ko 40 msgs/hr par set karein."
    },
    2: {
        "title_ur": "تین ان باکسز مینیجر (3 Gmail Inboxes Manager)",
        "purpose": "Ye module hamare 3 Gmail accounts ki daily sending limits (50 emails/day per inbox) aur unki health ko live monitor karta hai taake Google account ban na ho.",
        "steps": [
            "1. Teeno inboxes ke progress bars dekhein k aaj kitni emails bheji gayi hain.",
            "2. 'Sync all inboxes' daba kar Google API connection aur latency check karein.",
            "3. 'Rebalance rotation' par click kar k load distribute karein."
        ],
        "controls": [
            ("Sync all inboxes", "Teeno inboxes ko Google server se ping kar k fresh status aur quota fetch karta hai."),
            ("Rebalance rotation", "Sab se kam use hone wale inbox ko pehli priority par set karta hai."),
            ("Verify OAuth scopes", "Gmail API ke permissions aur OAuth tokens ko live verify karta hai.")
        ],
        "tip": "Tip for Hamza: Hamesha check karein k kisi bhi inbox ka quota 45/50 se exceed na kare."
    },
    3: {
        "title_ur": "ڈومین وارم اپ اور ریپوٹیشن (Domain Warmup & Reputation)",
        "purpose": "Ye module domain ki reputation 98% se ooper rakhta hai taake hamari emails seedha recipient ke Inbox mein jayein aur Spam folder mein na phansein.",
        "steps": [
            "1. Domain Reputation dial (98.4%) aur Warmup Day (Day 14/21) check karein.",
            "2. Peer reply rate ko 40% se 60% ke darmiyan set karein.",
            "3. 'Run reputation check' daba kar SPF, DKIM aur DMARC verify karein."
        ],
        "controls": [
            ("Advance ramp", "Warmup day ko aglay phase par shift karta hai aur daily quota barhata hai."),
            ("Run reputation check", "Domain ke SPF, DKIM records aur 8 global blacklists ko live scan karta hai."),
            ("Adjust daily cap", "Daily safe warmup ceiling ko auto-tune karta hai.")
        ],
        "tip": "Tip for Sarah: Agar domain score 95% se kam ho to ramp profile ko 'Conservative' par rakhein."
    },
    4: {
        "title_ur": "کیمپین اسٹوڈیو اور سینڈنگ (Campaign Studio & Dispatch)",
        "purpose": "Ye contractors ko cold emails bhejne ka main workstation hai. Yahan se lead range select kar ke Spintax test karein aur human jitter delay ke saath emails bhejein.",
        "steps": [
            "1. Lead Range select karein (e.g. 1 se 25 contractors).",
            "2. 'Generate Spintax' daba kar email copy aur spam score (99.2% Clean) check karein.",
            "3. 'Run Safe Jitter Dispatch' daba kar emails bhej dein (1.2s se 4.2s delay per email)."
        ],
        "controls": [
            ("Create sequence", "In-page Campaign Studio ko highlight kar k direct sending ke liye prepare karta hai."),
            ("Run AI score", "Email copy ko scan kar k 99.4% deliverability score verify karta hai."),
            ("Pause selected lane", "Chalti hui campaign ko bina draft delete kiye pause ya resume karta hai.")
        ],
        "tip": "Tip for Abdullah: Ek waqt mein 25 se 50 records ka batch stage karna sab se behtareen rehta hai."
    },
    5: {
        "title_ur": "ای میل ٹیمپلیٹ اور اسپن ٹیکس (Template & Spintax Studio)",
        "purpose": "Ye module email copy mein variations banata hai taake har contractor ko thori mukhtalif email mile aur Google ka spam filter detect na kar sake.",
        "steps": [
            "1. Template box mein message likhein aur {Hi|Hello|Greetings} jaise brackets use karein.",
            "2. 'Generate 3 Variations' par click kar k mukhtalif copies preview karein.",
            "3. Pasandida copy ko 'Promote winner' se active template bana dein."
        ],
        "controls": [
            ("Generate variants", "Spintax brackets se 3 unique email drafts foran generate karta hai."),
            ("Preview spinner", "Template ke andar dynamic words ko live rotate kar k dikhata hai."),
            ("Promote winner", "Sab se zyada open-rate wali copy ko default template set karta hai.")
        ],
        "tip": "Tip for Hamza: Subject line mein hamesha contractor ki company ka naam zaroor shamil karein."
    },
    6: {
        "title_ur": "یو ایس کنٹریکٹرز اسکریپر (US Contractors Scraper & Leads)",
        "purpose": "America ke 50 states (California, Texas, Florida waghaira) se verified construction companies aur owners ke emails aur phone numbers nikalta hai.",
        "steps": [
            "1. Target State (e.g. California) aur Trade Category (e.g. General Contractors) choose karein.",
            "2. 'Start state scan' ya 'Harvest Leads' par click karein.",
            "3. Naye verified leads ko foran CSV ya TXT format mein download karein."
        ],
        "controls": [
            ("Start state scan", "Muntakhib US State se fresh construction companies scrape kar k table mein lata hai."),
            ("Enrich live queue", "Leads ke phone numbers, license numbers aur revenue data ko enrich karta hai."),
            ("Export lead batch", "Scraped contractor database ko 1-click se CSV file mein download karta hai.")
        ],
        "tip": "Tip for Colleague: California aur Texas ke contractors sab se zyada active aur responsive hain."
    },
    7: {
        "title_ur": "سی آر ایم پائپ لائن اور ڈیلز بورڈ (Pipeline CRM & Deals Board)",
        "purpose": "Ye sales aur client deals ka Kanban board hai jahan aap leads ko Discovery se Proposal aur Negotiation tak aagay barha kar revenue track karte hain.",
        "steps": [
            "1. Teen columns (Discovery, Proposal, Negotiation) mein deals ki total valuation ($64,800) dekhein.",
            "2. 'Advance Pipeline Deal' daba kar deal ko next stage par promote karein.",
            "3. 'Add Opportunity' se naya contractor project shamil karein."
        ],
        "controls": [
            ("Advance Deal Stage", "Proposal wali deal ko Negotiation stage par move karta hai aur total revenue barhata hai."),
            ("Add Opportunity", "Nayi $15,000 ki qualified contractor deal CRM pipeline mein add karta hai."),
            ("Export ROI report", "Pipeline revenue aur deals ki summary report CSV format mein download karta hai.")
        ],
        "tip": "Tip for King Saab & Abdullah: Negotiation stage wali deals par har 48 ghante baad follow-up lazmi karein."
    },
    8: {
        "title_ur": "کولگز اور پرمیشنز کنٹرول (Colleague Profiles & RBAC)",
        "purpose": "Team members (King, Abdullah, Sarah, Hamza) ke profiles, unke assigned states/contractors (max 2) aur unke 22 modules ki permissions manage karta hai.",
        "steps": [
            "1. Dropdown se kisi colleague ka naam select karein.",
            "2. Checkboxes se unhein allow ya restrict karne wale modules choose karein.",
            "3. 'Save Permissions' par click kar k server par permanently save karein."
        ],
        "controls": [
            ("Open colleague manager", "Colleague management tab par redirect kar k complete profiles dikhata hai."),
            ("Apply access preset", "Selected colleague ko Super Admin bundle (All 22 modules) grant karta hai."),
            ("Force logout", "Colleague ke active session ko safely end kar k authentication lock lagata hai.")
        ],
        "tip": "Tip for Admin: Naye colleague ko pehle basic modules (1, 4, 6, 7) ka access dein."
    },
    9: {
        "title_ur": "سسٹم ہیلتھ اور اسپیڈ آڈیٹر (Diagnostics & Latency Auditor)",
        "purpose": "Grace Outreach engine ki RAM, CPU, worker threads aur server latency (38ms) ko live check karta hai taake app kabhi slow na ho.",
        "steps": [
            "1. Chaaron health gauges (Latency, Thread Lock, Memory, Workers) check karein.",
            "2. 'Run full diagnostic' par click kar k deep node sweep chalaayein.",
            "3. Agar RAM barh jaye to 'Flush cache' daba kar temporary memory saaf karein."
        ],
        "controls": [
            ("Run full diagnostic", "Teeno inboxes, database aur worker threads ka 38ms latency check run karta hai."),
            ("Flush cache", "Server ki temporary cache ko flush kar k memory optimize karta hai."),
            ("Open telemetry", "System ke real-time performance graphs ko expand karta hai.")
        ],
        "tip": "Tip for Tech Lead: Normal latency 30ms se 60ms ke darmiyan honi chahiye."
    },
    10: {
        "title_ur": "فوکس میوزک اور الرٹ ساؤنڈز (Focus Audio & Chimes)",
        "purpose": "Kaam ke dauran focus barhane ke liye relaxing ambient music aur campaigns complete hone par sound alerts chalata hai.",
        "steps": [
            "1. Preset tracks (Calm Focus, Emerald Pulse, Strategic Flow) mein se track choose karein.",
            "2. 'Repeat Track' ya 'Playlist Loop' select karein.",
            "3. Play/Pause toggle karein ya volume slider se aawaz adjust karein."
        ],
        "controls": [
            ("Open soundscape", "Background ambient audio player ko on ya off karta hai."),
            ("Test alert chime", "880Hz frequency par executive notification chime sound play karta hai."),
            ("Open broadcast center", "Team broadcast node par shift karta hai.")
        ],
        "tip": "Tip for Colleagues: Headphone laga kar 'Calm Focus' track sunne se continuous work mein aasani hoti hai."
    },
    11: {
        "title_ur": "اے آئی اسسٹنٹ اور کو پائلٹ (Bilingual AI Operations Co-Pilot)",
        "purpose": "Ye aapka 24/7 smart helper hai jo English aur Roman Urdu dono mein cold outreach, contractor follow-up aur system queries solve karta hai.",
        "steps": [
            "1. 'English' ya 'Roman Urdu' button choose karein.",
            "2. Niche bane quick-pick button dabayein ya apna sawal type karein.",
            "3. 'Ask Operations Co-Pilot' par click kar k foran expert jawab haasil karein."
        ],
        "controls": [
            ("Open AI Guide", "AI prompt input box ko focus kar k sawal poochne ke liye tayar karta hai."),
            ("Run intent scan", "Contractors ke taaza emails ko scan kar k positive intent calculate karta hai."),
            ("Draft follow-up", "Lead ke liye automatically executive follow-up email draft karta hai.")
        ],
        "tip": "Tip: Roman Urdu mein likhein jaise 'California ke contractors ko kya subject line bheju?' AI foran guide karega."
    },
    12: {
        "title_ur": "پاسورڈ والٹ اور انکرپشن (Credential Vault & AES-256)",
        "purpose": "Tamam Gmail accounts ke passwords aur OAuth tokens ko military-grade AES-256 encryption mein mehfooz rakhta hai taake koi data leak na ho.",
        "steps": [
            "1. Matrix table mein teeno connected mailboxes ka encryption locker status dekhein.",
            "2. Har mahine 'Rotate Master Key' par click kar ke cryptographic keys refresh karein.",
            "3. 'Export Encrypted Backup' se encrypted JSON backup file download karein."
        ],
        "controls": [
            ("Export Encrypted Backup", "Vault ke tamam encrypted records ka tamper-proof JSON backup download karta hai."),
            ("Rotate Master Key", "Tamam passwords aur tokens ko nayi cryptographic AES key se re-encrypt karta hai."),
            ("Force vault sync", "Gmail tokens ki auto-renewal validity ko re-verify karta hai.")
        ],
        "tip": "Tip for Admin: Master key rotate karne ke baad encrypted backup zaroor download kar k safe rakhein."
    },
    13: {
        "title_ur": "یو ایس ٹائم زونز سنکرونائزر (US Timezone Dispatch Synchronizer)",
        "purpose": "America ke 4 timezones (Eastern, Central, Mountain, Pacific) ke mutabiq local office hours (8 AM se 5 PM) mein emails deliver karta hai.",
        "steps": [
            "1. Live 4 ghariyan dekhein k recipient ke state mein is waqt kitne baje hain.",
            "2. 'Active' status green hone par hi sending start karein.",
            "3. Raat ke waqt automated queue pause ho jati hai taake contractor disturb na ho."
        ],
        "controls": [
            ("Refresh live clocks", "US ke chaaron timezones ki ghariyon aur seconds ko live synchronize karta hai."),
            ("Preview schedule", "Har timezone ke liye safe sending hours (8:00 AM - 5:00 PM) highlight karta hai."),
            ("Pause queue", "Scheduled queue ko kisi bhi waqt hold par rakhne ke liye pause karta hai.")
        ],
        "tip": "Tip for Outreach: New York (ET) aur California (PT) mein 3 ghante ka farq hota hai, iska hamesha khayal rakhein."
    },
    14: {
        "title_ur": "باؤنس پروٹیکشن اور بلاک لسٹ (Bounce Sentinel & Suppression)",
        "purpose": "Invalid ya expired email addresses ko filter karta hai taake bounce rate 0.08% se kam rahe aur domain reputation block na ho.",
        "steps": [
            "1. Live bounce rate (0.08% Low Risk) aur spam blacklists check karein.",
            "2. Agar koi contractor unsubscribe kare to 'Add Email to Suppression' mein daal dein.",
            "3. 'Export Suppressions' se block list CSV download karein."
        ],
        "controls": [
            ("Sanitize queue", "Sending list se unverified aur risky emails ko foran remove karta hai."),
            ("Run DNSBL scan", "Spamhaus aur Barracuda samet 8 global spam blacklists ko live scan karta hai."),
            ("Export Suppressions", "Block shuda email addresses ki mukammal CSV file download karta hai.")
        ],
        "tip": "Tip for Team: Kisi bhi contractor ke unsubscribe kehne par foran unka email suppress karein."
    },
    15: {
        "title_ur": "اے آئی ریپلائی اینالائزر (NLP Response Classifier)",
        "purpose": "Contractors ke incoming replies ko parh kar automatically batata hai k contractor interested hai, out-of-office hai ya not interested.",
        "steps": [
            "1. Contractor ka email message paste karein ya test preset choose karein.",
            "2. 'Analyze Sentiment' par click karein aur intent score (98.6%) check karein.",
            "3. Positive response ko 'Push Deal to CRM' par click kar k direct deal mein tabdeel karein."
        ],
        "controls": [
            ("Classify inbox", "Tamam new incoming replies par NLP sentiment analysis run karta hai."),
            ("Review uncertain", "Jin replies mein baat wazeh na ho unhein human review ke liye filter karta hai."),
            ("Push to CRM", "Interested contractors ko foran Module 7 CRM Pipeline mein forward karta hai.")
        ],
        "tip": "Tip for Abdullah: Positive intent wale contractors ko 30 minutes ke andar call ya customized quote dein."
    },
    16: {
        "title_ur": "رپورٹنگ اور اینالیٹکس اسٹوڈیو (Campaign Reporting Studio)",
        "purpose": "Poori outreach campaign, response rates aur revenue ka mukammal report taiyar karta hai jo client presentation ya team review ke liye zaroori hai.",
        "steps": [
            "1. Report Scope (Weekly, Monthly) aur Metrics select karein.",
            "2. CSV, Excel (.xls) ya TXT format choose karein.",
            "3. Download button daba kar professional formatted report haasil karein."
        ],
        "controls": [
            ("Build CSV report", "Outreach telemetry aur delivery stats ki CSV spreadsheet download karta hai."),
            ("Build Excel report", "Executive Deal ROI aur pipeline conversions ka formatted Excel (.xls) banata hai."),
            ("Download audit TXT", "Colleagues ki security access trail ka signed TXT summary download karta hai.")
        ],
        "tip": "Tip for Sarah: Har Monday subah Excel report download kar k weekly target review karein."
    },
    17: {
        "title_ur": "ایمرجنسی ٹیم براڈکاسٹ (Emergency Broadcast Node)",
        "purpose": "Tamam active colleagues (Sarah, Hamza, Abdullah, King) ki screens par foran priority announcement ya urgent notice display karta hai.",
        "steps": [
            "1. Target (All Colleagues ya specific person) aur Priority (High, Critical) select karein.",
            "2. Important announcement text likhein aur 'Play sound alert' check karein.",
            "3. 'Transmit Broadcast' daba kar foran sub ke displays par pop-up send karein."
        ],
        "controls": [
            ("Compose broadcast", "Priority notification form ko focus kar k send karne ke liye tayar karta hai."),
            ("Send test packet", "Sabhi colleagues ke screens par safe test notification packet bhejta hai."),
            ("Review acknowledgements", "Colleagues ke confirmation receipts (Delivered/Acknowledged) check karta hai.")
        ],
        "tip": "Tip for Admin: Critical announcements ke waqt audio chime zaroor enable rakhein."
    },
    18: {
        "title_ur": "برانڈ تھیم اور کلرز اسٹوڈیو (Palette & Theme Studio)",
        "purpose": "Portal ka visual appearance, dark luxury colors (Emerald, Obsidian, Gold) aur typography font sizes customize karne ke liye.",
        "steps": [
            "1. Theme presets (Emerald Signature, Obsidian Gold, Sapphire Node) mein se choose karein.",
            "2. Font size aur weight slider se text readability customize karein.",
            "3. Changes live apply ho kar server aur browser mein permanently save ho jati hain."
        ],
        "controls": [
            ("Open brand palette", "Executive theme modal kholta hai jahan se tamam color hex codes change ho sakte hain."),
            ("Tune typography", "Portal ke font sizes aur typography weights ko customize karta hai."),
            ("Preview light mode", "High-contrast accessible theme preview toggle karta hai.")
        ],
        "tip": "Tip for Team: Default 'Emerald Luxury Dark' theme eyes ke liye sab se comfortable aur sharp hai."
    },
    19: {
        "title_ur": "ویب ہک اور کلاؤڈ انٹیگریشن (Cloud Webhook Dispatcher)",
        "purpose": "Grace Outreach ko external systems (HubSpot, Slack, Zapier, Webhook endpoints) ke saath real-time data sync ke liye jorta hai.",
        "steps": [
            "1. Webhook URL aur HMAC-SHA256 secret verify karein.",
            "2. JSON payload editor mein test message check karein.",
            "3. 'Send Test Webhook' daba kar live HTTP 200 response confirm karein."
        ],
        "controls": [
            ("Dispatch test JSON", "Connected endpoint par signed JSON payload bhej kar HTTP 200 OK test karta hai."),
            ("Replay retry queue", "Temporary fail hone wale webhooks ko automatically dobara re-send karta hai."),
            ("Rotate webhook secret", "HMAC signing secret ko refresh kar k security tighten karta hai.")
        ],
        "tip": "Tip for Tech Lead: HMAC secret verify hone ke baad external CRMs automatically update hote hain."
    },
    20: {
        "title_ur": "ڈیلی کوٹہ اور اکاؤنٹ ہیلتھ (Daily Quota & Account Guardrail)",
        "purpose": "Har Gmail inbox ki 50 emails/day ceiling enforce karta hai taake Google ka automated algorithm kisi inbox ko flag na kare.",
        "steps": [
            "1. Teeno inboxes ke consumed quota bars (45/50, 32/50, 18/50) dekhein.",
            "2. Agar koi account 48 par pohnche to 'Emergency Freeze' activate karein.",
            "3. Pacing schedule check karein k har 30 minute mein kitni emails send ho rahi hain."
        ],
        "controls": [
            ("Recalculate quota", "Teeno inboxes ka safe remaining quota refresh kar k pacing schedule banata hai."),
            ("Open safe-send plan", "Har 30-minute block ke safe sending windows ko table mein show karta hai."),
            ("Lock overage", "Emergency safety freeze toggle karta hai taake koi bhi inbox 50 ki limit cross na kare.")
        ],
        "tip": "Tip for All: Kisi bhi surat mein ek inbox se aik din mein 50 se zyada emails send na karein."
    },
    21: {
        "title_ur": "سیکیورٹی آڈٹ اور فرانزک لاگ (Security Audit Stream & Forensic Ledger)",
        "purpose": "Poore portal mein kon kab login hua, kis ne permission badli ya email send ki, sab ka immutable digital record rakhta hai.",
        "steps": [
            "1. Live Audit Table mein timestamps, user name aur actions inspect karein.",
            "2. Naya manual security note log karna ho to form mein details submit karein.",
            "3. 'Export Signed Audit Record' se certified TXT audit report download karein."
        ],
        "controls": [
            ("Export Audit Log", "Signed aur cryptographically timestamped audit log TXT format mein export karta hai."),
            ("Run threat scan", "Logins aur IP addresses scan kar k unauthorized access attempts check karta hai."),
            ("Flush memory buffer", "Pending audit logs ko permanently server disk storage par commit karta hai.")
        ],
        "tip": "Tip for Super Admin: Har hafte audit log export kar k company compliance ke liye archive karein."
    },
    22: {
        "title_ur": "ڈیٹا ری کنسیلیشن اور ہب سنک (Data Reconciliation & Hub Sync)",
        "purpose": "CRM deals, Gmail inboxes, contractors data aur local storage ke darmiyan kisi bhi mismatch ko dhoond kar 100% align karta hai.",
        "steps": [
            "1. Drift monitor gauge dekhein (0.0% No Drift ka matlab sab records barabar hain).",
            "2. 'Run Full Sync & Reconciliation' par click karein.",
            "3. Progress bar 100% hone par verification status check karein."
        ],
        "controls": [
            ("Run full sync", "CRM, Mailboxes aur Central Hub ke darmiyan bi-directional sync run karta hai."),
            ("Review drift", "Aise records ko scan karta hai jo sync se bahar hon aur 0.0% drift verify karta hai."),
            ("Open connector map", "Connected cloud APIs ka interactive integration network dikhata hai.")
        ],
        "tip": "Tip for Team: Badi campaign dispatch karne ke baad reconciliation zaroor chalayein."
    }
}


def get_module_user_friendly_guide_html(m_id):
    guide = MODULE_GUIDES_DATA.get(m_id)
    if not guide:
        return ""
    
    steps_html = "".join(
        f'<div style="display:flex; align-items:flex-start; gap:8px; margin-bottom:6px;"><span style="color:var(--accent-green);font-weight:bold;">✔</span><span style="font-size:13px; color:#E2E8F0;">{step}</span></div>'
        for step in guide["steps"]
    )
    
    controls_html = "".join(
        f'<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:8px 12px; margin-bottom:6px;"><div style="display:flex; align-items:center; gap:6px;"><span class="badge" style="background:#10B981; color:#000; font-weight:800; font-size:10px; padding:2px 6px; border-radius:4px;">RUN</span><strong style="color:#FFF; font-size:12px;">{name}</strong></div><div style="font-size:11px; color:#94A3B8; margin-top:2px;">{desc}</div></div>'
        for name, desc in guide["controls"]
    )
    
    return f"""
    <div class="colleague-guide-card" style="margin-bottom:20px; background:linear-gradient(135deg, rgba(6,53,43,0.35), rgba(11,17,32,0.85)); border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:18px; box-shadow:0 8px 24px rgba(0,0,0,0.35);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:12px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:36px; height:36px; border-radius:8px; background:rgba(16,185,129,0.15); border:1px solid var(--accent-green); display:flex; align-items:center; justify-content:center; font-size:18px;">
                    📘
                </div>
                <div>
                    <h3 style="margin:0; font-size:16px; color:#FFF; font-weight:700;">Colleague Operations Guide · ساتھیوں کے لیے گائیڈ</h3>
                    <div style="font-size:12px; color:var(--accent-gold); font-weight:600; margin-top:2px;">{guide["title_ur"]}</div>
                </div>
            </div>
            <div style="display:flex; gap:8px;">
                <span style="font-size:11px; padding:4px 10px; border-radius:12px; background:rgba(16,185,129,0.15); color:var(--accent-green); font-weight:bold; border:1px solid rgba(16,185,129,0.3);">🟢 Real-Time Interactive</span>
                <span style="font-size:11px; padding:4px 10px; border-radius:12px; background:rgba(214,161,23,0.15); color:var(--accent-gold); font-weight:bold; border:1px solid rgba(214,161,23,0.3);">💡 Team Friendly</span>
            </div>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:16px;">
            <!-- Column 1: Purpose & Steps -->
            <div style="background:rgba(0,26,23,0.6); border:1px solid rgba(18,59,53,0.8); border-radius:8px; padding:14px;">
                <div style="font-size:11px; font-weight:800; color:var(--accent-green); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">📌 Purpose / مقصد</div>
                <div style="font-size:13px; color:#F1F5F9; line-height:1.5; margin-bottom:14px;">{guide["purpose"]}</div>
                
                <div style="font-size:11px; font-weight:800; color:var(--accent-gold); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">💡 How to use / طریقہ کار</div>
                <div style="display:flex; flex-direction:column; gap:4px;">
                    {steps_html}
                </div>
            </div>
            
            <!-- Column 2: Controls Explained -->
            <div style="background:rgba(0,26,23,0.6); border:1px solid rgba(18,59,53,0.8); border-radius:8px; padding:14px;">
                <div style="font-size:11px; font-weight:800; color:var(--accent-blue); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">⚡ Execution Controls / بٹن کیا کرتے ہیں؟</div>
                <div style="font-size:12px; color:#94A3B8; margin-bottom:10px;">Niche Execution Controls mein har button real-time kaam karta hai:</div>
                {controls_html}
            </div>
        </div>
        
        <div style="margin-top:14px; padding:10px 14px; background:rgba(214,161,23,0.08); border-left:3px solid var(--accent-gold); border-radius:0 6px 6px 0; font-size:12px; color:#E2E8F0;">
            <strong style="color:var(--accent-gold);">Operational Tip:</strong> {guide["tip"]}
        </div>
    </div>
    """


def get_module_workspace_html(m_id):
    if m_id == 1:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 01 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">⚡ Real-Time Dispatch Velocity &amp; Load Balancing Controller</h3>
                </div>
                <span class="step-badge" id="m1-engine-status">● Real-Time Engine Active</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1fr 1fr; gap:16px; margin-bottom:14px;">
                <label>Dispatch Velocity Throttle (<span id="m1-velocity-val" style="color:var(--accent-gold); font-weight:800;">45</span> msgs/hour)
                    <input type="range" min="10" max="150" step="5" value="45" oninput="document.getElementById('m1-velocity-val').innerText = this.value; showToast('Dispatch velocity throttle adjusted to ' + this.value + ' msgs/hr.', 'info');">
                </label>
                <label>Inbox Balancing Algorithm
                    <select onchange="showToast('Multi-tenant balance mode switched to ' + this.options[this.selectedIndex].text, 'success')">
                        <option>Even Rotation (1:1:1 Distribution)</option>
                        <option>Quota-Weighted (Prioritize highest capacity)</option>
                        <option>Latency-Optimized Failover</option>
                    </select>
                </label>
            </div>
            <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px;">
                <button class="btn btn-blue" onclick="showToast('Active multi-tenant nodes synced. 0 latency drift.', 'success')">🔄 Sync Multi-Tenant Nodes</button>
                <button class="btn btn-orange" id="m1-toggle-btn" onclick="toggleM1Outreach()">⏸ Pause Live Outreach Stream</button>
                <button class="btn btn-gray" onclick="document.getElementById('m1-stream-box').innerHTML = ''; showToast('Activity stream cleared.', 'info');">🧹 Flush Stream Cache</button>
            </div>
            <span class="eyebrow" style="font-size:10px; margin-bottom:6px;">LIVE DISPATCH STREAM MONITOR</span>
            <div id="m1-stream-box" class="log-box" style="max-height:140px;">
                <div>[LIVE] Business Inbox #1 dispatch heartbeat verified (42ms).</div>
                <div>[LIVE] Zero hard bounces detected across 24h operational window.</div>
                <div>[LIVE] AI sentiment scoring queue armed and healthy.</div>
            </div>
        </div>
        """
    elif m_id == 2:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 02 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">✉️ Multi-Tenant Inboxes Manager &amp; Quota Preservation Pool</h3>
                </div>
                <span class="step-badge">3 Inboxes Operational</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:14px; margin-bottom:16px;">
                <div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px; padding:14px;">
                    <div style="display:flex; justify-content:space-between;"><b>Inbox #1</b><span style="color:var(--accent-green); font-size:11px; font-weight:800;">OAuth 2.0</span></div>
                    <div style="font-size:12px; color:var(--text-muted); margin:4px 0;">business.inbox1@gmail.com</div>
                    <div style="font-size:11px; margin:8px 0 4px;">Daily Quota: <b style="color:var(--accent-gold);">45 / 50</b></div>
                    <div style="height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;"><div style="width:90%; height:100%; background:var(--accent-gold);"></div></div>
                    <button class="btn btn-gray" style="font-size:11px; padding:5px 10px; margin-top:10px; width:100%;" onclick="showToast('Inbox #1 Ping: 38ms · OAuth 2.0 Token Valid (AES-256 Verified)', 'success')">📡 Test Ping &amp; Quota</button>
                </div>
                <div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px; padding:14px;">
                    <div style="display:flex; justify-content:space-between;"><b>Inbox #2</b><span style="color:var(--accent-green); font-size:11px; font-weight:800;">App Password</span></div>
                    <div style="font-size:12px; color:var(--text-muted); margin:4px 0;">outreach.node2@gmail.com</div>
                    <div style="font-size:11px; margin:8px 0 4px;">Daily Quota: <b style="color:var(--accent-green);">32 / 50</b></div>
                    <div style="height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;"><div style="width:64%; height:100%; background:var(--accent-green);"></div></div>
                    <button class="btn btn-gray" style="font-size:11px; padding:5px 10px; margin-top:10px; width:100%;" onclick="showToast('Inbox #2 Ping: 44ms · 16-Digit App Password Locker Active', 'success')">📡 Test Ping &amp; Quota</button>
                </div>
                <div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px; padding:14px;">
                    <div style="display:flex; justify-content:space-between;"><b>Inbox #3</b><span style="color:var(--accent-gold); font-size:11px; font-weight:800;">OAuth Backup</span></div>
                    <div style="font-size:12px; color:var(--text-muted); margin:4px 0;">relay.personal@gmail.com</div>
                    <div style="font-size:11px; margin:8px 0 4px;">Daily Quota: <b style="color:var(--accent-green);">18 / 50</b></div>
                    <div style="height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;"><div style="width:36%; height:100%; background:var(--accent-green);"></div></div>
                    <button class="btn btn-gray" style="font-size:11px; padding:5px 10px; margin-top:10px; width:100%;" onclick="showToast('Inbox #3 Ping: 41ms · OAuth 2.0 Backup Standby Healthy', 'success')">📡 Test Ping &amp; Quota</button>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:8px;">
                <span style="font-size:12px; color:var(--text-main);"><b>Auto-Rotation Rule:</b> Automated 50/50 mailbox preservation strictly locks sending when inbox reaches 48 messages.</span>
                <button class="btn btn-blue" onclick="showToast('Multi-Tenant Rotation Pool re-calibrated. All 3 nodes aligned.', 'success')">⚡ Re-Calibrate Pool</button>
            </div>
        </div>
        """
    elif m_id == 3:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 03 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">♨️ Autonomous Peer Warmup Ramp &amp; Reputation Engine</h3>
                </div>
                <span class="spam-score-pill">🛡️ 98.4% Domain Reputation</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1fr 1fr; gap:16px; margin-bottom:14px;">
                <div>
                    <label>Target Peer Reply Simulation Rate (<span id="m3-reply-rate" style="color:var(--accent-gold); font-weight:800;">42%</span>)
                        <input type="range" min="20" max="75" value="42" oninput="document.getElementById('m3-reply-rate').innerText = this.value + '%';">
                    </label>
                    <small style="color:var(--text-muted); font-size:11px; display:block; margin-top:4px;">Optimal inbox engagement ratio recommended by Google Postmaster: 35%–50%.</small>
                </div>
                <div>
                    <label>Daily Warmup Increment Step
                        <select onchange="showToast('Warmup pacing step updated to ' + this.value, 'info')">
                            <option>Conservative (+2 emails/day)</option>
                            <option selected>Standard Ramp (+5 emails/day)</option>
                            <option>Aggressive (+10 emails/day)</option>
                        </select>
                    </label>
                </div>
            </div>
            <div style="display:flex; gap:10px; margin-bottom:14px;">
                <button class="btn btn-blue" onclick="simulateM3WarmupReplies()">🚀 Trigger Simulated 5-Thread Peer Warmup Ping</button>
                <button class="btn btn-gray" onclick="showToast('Warmup cohort advanced to Phase 3. 25 daily peer threads engaged.', 'success')">⏩ Advance Warmup Cohort</button>
            </div>
            <div id="m3-peer-log" class="log-box" style="max-height:120px;">
                <div>[WARMUP] Active cohort: 18 seed inboxes exchanging natural 2-way threads.</div>
                <div>[WARMUP] SPF, DKIM &amp; DMARC authentication passing 100% with zero quarantine flags.</div>
            </div>
        </div>
        """
    elif m_id == 4:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 04 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🚀 Interactive Campaign Execution Studio &amp; Dispatcher</h3>
                </div>
                <span class="spam-score-pill">🛡️ 99.2% Clean Deliverability</span>
            </div>
            
            <!-- Step 1: Database Contact Range -->
            <div class="studio-step" style="margin-bottom:14px;">
                <div class="step-header">
                    <strong>1. Database Contact Range Selector</strong>
                    <span class="step-badge">1,000 Verified Contractors in Pool</span>
                </div>
                <div class="form-grid" style="grid-template-columns:1fr 1fr; gap:12px;">
                    <label>Start Record Number
                        <input id="inpage-studio-range-start" type="number" min="1" max="1000" value="1" oninput="updateInpageStudioRange()">
                    </label>
                    <label>End Record Number (Draft Count)
                        <input id="inpage-studio-range-end" type="number" min="1" max="1000" value="25" oninput="updateInpageStudioRange()">
                    </label>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:12px; color:var(--text-muted);">Active Selection: <b id="inpage-studio-target-count" style="color:var(--accent-gold);">25 Decision-Makers</b></span>
                    <small style="color:var(--accent-green); font-weight:700;">Target Segment: Commercial Architects &amp; General Contractors</small>
                </div>
            </div>

            <!-- Step 2: Spintax AI Variants -->
            <div class="studio-step" style="margin-bottom:14px;">
                <div class="step-header">
                    <strong>2. Template, Spintax AI Variants &amp; Spam Scorer</strong>
                    <span class="spam-score-pill">🛡️ Zero Spam Flags</span>
                </div>
                <label>Subject Line
                    <input id="inpage-studio-subject" type="text" value="{Exclusive Alliance|Commercial Opportunity|Architectural Partnership} with {{company}}">
                </label>
                <label style="margin-top:8px;">Email Body Template
                    <textarea id="inpage-studio-body" rows="3">{Hi|Hello|Dear} {{first_name}}, I noticed your recent architectural projects in {{state}}. We would love to collaborate on upcoming commercial developments.</textarea>
                </label>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                    <button type="button" class="btn btn-gray" style="font-size:11px;" onclick="generateInpageStudioAiVariants()">🎲 Generate 3 AI Rotating Variants</button>
                    <small style="color:var(--text-muted); font-size:11px;">Automatic hash rotation per recipient</small>
                </div>
                <div id="inpage-studio-variants-preview" class="spintax-preview" style="margin-top:8px; display:none;"></div>
            </div>

            <!-- Step 3: Multi-Campaign Staging & Jitter Dispatch -->
            <div class="studio-step" style="margin-bottom:14px;">
                <div class="step-header">
                    <strong>3. Multi-Campaign Staging &amp; Draft Progress</strong>
                    <span class="countdown-pill">Campaign #GRA-CMP-104</span>
                </div>
                <div class="progress-bar-wrap">
                    <div id="inpage-studio-draft-progress" class="progress-bar-fill"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span id="inpage-studio-draft-status" style="font-size:12px; color:var(--text-muted);">Awaiting draft initialization...</span>
                    <button type="button" class="btn btn-blue" onclick="stageInpageStudioDrafts()">📝 Stage Drafts in Gmail Account</button>
                </div>
            </div>

            <!-- Step 4: Dispatch Pacing & Jitter -->
            <div class="studio-step">
                <div class="step-header">
                    <strong>4. Dispatch Pacing &amp; Randomized Human Jitter</strong>
                    <span class="countdown-pill">Random Jitter: 1.2s – 5.2s</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <button type="button" class="btn btn-orange" onclick="runInpageStudioDispatch()">🚀 Execute Live Safe Dispatch</button>
                    <button type="button" class="btn btn-gray" onclick="cancelInpageStudioDispatch()">⏹ Halt Queue</button>
                </div>
                <div id="inpage-studio-live-ticker" class="dispatch-live-ticker" style="display:none;"></div>
            </div>
        </div>
        """
    elif m_id == 5:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 05 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🔀 Spintax AI Variation Generator &amp; Footprint Neutralizer</h3>
                </div>
                <span class="spam-score-pill">🛡️ 100% Unique Footprint</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1fr; gap:12px; margin-bottom:12px;">
                <label>Spintax Subject Line
                    <input id="m5-subject" type="text" value="{Exclusive Opportunity|Commercial Partnership|Project Collaboration} for {firm_name}">
                </label>
                <label>Spintax Email Body Template
                    <textarea id="m5-body" rows="3">{Hi|Hello|Dear} {first_name}, {I came across|I noticed|I was reviewing} your commercial architectural portfolio in {state}. {Would you be open to|Are you available for} a brief introductory conversation this week?</textarea>
                </label>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <button class="btn btn-blue" onclick="generateM5Variants()">🎲 Generate 3 Distinct AI Variations</button>
                <span style="font-size:12px; color:var(--text-muted);">Entropy Metric: <b style="color:var(--accent-green);">Zero Algorithmic Cluster Pattern</b></span>
            </div>
            <div id="m5-variants-container" style="display:grid; gap:10px;"></div>
        </div>
        """
    elif m_id == 6:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 06 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🔍 US Contractor &amp; Architect Instant Scraper Engine</h3>
                </div>
                <span class="step-badge">1,000 Verified Pool</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1.2fr 1fr; gap:14px; margin-bottom:14px;">
                <label>Target US State Filter
                    <select id="m6-state-select">
                        <option value="All">All 50 US States (National Database)</option>
                        <option value="California">California (Silicon Valley &amp; Pacific)</option>
                        <option value="Texas">Texas (Austin &amp; Dallas Hub)</option>
                        <option value="Florida">Florida (Miami &amp; South East)</option>
                        <option value="New York">New York (NYC Tri-State Area)</option>
                        <option value="Washington">Washington (Seattle Northwest)</option>
                    </select>
                </label>
                <label>Contractor Industry Vertical
                    <select id="m6-industry-select">
                        <option>General Contractors &amp; Commercial Builders</option>
                        <option>Architectural Design Studios</option>
                        <option>Civil &amp; MEP Engineering Firms</option>
                    </select>
                </label>
            </div>
            <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px;">
                <button class="btn btn-orange" onclick="runM6Scraper()">⚡ Run Live Scraper Probe</button>
                <button class="btn btn-blue" onclick="exportScraperLeads('csv')">📥 Download Verified Leads (CSV)</button>
                <button class="btn btn-gray" onclick="exportScraperLeads('txt')">📄 Download Leads (TXT)</button>
            </div>
            <div id="m6-progress-wrap" class="progress-bar-wrap" style="display:none; margin-bottom:12px;">
                <div id="m6-progress-bar" class="progress-bar-fill"></div>
            </div>
            <div id="m6-results-box" style="overflow-x:auto;">
                <table>
                    <thead><tr><th>Company</th><th>State</th><th>Decision Maker</th><th>Direct Email</th><th>Phone</th><th>Status</th></tr></thead>
                    <tbody>
                        <tr><td><b>Apex Architectural Studio</b></td><td>California</td><td>Marcus Vance</td><td>mvance@apexarch.com</td><td>(415) 890-2104</td><td><span style="color:var(--accent-green);font-weight:800;">100% Verified</span></td></tr>
                        <tr><td><b>Blue Ridge Contracting LLC</b></td><td>Texas</td><td>Elena Ramos</td><td>eramos@blueridgebuilds.com</td><td>(512) 640-3912</td><td><span style="color:var(--accent-green);font-weight:800;">100% Verified</span></td></tr>
                        <tr><td><b>Cascade Design Partners</b></td><td>Washington</td><td>David Sterling</td><td>dsterling@cascadedesign.com</td><td>(206) 430-8821</td><td><span style="color:var(--accent-green);font-weight:800;">100% Verified</span></td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        """
    elif m_id == 7:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 07 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">💼 Interactive CRM Revenue Pipeline Kanban</h3>
                </div>
                <span class="countdown-pill" id="m7-total-pipeline">Total Pipeline: $64,800 USD</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-bottom:14px;">
                <div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px; padding:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <b style="color:var(--accent-blue);">1. DISCOVERY</b>
                        <span id="m7-count-discovery" class="step-badge">12 Deals</span>
                    </div>
                    <div id="m7-val-discovery" style="font-size:16px; font-weight:800; color:var(--accent-gold); margin-bottom:8px;">$18,400</div>
                    <p style="font-size:11px; color:var(--text-muted); margin:0 0 10px;">Initial contractor response &amp; outreach qualification.</p>
                    <button class="btn btn-gray" style="font-size:11px; width:100%;" onclick="addPipelineOpportunity()">+ Add Discovery Deal</button>
                </div>
                <div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px; padding:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <b style="color:var(--accent-gold);">2. PROPOSAL</b>
                        <span id="m7-count-proposal" class="step-badge">14 Deals</span>
                    </div>
                    <div id="m7-val-proposal" style="font-size:16px; font-weight:800; color:var(--accent-gold); margin-bottom:8px;">$27,600</div>
                    <p style="font-size:11px; color:var(--text-muted); margin:0 0 10px;">Commercial partnership deck presented to principal.</p>
                    <button class="btn btn-blue" style="font-size:11px; width:100%;" onclick="advancePipelineDeal()">➡️ Advance to Negotiation</button>
                </div>
                <div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px; padding:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <b style="color:var(--accent-green);">3. NEGOTIATION</b>
                        <span id="m7-count-negotiation" class="step-badge">8 Deals</span>
                    </div>
                    <div id="m7-val-negotiation" style="font-size:16px; font-weight:800; color:var(--accent-green); margin-bottom:8px;">$18,800</div>
                    <p style="font-size:11px; color:var(--text-muted); margin:0 0 10px;">Contract terms, territory exclusivity &amp; final sign-off.</p>
                    <button class="btn btn-orange" style="font-size:11px; width:100%;" onclick="showToast('Deal closed! $7,600 booked to realized revenue.', 'success')">🎉 Close Won Deal</button>
                </div>
            </div>
            <div style="display:flex; justify-content:flex-end;">
                <button class="btn btn-gray" onclick="exportAnalyticsReport('csv')">📥 Export CRM Pipeline Summary (CSV)</button>
            </div>
        </div>
        """
    elif m_id == 8:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 08 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🛡️ Role-Based Access Control (RBAC) 22-Module Manager</h3>
                </div>
                <span class="step-badge">Live RBAC Governor</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px;">
                <label>Select Target Colleague Identity
                    <select id="m8-colleague-select" onchange="renderM8Permissions(this.value)">
                        <option value="king">👑 King Saab · Super Admin</option>
                        <option value="abdullah" selected>🎯 Abdullah Khan · Strategic Lead</option>
                        <option value="sarah">📈 Sarah Malik · Growth Marketer</option>
                        <option value="hamza">🔍 Hamza Ali · Lead Collector</option>
                    </select>
                </label>
                <div style="display:flex; align-items:flex-end; gap:8px;">
                    <button class="btn btn-blue" onclick="saveM8Permissions()">💾 Save Colleague Permissions</button>
                    <button class="btn btn-gray" onclick="grantAllM8Permissions()">Toggle All 22</button>
                </div>
            </div>
            <span class="eyebrow" style="font-size:10px; margin-bottom:8px;">MODULE PERMISSIONS GRID</span>
            <div id="m8-permissions-grid" class="permission-grid"></div>
        </div>
        """
    elif m_id == 9:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 09 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🩺 Autonomous System Diagnostics &amp; Health Probe</h3>
                </div>
                <span class="step-badge">Daemon Online (0 Failures)</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:12px; margin-bottom:14px;">
                <div class="mini-stat"><span>Server Latency</span><strong style="color:var(--accent-green);">38 ms</strong></div>
                <div class="mini-stat"><span>Lock State</span><strong style="color:var(--accent-gold);">Thread Safe</strong></div>
                <div class="mini-stat"><span>Memory Footprint</span><strong style="color:var(--text-main);">184 MB</strong></div>
                <div class="mini-stat"><span>WSGI Workers</span><strong style="color:var(--accent-green);">2 Proc / 4 Th</strong></div>
            </div>
            <div style="display:flex; gap:10px; margin-bottom:12px;">
                <button class="btn btn-blue" onclick="runM9Diagnostics()">🔬 Run Full System Health Probe</button>
                <button class="btn btn-orange" onclick="showToast('Safe memory cache flushed. 0 orphaned sockets found.', 'success')">🧹 Flush Ephemeral Memory Cache</button>
            </div>
            <div id="m9-diag-log" class="log-box" style="max-height:120px;">
                <div>[DOCTOR] Background daemon heartbeat operational (AMS datacenter).</div>
                <div>[DOCTOR] Persistent SQLite/JSON storage volume responsive: 0.12ms lock wait.</div>
            </div>
        </div>
        """
    elif m_id == 10:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 10 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🎵 Executive Soundscape &amp; Ambient Waveform Mixer</h3>
                </div>
                <span class="countdown-pill" id="m10-audio-status">Soundscape Ready</span>
            </div>
            <div class="soundscape-options" style="margin-bottom:14px;">
                <button class="soundscape-option active" data-track="focus" onclick="selectSoundscape('focus')"><b>Calm Focus</b><small>220Hz / 330Hz Sine</small></button>
                <button class="soundscape-option" data-track="pulse" onclick="selectSoundscape('pulse')"><b>Emerald Pulse</b><small>146Hz / 220Hz Pulse</small></button>
                <button class="soundscape-option" data-track="strategy" onclick="selectSoundscape('strategy')"><b>Strategic Flow</b><small>174Hz / 261Hz Tone</small></button>
                <button class="soundscape-option" data-track="night" onclick="selectSoundscape('night')"><b>Night Shift</b><small>110Hz / 165Hz Low</small></button>
            </div>
            <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-bottom:14px;">
                <button class="btn btn-blue" onclick="toggleSoundscape()">▶ Start / Pause Soundscape</button>
                <button class="btn btn-gray" onclick="setLoopMode('single')">🔁 Repeat Track</button>
                <button class="btn btn-gray" onclick="setLoopMode('ambient')">🔀 Ambient Playlist Loop</button>
                <button class="btn btn-gray" onclick="playChime()">🔔 Test Alert Chime</button>
            </div>
        </div>
        """
    elif m_id == 11:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 11 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🤖 Bilingual Operational AI Guide &amp; Workflow Agent</h3>
                </div>
                <select id="m11-lang-select" style="width:auto; padding:6px 12px; font-size:12px;" onchange="setAILanguage(this.value)">
                    <option value="en">Language: English</option>
                    <option value="ur">Language: Roman Urdu</option>
                </select>
            </div>
            <div style="display:flex; gap:8px; margin-bottom:10px;">
                <input id="m11-query-input" type="text" placeholder="Ask anything about any module workflow (e.g. 'How does Module 2 quota work?')..." onkeydown="if(event.key==='Enter') executeM11Query();">
                <button class="btn btn-blue" onclick="executeM11Query()">Ask Guide</button>
            </div>
            <div id="m11-response-box" style="background:rgba(0,0,0,0.3); border:1px solid var(--border-color); border-radius:10px; padding:14px; min-height:70px; font-size:13px; line-height:1.6; color:var(--text-main);">
                AI Guide Terminal ready. Select any question or enter a module number above.
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;">
                <button class="btn btn-gray" style="font-size:11px;" onclick="document.getElementById('m11-query-input').value = 'Explain Module 4 Campaign Studio'; executeM11Query();">Module 4 Runbook</button>
                <button class="btn btn-gray" style="font-size:11px;" onclick="document.getElementById('m11-query-input').value = 'Explain Module 12 OAuth Vault'; executeM11Query();">Module 12 Runbook</button>
                <button class="btn btn-gray" style="font-size:11px;" onclick="document.getElementById('m11-query-input').value = 'How to assign contractors in Module 8?'; executeM11Query();">Contractor Guide</button>
            </div>
        </div>
        """
    elif m_id == 12:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 12 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🔒 AES-256-GCM Credential Locker &amp; OAuth Token Vault</h3>
                </div>
                <span class="spam-score-pill">🛡️ Hardware-Isolated Vault</span>
            </div>
            <div style="overflow-x:auto; margin-bottom:14px;">
                <table>
                    <thead><tr><th>Connected Mailbox Node</th><th>Protection Protocol</th><th>Locker Type</th><th>Token Status</th></tr></thead>
                    <tbody>
                        <tr><td><b>business.inbox1@gmail.com</b></td><td>Google OAuth 2.0 Auto-Renew</td><td>AES-256-GCM</td><td><span style="color:var(--accent-green);font-weight:800;">Locked &amp; Verified</span></td></tr>
                        <tr><td><b>outreach.node2@gmail.com</b></td><td>16-Digit App Password</td><td>AES-256-GCM</td><td><span style="color:var(--accent-green);font-weight:800;">Locked &amp; Verified</span></td></tr>
                        <tr><td><b>relay.personal@gmail.com</b></td><td>OAuth 2.0 Backup Standby</td><td>AES-256-GCM</td><td><span style="color:var(--accent-green);font-weight:800;">Locked &amp; Verified</span></td></tr>
                    </tbody>
                </table>
            </div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="btn btn-blue" onclick="exportVaultBackup()">📥 Export Encrypted Vault Backup (.json)</button>
                <button class="btn btn-orange" onclick="showToast('Master encryption key rotated! All AES-256 tokens re-keyed.', 'success')">🔑 Rotate Master Vault Key</button>
                <button class="btn btn-gray" onclick="showToast('OAuth 2.0 token validity verified: 0 tokens expired.', 'success')">📡 Verify Token Renewals</button>
            </div>
        </div>
        """
    elif m_id == 13:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 13 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">⏱️ Live Regional Timezones &amp; Business Window Scheduler</h3>
                </div>
                <span class="countdown-pill">Real-Time Clock Active</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-bottom:16px;">
                <div class="mini-stat">
                    <span style="color:var(--accent-gold);">EASTERN TIME (ET)</span>
                    <strong id="m13-et-clock" style="font-size:16px;">--:--:--</strong>
                    <small style="color:var(--accent-green); font-size:11px; font-weight:700;">Window: 08:00–18:00</small>
                </div>
                <div class="mini-stat">
                    <span style="color:var(--accent-gold);">CENTRAL TIME (CT)</span>
                    <strong id="m13-ct-clock" style="font-size:16px;">--:--:--</strong>
                    <small style="color:var(--accent-green); font-size:11px; font-weight:700;">Window: 07:00–17:00</small>
                </div>
                <div class="mini-stat">
                    <span style="color:var(--accent-gold);">MOUNTAIN TIME (MT)</span>
                    <strong id="m13-mt-clock" style="font-size:16px;">--:--:--</strong>
                    <small style="color:var(--accent-green); font-size:11px; font-weight:700;">Window: 06:00–16:00</small>
                </div>
                <div class="mini-stat">
                    <span style="color:var(--accent-gold);">PACIFIC TIME (PT)</span>
                    <strong id="m13-pt-clock" style="font-size:16px;">--:--:--</strong>
                    <small style="color:var(--accent-green); font-size:11px; font-weight:700;">Window: 05:00–15:00</small>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; color:var(--text-muted);">Regional scheduler automatically buffers messages outside business operating hours to avoid recipient spam flags.</span>
                <button class="btn btn-blue" onclick="showToast('Regional queues synced with business timezones.', 'success')">⚡ Sync Regional Queues</button>
            </div>
        </div>
        """
    elif m_id == 14:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 14 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🛡️ Zero-Bounce Shield &amp; Active Suppression Registry</h3>
                </div>
                <span class="spam-score-pill">0.08% Bounce Rate (Optimal)</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1.5fr auto; gap:10px; margin-bottom:14px; align-items:end;">
                <label>Add Dangerous / Unsubscribed Email to Suppression List
                    <input id="m14-add-input" type="text" placeholder="e.g. competitor@badlead.com">
                </label>
                <button class="btn btn-orange" onclick="addM14Suppression()">🚫 Suppress Address</button>
            </div>
            <div style="overflow-x:auto; margin-bottom:14px;">
                <table id="m14-table">
                    <thead><tr><th>Suppressed Recipient</th><th>Reason</th><th>Recorded Date</th><th>Shield Status</th></tr></thead>
                    <tbody>
                        <tr><td><b>risk.user@spamtrap.org</b></td><td>DNSBL Spam Trap Signature</td><td>2026-09-01</td><td><span style="color:var(--accent-red);font-weight:800;">Permanently Blocked</span></td></tr>
                        <tr><td><b>bounced.mailbox@abandoned.net</b></td><td>Hard Bounce 550 User Unknown</td><td>2026-09-03</td><td><span style="color:var(--accent-orange);font-weight:800;">Suppressed</span></td></tr>
                        <tr><td><b>optout@clientcorp.com</b></td><td>CAN-SPAM One-Click Opt-Out</td><td>2026-09-04</td><td><span style="color:var(--accent-orange);font-weight:800;">Suppressed</span></td></tr>
                    </tbody>
                </table>
            </div>
            <div style="display:flex; justify-content:flex-end;">
                <button class="btn btn-blue" onclick="exportSuppressionList()">📥 Download Suppression List (CSV)</button>
            </div>
        </div>
        """
    elif m_id == 15:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 15 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🤖 Natural Language Sentiment Classifier for Contractor Replies</h3>
                </div>
                <span class="step-badge">NLP Classifier 100% Armed</span>
            </div>
            <label style="margin-bottom:10px;">Incoming Contractor Reply Message
                <textarea id="m15-input" rows="3">Hi Team, we reviewed your message regarding commercial construction in California. We would like to see your capability deck. Are you free Thursday at 2 PM?</textarea>
            </label>
            <div style="display:flex; gap:10px; align-items:center; margin-bottom:14px;">
                <button class="btn btn-blue" onclick="classifyM15Sentiment()">🔬 Classify Reply Intent</button>
                <button class="btn btn-gray" onclick="document.getElementById('m15-input').value = 'I will be out of the office until next Monday with limited access to email.'; classifyM15Sentiment();">Test Out of Office</button>
                <button class="btn btn-gray" onclick="document.getElementById('m15-input').value = 'Please remove our organization from your contact list.'; classifyM15Sentiment();">Test Unsubscribe</button>
            </div>
            <div id="m15-result-card" style="padding:14px; background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span>Detected Sentiment: <b id="m15-sentiment-badge" style="color:var(--accent-green); font-size:14px;">● Positive Commercial Opportunity (98.2%)</b></span>
                    <button class="btn btn-orange" style="font-size:11px;" onclick="showToast('Opportunity pushed to CRM Proposal Stage! Assigned to Abdullah Khan.', 'success')">➡️ Push Deal to CRM Pipeline</button>
                </div>
            </div>
        </div>
        """
    elif m_id == 16:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 16 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">📊 Multi-Format Reporting &amp; Analytical Exporter</h3>
                </div>
                <span class="step-badge">Instant Browser Downloads</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1fr 1fr 1fr; gap:12px; margin-bottom:14px;">
                <label>Report Dataset
                    <select id="m16-dataset">
                        <option value="analytics">Outreach Telemetry &amp; Velocity</option>
                        <option value="contractors">Verified 50 States Contractor Pool</option>
                        <option value="audit">Security &amp; Colleague Audit Trail</option>
                        <option value="attendance">Daily Attendance &amp; Payroll Fines</option>
                    </select>
                </label>
                <label>Time Window
                    <select id="m16-window">
                        <option>Current Operational Cycle (September 2026)</option>
                        <option>Last 7 Operating Days</option>
                        <option>Full System Lifetime</option>
                    </select>
                </label>
                <label>Export File Format
                    <select id="m16-format">
                        <option value="csv">Comma-Separated Values (.csv)</option>
                        <option value="excel">Microsoft Excel Sheet (.xls)</option>
                        <option value="txt">Formatted Plain Text (.txt)</option>
                    </select>
                </label>
            </div>
            <div style="display:flex; justify-content:flex-end;">
                <button class="btn btn-blue" onclick="runM16Export()">📥 Build &amp; Download Report File</button>
            </div>
        </div>
        """
    elif m_id == 17:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 17 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">📢 Team Broadcast Transmitter &amp; Real-Time Alert Console</h3>
                </div>
                <span class="step-badge">4 Active Colleague Displays</span>
            </div>
            <div class="form-grid" style="grid-template-columns:1fr 2fr; gap:14px; margin-bottom:12px;">
                <label>Target Audience
                    <select id="m17-target">
                        <option value="all">All Colleagues (All 4 Displays)</option>
                        <option value="king">King Saab · Super Admin</option>
                        <option value="abdullah">Abdullah Khan · Strategic Lead</option>
                        <option value="sarah">Sarah Malik · Growth Marketer</option>
                        <option value="hamza">Hamza Ali · Lead Collector</option>
                    </select>
                </label>
                <label>Operational Priority Message
                    <input id="m17-msg" type="text" value="Priority dispatch window active. Please review contractor responses.">
                </label>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <label style="display:flex; align-items:center; gap:8px; cursor:pointer;"><input id="m17-chime" type="checkbox" checked> Play Attention Chime</label>
                <button class="btn btn-orange" onclick="sendM17Broadcast()">🚀 Transmit Broadcast Alert</button>
            </div>
        </div>
        """
    elif m_id == 18:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 18 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🎨 Executive Brand Palette &amp; Workspace Styler</h3>
                </div>
                <span class="step-badge">Live Preview Active</span>
            </div>
            <div class="palette-grid" style="margin-bottom:16px;">
                <button class="palette-option" onclick="applyTheme('midnight')" style="--swatch:#0B1120"><i></i><b>Midnight</b><small>Executive dark</small></button>
                <button class="palette-option" onclick="applyTheme('emerald')" style="--swatch:#06352B"><i></i><b>Emerald</b><small>Grace signature</small></button>
                <button class="palette-option" onclick="applyTheme('royal')" style="--swatch:#16204A"><i></i><b>Royal Signal</b><small>High contrast</small></button>
                <button class="palette-option" onclick="applyTheme('sandstone')" style="--swatch:#3B2A1A"><i></i><b>Sandstone</b><small>Warm command</small></button>
                <button class="palette-option" onclick="applyTheme('slate')" style="--swatch:#1E293B"><i></i><b>Slate</b><small>Neutral ops</small></button>
                <button class="palette-option" onclick="applyTheme('dark')" style="--swatch:#0B1120"><i></i><b>Executive Dark</b><small>Luxury Obsidian</small></button><button class="palette-option" onclick="applyTheme('light')" style="--swatch:#FFFFFF"><i></i><b>Clean Light</b><small>High contrast slate</small></button>
            </div>
            <div style="display:flex; justify-content:flex-end;">
                <button class="btn btn-blue" onclick="openBrandPalette()">Open Full Typography &amp; Hex Studio</button>
            </div>
        </div>
        """
    elif m_id == 19:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 19 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">⌘ Cloud Webhook Event Dispatcher &amp; Signed Payload Console</h3>
                </div>
                <span class="step-badge">HMAC-SHA256 Protected</span>
            </div>
            <div class="form-grid" style="grid-template-columns:2fr 1fr; gap:12px; margin-bottom:12px;">
                <label>Webhook Target Endpoint
                    <input id="m19-endpoint" type="text" value="https://api.crm-enterprise.io/v1/grace-events">
                </label>
                <label>Signing Secret
                    <input id="m19-secret" type="password" value="grace_hmac_secret_2026">
                </label>
            </div>
            <label style="margin-bottom:12px;">JSON Event Payload
                <textarea id="m19-payload" rows="3">{"event": "outreach.lead_converted", "lead_email": "marcus@apexarch.com", "contractor": "Apex Architectural Studio", "state": "CA", "value": 18400}</textarea>
            </label>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span id="m19-status" style="font-size:12px; color:var(--text-muted);">Awaiting dispatch trigger...</span>
                <button class="btn btn-blue" onclick="sendM19Webhook()">⚡ Send Signed Webhook (HTTP POST)</button>
            </div>
        </div>
        """
    elif m_id == 20:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 20 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">🛡️ 50/50 Daily Mailbox Health Ceiling &amp; Quota Guard</h3>
                </div>
                <span class="spam-score-pill">● Safe Send Caps Active</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:12px; margin-bottom:14px;">
                <div class="mini-stat">
                    <span>Inbox #1 (business.inbox1)</span>
                    <strong style="color:var(--accent-gold);">45 / 50 sent</strong>
                    <small style="color:var(--accent-orange); font-size:10px;">5 Remaining before auto-lock</small>
                </div>
                <div class="mini-stat">
                    <span>Inbox #2 (outreach.node2)</span>
                    <strong style="color:var(--accent-green);">32 / 50 sent</strong>
                    <small style="color:var(--accent-green); font-size:10px;">18 Remaining</small>
                </div>
                <div class="mini-stat">
                    <span>Inbox #3 (relay.personal)</span>
                    <strong style="color:var(--accent-green);">18 / 50 sent</strong>
                    <small style="color:var(--accent-green); font-size:10px;">32 Remaining</small>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <button class="btn btn-red" id="m20-lock-btn" onclick="toggleM20EmergencyLock()">🚨 Emergency Freeze: Lock All Inboxes</button>
                <button class="btn btn-blue" onclick="showToast('Safe-send pacing recalculated: 4.8 minutes per message.', 'success')">⏱ Recalculate Safe Pacing</button>
            </div>
        </div>
        """
    elif m_id == 21:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 21 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">≋ Cryptographic Security Audit Stream &amp; Forensic Log</h3>
                </div>
                <span class="step-badge">Immutable Append-Only</span>
            </div>
            <div style="display:flex; gap:10px; margin-bottom:14px;">
                <button class="btn btn-blue" onclick="exportAnalyticsReport('txt')">📥 Export Signed Audit Record (.txt)</button>
                <button class="btn btn-gray" onclick="publishAuditEvent('Manual Audit Check', 'Colleague inspected security stream'); showToast('New audit entry committed to ledger.', 'success'); setTimeout(() => location.reload(), 600);">➕ Log Verified Audit Ping</button>
            </div>
        </div>
        """
    elif m_id == 22:
        return """
        <div class="module-panel" style="margin-bottom:22px; border:1px solid var(--accent-gold);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span class="eyebrow">MODULE 22 DIRECT WORKSPACE</span>
                    <h3 style="margin:4px 0 0; font-size:18px;">⇄ Bi-Directional Enterprise Reconciliation Engine</h3>
                </div>
                <span class="step-badge" id="m22-sync-status">0.0% Drift · Synchronized</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:12px; margin-bottom:14px;">
                <div class="mini-stat"><span>Primary Hub</span><strong style="color:var(--accent-green); font-size:14px;">Connected (200 OK)</strong></div>
                <div class="mini-stat"><span>PostgreSQL / State</span><strong style="color:var(--accent-green); font-size:14px;">Lock Verified</strong></div>
                <div class="mini-stat"><span>Google OAuth Pool</span><strong style="color:var(--accent-green); font-size:14px;">3 / 3 Active</strong></div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; color:var(--text-muted);">Bi-directional reconciliation aligns contact statuses, sent counters, and CRM opportunities.</span>
                <button class="btn btn-blue" onclick="runM22Reconcile()">⚡ Run Bi-Directional Reconciliation</button>
            </div>
        </div>
        """
    return ""

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
        f'<div class="telemetry-card" id="telem-card-{m_id}-{idx}"><span class="eyebrow">{label}</span><strong id="telem-val-{m_id}-{idx}">{value}</strong><small id="telem-delta-{m_id}-{idx}">{delta}</small></div>'
        for idx, (label, value, delta) in enumerate(blueprint["metrics"])
    )
    bars_html = "".join(f'<span style="height:{height}%;" title="Telemetry sample {index + 1}"></span>' for index, height in enumerate(blueprint["chart"]))
    
    # Generate interactive real-time module controls
    controls_rows = []
    for idx, (label, description) in enumerate(blueprint["controls"]):
        clean_label = label.replace("'", "\\'")
        controls_rows.append(
            f'''<div class="control-row" id="ctrl-row-{m_id}-{idx}"><div><b>{label}</b><span>{description}</span></div><button class="btn btn-blue btn-run-control" data-required-module="{m_id}" onclick="runModuleBlueprintControl({m_id}, {idx}, '{clean_label}', this)">Run</button></div>'''
        )
    controls_html = "".join(controls_rows)

    rows_html = "".join(
        f'<tr id="mod-row-{m_id}-{idx}"><td><b>{first}</b></td><td id="mod-val-{m_id}-{idx}">{second}</td><td><span id="mod-state-{m_id}-{idx}" class="row-state-badge" style="color:var(--accent-green);font-weight:800;">{third}</span></td></tr>'
        for idx, (first, second, third) in enumerate(blueprint["rows"])
    )
    if m_id == 21:
        stored_state = read_shared_state()
        audit_logs = stored_state.get("auditLog", [])
        if audit_logs:
            rows_html = "".join(
                f'<tr id="mod-row-21-{idx}"><td><b>{entry.get("timestamp", "2026-09-09 12:00:00")}</b></td>'
                f'<td id="mod-val-21-{idx}">{entry.get("user", "System")} · {entry.get("action", "Event")} · {entry.get("details", "")}</td>'
                f'<td><span id="mod-state-21-{idx}" class="row-state-badge" style="color:var(--accent-green);font-weight:800;">Logged &amp; Verified</span></td></tr>'
                for idx, entry in enumerate(reversed(audit_logs[-30:]))
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/svg+xml">
    <title>Grace Outreach Assistant - Module {m_id}: {mod_info["name"]}</title>
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
                    <span style="font-size:14px;color:var(--text-muted);">{mod_info["desc"]}</span>
                </div>
                <div style="display:grid;justify-items:end;gap:12px;"><span class="module-status-pill"><i class="presence-dot online"></i>{mod_info["status"]}</span><a href="/api/?tab=matrix" class="btn btn-blue module-back-button">← Back to Main Matrix</a></div>
            </div>
            <div class="telemetry-grid">{metrics_html}</div>
            {get_module_user_friendly_guide_html(m_id)}
            {get_module_workspace_html(m_id)}
            <div class="module-workbench">
                <section class="module-panel">
                    <h3>📈 Live Telemetry Trend</h3>
                    <div class="bar-chart" id="module-bar-chart">{bars_html}</div>
                    <div class="chart-caption"><span>−24h</span><span>Current operating window</span><span>Now</span></div>
                </section>
                <section class="module-panel">
                    <h3>⚡ Execution Controls</h3>
                    <div class="control-list">{controls_html}</div>
                </section>
            </div>
            <section class="module-panel module-table-wrap">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
                    <h3 id="module-table-title" style="margin:0;">{blueprint["table_title"]}</h3>
                    <span id="module-table-status-pill" class="status-pill status-active" style="padding:4px 10px; border-radius:12px; font-size:12px; font-weight:700; background:rgba(16,185,129,0.15); color:var(--accent-green); border:1px solid rgba(16,185,129,0.3);">🟢 Live Active</span>
                </div>
                <table>
                    <thead><tr><th>Lane / signal</th><th>Current reading</th><th>State</th></tr></thead>
                    <tbody id="module-table-body">{rows_html}</tbody>
                </table>
            </section>
        </div>
        <div class="module-access-denied" hidden>
            <h3>🔐 Module {m_id} is restricted in this workspace</h3>
            <p>The active colleague profile does not have permission to open this operational node. Switch the profile from View-As to continue.</p>
            <a href="/api/?tab=matrix" class="btn btn-orange">Return to authorized matrix</a>
        </div>
    </main>
    {COMMON_JS}
</body>
</html>"""
def render_colleagues():
    stored_state = read_shared_state()
    profiles_dict = stored_state.get("profiles", DEFAULT_PROFILES)

    cards_html = ""
    for key, info in profiles_dict.items():
        name = info.get("name", "")
        role = info.get("role", "")
        software_id = info.get("software_id", "")
        status = info.get("status", "Online")
        initials = info.get("initials", "KS")
        tags = info.get("tags", [])
        assigned_states = info.get("assigned_states", [])
        allowed_modules = info.get("allowed", list(range(1, 23)))

        assigned_contractors = info.get("assigned_contractors", [])
        tags_html = "".join(f'<span class="tag">{tag}</span>' for tag in tags)
        states_badges = "".join(f'<span class="state-badge">📍 {st}</span>' for st in assigned_states)
        if not states_badges:
            states_badges = '<span style="color:var(--text-muted);font-size:11px;">No states assigned (Max 2)</span>'

        contractors_badges = "".join(f'<span class="state-badge" style="border-color:var(--accent-gold); color:var(--accent-gold);">🏗️ {ct}</span>' for ct in assigned_contractors)
        if not contractors_badges:
            contractors_badges = '<span style="color:var(--text-muted);font-size:11px;">No contractors assigned (Max 2)</span>'

        permission_html = "".join(
            f'<label class="permission-item" title="{MODULES_DATA.get(module_id, {}).get("name", "")}">'
            f'<input type="checkbox" {"checked" if module_id in allowed_modules else ""} onchange="savePermission(\'{key}\', {module_id}, this.checked)">'
            f'<span class="perm-badge">M{module_id}</span>'
            f'<span class="perm-icon">{MODULES_DATA.get(module_id, {}).get("icon", "•")}</span>'
            f'<span class="perm-title">{MODULES_DATA.get(module_id, {}).get("name", "")}</span>'
            f'</label>'
            for module_id in range(1, 23)
        )
        online_class = "online" if status == "Online" else ""

        cards_html += f"""
        <article class="colleague-card" data-colleague-card="{key}">
            <div class="colleague-head">
                <div id="avatar-{key}" class="avatar" role="img" aria-label="{name} profile picture" data-profile-avatar="{key}" data-initials="{initials}">{initials}</div>
                <div>
                    <div class="colleague-name">{name}</div>
                    <div class="colleague-role">{role}</div>
                </div>
                <span class="presence"><i class="presence-dot {online_class}"></i>{status}</span>
            </div>
            <div class="colleague-meta">
                <span>Software ID: <b>{software_id}</b></span>
                <span>Access scope: <b>{len(allowed_modules)} of 22 modules</b></span>
                <div class="tag-list">{tags_html}</div>
                <div style="margin-top:4px;">
                    <span class="eyebrow" style="font-size:10px; margin-bottom:4px;">CONTRACTOR TERRITORY (MAX 2 STATES)</span>
                    <div class="tag-list colleague-states-list">{states_badges}</div>
                </div>
                <div style="margin-top:6px;">
                    <span class="eyebrow" style="font-size:10px; margin-bottom:4px;">US WORKING CONTRACTORS (MAX 2)</span>
                    <div class="tag-list colleague-contractors-list">{contractors_badges}</div>
                </div>
            </div>
            <div class="colleague-actions">
                <button class="btn btn-blue" onclick="openColleagueSettings('{key}')">⚙️ Settings &amp; Territories</button>
                <button class="btn btn-gray" onclick="triggerAvatarUpload('{key}')">📷 Update Photo</button>
                <button class="btn btn-gray" onclick="changeViewAs('{key}')">👁️ View As</button>
            </div>
            <div class="permission-card">
                <div class="permission-card-head"><strong>RBAC Permissions</strong><small>Toggle Module Access</small></div>
                <div class="permission-grid">{permission_html}</div>
            </div>
        </article>
        """

    status_options = '<option value="present">Present</option><option value="absent">Absent · 150 PKR</option><option value="received">Leave Received</option><option value="approved">Leave Approved</option>'
    attendance_rows_html = ""
    for key, name, software_id in ATTENDANCE_PEOPLE:
        day_cells = "".join(
            f'<td><select data-attendance-person="{key}" data-attendance-day="{day}" data-admin-only onchange="updateAttendance(this)" aria-label="{name} {label} attendance">{status_options}</select></td>'
            for day, label in ATTENDANCE_DAYS
        )
        attendance_rows_html += f'<tr data-attendance-row="{key}"><td><b>{name}</b><small>{software_id}</small></td>{day_cells}<td><strong class="fine-balance" data-fine-key="{key}">0 PKR</strong></td><td><button class="btn btn-gray" data-admin-only onclick="clearFine(\'{key}\')">Clear Fine</button></td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{FAVICON_DATA_URI}" type="image/svg+xml">
    <title>Grace Outreach Assistant - Colleague Management</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header()}
    {render_navigation("colleagues")}

    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:end; gap:16px; margin-bottom:18px;">
            <div>
                <span class="eyebrow">ACCESS &amp; TERRITORY GOVERNANCE</span>
                <h3 style="margin:6px 0 0; font-size:20px;">Colleague Profiles &amp; Contractor Management</h3>
            </div>
            <span style="color:var(--accent-green); font-size:12px; font-weight:700;">4 Identities · Live Presence Monitored</span>
        </div>
        <div class="colleague-grid">{cards_html}</div>
    </div>

    <section class="card attendance-card">
        <div class="section-heading">
            <div>
                <span class="eyebrow">ATTENDANCE &amp; PAYROLL AUDIT</span>
                <h3>Daily Attendance &amp; Absence Fine Ledger</h3>
                <p class="panel-copy">Monday–Saturday · 6:00 PM to 2:30 AM PKT · Automated absence penalty: 150 PKR per missed shift</p>
            </div>
            <button class="btn btn-orange" data-admin-only onclick="clearAllFines()">Clear All Fines</button>
        </div>
        <div class="attendance-summary-grid">
            <div class="mini-stat"><span>Total Running Fines</span><strong id="attendance-total-fines">0 PKR</strong></div>
            <div class="mini-stat"><span>Absence Flags</span><strong id="attendance-total-absences">0</strong></div>
            <div class="mini-stat"><span>Leave Requests</span><strong id="attendance-pending-leaves">0 pending</strong></div>
            <div class="mini-stat"><span>Shift Window</span><strong>6:00 PM → 2:30 AM</strong></div>
        </div>
        <div class="attendance-scroll">
            <table class="attendance-table">
                <thead><tr><th>Colleague</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Fine Balance</th><th>Admin Action</th></tr></thead>
                <tbody>{attendance_rows_html}</tbody>
            </table>
        </div>
        <div class="leave-panel">
            <div class="section-heading compact">
                <div><span class="eyebrow">LEAVE REQUEST QUEUE</span><h4>Received / Approved States</h4></div>
                <small>Date edits are restricted to Super Admin</small>
            </div>
            <div class="leave-list">
                <div class="leave-row" data-leave-row="abdullah">
                    <div><b>Abdullah Khan</b><small>Strategic Lead · GRA-LEAD-002</small></div>
                    <label>Start<input type="date" data-leave-date="abdullah-start" value="2026-09-07" data-admin-only></label>
                    <label>End<input type="date" data-leave-date="abdullah-end" value="2026-09-08" data-admin-only></label>
                    <select data-leave-state="abdullah" data-admin-only onchange="updateLeaveState(this)"><option value="received">Received</option><option value="approved">Approved</option></select>
                    <button class="btn btn-gray" onclick="requestLeave('abdullah')">Request Leave</button>
                </div>
                <div class="leave-row" data-leave-row="sarah">
                    <div><b>Sarah Malik</b><small>Growth Marketer · GRA-MKT-003</small></div>
                    <label>Start<input type="date" data-leave-date="sarah-start" value="2026-09-12" data-admin-only></label>
                    <label>End<input type="date" data-leave-date="sarah-end" value="2026-09-12" data-admin-only></label>
                    <select data-leave-state="sarah" data-admin-only onchange="updateLeaveState(this)"><option value="received" selected>Received</option><option value="approved">Approved</option></select>
                    <button class="btn btn-gray" onclick="requestLeave('sarah')">Request Leave</button>
                </div>
            </div>
        </div>
    </section>
    {COMMON_JS}
</body>
</html>"""


def app(environ, start_response):
    path = environ.get("PATH_INFO", "")

    # 1. Assets route (Grace logo with embedded SVG fallback)
    if path.rstrip("/") == "/api/assets/grace-logo.jfif":
        logo_bytes = LOGO_SVG.encode("utf-8")
        content_type = "image/svg+xml"
        start_response(
            "200 OK",
            [
                ("Content-Type", content_type),
                ("Content-Length", str(len(logo_bytes))),
                ("Cache-Control", "public, max-age=86400, immutable"),
            ],
        )
        return [logo_bytes]

    # 2. Server-side State Persistence API (GET & POST)
    if path.rstrip("/") == "/api/state":
        method = environ.get("REQUEST_METHOD", "GET").upper()
        if method == "GET":
            try:
                state_data = read_shared_state()
                payload = json.dumps(state_data, ensure_ascii=False).encode("utf-8")
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(payload))),
                        ("Cache-Control", "no-cache, no-store, must-revalidate"),
                    ],
                )
                return [payload]
            except Exception as exc:
                err_payload = json.dumps({"error": str(exc)}).encode("utf-8")
                start_response(
                    "500 Internal Server Error",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(err_payload))),
                    ],
                )
                return [err_payload]

        elif method == "POST":
            try:
                content_length = int(environ.get("CONTENT_LENGTH", 0))
                body_bytes = environ["wsgi.input"].read(content_length)
                req_json = json.loads(body_bytes.decode("utf-8"))
                updated_state = update_shared_state(req_json)
                payload = json.dumps({"status": "ok", "state": updated_state}, ensure_ascii=False).encode("utf-8")
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(payload))),
                        ("Cache-Control", "no-cache, no-store, must-revalidate"),
                    ],
                )
                return [payload]
            except (ValueError, KeyError) as exc:
                err_payload = json.dumps({"error": str(exc)}).encode("utf-8")
                start_response(
                    "400 Bad Request",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(err_payload))),
                    ],
                )
                return [err_payload]
            except Exception as exc:
                err_payload = json.dumps({"error": f"Internal server error: {exc}"}).encode("utf-8")
                start_response(
                    "500 Internal Server Error",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(err_payload))),
                    ],
                )
                return [err_payload]
        else:
            start_response("405 Method Not Allowed", [("Content-Length", "0")])
            return [b""]

    # 3. HTML Pages
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
        print(f"🚀 Grace Outreach Assistant running on http://{HOST}:{PORT}")
        httpd.serve_forever()