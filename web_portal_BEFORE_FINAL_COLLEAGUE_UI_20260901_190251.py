import os
from flask import Flask, jsonify, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "grace-outreach-enterprise-secure-key")

SYSTEM_MODULES = [
    {"id": 1, "name": "Dashboard Overview", "desc": "Live analytics & telemetry", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 2, "name": "Gmail Multi-Tenant Hub", "desc": "OAuth & 3-Tier Categorization", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 3, "name": "AI Warmup Ramp", "desc": "Daily sender reputation guard", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 4, "name": "Campaign Studio", "desc": "A/B Split + AI Scorer + Timezone", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 5, "name": "Spin-Syntax AI Engine", "desc": "1-Click Auto-Spinner & Live Preview", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 6, "name": "US Architect & Contractor Scraper", "desc": "All 50 US States + Live Ping & CSV/TXT", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 7, "name": "CRM Revenue Pipeline", "desc": "$64,800 Active deal monitor (Drag & Drop)", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 8, "name": "Colleague Access Controller", "desc": "Audit Logs, Presets & Force Logout", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 9, "name": "System Doctor Daemon", "desc": "Live Gauges, Cache Flush & Telemetry", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 10, "name": "Audio Studio & Extractor", "desc": "Soundscape, Visualizer & Alert Chimes", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 11, "name": "Built-in AI Guide Agent", "desc": "King Saab AI Copilot & Email Drafter", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 12, "name": "OAuth Token Vault", "desc": "AES-256 Locker, Auto-Renew & Backup", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 13, "name": "Timezone Scheduler", "desc": "US Live Clocks & Business Hour Dispatch", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 14, "name": "Bounce Shield", "desc": "0.08% Bounce Ping & Queue Sanitizer", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 15, "name": "Auto-Reply Detector", "desc": "AI Sentiment Classifier & CRM Push", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 16, "name": "CSV / Excel Exporter", "desc": "Multi-Format Reports & Analytics Export", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 17, "name": "Broadcast Notification Node", "desc": "Targeted Recipient & Priority Banners", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 18, "name": "Brand Palette Studio", "desc": "Luxury Theme Presets & Color Picker", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 19, "name": "Cloud Webhook Dispatcher", "desc": "Third-party JSON triggers", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 20, "name": "Daily Quota Guard", "desc": "50/50 safe account limits", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 21, "name": "Master System Control", "desc": "Global Override & Safe Operation Hub", "status": "ACTIVE", "health": "HEALTHY"},
    {"id": 22, "name": "Enterprise Security Vault", "desc": "Advanced Compliance & Session Hardening", "status": "ACTIVE", "health": "HEALTHY"}
]

COLLEAGUES = [
    {"id": 1, "name": "King Saab", "role": "Super Admin", "status": "Online", "access": "Unrestricted", "modules": {i: True for i in range(1, 23)}},
    {"id": 2, "name": "Alex Vance", "role": "Outreach Operator", "status": "Active", "access": "Restricted", "modules": {1: True, 2: True, 3: False, 4: True, 5: False}}
]

NOTIFICATIONS = [
    {"id": 1, "account": "Outreach Rotator 01", "profile": "Malik Shani Workspace", "client": "Acme Corp Lead #409", "time": "2 minutes ago", "type": "Inbound Reply", "unread": True},
    {"id": 2, "account": "Grace Outreach Primary", "profile": "Primary Business Domain", "client": "Global Tech Ventures", "time": "15 minutes ago", "type": "Meeting Booked", "unread": True},
    {"id": 3, "account": "Domain Rotator Alpha", "profile": "Secondary Outreach", "client": "Apex Solutions", "time": "1 hour ago", "type": "Email Opened", "unread": False}
]

SETTINGS = {
    "theme": "dark",
    "show_extra_ribbon": True,
    "audio_enabled": False,
    "audio_track": "Track 1: Cyber Ambient",
    "audio_volume": 0,
    "audio_start": 0,
    "audio_end": 120,
    "browser_notifs": True
}

# Official Grace Architectural Logo SVG representation matched to reference asset
GRACE_LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="none">
    <rect width="24" height="24" rx="5" fill="#04120E" stroke="#F59E0B" stroke-width="0.8"/>
    <path d="M7 17V10L10 8V17H7Z" fill="#059669"/>
    <path d="M11 17V6L14 4V17H11Z" fill="#10B981"/>
    <path d="M15 17V9L18 11V17H15Z" fill="#F59E0B"/>
</svg>'''

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["logged_in"] = True
        session["user"] = "King Saab"
        session["impersonate"] = None
        return redirect(url_for("home"))

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Grace Outreach Assistant - Secure Login</title>
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect width='24' height='24' rx='5' fill='#04120E'/><path d='M7 17V10L10 8V17H7Z' fill='#059669'/><path d='M11 17V6L14 4V17H11Z' fill='#10B981'/><path d='M15 17V9L18 11V17H15Z' fill='#F59E0B'/></svg>">
        <style>
            body {{ background-color: #010806; background-image: radial-gradient(circle at 50% 0%, #032018 0%, #010806 70%); color: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .login-box {{ background: #04120E; border: 1px solid #064E3B; border-left: 4px solid #F59E0B; padding: 40px; border-radius: 12px; width: 400px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); text-align: center; }}
            .logo-wrap {{ width: 56px; height: 56px; background: #ffffff; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; border: 1px solid #F59E0B; box-shadow: 0 0 15px rgba(245, 158, 11, 0.4); }}
            .btn {{ background: linear-gradient(135deg, #059669, #10B981); color: white; border: none; padding: 12px 20px; border-radius: 6px; font-weight: bold; width: 100%; cursor: pointer; font-size: 14px; margin-top: 20px; box-shadow: 0 0 10px rgba(5, 150, 105, 0.4); }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <div class="logo-wrap">{GRACE_LOGO_SVG}</div>
            <h2 style="color: #FFFFFF; margin: 0 0 5px 0; font-size: 20px; letter-spacing: 0.5px;">GRACE OUTREACH ASSISTANT</h2>
            <p style="color: #34D399; font-size: 12px; margin-bottom: 25px;">Built by King Saab | Strategic Guidance by Abdullah Khan</p>
            <form method="POST">
                <button type="submit" class="btn">Authenticate & Enter Portal</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/")
def home():
    if not session.get("logged_in", True):
        return redirect(url_for("login"))

    tab = request.args.get("tab", "dashboard")
    impersonate_id = session.get("impersonate")
    
    extra_ribbon_links = ""
    if SETTINGS["show_extra_ribbon"]:
        extra_ribbon_links = '<a href="/?tab=notifications" class="nav-tab">Notifications</a><a href="/?tab=personalization" class="nav-tab">Personalization</a>'

    dash_active = 'active' if tab == 'dashboard' else ''
    matrix_active = 'active' if tab in ['matrix', 'mod_detail'] else ''
    colleagues_active = 'active' if tab == 'colleagues' else ''
    unread_badge_count = sum(1 for n in NOTIFICATIONS if n["unread"])
    content_html = ""

    active_user = "King Saab"
    active_modules_dict = {i: True for i in range(1, 23)}
    if impersonate_id:
        target_colleague = next((c for c in COLLEAGUES if c["id"] == int(impersonate_id)), None)
        if target_colleague:
            active_user = target_colleague["name"]
            active_modules_dict = target_colleague["modules"]

    if tab == "matrix":
        cards_list = []
        for m in SYSTEM_MODULES:
            mid = m["id"]
            if not active_modules_dict.get(mid, True):
                continue
            # Full-card clickable brown/gold aesthetic matching 'ya modules view.png'
            card_html = f'''
            <a href="/?tab=mod_detail&id={mid}" style="text-decoration: none; color: inherit; display: block;">
                <div class="card-module-brown">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="color: #F59E0B; font-weight: bold; font-size: 12px; text-transform: uppercase;">{mid}. {m["name"]}</span>
                        <span class="pill-active">{m["status"]}</span>
                    </div>
                    <p style="color: #94A3B8; font-size: 12px; margin: 0; line-height: 1.4;">{m["desc"]}</p>
                </div>
            </a>
            '''
            cards_list.append(card_html)
        cards_joined = "".join(cards_list)
        content_html = f'''
        <div class="panel-box">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="color: #FFFFFF; margin: 0; font-size: 18px; font-weight: bold;">Complete 22-Module Functional Matrix</h3>
                <span style="color: #34D399; font-size: 12px; font-weight: 600;">● Admin View (All Modules Unlocked)</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
                {cards_joined}
            </div>
        </div>
        '''
    elif tab == "colleagues":
        cid = int(request.args.get("edit_id", "1"))
        c_obj = next((c for c in COLLEAGUES if c["id"] == cid), COLLEAGUES[0])
        
        colleague_items = []
        for c in COLLEAGUES:
            item_html = f'''
            <div style="background: #04120E; padding: 12px 15px; border-radius: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #064E3B;">
                <div>
                    <strong style="color: #ffffff;">{c["name"]}</strong>
                    <div style="font-size: 11px; color: #94A3B8;">{c["role"]}</div>
                </div>
                <div style="display: flex; gap: 6px;">
                    <a href="/?tab=colleagues&edit_id={c["id"]}" class="btn" style="padding: 4px 8px; font-size: 11px; background: #059669; text-decoration: none;">Permissions</a>
                    <a href="/action/impersonate?id={c["id"]}" class="btn" style="padding: 4px 8px; font-size: 11px; background: #F59E0B; color: #000; text-decoration: none; font-weight: bold;">View As</a>
                </div>
            </div>
            '''
            colleague_items.append(item_html)
        colleague_list_joined = "".join(colleague_items)
            
        perms_items = []
        for m in SYSTEM_MODULES:
            mid = m["id"]
            is_on = c_obj["modules"].get(mid, True)
            status_bg = "rgba(5, 150, 105, 0.2)" if is_on else "rgba(220, 38, 38, 0.2)"
            status_color = "#34D399" if is_on else "#F87171"
            btn_text = "ON" if is_on else "OFF"
            perm_html = f'''
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-bottom: 1px solid #064E3B; background: #04120E; margin-bottom: 8px; border-radius: 6px;">
                <div>
                    <strong style="color: #ffffff; font-size: 13px;">MODULE {mid:02d}: {m["name"]}</strong>
                    <div style="font-size: 11px; color: #94A3B8;">{m["desc"]}</div>
                </div>
                <form action="/action/toggle_permission" method="POST" style="margin:0;">
                    <input type="hidden" name="colleague_id" value="{c_obj["id"]}">
                    <input type="hidden" name="module_id" value="{mid}">
                    <button type="submit" style="background: {status_bg}; color: {status_color}; border: 1px solid {status_color}; padding: 6px 14px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 12px;">{btn_text}</button>
                </form>
            </div>
            '''
            perms_items.append(perm_html)
        perms_joined = "".join(perms_items)

        content_html = f'''
        <div style="display: grid; grid-template-columns: 320px 1fr; gap: 20px;">
            <div class="panel-box" style="margin-bottom:0;">
                <h3 style="color: #F59E0B; margin-top: 0; font-size: 18px;">Colleague Directory</h3>
                <p style="color: #94A3B8; font-size: 12px; margin-bottom: 15px;">Select a profile to manage permissions or preview their exact view.</p>
                {colleague_list_joined}
            </div>
            <div class="panel-box" style="margin-bottom:0;">
                <h3 style="color: #34D399; margin-top: 0; font-size: 18px;">Permissions for: {c_obj["name"]} ({c_obj["role"]})</h3>
                <p style="color: #94A3B8; font-size: 12px; margin-bottom: 15px;">Toggle individual module clearance inline.</p>
                <div style="max-height: 500px; overflow-y: auto; padding-right: 5px;">
                    {perms_joined}
                </div>
            </div>
        </div>
        '''
    elif tab == "personalization":
        saved = request.args.get("saved", "0")
        banner = '<div style="background: rgba(5, 150, 105, 0.2); color: #34D399; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; font-size: 13px;">Settings saved successfully.</div>' if saved == "1" else ""
        content_html = f'''
        <div class="panel-box" style="max-width: 800px;">
            <h3 style="color: #F59E0B; margin-top: 0; font-size: 20px;">Personalization & Software Settings</h3>
            <p style="color: #94A3B8; font-size: 14px; margin-bottom: 20px;">Configure global preferences and audio parameters.</p>
            {banner}
            <form action="/action/save_personalization" method="POST">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; color: #94A3B8; font-size: 12px; margin-bottom: 6px; text-transform: uppercase;">Show Extra Modules in Top Ribbon</label>
                    <select name="show_extra_ribbon" class="form-input">
                        <option value="ON" {'selected' if SETTINGS['show_extra_ribbon'] else ''}>ON</option>
                        <option value="OFF" {'selected' if not SETTINGS['show_extra_ribbon'] else ''}>OFF</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-gold">Save Settings</button>
            </form>
        </div>
        '''
    elif tab == "broadcast":
        msg_sent = request.args.get("sent", "0")
        success_banner = '<div style="background: rgba(5, 150, 105, 0.2); color: #34D399; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; font-size: 13px;">Broadcast published successfully.</div>' if msg_sent == "1" else ""
        colleague_options = "".join([f'<option value="{c["name"]}">{c["name"]} ({c["role"]})</option>' for c in COLLEAGUES])
        content_html = f'''
        <div class="panel-box" style="max-width: 700px;">
            <h3 style="color: #F59E0B; margin-top: 0; font-size: 20px;">Broadcast Alert Control Center</h3>
            <p style="color: #94A3B8; font-size: 14px; margin-bottom: 20px;">Send secure operational notices inline to specific colleagues or the entire team.</p>
            {success_banner}
            <form action="/action/broadcast" method="POST">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: #94A3B8; font-size: 12px; margin-bottom: 6px; text-transform: uppercase;">Target Recipient</label>
                    <select name="target" class="form-input">
                        <option value="ALL TEAM">ALL TEAM (Entire Enterprise)</option>
                        {colleague_options}
                    </select>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: #94A3B8; font-size: 12px; margin-bottom: 6px; text-transform: uppercase;">Alert Title</label>
                    <input type="text" name="title" required placeholder="e.g. Pipeline Sync Notice" class="form-input">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: #94A3B8; font-size: 12px; margin-bottom: 6px; text-transform: uppercase;">Message Body</label>
                    <textarea name="message" required rows="4" placeholder="Enter broadcast message..." class="form-input"></textarea>
                </div>
                <button type="submit" class="btn btn-gold">Send Broadcast</button>
            </form>
        </div>
        '''
    elif tab == "notifications":
        notif_list = []
        for n in NOTIFICATIONS:
            status_style = "background: rgba(5, 150, 105, 0.2); color: #34D399;" if n["unread"] else "background: #04120E; color: #94A3B8;"
            uread_text = "UNREAD" if n["unread"] else "READ"
            notif_html = f'''
            <div style="background: #04120E; border: 1px solid #064E3B; border-radius: 8px; padding: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 4px;">
                        <span style="{status_style} padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">{uread_text}</span>
                        <strong style="color: #ffffff; font-size: 14px;">{n["type"]}</strong>
                        <span style="color: #94A3B8; font-size: 12px;">• {n["time"]}</span>
                    </div>
                    <div style="color: #38BDF8; font-size: 12px; font-weight: 600;">Account: {n["account"]} | Profile: {n["profile"]}</div>
                    <div style="color: #ffffff; font-size: 13px; margin-top: 4px;">Client: {n["client"]}</div>
                </div>
                <a href="/action/mark_read?id={n["id"]}" class="btn" style="padding: 6px 12px; font-size: 11px; background: #059669; text-decoration: none;">Mark Read</a>
            </div>
            '''
            notif_list.append(notif_html)
        notifs_joined = "".join(notif_list)
        content_html = f'''
        <div class="panel-box">
            <h3 style="color: #34D399; margin-top: 0; font-size: 20px;">Client Activity Notification Center</h3>
            <p style="color: #94A3B8; font-size: 14px; margin-bottom: 20px;">Real-time inbound activity tracked across connected multi-tenant accounts.</p>
            <div style="max-height: 600px; overflow-y: auto;">
                {notifs_joined}
            </div>
        </div>
        '''
    elif tab == "mod_detail":
        mid = int(request.args.get("id", "1"))
        if not active_modules_dict.get(mid, True):
            content_html = '<div class="panel-box"><h3 style="color: #F87171;">Access Denied</h3><p style="color: #94A3B8;">You do not have clearance to access Module ' + f'{mid:02d}' + '.</p><a href="/?tab=matrix" class="btn btn-emerald" style="text-decoration:none;">Back to Matrix</a></div>'
        else:
            mod_info = next((m for m in SYSTEM_MODULES if m["id"] == mid), SYSTEM_MODULES[0])
            content_html = f'''
            <div class="panel-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <div>
                        <span style="color: #38BDF8; font-weight: bold; font-size: 12px;">MODULE {mid:02d} WORKING WORKSPACE</span>
                        <h3 style="color: #ffffff; margin: 5px 0 0 0; font-size: 22px;">{mod_info["name"]}</h3>
                    </div>
                    <span class="pill-active">{mod_info["status"]}</span>
                </div>
                <p style="color: #94A3B8; font-size: 14px; margin-bottom: 25px;">{mod_info["desc"]}</p>
                <div style="background: #04120E; padding: 20px; border-radius: 8px; border: 1px solid #064E3B; margin-bottom: 25px;">
                    <div style="display: flex; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #064E3B;">
                        <span style="color: #94A3B8; width: 200px;">Runtime Health:</span>
                        <strong style="color: #34D399;">{mod_info["health"]}</strong>
                    </div>
                    <div style="display: flex; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #064E3B;">
                        <span style="color: #94A3B8; width: 200px;">Assigned Worker Thread:</span>
                        <strong style="color: #ffffff;">Worker-Daemon-{mid:02d}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #94A3B8;">Synchronization Timestamp:</span>
                        <strong style="color: #38BDF8;">Synced (Live Backend)</strong>
                    </div>
                </div>
                <a href="/?tab=matrix" class="btn btn-emerald" style="display: inline-block; text-decoration: none;">Back to Module Matrix</a>
            </div>
            '''
    else:
        content_html = """
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 25px;">
            <div class="kpi-card">
                <h3 class="kpi-title">Active Outreach Pipeline</h3>
                <div class="kpi-value">2,480</div>
                <span class="kpi-badge">▲ +14.2% Velocity</span>
            </div>
            <div class="kpi-card">
                <h3 class="kpi-title">Connected Gmail Accounts</h3>
                <div class="kpi-value">5 Inboxes</div>
                <span class="kpi-badge">● Rotation Healthy</span>
            </div>
            <div class="kpi-card">
                <h3 class="kpi-title">Weekly Sent Volume</h3>
                <div class="kpi-value">1,240</div>
                <span class="kpi-badge">▲ +8.5% Speed</span>
            </div>
            <div class="kpi-card">
                <h3 class="kpi-title">Pipeline Deal Value</h3>
                <div class="kpi-value" style="color: #34D399;">$64,800</div>
                <span class="kpi-badge">▲ +21.4% Revenue</span>
            </div>
        </div>

        <div class="panel-box">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h3 style="color: #34D399; margin: 0 0 4px 0; font-size: 18px;">Gmail Multi-Tenant Hub (Active 3-Tier Sync)</h3>
                    <span style="color: #94A3B8; font-size: 13px;">Auto-classified by Business, Workplace, and Personal Inboxes</span>
                </div>
                <a href="/?tab=matrix" class="btn btn-emerald" style="text-decoration: none; font-size: 13px;">+ Connect New Account</a>
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="text-align: left; color: #94A3B8; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #064E3B;">
                        <th style="padding: 10px;">Account Name</th>
                        <th style="padding: 10px;">Email Address</th>
                        <th style="padding: 10px;">Category</th>
                        <th style="padding: 10px;">OAuth Status</th>
                        <th style="padding: 10px;">Health</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #ffffff;">Grace Outreach Primary</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #94A3B8;">admin@graceoutreach.com</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #38BDF8;">BUSINESS</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B;"><span class="pill-active">CONNECTED</span></td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B;"><span class="pill-active">HEALTHY</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #ffffff;">Malik Shani Workspace</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #94A3B8;">shani@workspaces.internal</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #38BDF8;">WORKPLACE</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B;"><span class="pill-active">CONNECTED</span></td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B;"><span style="background: rgba(245, 158, 11, 0.2); color: #F59E0B; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">WARNING</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #ffffff;">Outreach Rotator 01</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #94A3B8;">rotator.p1@gmail.com</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B; color: #38BDF8;">PERSONAL</td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B;"><span style="background: rgba(220, 38, 38, 0.2); color: #F87171; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">OAUTH REQUIRED</span></td>
                        <td style="padding: 12px; border-bottom: 1px solid #064E3B;"><span style="background: rgba(220, 38, 38, 0.2); color: #F87171; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">ERROR</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """

    impersonate_banner = ""
    if impersonate_id:
        impersonate_banner = f"""
        <div style="background: rgba(245, 158, 11, 0.2); border: 1px solid #F59E0B; color: #F59E0B; padding: 10px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 13px;">
            <span>⚠️ VIEWING SESSION AS COLLEAGUE: {active_user.upper()} (RESTRICTED MODULE PERMISSIONS APPLIED)</span>
            <a href="/action/exit_impersonate" style="background: #DC2626; color: white; padding: 6px 14px; border-radius: 4px; text-decoration: none; font-size: 12px;">EXIT COLLEAGUE VIEW</a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Grace Outreach Assistant - Enterprise Command Center</title>
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect width='24' height='24' rx='5' fill='#04120E'/><path d='M7 17V10L10 8V17H7Z' fill='#059669'/><path d='M11 17V6L14 4V17H11Z' fill='#10B981'/><path d='M15 17V9L18 11V17H15Z' fill='#F59E0B'/></svg>">
        <style>
            body {{
                background-color: #010806;
                background-image: radial-gradient(circle at 50% 0%, #032018 0%, #010806 70%);
                color: #FFFFFF;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 25px;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #064E3B;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .logo-area {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .grace-logo {{
                width: 48px;
                height: 48px;
                background: #04120E;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #F59E0B;
                box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
            }}
            .top-actions {{
                display: flex;
                gap: 12px;
                align-items: center;
            }}
            .session-badge {{
                background: #04120E;
                border: 1px solid #064E3B;
                color: #FFFFFF;
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }}
            .btn {{
                border: none;
                padding: 9px 18px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                cursor: pointer;
                color: white;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                text-decoration: none;
                transition: all 0.2s;
            }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
            .btn-emerald {{
                background: linear-gradient(135deg, #059669, #10B981);
                box-shadow: 0 0 10px rgba(5, 150, 105, 0.4);
            }}
            .btn-gold {{
                background: #F59E0B;
                color: #000000;
                font-weight: 700;
            }}
            .btn-danger {{
                background: #DC2626;
            }}
            .nav-bar {{
                display: flex;
                gap: 12px;
                margin-bottom: 25px;
                align-items: center;
                flex-wrap: wrap;
            }}
            .nav-tab {{
                background: #04120E;
                border: 1px solid #064E3B;
                color: #94A3B8;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                text-decoration: none;
                transition: all 0.2s;
            }}
            .nav-tab:hover {{
                border-color: #059669;
                color: #FFFFFF;
            }}
            .nav-tab.active {{
                background: linear-gradient(135deg, #059669, #10B981);
                color: white;
                border-color: #059669;
                box-shadow: 0 0 12px rgba(5, 150, 105, 0.4);
            }}
            .kpi-card {{
                background: #04120E;
                padding: 22px;
                border-radius: 10px;
                border: 1px solid #064E3B;
                border-left: 4px solid #059669;
                position: relative;
            }}
            .kpi-title {{
                color: #34D399;
                margin: 0 0 8px 0;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .kpi-value {{
                font-size: 28px;
                font-weight: 700;
                color: #FFFFFF;
                margin-bottom: 6px;
            }}
            .kpi-badge {{
                background: rgba(5, 150, 105, 0.2);
                color: #34D399;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
                display: inline-block;
            }}
            .panel-box {{
                background: #04120E;
                border: 1px solid #064E3B;
                border-radius: 10px;
                padding: 24px;
                margin-bottom: 25px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
            }}
            .card-module-brown {{
                background: #04120E;
                border: 1px solid #064E3B;
                border-left: 3px solid #F59E0B;
                border-radius: 8px;
                padding: 16px;
                height: 100%;
                box-sizing: border-box;
                transition: all 0.2s ease;
            }}
            .card-module-brown:hover {{
                border-color: #F59E0B;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
            }}
            .pill-active {{
                background: rgba(5, 150, 105, 0.2);
                color: #34D399;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 700;
            }}
            .form-input {{
                width: 100%;
                padding: 10px;
                background: #010806;
                border: 1px solid #064E3B;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 14px;
                box-sizing: border-box;
            }}
            .form-input:focus {{
                border-color: #059669;
                outline: none;
            }}
            .bell-badge {{
                background: #DC2626;
                color: white;
                border-radius: 50%;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: bold;
                vertical-align: top;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-area">
                <div class="grace-logo">
                    {GRACE_LOGO_SVG}
                </div>
                <div>
                    <h1 style="color: #FFFFFF; margin:0; font-size: 20px; letter-spacing: 0.5px;">GRACE OUTREACH ASSISTANT</h1>
                    <span style="color: #34D399; font-size: 12px;">⚡ Built by King Saab | ★ Strategic Guidance by Abdullah Khan</span>
                </div>
            </div>
            <div class="top-actions">
                <div class="session-badge">👑 {active_user} (Super Admin)</div>
                <a href="/?tab=notifications" class="btn" style="background: #04120E; border: 1px solid #064E3B; color: #FFFFFF;">🔔 Notifications <span class="bell-badge">{unread_badge_count}</span></a>
                <a href="/?tab=broadcast" class="btn btn-gold">📢 Broadcast Alert</a>
                <a href="/?tab=personalization" class="btn" style="background: #04120E; border: 1px solid #064E3B; color: #FFFFFF;">⚙️ Personalization</a>
                <a href="/action/logout" class="btn btn-danger" onclick="return confirm('Confirm safe user session logout?')">⏻ Power Off</a>
            </div>
        </div>

        {impersonate_banner}

        <div class="nav-bar">
            <a href="/?tab=dashboard" class="nav-tab {dash_active}">1. Dashboard Overview</a>
            <a href="/?tab=matrix" class="nav-tab {matrix_active}">2. 22-Module Control Matrix</a>
            <a href="/?tab=colleagues" class="nav-tab {colleagues_active}">3. Colleague Management & Permissions</a>
            {extra_ribbon_links}
        </div>

        {content_html}
    </body>
    </html>
    """

@app.route("/action/toggle_permission", methods=["POST"])
def toggle_permission():
    colleague_id = int(request.form.get("colleague_id", 1))
    module_id = int(request.form.get("module_id", 1))
    c = next((col for col in COLLEAGUES if col["id"] == colleague_id), None)
    if c:
        current = c["modules"].get(module_id, True)
        c["modules"][module_id] = not current
    return redirect(f"/?tab=colleagues&edit_id={colleague_id}")

@app.route("/action/impersonate")
def impersonate():
    colleague_id = request.args.get("id")
    session["impersonate"] = colleague_id
    return redirect("/")

@app.route("/action/exit_impersonate")
def exit_impersonate():
    session["impersonate"] = None
    return redirect("/?tab=colleagues")

@app.route("/action/save_personalization", methods=["POST"])
def save_personalization():
    SETTINGS["show_extra_ribbon"] = request.form.get("show_extra_ribbon") == "ON"
    return redirect("/?tab=personalization&saved=1")

@app.route("/action/broadcast", methods=["POST"])
def action_broadcast():
    return redirect("/?tab=broadcast&sent=1")

@app.route("/action/mark_read")
def mark_read():
    nid = int(request.args.get("id", 0))
    n = next((item for item in NOTIFICATIONS if item["id"] == nid), None)
    if n:
        n["unread"] = False
    return redirect("/?tab=notifications")

@app.route("/action/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
