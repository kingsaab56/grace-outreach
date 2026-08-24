import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class GraceHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/favicon.ico', '/favicon.png', '/logo.png']:
            img_path = "logo.png"
            if not os.path.exists(img_path):
                # Fallback to any png in folder
                pngs = [f for f in os.listdir('.') if f.endswith('.png')]
                if pngs:
                    img_path = pngs[0]
            
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(data)
                return

        # Serve Main HTML
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        
        html_content = '''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Enterprise AI Command Center</title>
    
    <link rel="icon" type="image/png" href="/logo.png">
    <link rel="shortcut icon" type="image/png" href="/logo.png">
    <link rel="apple-touch-icon" href="/logo.png">
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #059669;
            --primary-glow: rgba(5, 150, 105, 0.45);
            --gold: #f59e0b;
            --gold-glow: rgba(245, 158, 11, 0.45);
            --gold-gradient: linear-gradient(135deg, #fef08a 0%, #f59e0b 50%, #b45309 100%);
            --bg-body: #030a0c;
            --bg-card: rgba(8, 22, 25, 0.92);
            --border-color: rgba(16, 185, 129, 0.22);
            --border-gold: rgba(245, 158, 11, 0.35);
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; overflow-x: hidden; }

        #worldCanvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; }

        .hologram-emblem {
            position: fixed;
            top: 48%; left: 50%;
            transform: translate(-50%, -50%);
            width: min(520px, 75vw);
            height: min(520px, 75vw);
            opacity: 0.22;
            z-index: 2;
            pointer-events: none;
            filter: drop-shadow(0 0 45px var(--gold-glow));
            border-radius: 40px;
            overflow: hidden;
        }
        .hologram-emblem img { width: 100%; height: 100%; object-fit: contain; }

        .robot-actor {
            position: fixed;
            bottom: 4%; left: 16%;
            width: 230px; height: 290px;
            z-index: 10;
            cursor: pointer;
        }
        .robot-speech {
            position: absolute;
            top: -45px; left: 50%;
            transform: translateX(-50%);
            background: rgba(3, 20, 23, 0.92);
            border: 1.5px solid var(--primary);
            color: #34d399;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 700;
            white-space: nowrap;
        }

        #authViewport {
            position: relative;
            z-index: 20;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 40px 8vw;
        }
        .auth-card {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1.5px solid var(--border-color);
            border-radius: 24px;
            padding: 34px 32px;
            width: 100%;
            max-width: 440px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
            position: relative;
        }
        .auth-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--gold-gradient);
        }

        .brand-crest {
            width: 140px; height: 140px;
            margin: 0 auto 14px;
            border-radius: 28px;
            overflow: hidden;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7), 0 0 25px var(--gold-glow);
        }
        .brand-crest img { width: 100%; height: 100%; object-fit: contain; }

        .form-group { text-align: left; margin-bottom: 16px; }
        .form-group label { display: block; font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; }
        .form-control {
            width: 100%;
            padding: 12px 15px;
            background: rgba(3, 10, 12, 0.6);
            border: 1.5px solid var(--border-color);
            border-radius: 10px;
            color: #fff;
            font-size: 14px;
            outline: none;
        }

        .btn-luxury {
            width: 100%;
            padding: 13px 20px;
            background: linear-gradient(135deg, var(--primary) 0%, #022c22 100%);
            border: 1px solid var(--primary);
            border-radius: 10px;
            color: #ffffff;
            font-size: 13.5px;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 6px 20px var(--primary-glow);
        }

        #enterpriseApp {
            display: none;
            position: relative;
            z-index: 30;
            min-height: 100vh;
            flex-direction: column;
            background: var(--bg-body);
        }
        .top-navbar {
            background: rgba(3, 20, 23, 0.96);
            border-bottom: 2px solid var(--border-gold);
            padding: 10px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-logo-thumb {
            width: 48px; height: 48px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 0 15px var(--gold-glow);
        }
        .nav-logo-thumb img { width: 100%; height: 100%; object-fit: contain; }

        .nav-ribbon {
            background: #08171a;
            border-bottom: 1px solid var(--border-color);
            padding: 8px 24px;
            display: flex; gap: 8px; overflow-x: auto;
        }
        .ribbon-btn {
            background: transparent; border: none; color: var(--text-muted);
            padding: 8px 14px; font-size: 12.5px; font-weight: 700; cursor: pointer; border-radius: 8px;
        }
        .ribbon-btn.active {
            background: var(--primary); color: #fff; box-shadow: 0 4px 15px var(--primary-glow);
        }

        .module-capsule {
            position: fixed;
            background: rgba(4, 24, 28, 0.75);
            backdrop-filter: blur(10px);
            border: 1.5px solid var(--primary);
            padding: 9px 18px;
            border-radius: 24px;
            font-size: 12px;
            font-weight: 800;
            color: #34d399;
            z-index: 15;
            box-shadow: 0 0 20px var(--primary-glow);
        }
    </style>
</head>
<body>

    <canvas id="worldCanvas"></canvas>
    <div class="hologram-emblem"><img src="/logo.png" alt="Grace Hologram"></div>

    <div class="robot-actor">
        <div class="robot-speech">👑 King Saab System Ready</div>
        <svg viewBox="0 0 240 310" width="100%" height="100%">
            <rect x="68" y="45" width="104" height="78" rx="28" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
            <rect x="80" y="60" width="80" height="44" rx="16" fill="#021a1d" stroke="#059669" stroke-width="2"/>
            <path d="M94 80 Q102 72 110 80" stroke="#10b981" stroke-width="3.5" fill="none"/>
            <path d="M130 80 Q138 72 146 80" stroke="#10b981" stroke-width="3.5" fill="none"/>
            <circle cx="120" cy="14" r="6.5" fill="#fbbf24"/>
            <path d="M75 130 C75 122 165 122 165 130 L175 210 C175 228 65 228 65 210 Z" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
            <rect x="70" y="190" width="100" height="52" rx="6" fill="#022c22" stroke="#10b981" stroke-width="2"/>
            <text x="120" y="222" font-family="Georgia" font-style="italic" font-weight="900" font-size="11.5" fill="#fbbf24" text-anchor="middle">👑 KING SAAB</text>
        </svg>
    </div>

    <div class="module-capsule" style="left: 12vw; top: 35vh;"><i class="fas fa-cubes"></i> 22 Engines Online</div>
    <div class="module-capsule" style="left: 34vw; top: 25vh;"><i class="fas fa-bolt"></i> 24/7 Cloud Worker</div>
    <div class="module-capsule" style="left: 15vw; top: 55vh;"><i class="fas fa-dollar-sign"></i> ,800 CRM Deals</div>
    <div class="module-capsule" style="left: 36vw; top: 65vh;"><i class="fas fa-robot"></i> AI Guide Ready</div>

    <!-- 1. AUTH LOGIN VIEW -->
    <div id="authViewport">
        <div class="auth-card">
            <div class="brand-crest"><img src="/logo.png" alt="Grace Crest"></div>
            <div style="font-size: 22px; font-weight: 900; letter-spacing: 1.5px;">GRACE OUTREACH</div>
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px dashed rgba(245, 158, 11, 0.35); padding: 10px; border-radius: 12px; margin: 12px 0 20px;">
                <div style="font-family: Georgia; font-style: italic; font-weight: 800; font-size: 13.5px; color: #fbbf24;">✨ Architected & Engineered by King Saab</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">🌟 Strategic Guidance by <strong style="color: #34d399;">Abdullah Khan</strong></div>
            </div>

            <form onsubmit="handleLogin(event)" autocomplete="off">
                <div class="form-group">
                    <label>Colleague Identifier / ID</label>
                    <input type="text" class="form-control" placeholder="Enter Colleague ID" required>
                </div>
                <div class="form-group">
                    <label>Security Keyphrase</label>
                    <input type="password" class="form-control" placeholder="Enter Keyphrase" required>
                </div>
                <button type="submit" class="btn-luxury"><i class="fas fa-fingerprint"></i> Enter Command Center</button>
            </form>
        </div>
    </div>

    <!-- 2. ENTERPRISE APP VIEW -->
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
                <button style="background: linear-gradient(135deg, #d97706, #b45309); border:none; color:#fff; padding:9px 18px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="alert('📢 Broadcast Sent')"><i class="fas fa-bullhorn"></i> Broadcast Alert</button>
                <button style="background: #dc2626; border:none; color:#fff; padding:9px 16px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="handlePowerOff()"><i class="fas fa-power-off"></i> Power Off</button>
            </div>
        </header>

        <nav class="nav-ribbon">
            <button class="ribbon-btn active"><i class="fas fa-chart-pie"></i> 1. Dashboard</button>
            <button class="ribbon-btn"><i class="fas fa-th"></i> 2. 22-Module Matrix</button>
            <button class="ribbon-btn"><i class="fas fa-envelope-open-text"></i> 3. Gmail Hub & Warmup</button>
            <button class="ribbon-btn"><i class="fas fa-paper-plane"></i> 4. Campaign Studio</button>
            <button class="ribbon-btn"><i class="fas fa-search-location"></i> 5. Lead Scraper</button>
            <button class="ribbon-btn"><i class="fas fa-funnel-dollar"></i> 6. CRM Pipeline Deals</button>
            <button class="ribbon-btn"><i class="fas fa-users-cog"></i> 7. Colleagues Manager</button>
            <button class="ribbon-btn"><i class="fas fa-terminal"></i> 8. System Doctor</button>
            <button class="ribbon-btn"><i class="fas fa-sliders-h"></i> 9. Settings & Audio</button>
        </nav>

        <main style="padding: 28px; max-width: 1400px; margin: 0 auto; width: 100%;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 24px;">
                <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">ACTIVE OUTREACH PIPELINE</div><div style="font-size:28px; font-weight:900;">2,480 Leads</div></div>
                <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">CONNECTED GMAIL ACCOUNTS</div><div style="font-size:28px; font-weight:900;">5 Inboxes</div></div>
                <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">WEEKLY SENT VOLUME</div><div style="font-size:28px; font-weight:900;">1,240 Emails</div></div>
                <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">PIPELINE DEAL VALUE</div><div style="font-size:28px; font-weight:900; color:#10b981;">,800</div></div>
            </div>
        </main>
    </div>

    <script>
        const canvas = document.getElementById('worldCanvas');
        const ctx = canvas.getContext('2d');
        function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        resize(); window.addEventListener('resize', resize);

        function draw() {
            ctx.fillStyle = '#02090b'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            requestAnimationFrame(draw);
        }
        draw();

        function handleLogin(e) {
            e.preventDefault();
            document.getElementById('authViewport').style.display = 'none';
            document.querySelectorAll('.module-capsule').forEach(c => c.style.display = 'none');
            document.querySelector('.robot-actor').style.display = 'none';
            document.querySelector('.hologram-emblem').style.display = 'none';
            document.getElementById('enterpriseApp').style.display = 'flex';
        }

        function handlePowerOff() {
            document.getElementById('enterpriseApp').style.display = 'none';
            document.getElementById('authViewport').style.display = 'flex';
            document.querySelectorAll('.module-capsule').forEach(c => c.style.display = 'block');
            document.querySelector('.robot-actor').style.display = 'block';
            document.querySelector('.hologram-emblem').style.display = 'block';
        }
    </script>
</body>
</html>'''
        self.wfile.write(html_content.encode('utf-8'))

    def do_POST(self):
        self.do_GET()

def main():
    server = ThreadedHTTPServer((HOST, PORT), GraceHandler)
    print(f"✔ Online on {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    main()
