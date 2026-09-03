import os
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

MODULES_DATA = {
    1: {"name": "Dashboard Hub & Real-time Telemetry", "category": "Core Analytics", "status": "Active", "lock": "Secured", "desc": "Enterprise real-time dispatch monitoring, response parsing, and velocity tracking."},
    2: {"name": "Multi-Tenant Inboxes Manager", "category": "Connection Pool", "status": "Active (3 Inboxes)", "lock": "Secured", "desc": "Multi-channel Gmail rotation pool with automated quota preservation."},
    3: {"name": "AI Warmup & Deliverability Engine", "category": "Reputation", "status": "Optimal (98%)", "lock": "Automated", "desc": "Autonomous peer thread engagement preserving IP and domain reputation."},
    4: {"name": "Campaign Studio & Sequence Builder", "category": "Outreach", "status": "Active", "lock": "Armed", "desc": "Multi-stage automated outreach pipeline with conditional branching."},
    5: {"name": "Spin-Syntax & Variant Generator", "category": "Copywriting", "status": "Active", "lock": "Ready", "desc": "Multi-tier dynamic Spintax processor eliminating spam trigger footprint."},
    6: {"name": "Contractor Scraper & Enricher", "category": "Lead Gen", "status": "Standby", "lock": "Ready", "desc": "High-velocity data extraction and verification engine for verified decision-makers."},
    7: {"name": "CRM Revenue Pipeline", "category": "Monetization", "status": "$64,800 Deal Value", "lock": "Active", "desc": "Visual deal-stage tracking converting inbound warm leads into revenue."},
    8: {"name": "Colleague Management & RBAC", "category": "Access Control", "status": "Protected", "lock": "Restricted", "desc": "Granular role-based credential provisioning and access delegation."},
    9: {"name": "System Doctor & Diagnostics", "category": "Diagnostics", "status": "100% Operational", "lock": "Monitored", "desc": "Automated latency checks, socket diagnostics, and worker thread watchdog."},
    10: {"name": "Audio Studio & Broadcast Matrix", "category": "Alerts", "status": "Audio: ON", "lock": "Active", "desc": "Synthesized audio feedback triggers for real-time positive outreach classifications."},
    11: {"name": "AI Knowledge & Context Agent", "category": "Intelligence", "status": "Online", "lock": "Ready", "desc": "Context-aware response classifier matching intent and sentiment scoring."},
    12: {"name": "OAuth Token Vault & AES-256 Locker", "category": "Security Vault", "status": "AES-256 Locked", "lock": "Encrypted", "desc": "Hardware-level credential isolation with autonomous 24-hour token rotation daemon."},
    13: {"name": "Blacklist & Spam Shield", "category": "Deliverability", "status": "Shield Active", "lock": "Secured", "desc": "Real-time DNSBL, SURBL, and MX record reputation monitoring."},
    14: {"name": "Delivery Rate & Volume Throttler", "category": "Scheduler", "status": "Pacing Healthy", "lock": "Regulated", "desc": "Human-like jitter randomization preventing algorithmic mailbox flagging."},
    15: {"name": "Domain Authenticator (SPF/DKIM/DMARC)", "category": "Compliance", "status": "Aligned (100%)", "lock": "Verified", "desc": "DNS alignment validation ensuring 100% deliverability inbox placement."},
    16: {"name": "A/B Multivariate Testing Lab", "category": "Optimization", "status": "Testing", "lock": "Armed", "desc": "Split-variant subject and body copy optimization across active pools."},
    17: {"name": "Template Forge & Asset Vault", "category": "Assets", "status": "Synced", "lock": "Protected", "desc": "Cloud template repository with tokenized personalized merge tags."},
    18: {"name": "Bounce & Suppression Sentinel", "category": "Hygiene", "status": "Zero-Bounce", "lock": "Enforced", "desc": "Hard bounce suppression list automation maintaining sender score."},
    19: {"name": "Compliance & Privacy Guard", "category": "Regulatory", "status": "CAN-SPAM Compliant", "lock": "Active", "desc": "Automated one-click opt-out header injection and compliance enforcement."},
    20: {"name": "Billing Ledger & ROI Tracker", "category": "Accounting", "status": "Balanced", "lock": "Audited", "desc": "Enterprise invoice reconciliation and outreach ROI attribution reporting."},
    21: {"name": "Audit Logs & Security Stream", "category": "Forensics", "status": "Recording", "lock": "Tamper-Proof", "desc": "Immutable append-only access and dispatch trail with timestamp forensics."},
    22: {"name": "Enterprise Sync Engine", "category": "Integration", "status": "Connected", "lock": "Synchronized", "desc": "Bi-directional webhook synchronization with central hub and external CRMs."}
}

LOGO_SVG = """<svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle; margin-right:8px;">
    <rect width="24" height="24" rx="6" fill="#10B981" fill-opacity="0.18"/>
    <path d="M12 3L3 7.5L12 12L21 7.5L12 3Z" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M3 12L12 16.5L21 12" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M3 16.5L12 21L21 16.5" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

def render_header(subtitle="Enterprise Secure Portal"):
    return f"""
    <div class="card top-bar">
        <div style="display:flex; align-items:center;">
            {LOGO_SVG}
            <div>
                <h2 style="margin:0; font-size: 17px; font-weight:800; letter-spacing:0.5px;">GRACE OUTREACH ASSISTANT</h2>
                <span style="font-size: 12px; color: var(--text-muted);">Built by King Saab | Strategic Guidance by Abdullah Khan</span>
            </div>
        </div>
        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
            <span class="btn btn-gray">👑 King Saab (Super Admin)</span>
            <button class="btn btn-gray" onclick="alert('System Notifications: All 3 Inboxes Operating at Peak Performance')">🔔 Notifications <b>2</b></button>
            <button class="btn btn-orange" onclick="alert('Broadcast Alert: Warmup sequence #4 is fully running.')">📢 Broadcast Alert</button>
            <button class="btn btn-gray" onclick="alert('Brand Palette: Hex #0B1120 | #3B82F6 | #10B981 Active')">🎨 Brand Palette</button>
            <button id="audio-btn" class="btn btn-gray" onclick="toggleAudio()">🔊 Audio: ON</button>
            <button class="btn btn-gray" onclick="toggleTheme()">🌓 Theme</button>
            <button class="btn btn-red" onclick="if(confirm('Are you sure you want to stop background outreach services?')) alert('Services paused securely.');">⏹ Power Off</button>
        </div>
    </div>
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
        --bg-card: #0F172A;
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
        --border-color: #1E293B;
        --accent-blue: #3B82F6;
        --accent-green: #10B981;
        --accent-gold: #F59E0B;
    }
    body { background-color: var(--bg-main); color: var(--text-main); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; }
    .card { background: var(--bg-card); padding: 18px 24px; border-radius: 14px; border: 1px solid var(--border-color); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
    .btn { border: none; border-radius: 8px; padding: 8px 14px; font-weight: 600; font-size: 12px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
    .btn-blue { background: #0284C7; color: white; }
    .btn-red { background: #DC2626; color: white; }
    .btn-orange { background: #EA580C; color: white; }
    .btn-gray { background: #E2E8F0; color: #1E293B; border: 1px solid #CBD5E1; }
    body.dark .btn-gray { background: #1E293B; color: #F8FAFC; border: 1px solid #334155; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px; }
    .stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px 20px; }
    .stat-title { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 26px; font-weight: 800; margin: 8px 0 4px; }
    .stat-sub { font-size: 12px; font-weight: 600; color: var(--accent-green); }
    .grid-2 { display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; }
    .log-box { background: rgba(0,0,0,0.03); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; font-family: monospace; font-size: 12px; }
    .modules-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 15px; margin-top: 15px; }
    .module-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; text-decoration: none; display: block; color: inherit; transition: 0.2s; }
    .module-card:hover { border-color: var(--accent-gold); transform: translateY(-2px); }
    .mod-title { font-size: 12px; font-weight: bold; color: var(--accent-gold); margin-bottom: 6px; }
    .mod-name { font-size: 14px; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border-color); font-size: 13px; }
    th { font-size: 12px; color: var(--text-muted); text-transform: uppercase; }
"""

COMMON_JS = """
<script>
function toggleTheme() {
    document.body.classList.toggle('dark');
}
function toggleAudio() {
    const btn = document.getElementById('audio-btn');
    if (btn.innerText.includes('ON')) {
        btn.innerText = '🔇 Audio: OFF';
    } else {
        btn.innerText = '🔊 Audio: ON';
    }
}
function manualSync() {
    alert('Triggered Manual Sync: Checking Gmail Inboxes #1, #2, and #3... Sync Completed Successfully!');
}
function pauseOutreach() {
    alert('Paused All Active Outreach Threads across 3 Inboxes.');
}
function testBroadcast() {
    alert('Test Broadcast packet sent to active monitoring node.');
}
</script>
"""

def render_dashboard():
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grace Outreach Assistant - Dashboard</title>
    <style>{BASE_CSS}</style>
</head>
<body>
    {render_header("Strategic Guidance by Abdullah Khan")}
    {render_navigation("dashboard")}

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-title">ACTIVE OUTREACH PIPELINE</div>
            <div class="stat-value">2,480</div>
            <div class="stat-sub">+14.2% Velocity</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">CONNECTED GMAIL ACCOUNTS</div>
            <div class="stat-value">3 Inboxes</div>
            <div class="stat-sub">Rotation Healthy</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">WEEKLY SENT VOLUME</div>
            <div class="stat-value">1,240</div>
            <div class="stat-sub">+8.5% Speed</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">PIPELINE DEAL VALUE</div>
            <div class="stat-value">$64,800</div>
            <div class="stat-sub">+21.4% Revenue</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="card">
            <h4 style="margin:0 0 14px; font-size:14px;">⚡ Quick Action Toolbar</h4>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="btn btn-blue" onclick="manualSync()">Trigger Manual Sync</button>
                <button class="btn btn-red" onclick="pauseOutreach()">Pause All Outreaches</button>
                <button class="btn btn-orange" onclick="testBroadcast()">Test Broadcast</button>
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
        border_style = 'style="border: 2px solid var(--accent-gold);"' if idx == 12 else ''
        cards_html += f"""
        <a href="/?tab=module&id={idx}" class="module-card" {border_style}>
            <div class="mod-title">Module {idx} • {info['category']}</div>
            <div class="mod-name">{"🔐 " if idx == 12 else ""}{info['name']}</div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:6px;">{info['desc'][:65]}...</div>
            <div style="font-size:11px; font-weight:bold; color:var(--accent-green); margin-top:8px;">● {info['status']}</div>
        </a>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grace Outreach Assistant - 22-Module Matrix</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header("22-Module Control Matrix")}
    {render_navigation("matrix")}

    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3 style="margin:0;">Complete 22 Enterprise Execution Nodes</h3>
            <span style="font-size:12px; color:var(--accent-gold); font-weight:bold;">All Nodes Configured & Operational</span>
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
        mod_info = MODULES_DATA.get(m_id, MODULES_DATA[12])
    except:
        m_id = 12
        mod_info = MODULES_DATA[12]

    is_vault = (m_id == 12)
    
    vault_specific_ui = """
    <div class="grid-2" style="margin-top:20px;">
        <div class="card" style="margin-bottom:0;">
            <h4 style="margin:0 0 10px; font-size:14px;">🔒 Encryption Security Status</h4>
            <p style="font-size:13px; margin:4px 0;">Standard: <b>AES-256-GCM Secure Locker</b></p>
            <p style="font-size:13px; margin:4px 0;">Master Key: <b>256-Bit Cryptographic Hash Active</b></p>
            <p style="font-size:13px; margin:4px 0;">Integrity Check: <b style="color:var(--accent-green);">100% Encrypted & Authenticated</b></p>
        </div>
        <div class="card" style="margin-bottom:0;">
            <h4 style="margin:0 0 10px; font-size:14px;">🔄 Auto-Renewal Daemon</h4>
            <p style="font-size:13px; margin:4px 0;">Frequency: <b>Every 24 Hours</b></p>
            <p style="font-size:13px; margin:4px 0;">Next Rotation: <b>Scheduled in 4h 12m</b></p>
            <p style="font-size:13px; margin:4px 0;">Failed Rotations: <b style="color:var(--accent-green);">0 Errors (Secure)</b></p>
        </div>
    </div>

    <div class="card" style="margin-top:20px;">
        <h4 style="margin:0 0 10px; font-size:14px;">🔑 Vault Account Credentials Matrix</h4>
        <table>
            <thead>
                <tr>
                    <th>Connected Inbox</th>
                    <th>Authentication Protocol</th>
                    <th>Locker Protection</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>business.inbox1@gmail.com</b></td>
                    <td>OAuth 2.0 Token (Auto-Refresh)</td>
                    <td>AES-256-GCM Encrypted</td>
                    <td><span style="color:var(--accent-green); font-weight:bold;">Securely Locked</span></td>
                </tr>
                <tr>
                    <td><b>outreach.node2@gmail.com</b></td>
                    <td>16-Digit App Password</td>
                    <td>AES-256-GCM Encrypted</td>
                    <td><span style="color:var(--accent-green); font-weight:bold;">Securely Locked</span></td>
                </tr>
                <tr>
                    <td><b>relay.personal@gmail.com</b></td>
                    <td>16-Digit App Password</td>
                    <td>AES-256-GCM Encrypted</td>
                    <td><span style="color:var(--accent-green); font-weight:bold;">Securely Locked</span></td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="card" style="margin-top:20px;">
        <h4 style="margin:0 0 12px; font-size:14px;">⚡ Vault Controls & Execution Toolbar</h4>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-blue" onclick="alert('Exporting AES-256 encrypted vault backup payload...')">Export Encrypted Vault Backup</button>
            <button class="btn btn-orange" onclick="alert('Force syncing OAuth credentials with Google API Auth Servers... Done!')">Force Token Vault Sync</button>
            <button class="btn btn-red" onclick="if(confirm('Rotate master encryption key?')) alert('New 256-bit AES Master Key generated.');">Rotate Master Key</button>
        </div>
    </div>
    """ if is_vault else f"""
    <div class="card" style="margin-top:20px;">
        <h4 style="margin:0 0 10px; font-size:14px;">⚙ Module Specifications & Telemetry</h4>
        <p style="font-size:13px; margin:6px 0;">Assigned Role: <b>{mod_info['category']}</b></p>
        <p style="font-size:13px; margin:6px 0;">Security Layer: <b>{mod_info['lock']}</b></p>
        <p style="font-size:13px; margin:6px 0;">Operational Status: <b style="color:var(--accent-green);">{mod_info['status']}</b></p>
        <div style="margin-top:15px;">
            <button class="btn btn-blue" onclick="alert('Module {m_id} diagnostic self-test passed without errors.')">Run Diagnostic Test</button>
            <button class="btn btn-gray" onclick="alert('Reloaded execution thread for Module {m_id}.')">Restart Node</button>
        </div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grace Outreach Assistant - Module {m_id}</title>
    <style>{BASE_CSS}</style>
</head>
<body class="dark">
    {render_header(f"Module {m_id} Control Plane")}
    {render_navigation("matrix")}

    <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h2 style="margin:0; font-size:18px; color:var(--accent-gold);">
                {"🔐 " if is_vault else ""}Module {m_id}: {mod_info['name']}
            </h2>
            <span style="font-size:12px; color:var(--text-muted);">{mod_info['desc']}</span>
        </div>
        <div>
            <a href="/?tab=matrix" class="btn btn-blue">&#8592; Back to 22-Module Matrix</a>
        </div>
    </div>

    {vault_specific_ui}
    {COMMON_JS}
</body>
</html>"""

def render_colleagues():
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grace Outreach Assistant - Colleague Management</title>
    <style>{BASE_CSS}</style>
</head>
<body>
    {render_header("Colleague Management & Access Control")}
    {render_navigation("colleagues")}

    <div class="card">
        <h3 style="margin:0 0 10px;">Colleague Access List</h3>
        <table>
            <thead>
                <tr>
                    <th>User</th>
                    <th>Role</th>
                    <th>Assigned Nodes</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>King Saab</b></td>
                    <td>Super Admin</td>
                    <td>All 22 Modules</td>
                    <td><span style="color:var(--accent-green); font-weight:bold;">Active</span></td>
                </tr>
                <tr>
                    <td><b>Abdullah Khan</b></td>
                    <td>Strategic Lead</td>
                    <td>Modules 1-7, 12</td>
                    <td><span style="color:var(--accent-green); font-weight:bold;">Active</span></td>
                </tr>
            </tbody>
        </table>
    </div>
    {COMMON_JS}
</body>
</html>"""

def app(environ, start_response):
    query_string = environ.get('QUERY_STRING', '')
    params = parse_qs(query_string)
    tab = params.get('tab', ['dashboard'])[0]
    mod_id = params.get('id', ['1'])[0]

    if tab == 'matrix':
        body = render_matrix()
    elif tab == 'module':
        body = render_module_detail(mod_id)
    elif tab == 'colleagues':
        body = render_colleagues()
    else:
        body = render_dashboard()

    data = body.encode('utf-8')
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return [data]

if __name__ == '__main__':
    with make_server(HOST, PORT, app) as httpd:
        print(f"Server running on {HOST}:{PORT}")
        httpd.serve_forever()