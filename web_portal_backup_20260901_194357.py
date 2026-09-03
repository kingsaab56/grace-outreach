import os
from flask import Flask, request, redirect, session, send_from_directory
from markupsafe import escape

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "grace-outreach-enterprise-secure-key")

SYSTEM_MODULES = [
    {"id": 1, "name": "Gmail Multi-Tenant Hub", "desc": "3-tier inbox sync & tenant health"},
    {"id": 2, "name": "Gmail Account Manager", "desc": "Accounts, identity & session state"},
    {"id": 3, "name": "OAuth & Identity Tokenizer", "desc": "OAuth refresh & identity verification"},
    {"id": 4, "name": "Account Health Monitor", "desc": "Live diagnostics & preflight"},
    {"id": 5, "name": "Account Rotation Engine", "desc": "Pool rotation & sending limits"},
    {"id": 6, "name": "Lead Collector Daemon", "desc": "Scraping & ingestion pipeline"},
    {"id": 7, "name": "CRM / Lead Pipeline", "desc": "Lead stages, contacts & deal value"},
    {"id": 8, "name": "Colleague Access Controller", "desc": "RBAC & 22-module clearance"},
    {"id": 9, "name": "System Doctor / Diagnostics", "desc": "CPU, memory & daemon telemetry"},
    {"id": 10, "name": "Audio Studio / Extractor", "desc": "Audio extraction & trimming"},
    {"id": 11, "name": "Built-in AI Guide Agent", "desc": "Strategic assistant & advisory logs"},
    {"id": 12, "name": "OAuth Token Vault", "desc": "Token store & scope inspector"},
    {"id": 13, "name": "Timezone Scheduler", "desc": "Dispatch windows & queue timing"},
    {"id": 14, "name": "Bounce Shield", "desc": "Validation & bounce protection"},
    {"id": 15, "name": "Auto-Reply Detector", "desc": "Reply classification & CRM triggers"},
    {"id": 16, "name": "CSV / Excel Exporter", "desc": "Reports & custom data export"},
    {"id": 17, "name": "Broadcast Notification Node", "desc": "Targeted team alerts"},
    {"id": 18, "name": "Brand Palette Studio", "desc": "Theme & brand customization"},
    {"id": 19, "name": "Cloud Webhook Dispatcher", "desc": "Event endpoints & delivery logs"},
    {"id": 20, "name": "Daily Quota Guard", "desc": "Daily limits & auto-pause"},
    {"id": 21, "name": "Broadcast Control", "desc": "Global announcement history"},
    {"id": 22, "name": "Master System Control", "desc": "Global overrides & safe controls"},
]

COLLEAGUES = [
    {"id":1,"name":"King Saab","role":"Super Admin","user_id":"KS-001","online":True,"last_activity":"Now","last_seen":"Active now","usage":"92%","modules":{i:True for i in range(1,23)}},
    {"id":2,"name":"Alex Vance","role":"Outreach Operator","user_id":"AV-002","online":True,"last_activity":"2 min ago","last_seen":"Active now","usage":"68%","modules":{i:i in {1,2,4,6,7,11,13,14,15,20} for i in range(1,23)}},
    {"id":3,"name":"Rise Caffery","role":"Campaign Operator","user_id":"RC-003","online":False,"last_activity":"1 hr ago","last_seen":"Today, 5:12 PM","usage":"41%","modules":{i:i in {1,2,4,5,6,7,13,14,15,16,20} for i in range(1,23)}},
]

NOTIFICATIONS = [
    {"id":1,"title":"Inbound Reply","text":"New client activity detected.","time":"2 min ago","unread":True},
    {"id":2,"title":"Meeting Booked","text":"A pipeline lead booked a meeting.","time":"15 min ago","unread":True},
    {"id":3,"title":"Email Opened","text":"A prospect opened an outreach email.","time":"1 hr ago","unread":False},
]

def active_colleague():
    iid = session.get("impersonate")
    if iid:
        c = next((x for x in COLLEAGUES if x["id"] == int(iid)), None)
        if c: return c
    return COLLEAGUES[0]

CSS = r'''
:root{--bg:#020b08;--panel:#061712;--green:#00c98b;--gold:#f5a400;--red:#ff4d4d;--text:#f3faf7;--muted:#8aa9a1}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 50% -10%,#0b241b 0,#020b08 46%,#010604 100%);color:var(--text);font:14px Segoe UI,Arial,sans-serif}
a{color:inherit;text-decoration:none}.wrap{padding:18px 24px 30px}.header{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #0a3d30;padding-bottom:14px}
.brand{display:flex;gap:12px;align-items:center}.brand img{width:58px;height:58px;object-fit:cover;border-radius:12px;border:1px solid var(--gold);background:#fff;box-shadow:0 0 16px #00a97955}.brand h1{font-size:20px;margin:0 0 3px}.brand p{margin:0;color:#39d8b0;font-size:11px}
.actions{display:flex;gap:10px;align-items:center}.btn,.session{border:1px solid #0b5d49;background:#061712;color:#eafaf5;border-radius:7px;padding:9px 13px;font-weight:700;font-size:12px}.btn.gold{background:var(--gold);color:#111}.btn.red{background:#e32626;border-color:#ff4444}
.session{position:relative;cursor:pointer;min-width:220px;text-align:left}.session .sub{display:block;color:#7fd8bf;font-size:10px;font-weight:500;margin-top:2px}.switcher{display:none;position:absolute;right:0;top:48px;width:290px;background:#04120e;border:1px solid #117d61;border-radius:10px;padding:8px;z-index:50;box-shadow:0 18px 45px #000c}.session:hover .switcher{display:block}
.switch-item{display:flex;gap:9px;align-items:center;padding:10px;border-radius:7px}.switch-item:hover{background:#0b241c}.switch-item small{display:block;color:var(--muted);font-weight:500;margin-top:2px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block;box-shadow:0 0 8px currentColor}.online{background:#18d67d;color:#18d67d}.offline{background:#ff4747;color:#ff4747}
.impersonate{margin:16px 0;padding:11px 15px;border:1px solid var(--gold);background:#3a2905;color:#ffd36a;border-radius:8px;display:flex;justify-content:space-between;align-items:center;font-size:12px}.impersonate a{background:#e32626;color:#fff;padding:7px 11px;border-radius:5px;font-weight:800}
.nav{display:flex;gap:9px;margin:17px 0;flex-wrap:wrap}.nav a{padding:10px 16px;border:1px solid #0b5d49;border-radius:7px;color:#8eb3aa;font-weight:700}.nav a.active,.nav a:hover{background:linear-gradient(135deg,#059d72,#08c991);color:#fff}
.panel{background:linear-gradient(180deg,#061a14,#04120e);border:1px solid #0b5d49;border-radius:11px;padding:20px;box-shadow:0 10px 35px #0008;margin-bottom:18px}.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:16px}h2{margin:0;color:#09d39b;font-size:18px}.muted{color:var(--muted);font-size:12px}
.profile-grid{display:grid;grid-template-columns:310px 1fr;gap:16px}.people{display:flex;flex-direction:column;gap:9px}.person{border:1px solid #0b5d49;background:#061a14;border-radius:9px;padding:12px;cursor:pointer}.person.selected{border-color:#08c991;box-shadow:0 0 0 1px #08c99155 inset}.person-top{display:flex;justify-content:space-between;align-items:center}.person-name{font-size:14px;font-weight:800}.person-meta{color:var(--muted);font-size:10px;margin-top:4px}.person-stats{display:flex;gap:10px;margin-top:10px;color:#a9c8c0;font-size:10px}.person-actions{display:flex;gap:6px;margin-top:10px}.mini{padding:5px 8px;border-radius:5px;border:1px solid #0b5d49;font-size:10px;font-weight:800;background:#08261d}.mini.gold{background:var(--gold);color:#111}
.module-grid{display:grid;grid-template-columns:repeat(6,minmax(120px,1fr));gap:9px}.module{min-height:118px;background:#071e17;border:1px solid #0b5d49;border-radius:8px;padding:11px;display:flex;flex-direction:column;justify-content:space-between}.module:hover{border-color:#11c993;transform:translateY(-1px)}.module .num{color:#39d8b0;font-size:9px;font-weight:900}.module .name{font-weight:800;font-size:11px;line-height:1.25;margin-top:5px}.module .desc{color:#76968e;font-size:9px;line-height:1.25;margin-top:4px}
.toggle{width:38px;height:21px;border-radius:20px;border:1px solid #8b302f;background:#3a1111;position:relative;cursor:pointer;padding:0}.toggle span{position:absolute;top:2px;left:2px;width:15px;height:15px;border-radius:50%;background:#ff5b5b;transition:.2s}.toggle.on{background:#063d2e;border-color:#00c98b}.toggle.on span{left:19px;background:#00e29b;box-shadow:0 0 8px #00e29b}.mod-foot{display:flex;justify-content:space-between;align-items:center}.state{font-size:9px;font-weight:900;color:#ff6666}.module:has(.toggle.on) .state{color:#00d99a}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.kpi{background:#061a14;border:1px solid #0b5d49;border-left:3px solid #00c98b;border-radius:9px;padding:16px}.kpi b{font-size:27px;display:block;margin:5px 0}.kpi span{font-size:10px;color:#00d99a}table{width:100%;border-collapse:collapse}th,td{padding:11px;border-bottom:1px solid #0b3b30;text-align:left}th{font-size:10px;color:#6f958b;text-transform:uppercase}
@media(max-width:1100px){.module-grid{grid-template-columns:repeat(4,1fr)}.profile-grid{grid-template-columns:1fr}}@media(max-width:700px){.wrap{padding:12px}.header{flex-direction:column;align-items:flex-start;gap:10px}.module-grid{grid-template-columns:repeat(2,1fr)}.stats{grid-template-columns:repeat(2,1fr)}}
'''

def page(title, body):
    c=active_colleague(); unread=sum(1 for n in NOTIFICATIONS if n['unread'])
    switch=''.join(f'<a class="switch-item" href="/action/impersonate?id={x["id"]}"><span class="dot {"online" if x["online"] else "offline"}"></span><span><b>{escape(x["name"])}</b><small>{escape(x["role"])}</small></span></a>' for x in COLLEAGUES)
    banner=''
    if session.get('impersonate'): banner=f'<div class="impersonate"><span>⚠ VIEWING AS <b>{escape(c["name"]).upper()}</b> · RESTRICTED MODULE PERMISSIONS ACTIVE</span><a href="/action/exit_impersonate">EXIT COLLEAGUE VIEW</a></div>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · Grace Outreach Assistant</title><link rel="icon" type="image/png" href="/logo.png"><style>{CSS}</style></head><body><div class="wrap">
    <header class="header"><div class="brand"><img src="/logo.png" alt="Grace"><div><h1>GRACE OUTREACH ASSISTANT</h1><p>⚡ Built by King Saab · Strategic Guidance by Abdullah Khan</p></div></div>
    <div class="actions"><div class="session">👑 {escape(c['name'])}<span class="sub">{escape(c['role'])} · {escape(c['user_id'])}</span><div class="switcher">{switch}</div></div><a class="btn" href="/?tab=notifications">🔔 Notifications <b style="color:#ff5555">{unread}</b></a><a class="btn gold" href="/?tab=broadcast">📢 Broadcast Alert</a><a class="btn" href="/?tab=personalization">⚙ Personalization</a><a class="btn red" href="/action/logout">⏻ Power Off</a></div></header>{banner}
    <nav class="nav"><a class="{'active' if title=='Dashboard' else ''}" href="/?tab=dashboard">1. Dashboard Overview</a><a class="{'active' if 'Colleague' in title else ''}" href="/?tab=colleagues">2. Colleague Management</a><a class="{'active' if 'Matrix' in title else ''}" href="/?tab=matrix">3. 22-Module Control Matrix</a></nav>{body}</div></body></html>'''
def colleague_page():
    cid=int(request.args.get('edit_id',1)); selected=next((x for x in COLLEAGUES if x['id']==cid),COLLEAGUES[0])
    people=''
    for x in COLLEAGUES:
        people+=f'''<div class="person {'selected' if x['id']==selected['id'] else ''}" onclick="location.href='/?tab=colleagues&edit_id={x['id']}'"><div class="person-top"><span class="person-name"><i class="dot {'online' if x['online'] else 'offline'}"></i> {escape(x['name'])}</span><span class="muted">{escape(x['role'])}</span></div><div class="person-meta">User ID: {escape(x['user_id'])}</div><div class="person-stats"><span>Last activity: {escape(x['last_activity'])}</span><span>Last seen: {escape(x['last_seen'])}</span><span>Usage: {escape(x['usage'])}</span></div><div class="person-actions"><a class="mini" href="/?tab=colleagues&edit_id={x['id']}" onclick="event.stopPropagation()">Permissions</a><a class="mini gold" href="/action/impersonate?id={x['id']}" onclick="event.stopPropagation()">View As</a></div></div>'''
    modules=''
    for m in SYSTEM_MODULES:
        on=bool(selected['modules'].get(m['id'],False))
        modules+=f'''<div class="module"><div><div class="num">MODULE {m['id']:02d}</div><div class="name">{escape(m['name'])}</div><div class="desc">{escape(m['desc'])}</div></div><div class="mod-foot"><span class="state">{'ON' if on else 'OFF'}</span><form method="post" action="/action/toggle_permission"><input type="hidden" name="colleague_id" value="{selected['id']}"><input type="hidden" name="module_id" value="{m['id']}"><button class="toggle {'on' if on else ''}" type="submit"><span></span></button></form></div></div>'''
    body=f'''<div class="panel"><div class="panel-head"><div><h2>Colleague Directory</h2><div class="muted">Profile, presence, last activity, last seen and usage.</div></div><div class="muted">Click the top-right session name anytime to switch view.</div></div><div class="profile-grid"><div class="people">{people}</div><div><div class="panel" style="margin:0;padding:15px"><div class="panel-head"><div><h2>Permissions for {escape(selected['name'])}</h2><div class="muted">{escape(selected['role'])} · {escape(selected['user_id'])} · Usage {escape(selected['usage'])}</div></div><span><i class="dot {'online' if selected['online'] else 'offline'}"></i> {'ONLINE' if selected['online'] else 'OFFLINE'}</span></div><div class="module-grid">{modules}</div></div></div></div></div>'''
    return page('Colleague Management',body)

@app.route('/logo.png')
def logo(): return send_from_directory(os.path.dirname(os.path.abspath(__file__)),'logo.png')

@app.route('/')
def home():
    tab=request.args.get('tab','dashboard')
    if tab=='colleagues': return colleague_page()
    if tab=='matrix':
        cards=''.join(f'<div class="module"><div><div class="num">MODULE {m["id"]:02d}</div><div class="name">{escape(m["name"])}</div><div class="desc">{escape(m["desc"])}</div></div><div class="muted">AVAILABLE</div></div>' for m in SYSTEM_MODULES)
        return page('22-Module Matrix',f'<div class="panel"><div class="panel-head"><div><h2>22-Module Control Matrix</h2><div class="muted">6 modules per row on desktop.</div></div></div><div class="module-grid">{cards}</div></div>')
    if tab=='notifications':
        rows=''.join(f'<div class="person"><b>{escape(n["title"])}</b><div class="muted">{escape(n["text"])} · {escape(n["time"])}</div><a class="mini" href="/action/mark_read?id={n["id"]}">Mark read</a></div>' for n in NOTIFICATIONS)
        return page('Notifications',f'<div class="panel"><h2>Notifications</h2><div class="people" style="margin-top:14px">{rows}</div></div>')
    if tab=='broadcast': return page('Broadcast','<div class="panel" style="max-width:760px"><h2>Broadcast Alert</h2><p class="muted">Send an operational announcement.</p><form method="post" action="/action/broadcast"><input class="btn" style="width:100%;margin:8px 0" name="title" placeholder="Alert title" required><textarea class="btn" style="width:100%;min-height:120px;margin:8px 0" name="message" placeholder="Message" required></textarea><button class="btn gold">Send Broadcast</button></form></div>')
    if tab=='personalization': return page('Personalization','<div class="panel"><h2>Personalization</h2><p class="muted">Interface settings.</p></div>')
    body='<div class="stats"><div class="kpi"><small>ACTIVE OUTREACH PIPELINE</small><b>2,480</b><span>▲ +14.2% Velocity</span></div><div class="kpi"><small>CONNECTED GMAIL</small><b>5</b><span>● Rotation Healthy</span></div><div class="kpi"><small>WEEKLY SENT</small><b>1,240</b><span>▲ +8.5% Speed</span></div><div class="kpi"><small>PIPELINE VALUE</small><b>$64,800</b><span>▲ +21.4% Revenue</span></div></div><div class="panel" style="margin-top:18px"><div class="panel-head"><div><h2>Gmail Multi-Tenant Hub</h2><div class="muted">Business · Workplace · Personal</div></div><a class="btn" href="/?tab=colleagues">Manage Access</a></div><table><tr><th>Account</th><th>Email</th><th>Category</th><th>OAuth</th><th>Health</th></tr><tr><td>Grace Outreach Primary</td><td>admin@graceoutreach.com</td><td>BUSINESS</td><td>CONNECTED</td><td>HEALTHY</td></tr><tr><td>Malik Shani Workspace</td><td>shani@workspaces.internal</td><td>WORKPLACE</td><td>CONNECTED</td><td>WARNING</td></tr><tr><td>Outreach Rotator 01</td><td>rotator.p1@gmail.com</td><td>PERSONAL</td><td>OAUTH REQUIRED</td><td>ERROR</td></tr></table></div>'
    return page('Dashboard',body)

@app.post('/action/toggle_permission')
def toggle_permission():
    cid=int(request.form.get('colleague_id',1)); mid=int(request.form.get('module_id',1)); c=next((x for x in COLLEAGUES if x['id']==cid),None)
    if c and c['role']!='Super Admin': c['modules'][mid]=not c['modules'].get(mid,False)
    return redirect(f'/?tab=colleagues&edit_id={cid}')

@app.get('/action/impersonate')
def impersonate():
    cid=int(request.args.get('id',1))
    if any(x['id']==cid for x in COLLEAGUES): session['impersonate']=cid
    return redirect('/')

@app.get('/action/exit_impersonate')
def exit_impersonate(): session.pop('impersonate',None); return redirect('/?tab=colleagues')

@app.get('/action/mark_read')
def mark_read():
    nid=int(request.args.get('id',0)); n=next((x for x in NOTIFICATIONS if x['id']==nid),None)
    if n: n['unread']=False
    return redirect('/?tab=notifications')

@app.post('/action/broadcast')
def broadcast(): return redirect('/?tab=broadcast&sent=1')

@app.get('/action/logout')
def logout(): session.clear(); return redirect('/')

if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))