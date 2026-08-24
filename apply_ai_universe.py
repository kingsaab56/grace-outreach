import os

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
    f.write('''import os
import sys
import json
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Crisp High-Definition Emblem
SVG_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="100%" height="100%">
  <defs>
    <linearGradient id="gGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fde047"/><stop offset="50%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#b45309"/>
    </linearGradient>
    <linearGradient id="gEmerald" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34d399"/><stop offset="50%" stop-color="#059669"/><stop offset="100%" stop-color="#064e3b"/>
    </linearGradient>
    <filter id="glow"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.3"/></filter>
  </defs>
  <rect width="120" height="120" rx="26" fill="#042f2e" stroke="#10b981" stroke-width="3"/>
  <rect x="5" y="5" width="110" height="110" rx="22" fill="none" stroke="url(#gGold)" stroke-width="1.5" stroke-dasharray="6,3"/>
  <g filter="url(#glow)">
    <path d="M38 78 L38 52 L50 40 L50 78 Z" fill="url(#gEmerald)"/>
    <path d="M54 78 L54 30 L66 18 L66 78 Z" fill="url(#gEmerald)"/>
    <path d="M62 18 L66 18 L66 30 L62 30 Z" fill="url(#gGold)"/>
    <path d="M70 38 L84 54 L84 78 L74 78 L74 66 L70 66 Z" fill="url(#gGold)"/>
  </g>
  <text x="60" y="94" font-family="-apple-system, sans-serif" font-weight="900" font-size="12" fill="#f3f4f6" text-anchor="middle" letter-spacing="2">GRACE</text>
  <text x="60" y="106" font-family="-apple-system, sans-serif" font-weight="700" font-size="7" fill="#fbbf24" text-anchor="middle" letter-spacing="1.5">OUTREACH</text>
</svg>"""

B64_SVG = base64.b64encode(SVG_LOGO.encode('utf-8')).decode('utf-8')

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Enterprise AI Portal</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,__B64_SVG__">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #059669;
            --primary-hover: #047857;
            --gold: #f59e0b;
            --bg-body: #061012;
            --bg-card: #0d1e21;
            --bg-nav: #041416;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border-color: #16363b;
            --card-shadow: 0 20px 40px -10px rgba(0,0,0,0.7);
        }

        [data-theme="light"] {
            --primary: #059669;
            --primary-hover: #047857;
            --gold: #d97706;
            --bg-body: #f3f4f6;
            --bg-card: #ffffff;
            --bg-nav: #022c22;
            --text-main: #111827;
            --text-muted: #4b5563;
            --border-color: #e5e7eb;
            --card-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; transition: background 0.2s, color 0.2s; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; overflow-x: hidden; }

        /* CYBER AI LOGIN SCREEN WITH ANIMATED CANVAS */
        .auth-container { min-height: 100vh; display: flex; align-items: center; justify-content: space-around; padding: 30px; position: relative; overflow: hidden; background: radial-gradient(circle at center, #062e2e 0%, #021114 100%); flex-wrap: wrap; }
        #matrixCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.25; pointer-events: none; }

        /* AI ROBOT & FLOATING FEATURE BUBBLES */
        .ai-guide-wrapper { z-index: 2; display: flex; flex-direction: column; align-items: center; justify-content: center; max-width: 480px; position: relative; margin: 20px; }
        .robot-stage { position: relative; width: 220px; height: 260px; }
        
        .floating-bubble { position: absolute; background: rgba(13, 30, 33, 0.85); backdrop-filter: blur(8px); border: 1.5px solid var(--primary); padding: 10px 16px; border-radius: 20px; font-size: 12px; font-weight: 800; color: #34d399; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); animation: floatBubble 4s ease-in-out infinite; white-space: nowrap; }
        .bubble-1 { top: -10px; left: -100px; animation-delay: 0s; }
        .bubble-2 { top: 70px; right: -110px; border-color: var(--gold); color: #fbbf24; box-shadow: 0 0 15px rgba(245, 158, 11, 0.4); animation-delay: 1.5s; }
        .bubble-3 { bottom: 10px; left: -90px; animation-delay: 2.5s; }

        @keyframes floatBubble {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-10px) scale(1.05); }
        }

        .auth-card { z-index: 2; background: rgba(13, 30, 33, 0.92); backdrop-filter: blur(12px); border-radius: 20px; padding: 36px 32px; width: 100%; max-width: 420px; box-shadow: var(--card-shadow); border: 1.5px solid var(--border-color); text-align: center; margin: 20px; }
        .logo-box { width: 78px; height: 78px; margin: 0 auto 12px; }
        .logo-box svg { width: 100%; height: 100%; }
        
        .auth-title { font-size: 22px; font-weight: 900; color: #ffffff; letter-spacing: 1px; }
        .aesthetic-badge { background: rgba(245, 158, 11, 0.1); border: 1px dashed #f59e0b; padding: 8px 12px; border-radius: 10px; margin: 12px 0 18px 0; }
        .dev-credit { font-family: "Georgia", serif; font-style: italic; font-size: 13px; font-weight: 700; color: #fbbf24; }
        .appreciation-credit { font-size: 11px; color: #9ca3af; margin-top: 4px; }
        .appreciation-credit strong { color: #34d399; }

        .input-group { text-align: left; margin-bottom: 14px; }
        .input-group label { display: block; font-size: 11px; font-weight: 800; color: var(--text-muted); margin-bottom: 5px; text-transform: uppercase; }
        .input-group input, .input-group select, .input-group textarea { width: 100%; padding: 11px 13px; background: var(--bg-body); color: var(--text-main); border: 1.5px solid var(--border-color); border-radius: 8px; font-size: 14px; outline: none; }
        .input-group input:focus { border-color: var(--primary); }

        .btn { padding: 10px 18px; border: none; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-primary { background: var(--primary); color: #ffffff; width: 100%; }
        .btn-primary:hover { background: var(--primary-hover); }
        .btn-gold { background: var(--gold); color: #ffffff; }

        /* DASHBOARD */
        .app-container { display: none; min-height: 100vh; flex-direction: column; }
        .navbar { background: var(--bg-nav); color: #ffffff; padding: 10px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid var(--gold); }
        .nav-brand { display: flex; align-items: center; gap: 14px; }
        .nav-logo-box { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; }
        
        .nav-title { font-size: 18px; font-weight: 900; color: #ffffff; letter-spacing: 0.5px; }
        .nav-sub { font-size: 11px; margin-top: 2px; }
        .nav-dev { font-family: "Georgia", serif; font-style: italic; font-weight: 700; color: #fbbf24; }
        .nav-mentor { color: #6ee7b7; font-weight: 600; }

        .nav-actions { display: flex; align-items: center; gap: 10px; }
        .nav-ribbon { background: var(--bg-card); border-bottom: 1px solid var(--border-color); padding: 10px 24px; display: flex; gap: 8px; overflow-x: auto; align-items: center; }
        .tab-btn { background: transparent; border: 1px solid transparent; color: var(--text-muted); padding: 8px 16px; font-size: 13px; font-weight: 700; cursor: pointer; border-radius: 6px; white-space: nowrap; }
        .tab-btn.active, .tab-btn:hover { background: var(--primary); color: #ffffff; border-color: var(--primary); }

        .main-content { padding: 24px; max-width: 1300px; margin: 0 auto; width: 100%; flex: 1; }
        .tab-pane { display: none; }
        .tab-pane.active { display: block; }

        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: var(--bg-card); padding: 20px; border-radius: 12px; box-shadow: var(--card-shadow); border: 1px solid var(--border-color); border-left: 5px solid var(--primary); }
        .stat-val { font-size: 26px; font-weight: 800; color: var(--text-main); margin-top: 4px; }
        .stat-lbl { font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; }

        .content-box { background: var(--bg-card); padding: 24px; border-radius: 12px; box-shadow: var(--card-shadow); border: 1px solid var(--border-color); margin-bottom: 24px; }
        .section-header { font-size: 16px; font-weight: 800; color: var(--text-main); margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
        
        .badge { padding: 4px 8px; font-size: 11px; font-weight: 700; border-radius: 4px; }
        .badge-live { background: rgba(5, 150, 105, 0.2); color: #34d399; border: 1px solid #059669; }
        .badge-gold { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }

        /* LIVE BROADCAST MODAL */
        #alertModal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); z-index: 9999; align-items: center; justify-content: center; }
        .modal-box { background: var(--bg-card); border: 2px solid var(--gold); border-radius: 16px; width: 90%; max-width: 480px; padding: 24px; text-align: left; }
    </style>
</head>
<body>

    <!-- DIGITAL AI LOGIN SCREEN -->
    <div id="authScreen" class="auth-container">
        <canvas id="matrixCanvas"></canvas>

        <!-- AI ROBOT GUIDE WITH POINTER STICK -->
        <div class="ai-guide-wrapper">
            <div class="robot-stage">
                <!-- SVG Vector AI Robot with Pointer Stick -->
                <svg viewBox="0 0 200 240" width="100%" height="100%">
                    <defs>
                        <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#10b981"/><stop offset="100%" stop-color="#042f2e"/>
                        </linearGradient>
                        <filter id="neon"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#34d399"/></filter>
                    </defs>
                    <!-- Body & Head -->
                    <ellipse cx="100" cy="140" rx="42" ry="50" fill="url(#botGrad)" stroke="#34d399" stroke-width="3"/>
                    <rect x="65" y="55" width="70" height="50" rx="16" fill="#042f2e" stroke="#34d399" stroke-width="3"/>
                    <!-- Cyber Visor Eyes -->
                    <rect x="75" y="70" width="50" height="18" rx="8" fill="#061012" stroke="#f59e0b" stroke-width="1.5"/>
                    <circle cx="88" cy="79" r="4" fill="#34d399" filter="url(#neon)"/>
                    <circle cx="112" cy="79" r="4" fill="#34d399" filter="url(#neon)"/>
                    <!-- Antenna -->
                    <line x1="100" y1="55" x2="100" y2="35" stroke="#34d399" stroke-width="3"/>
                    <circle cx="100" cy="32" r="5" fill="#f59e0b" filter="url(#neon)"/>
                    <!-- Pointer Stick in Hand -->
                    <line x1="135" y1="135" x2="190" y2="45" stroke="#f59e0b" stroke-width="4" stroke-linecap="round" filter="url(#neon)"/>
                    <circle cx="190" cy="45" r="5" fill="#ffffff" filter="url(#neon)"/>
                    <circle cx="135" cy="135" r="8" fill="#10b981"/>
                </svg>

                <div class="floating-bubble bubble-1"><i class="fas fa-sync fa-spin"></i> Smart 5-Account Rotator</div>
                <div class="floating-bubble bubble-2"><i class="fas fa-bolt"></i> 24/7 Cloud Automation</div>
                <div class="floating-bubble bubble-3"><i class="fas fa-funnel-dollar"></i> CRM Pipeline Deals</div>
            </div>
            <div style="margin-top: 15px; text-align: center; z-index: 2;">
                <span style="font-family: 'Georgia', serif; font-style: italic; font-size: 15px; font-weight: 700; color: #fbbf24;">⚡ System Engineered by King Saab</span>
            </div>
        </div>

        <!-- AUTH CARD -->
        <div class="auth-card">
            <div class="logo-box">__SVG_LOGO__</div>
            <div class="auth-title">GRACE OUTREACH</div>
            
            <div class="aesthetic-badge">
                <div class="dev-credit">✨ Architected & Engineered by King Saab</div>
                <div class="appreciation-credit">🌟 Executive Strategic Guidance by <strong>Abdullah Khan</strong></div>
            </div>

            <div id="loginForm">
                <div class="input-group">
                    <label>Colleague Access ID</label>
                    <input type="text" id="loginUser" placeholder="kingsaab56" value="kingsaab56">
                </div>
                <div class="input-group">
                    <label>Password</label>
                    <input type="password" id="loginPass" placeholder="••••••••" value="admin56">
                </div>
                <button class="btn btn-primary" onclick="login()"><i class="fas fa-sign-in-alt"></i> Access Command Center</button>
                <p style="margin-top: 14px; font-size: 12px; color: var(--text-muted);">
                    New Colleague? <a href="#" onclick="toggleAuth(true)" style="color: var(--primary); font-weight: 700;">Register Account</a>
                </p>
            </div>

            <div id="registerForm" style="display: none;">
                <div class="input-group">
                    <label>Full Name</label>
                    <input type="text" id="regName" placeholder="e.g. Ali Ahmed">
                </div>
                <div class="input-group">
                    <label>Company Email</label>
                    <input type="email" id="regEmail" placeholder="name@gracearchitectures.com">
                </div>
                <div class="input-group">
                    <label>Secret Passcode</label>
                    <input type="password" id="regCode" placeholder="Enter 'grace'">
                </div>
                <button class="btn btn-primary" onclick="register()"><i class="fas fa-user-plus"></i> Create Account</button>
                <p style="margin-top: 14px; font-size: 12px; color: var(--text-muted);">
                    Already registered? <a href="#" onclick="toggleAuth(false)" style="color: var(--primary); font-weight: 700;">Sign In</a>
                </p>
            </div>
        </div>
    </div>

    <!-- MAIN ADMIN SYSTEM -->
    <div id="appScreen" class="app-container">
        <div class="navbar">
            <div class="nav-brand">
                <div class="nav-logo-box">__SVG_LOGO__</div>
                <div>
                    <div class="nav-title">GRACE OUTREACH ASSISTANT</div>
                    <div class="nav-sub">
                        <span class="nav-dev">⚡ Built by King Saab</span> &nbsp;|&nbsp; 
                        <span class="nav-mentor">🌟 Strategic Guidance by Abdullah Khan</span>
                    </div>
                </div>
            </div>
            <div class="nav-actions">
                <button class="btn btn-sm btn-gold" onclick="openAlertModal()"><i class="fas fa-bullhorn"></i> Broadcast Alert</button>
                <button class="btn btn-sm" style="background: rgba(255,255,255,0.1); color:#fff;" onclick="toggleTheme()"><i id="themeIcon" class="fas fa-sun"></i></button>
                <button class="btn btn-sm" style="background: #dc2626; color:#fff;" onclick="logout()"><i class="fas fa-power-off"></i></button>
            </div>
        </div>

        <!-- TOP NAVIGATION RIBBON -->
        <div class="nav-ribbon" id="ribbonBar">
            <button id="ribbon-dash" class="tab-btn active" onclick="showTab('tab-dash', this)"><i class="fas fa-chart-pie"></i> Dashboard</button>
            <button id="ribbon-gmail" class="tab-btn" onclick="showTab('tab-gmail', this)"><i class="fas fa-envelope-open-text"></i> Gmail Hub</button>
            <button id="ribbon-studio" class="tab-btn" onclick="showTab('tab-studio', this)"><i class="fas fa-paper-plane"></i> Campaign Studio</button>
            <button id="ribbon-crm" class="tab-btn" onclick="showTab('tab-crm', this)"><i class="fas fa-funnel-dollar"></i> CRM & Scraper</button>
            <button id="ribbon-team" class="tab-btn" onclick="showTab('tab-team', this)"><i class="fas fa-users-cog"></i> Colleagues</button>
            <button id="ribbon-admin" class="tab-btn" onclick="showTab('tab-admin', this)"><i class="fas fa-terminal"></i> System Doctor</button>
        </div>

        <div class="main-content">
            <!-- DASHBOARD -->
            <div id="tab-dash" class="tab-pane active">
                <div class="grid-stats">
                    <div class="stat-card">
                        <div class="stat-lbl">Active Outreach Pipeline</div>
                        <div class="stat-val">2,480 Leads</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Connected Gmails</div>
                        <div class="stat-val">5 Accounts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Weekly Sent Volume</div>
                        <div class="stat-val">1,240 Sent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Pipeline Deal Value</div>
                        <div class="stat-val">$64,800</div>
                    </div>
                </div>

                <div class="content-box">
                    <div class="section-header">
                        <span>⚡ 24/7 Cloud Engine Overview</span>
                        <span class="badge badge-live">● Permanent Cloud Active</span>
                    </div>
                    <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6;">
                        Cloud daemon is running continuously on Railway. You do not need to keep any local terminal open. All sequences, email rotations, and lead tracking persist seamlessly.
                    </p>
                </div>
            </div>

            <!-- GMAIL HUB -->
            <div id="tab-gmail" class="tab-pane">
                <div class="content-box">
                    <div class="section-header">
                        <span>📬 Connected Outreach Accounts</span>
                        <button class="btn btn-sm btn-primary" onclick="alert('OAuth Connection Flow Triggered')"><i class="fas fa-plus"></i> Connect Account</button>
                    </div>
                    <p style="color: var(--text-muted); font-size: 13px;">calvin.gracearchitectures.llc@gmail.com (Quota: 48/50) • Status: Optimal</p>
                </div>
            </div>

            <!-- CAMPAIGN STUDIO -->
            <div id="tab-studio" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🚀 Launch Outreach Campaign</span></div>
                    <div class="input-group">
                        <label>Campaign Title</label>
                        <input type="text" placeholder="e.g. Architectural Leads Q3">
                    </div>
                    <button class="btn btn-primary" onclick="alert('Campaign Dispatched!')"><i class="fas fa-rocket"></i> Launch</button>
                </div>
            </div>

            <!-- CRM -->
            <div id="tab-crm" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🎯 CRM Leads & Deals</span></div>
                    <p style="color: var(--text-muted); font-size: 13px;">Robert Sterling • Sterling Studio NYC • Deal: $15,000</p>
                </div>
            </div>

            <!-- COLLEAGUES -->
            <div id="tab-team" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>👥 Executive Leadership</span></div>
                    <p style="font-weight: 800; color: #fbbf24;">KING SAAB - Lead System Architect & Owner 👑</p>
                    <p style="font-weight: 800; color: #34d399; margin-top: 6px;">ABDULLAH KHAN - Executive Strategy & Operations 🌟</p>
                </div>
            </div>

            <!-- SYSTEM DOCTOR -->
            <div id="tab-admin" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🛠️ System Doctor Diagnostics</span></div>
                    <div style="background: #000; color: #34d399; font-family: monospace; font-size: 12px; padding: 16px; border-radius: 8px;">
                        [Railway Cloud] 24/7 Engine Heartbeat: ACTIVE<br>
                        [Lead Scraper] System rotation health: 100%<br>
                        [Security Guard] Auth pass verified
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- LIVE BROADCAST MODAL -->
    <div id="alertModal">
        <div class="modal-box">
            <h3 style="color: #fbbf24; margin-bottom: 12px;"><i class="fas fa-bullhorn"></i> Send Colleague Alert</h3>
            <div class="input-group">
                <label>Alert Message / Company Announcement</label>
                <textarea id="broadcastMsg" rows="4" placeholder="Type urgent update for all team members..."></textarea>
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn btn-sm" style="background: #4b5563; color: #fff;" onclick="closeAlertModal()">Cancel</button>
                <button class="btn btn-sm btn-gold" onclick="sendBroadcast()"><i class="fas fa-paper-plane"></i> Broadcast Now</button>
            </div>
        </div>
    </div>

    <script>
        // Interactive Matrix Canvas Animation
        const canvas = document.getElementById('matrixCanvas');
        const ctx = canvas.getContext('2d');
        function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const chars = '01GRACEKINGSAAB';
        const fontSize = 14;
        const columns = Math.floor(window.innerWidth / fontSize);
        const drops = Array(columns).fill(1);

        function drawMatrix() {
            ctx.fillStyle = 'rgba(2, 17, 20, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#10b981';
            ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 40);

        function toggleTheme() {
            var html = document.documentElement;
            var current = html.getAttribute('data-theme');
            var next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            document.getElementById('themeIcon').className = next === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }

        function openAlertModal() { document.getElementById('alertModal').style.display = 'flex'; }
        function closeAlertModal() { document.getElementById('alertModal').style.display = 'none'; }
        function sendBroadcast() {
            var msg = document.getElementById('broadcastMsg').value;
            if(msg) {
                alert('📢 Alert successfully broadcasted to all active Colleagues: ' + msg);
                closeAlertModal();
            }
        }

        function toggleAuth(showReg) {
            document.getElementById('loginForm').style.display = showReg ? 'none' : 'block';
            document.getElementById('registerForm').style.display = showReg ? 'block' : 'none';
        }

        function login() {
            document.getElementById('authScreen').style.display = 'none';
            document.getElementById('appScreen').style.display = 'flex';
        }

        function register() {
            var code = document.getElementById('regCode').value;
            if(code.toLowerCase() === 'grace') {
                alert('✔ Account registered! Please login.');
                toggleAuth(false);
            } else {
                alert('❌ Invalid Passcode! Contact King Saab.');
            }
        }

        function logout() {
            document.getElementById('appScreen').style.display = 'none';
            document.getElementById('authScreen').style.display = 'flex';
        }

        function showTab(id, btn) {
            var panes = document.getElementsByClassName('tab-pane');
            for(var i=0; i<panes.length; i++) panes[i].classList.remove('active');
            var btns = document.getElementsByClassName('tab-btn');
            for(var j=0; j<btns.length; j++) btns[j].classList.remove('active');
            document.getElementById(id).classList.add('active');
            if(btn) btn.classList.add('active');
        }
    </script>
</body>
</html>""".replace("__SVG_LOGO__", SVG_LOGO).replace("__B64_SVG__", B64_SVG)

class GraceRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.end_headers()
            self.wfile.write(SVG_LOGO.encode('utf-8'))
            return
            
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

    def do_POST(self):
        self.do_GET()

def run():
    server = HTTPServer((HOST, PORT), GraceRequestHandler)
    print(f"✔ Grace Cloud Permanent Server Active on http://{HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
''')

print("✔ AI Digital Universe, Broadcast System & Enhanced Emblem Applied!")
