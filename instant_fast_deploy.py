import os
import subprocess
import time

print("⚡ [1/3] Optimizing package to fix Railway Timeout...")

# Heavy/junk files ignore list taake upload 3 second me ho
dockerignore_data = """__pycache__/
*.pyc
.git/
venv/
*.mp4
*.mkv
*.avi
*.mov
*.wav
*.zip
*.tar
*.tmp
*.bak
*.png
*.jpg
*.jpeg
"""
with open(".dockerignore", "w", encoding="utf-8") as f:
    f.write(dockerignore_data)

print("🎨 [2/3] Writing Clean Zero-Overlap Web Portal...")

clean_portal_code = r'''import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

APP_HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Command Center</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #059669;
            --primary-dark: #022c22;
            --gold: #f59e0b;
            --bg-body: #030a0c;
            --bg-card: rgba(8, 22, 25, 0.85);
            --bg-nav: #031417;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border-color: rgba(16, 185, 129, 0.2);
            --border-gold: rgba(245, 158, 11, 0.3);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; overflow-x: hidden; }

        /* CLEAN NAVBAR - STRICTLY NO OVERLAPPING BUTTONS */
        .top-navbar {
            background: var(--bg-nav);
            border-bottom: 2px solid var(--border-gold);
            padding: 12px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand-meta-box { display: flex; align-items: center; gap: 14px; }
        .nav-app-title { font-size: 17px; font-weight: 900; letter-spacing: 0.5px; }
        .nav-app-credits { font-size: 11.5px; margin-top: 2px; }
        .nav-app-credits .dev { font-family: Georgia, serif; font-style: italic; font-weight: 800; color: #fbbf24; }
        .nav-app-credits .advisor { color: #6ee7b7; font-weight: 600; }

        .nav-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .btn-broadcast {
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
            border: 1px solid var(--gold);
            color: #ffffff;
            padding: 9px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn-logout {
            background: #dc2626;
            border: none;
            color: #fff;
            padding: 9px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        .nav-ribbon-bar {
            background: #08171a;
            border-bottom: 1px solid var(--border-color);
            padding: 8px 28px;
            display: flex;
            gap: 8px;
            overflow-x: auto;
        }
        .ribbon-btn {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 8px 18px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }
        .ribbon-btn.active, .ribbon-btn:hover {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }

        .dashboard-body { padding: 28px 28px; max-width: 1400px; margin: 0 auto; }
        .tab-section { display: none; }
        .tab-section.active { display: block; }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 5px solid var(--primary);
            border-radius: 12px;
            padding: 20px;
        }
        .metric-label { font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); }
        .metric-value { font-size: 26px; font-weight: 900; margin-top: 6px; }

        .panel-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
        }
        .panel-header { font-size: 16px; font-weight: 800; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }

        .btn-action {
            background: var(--primary);
            border: 1px solid var(--primary);
            color: #fff;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            font-size: 13px;
        }

        /* PERMANENTLY SUPPRESS ANY FLOATING ICONS */
        .ambient-controls, .ambient-controls-login, .floating-settings {
            display: none !important;
            visibility: hidden !important;
        }
    </style>
</head>
<body>

    <header class="top-navbar">
        <div class="brand-meta-box">
            <svg viewBox="0 0 100 100" width="38" height="38">
                <rect width="100" height="100" rx="20" fill="#032024" stroke="#10b981" stroke-width="4"/>
                <path d="M30 65 L30 42 L42 30 L42 65 Z" fill="#059669"/>
                <path d="M46 65 L46 22 L58 12 L58 65 Z" fill="#059669"/>
                <path d="M62 30 L76 44 L76 65 L66 65 Z" fill="#f59e0b"/>
            </svg>
            <div>
                <div class="nav-app-title">GRACE OUTREACH ASSISTANT</div>
                <div class="nav-app-credits">
                    <span class="dev">⚡ Built by King Saab</span> &nbsp;|&nbsp; 
                    <span class="advisor">🌟 Strategic Guidance by Abdullah Khan</span>
                </div>
            </div>
        </div>

        <div class="nav-actions">
            <button class="btn-broadcast" onclick="alert('📢 Broadcast Alert modal opened!')"><i class="fas fa-bullhorn"></i> Broadcast Alert</button>
            <button class="btn-logout" onclick="location.reload()" title="Logout"><i class="fas fa-power-off"></i></button>
        </div>
    </header>

    <nav class="nav-ribbon-bar">
        <button class="ribbon-btn active" onclick="switchTab('tab-dash', this)"><i class="fas fa-chart-pie"></i> Dashboard</button>
        <button class="ribbon-btn" onclick="switchTab('tab-gmail', this)"><i class="fas fa-envelope-open-text"></i> Gmail Hub</button>
        <button class="ribbon-btn" onclick="switchTab('tab-studio', this)"><i class="fas fa-paper-plane"></i> Campaign Studio</button>
        <button class="ribbon-btn" onclick="switchTab('tab-crm', this)"><i class="fas fa-funnel-dollar"></i> CRM Pipeline</button>
        <button class="ribbon-btn" onclick="switchTab('tab-team', this)"><i class="fas fa-users-cog"></i> Colleagues</button>
        <button class="ribbon-btn" onclick="switchTab('tab-doctor', this)"><i class="fas fa-terminal"></i> System Doctor</button>
        <button class="ribbon-btn" onclick="switchTab('tab-custom', this)"><i class="fas fa-sliders-h"></i> Settings & Audio</button>
    </nav>

    <main class="dashboard-body">
        <section id="tab-dash" class="tab-section active">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Active Outreach Pipeline</div>
                    <div class="metric-value">2,480</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Connected Gmails</div>
                    <div class="metric-value">5 Accounts</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Weekly Sent Volume</div>
                    <div class="metric-value">1,240</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Pipeline Deal Value</div>
                    <div class="metric-value" style="color:#10b981;">$64,800</div>
                </div>
            </div>

            <div class="panel-card">
                <div class="panel-header">
                    <span>⚡ 24/7 Cloud Outreach Engine Active</span>
                    <span style="color:#34d399; font-weight:700; font-size:12px;">● Permanent Cloud Active</span>
                </div>
                <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6;">
                    Cloud daemon is running continuously on Railway. Your campaigns, auto-rotations, and Gmail account warmups continue uninterrupted.
                </p>
            </div>
        </section>

        <section id="tab-gmail" class="tab-section">
            <div class="panel-card">
                <div class="panel-header">
                    <span>📬 Connected Outreach Accounts</span>
                    <button class="btn-action" onclick="alert('OAuth Connected!')"><i class="fas fa-plus"></i> Connect Account</button>
                </div>
                <p style="color:var(--text-muted); font-size:14px;">calvin.gracearchitectures.llc@gmail.com (Quota: 48/50) • Status: Optimal</p>
            </div>
        </section>

        <section id="tab-studio" class="tab-section">
            <div class="panel-card">
                <div class="panel-header"><span>🚀 Launch Outreach Campaign</span></div>
                <p style="color:var(--text-muted); font-size:14px;">Campaign Studio tools are ready.</p>
            </div>
        </section>

        <section id="tab-crm" class="tab-section">
            <div class="panel-card">
                <div class="panel-header"><span>🎯 CRM Deals & Pipeline</span></div>
                <p style="color:var(--text-muted); font-size:14px;">Robert Sterling • Sterling Studio NYC • Deal: $15,000</p>
            </div>
        </section>

        <section id="tab-team" class="tab-section">
            <div class="panel-card">
                <div class="panel-header"><span>👥 Executive Leadership</span></div>
                <p style="color:#fbbf24; font-weight:800; font-size:14px;">KING SAAB (Lead Architect & Owner) 👑</p>
                <p style="color:#34d399; font-weight:800; font-size:14px; margin-top:8px;">ABDULLAH KHAN (Executive Strategy & Operations) 🌟</p>
            </div>
        </section>

        <section id="tab-doctor" class="tab-section">
            <div class="panel-card">
                <div class="panel-header"><span>🛠️ System Doctor Diagnostics</span></div>
                <div style="background:#01080a; color:#10b981; font-family:monospace; padding:16px; border-radius:8px; font-size:12px;">
                    [Railway Cloud] 24/7 Engine Heartbeat: ACTIVE<br>
                    [OAuth Guard] 5 Multi-tenant Gmail accounts ready<br>
                    [Lead Scraper] System rotation health: 100%
                </div>
            </div>
        </section>

        <section id="tab-custom" class="tab-section">
            <div class="panel-card">
                <div class="panel-header"><span>🎵 Ambient Audio & Media Player</span></div>
                <p style="color:var(--text-muted); font-size:14px;">Sound presets and video audio extractor settings are ready.</p>
            </div>
        </section>
    </main>

    <script>
        function switchTab(id, btn) {
            document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.ribbon-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            if(btn) btn.classList.add('active');
        }
    </script>
</body>
</html>"""

class GraceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        self.wfile.write(APP_HTML.encode('utf-8'))

    def do_POST(self):
        self.do_GET()

def main():
    server = ThreadedHTTPServer((HOST, PORT), GraceHandler)
    print(f"✔ Server online on http://{HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    main()
'''

with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
    f.write(clean_portal_code)

print("🚀 [3/3] Direct Pushing to Railway Cloud (Fast Mode)...")
os.system(r".\railway.exe up --service heartfelt-nourishment --detach")
