import os
import sys
import base64

img_file = "logo.png"
if not os.path.exists(img_file):
    for f in os.listdir('.'):
        if f.lower().endswith('.png') and 'logo' in f.lower():
            img_file = f
            break

with open(img_file, "rb") as f:
    raw_bytes = f.read()

b64_str = base64.b64encode(raw_bytes).decode('utf-8')

portal_py = '''import os
import sys
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

RAW_B64 = "''' + b64_str + '''"
IMG_BYTES = base64.b64decode(RAW_B64)
DATA_URI = "data:image/png;base64," + RAW_B64

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

APP_HTML = \'\'\'<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="emerald">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Enterprise AI Command Center</title>
    
    <!-- HARD FORCED CACHE-BUSTED FAVICONS -->
    <link rel="icon" type="image/png" href="/favicon.ico?v=999">
    <link rel="shortcut icon" type="image/png" href="/favicon.ico?v=999">
    <link rel="apple-touch-icon" href="/favicon.ico?v=999">
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #059669;
            --primary-glow: rgba(5, 150, 105, 0.45);
            --primary-dark: #022c22;
            --gold: #f59e0b;
            --gold-glow: rgba(245, 158, 11, 0.45);
            --gold-gradient: linear-gradient(135deg, #fef08a 0%, #f59e0b 50%, #b45309 100%);
            --bg-body: #030a0c;
            --bg-card: rgba(8, 22, 25, 0.90);
            --bg-card-solid: #08171a;
            --bg-nav: rgba(3, 20, 23, 0.96);
            --border-color: rgba(16, 185, 129, 0.22);
            --border-gold: rgba(245, 158, 11, 0.35);
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; overflow-x: hidden; }

        #launchSplash {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: #02080a; z-index: 9999;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            transition: opacity 0.6s ease, visibility 0.6s ease;
        }
        .splash-crest {
            width: 140px; height: 140px; border-radius: 28px; overflow: hidden;
            box-shadow: 0 0 35px var(--gold-glow);
            animation: pulseSplash 1.4s ease-in-out infinite alternate;
        }
        .splash-crest img { width: 100%; height: 100%; object-fit: contain; }
        @keyframes pulseSplash {
            0% { transform: scale(0.92); opacity: 0.85; }
            100% { transform: scale(1.05); opacity: 1; }
        }
        .splash-title {
            margin-top: 18px; font-size: 22px; font-weight: 900; letter-spacing: 4px;
            background: var(--gold-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        #cinematicStage { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; overflow: hidden; pointer-events: none; }
        #worldCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }

        .hologram-emblem {
            position: absolute; top: 48%; left: 50%; transform: translate(-50%, -50%);
            width: min(520px, 75vw); height: min(520px, 75vw);
            opacity: 0.22; pointer-events: none;
            filter: drop-shadow(0 0 45px var(--primary-glow));
            border-radius: 40px; overflow: hidden;
        }
        .hologram-emblem img { width: 100%; height: 100%; object-fit: contain; }

        .robot-interactive-actor {
            position: absolute; bottom: 4%; left: 16%; width: 230px; height: 290px;
            pointer-events: auto; cursor: pointer; z-index: 10;
        }
        .robot-speech-balloon {
            position: absolute; top: -45px; left: 50%; transform: translateX(-50%);
            background: rgba(3, 20, 23, 0.92); border: 1.5px solid var(--primary);
            color: #34d399; padding: 8px 16px; border-radius: 20px; font-size: 11.5px; font-weight: 700; white-space: nowrap;
        }

        .module-capsule {
            position: absolute; background: rgba(4, 24, 28, 0.75); backdrop-filter: blur(10px);
            border: 1.5px solid var(--primary); padding: 9px 18px; border-radius: 24px;
            font-size: 12px; font-weight: 800; color: #34d399; box-shadow: 0 0 20px var(--primary-glow);
            z-index: 15;
        }

        #authViewport {
            position: relative; z-index: 20; min-height: 100vh;
            display: flex; align-items: center; justify-content: flex-end; padding: 40px 8vw;
        }
        .auth-glass-panel {
            background: var(--bg-card); backdrop-filter: blur(14px);
            border: 1.5px solid var(--border-color); border-radius: 24px;
            padding: 34px 32px; width: 100%; max-width: 440px;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8); text-align: center; position: relative;
        }
        .auth-glass-panel::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--gold-gradient);
        }
        .brand-crest {
            width: 135px; height: 135px; margin: 0 auto 12px; border-radius: 24px; overflow: hidden;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6), 0 0 25px var(--gold-glow);
        }
        .brand-crest img { width: 100%; height: 100%; object-fit: contain; }

        .form-group { text-align: left; margin-bottom: 16px; }
        .form-group label { display: block; font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; }
        .form-control {
            width: 100%; padding: 12px 15px; background: rgba(3, 10, 12, 0.6);
            border: 1.5px solid var(--border-color); border-radius: 10px; color: var(--text-main); font-size: 14px; outline: none;
        }

        .btn-luxury {
            width: 100%; padding: 13px 20px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border: 1px solid var(--primary); border-radius: 10px; color: #ffffff;
            font-size: 13.5px; font-weight: 800; cursor: pointer; box-shadow: 0 6px 20px var(--primary-glow);
        }

        #enterpriseApp {
            display: none; position: relative; z-index: 30; min-height: 100vh; flex-direction: column; background: var(--bg-body);
        }
        .top-navbar {
            background: var(--bg-nav); border-bottom: 2px solid var(--border-gold);
            padding: 10px 28px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100;
        }
        .nav-logo-thumb { width: 48px; height: 48px; border-radius: 12px; overflow: hidden; box-shadow: 0 0 15px var(--gold-glow); }
        .nav-logo-thumb img { width: 100%; height: 100%; object-fit: contain; }

        .nav-ribbon-bar {
            background: var(--bg-card-solid); border-bottom: 1px solid var(--border-color);
            padding: 8px 24px; display: flex; gap: 6px; overflow-x: auto;
        }
        .ribbon-btn {
            background: transparent; border: 1px solid transparent; color: var(--text-muted);
            padding: 8px 14px; font-size: 12.5px; font-weight: 700; cursor: pointer; border-radius: 8px; white-space: nowrap;
        }
        .ribbon-btn.active { background: var(--primary); color: #ffffff; box-shadow: 0 4px 15px var(--primary-glow); }

        .dashboard-body { padding: 28px 28px; max-width: 1400px; margin: 0 auto; width: 100%; flex: 1; }
        .tab-section { display: none; }
        .tab-section.active { display: block; }
        .panel-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 16px; padding: 26px; }
    </style>
</head>
<body>

    <div id="launchSplash">
        <div class="splash-crest"><img src="/logo.png" alt="Grace Crest"></div>
        <div class="splash-title">GRACE OUTREACH ASSISTANT</div>
        <div style="color:#6ee7b7; font-size:12px; margin-top:8px; font-weight:700;"><i class="fas fa-circle-notch fa-spin"></i> Initializing 22 Core Modules...</div>
    </div>

    <div id="cinematicStage">
        <canvas id="worldCanvas"></canvas>
        <div class="hologram-emblem"><img src="/logo.png" alt="Grace Hologram"></div>

        <div class="robot-interactive-actor" onclick="triggerRobot()">
            <div class="robot-speech-balloon" id="robotSpeech">👑 King Saab System Ready</div>
            <svg viewBox="0 0 240 310" width="100%" height="100%">
                <rect x="68" y="45" width="104" height="78" rx="28" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
                <rect x="80" y="60" width="80" height="44" rx="16" fill="#021a1d" stroke="#059669" stroke-width="2"/>
                <path d="M94 80 Q102 72 110 80" stroke="#10b981" stroke-width="3.5" fill="none"/>
                <path d="M130 80 Q138 72 146 80" stroke="#10b981" stroke-width="3.5" fill="none"/>
                <circle cx="120" cy="14" r="6.5" fill="#fbbf24"/>
                <path d="M75 130 C75 122 165 122 165 130 L175 210 C175 228 65 228 65 210 Z" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
                <rect x="70" y="190" width="100" height="52" rx="6" fill="#022c22" stroke="#10b981" stroke-width="2"/>
                <text x="120" y="222" font-family="'Georgia', serif" font-style="italic" font-weight="900" font-size="11.5" fill="#fbbf24" text-anchor="middle">👑 KING SAAB</text>
            </svg>
        </div>

        <div class="module-capsule" style="left: 12vw; top: 35vh;"><i class="fas fa-cubes"></i> 22 Engines Online</div>
        <div class="module-capsule" style="left: 34vw; top: 25vh;"><i class="fas fa-bolt"></i> 24/7 Cloud Worker</div>
        <div class="module-capsule" style="left: 15vw; top: 55vh;"><i class="fas fa-dollar-sign"></i> ,800 CRM Deals</div>
        <div class="module-capsule" style="left: 36vw; top: 65vh;"><i class="fas fa-robot"></i> AI Guide Ready</div>
    </div>

    <div id="authViewport">
        <div class="auth-glass-panel">
            <div class="brand-crest"><img src="/logo.png" alt="Grace Crest"></div>
            <div style="font-size: 22px; font-weight: 900; letter-spacing: 1.5px;">GRACE OUTREACH</div>
            
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px dashed rgba(245, 158, 11, 0.35); padding: 10px; border-radius: 12px; margin: 12px 0 20px;">
                <div style="font-family: Georgia, serif; font-style: italic; font-weight: 800; font-size: 13.5px; color: #fbbf24;">✨ Architected & Engineered by King Saab</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">🌟 Strategic Guidance by <strong style="color: #34d399;">Abdullah Khan</strong></div>
            </div>

            <form onsubmit="handleAuthSubmit(event)" autocomplete="off">
                <div class="form-group">
                    <label>Colleague Identifier / ID</label>
                    <input type="text" id="authUsername" class="form-control" placeholder="Enter Colleague ID" required autocomplete="off">
                </div>
                <div class="form-group">
                    <label>Security Keyphrase</label>
                    <input type="password" id="authPassword" class="form-control" placeholder="Enter Keyphrase" required autocomplete="new-password">
                </div>
                <button type="submit" class="btn-luxury" id="loginBtn"><i class="fas fa-fingerprint"></i> Enter Command Center</button>
            </form>
        </div>
    </div>

    <div id="enterpriseApp">
        <header class="top-navbar">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div class="nav-logo-thumb"><img src="/logo.png" alt="Grace Logo"></div>
                <div>
                    <div style="font-size: 17px; font-weight: 900;">GRACE OUTREACH ASSISTANT</div>
                    <div style="font-size: 11.5px;"><span style="color: #fbbf24; font-style: italic;">⚡ Built by King Saab</span> | <span style="color: #6ee7b7;">🌟 Strategic Guidance by Abdullah Khan</span></div>
                </div>
            </div>
            <div style="display: flex; gap: 12px;">
                <button style="background: linear-gradient(135deg, #d97706, #b45309); border:none; color:#fff; padding:9px 18px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="alert('📢 Broadcast Alert Sent Across All 22 Nodes.')"><i class="fas fa-bullhorn"></i> Broadcast Alert</button>
                <button style="background: #dc2626; border:none; color:#fff; padding:9px 16px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="handlePowerOff()"><i class="fas fa-power-off"></i> Power Off</button>
            </div>
        </header>

        <nav class="nav-ribbon-bar">
            <button class="ribbon-btn active" onclick="switchTab(\'tab-dash\', this)"><i class="fas fa-chart-pie"></i> 1. Dashboard</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-matrix\', this)"><i class="fas fa-th"></i> 2. 22-Module Matrix</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-gmail\', this)"><i class="fas fa-envelope-open-text"></i> 3. Gmail Hub & Warmup</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-studio\', this)"><i class="fas fa-paper-plane"></i> 4. Campaign Studio</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-leads\', this)"><i class="fas fa-search-location"></i> 5. Lead Scraper</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-crm\', this)"><i class="fas fa-funnel-dollar"></i> 6. CRM Pipeline Deals</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-team\', this)"><i class="fas fa-users-cog"></i> 7. Colleagues Manager</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-doctor\', this)"><i class="fas fa-terminal"></i> 8. System Doctor</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-custom\', this)"><i class="fas fa-sliders-h"></i> 9. Settings & Audio</button>
        </nav>

        <main class="dashboard-body">
            <section id="tab-dash" class="tab-section active">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 24px;">
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">ACTIVE OUTREACH PIPELINE</div><div style="font-size:28px; font-weight:900;">2,480 Leads</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">CONNECTED GMAIL ACCOUNTS</div><div style="font-size:28px; font-weight:900;">5 Inboxes</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">WEEKLY SENT VOLUME</div><div style="font-size:28px; font-weight:900;">1,240 Emails</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">PIPELINE DEAL VALUE</div><div style="font-size:28px; font-weight:900; color:#10b981;">,800</div></div>
                </div>
                <div class="panel-card">
                    <div style="font-size:16px; font-weight:800; margin-bottom:8px;">⚡ 24/7 Cloud Outreach Engine Active</div>
                    <p style="color:var(--text-muted); font-size:14px; line-height:1.6;">Cloud daemon is running continuously on Railway. All 22 modules operate synchronously.</p>
                </div>
            </section>
        </main>
    </div>

    <script>
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const splash = document.getElementById('launchSplash');
                if(splash) {
                    splash.style.opacity = '0';
                    setTimeout(() => { splash.style.display = 'none'; }, 600);
                }
            }, 1100);
        });

        const canvas = document.getElementById('worldCanvas');
        const ctx = canvas.getContext('2d');
        function setCanvasSize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        setCanvasSize(); window.addEventListener('resize', setCanvasSize);

        function renderScene() {
            ctx.fillStyle = '#02090b'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            requestAnimationFrame(renderScene);
        }
        renderScene();

        function triggerRobot() {
            const speech = document.getElementById('robotSpeech');
            speech.innerText = "✨ 22-Module Hub Online!";
            setTimeout(() => { speech.innerText = "👑 King Saab AI System Ready"; }, 2500);
        }

        function handleAuthSubmit(e) {
            e.preventDefault();
            document.getElementById('authViewport').style.display = 'none';
            document.getElementById('cinematicStage').style.display = 'none';
            document.getElementById('enterpriseApp').style.display = 'flex';
        }

        function handlePowerOff() {
            document.getElementById('enterpriseApp').style.display = 'none';
            document.getElementById('cinematicStage').style.display = 'block';
            document.getElementById('authViewport').style.display = 'flex';
        }

        function switchTab(tabId, btn) {
            document.querySelectorAll('.tab-section').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.ribbon-btn').forEach(b => b.classList.remove('active'));
            const target = document.getElementById(tabId);
            if(target) target.classList.add('active');
            if(btn) btn.classList.add('active');
        }
    </script>
</body>
</html>\'\'\'

class GraceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/favicon.ico') or self.path.startswith('/logo.png') or self.path == '/favicon.png':
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(IMG_BYTES)
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        self.wfile.write(APP_HTML.encode('utf-8'))

    def do_POST(self):
        self.do_GET()

def main():
    server = ThreadedHTTPServer((HOST, PORT), GraceHandler)
    print(f"✔ Online on {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    main()
'''

with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write(portal_py)

print("✔ Generated clean web_portal.py with proper Favicon Cache-Busting!")
