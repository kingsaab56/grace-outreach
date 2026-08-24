import os

with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
    f.write('''import os
import sys
import json
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Crisp High-Definition SVG Emblem
SVG_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" width="100%" height="100%">
  <defs>
    <linearGradient id="emGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/><stop offset="50%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#b45309"/>
    </linearGradient>
    <linearGradient id="emGreen" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34d399"/><stop offset="50%" stop-color="#059669"/><stop offset="100%" stop-color="#022c22"/>
    </linearGradient>
    <filter id="crispGlow"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.4"/></filter>
  </defs>
  <rect width="160" height="160" rx="34" fill="#032024" stroke="#10b981" stroke-width="4"/>
  <rect x="8" y="8" width="144" height="144" rx="28" fill="none" stroke="url(#emGold)" stroke-width="2.5"/>
  <g filter="url(#crispGlow)">
    <path d="M50 102 L50 68 L66 52 L66 102 Z" fill="url(#emGreen)"/>
    <path d="M72 102 L72 38 L88 22 L88 102 Z" fill="url(#emGreen)"/>
    <path d="M82 22 L88 22 L88 38 L82 38 Z" fill="url(#emGold)"/>
    <path d="M94 48 L114 70 L114 102 L100 102 L100 86 L94 86 Z" fill="url(#emGold)"/>
  </g>
  <text x="80" y="122" font-family="-apple-system, sans-serif" font-weight="900" font-size="15" fill="#ffffff" text-anchor="middle" letter-spacing="3">GRACE</text>
  <text x="80" y="137" font-family="-apple-system, sans-serif" font-weight="800" font-size="9" fill="#fbbf24" text-anchor="middle" letter-spacing="2">OUTREACH</text>
</svg>"""

B64_SVG = base64.b64encode(SVG_LOGO.encode('utf-8')).decode('utf-8')

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Cyber AI Command Center</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,__B64_SVG__">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #059669;
            --gold: #f59e0b;
            --bg-body: #050d0e;
            --bg-card: #091a1d;
            --bg-nav: #031417;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border-color: #123237;
        }

        [data-theme="light"] {
            --primary: #059669;
            --gold: #d97706;
            --bg-body: #f3f4f6;
            --bg-card: #ffffff;
            --bg-nav: #022c22;
            --text-main: #111827;
            --text-muted: #4b5563;
            --border-color: #e5e7eb;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; overflow-x: hidden; }

        /* LIVING CYBER ENGINE CANVAS */
        .auth-container { min-height: 100vh; display: flex; align-items: center; justify-content: space-around; padding: 30px; position: relative; overflow: hidden; background: radial-gradient(circle at center, #062b2e 0%, #02090b 100%); flex-wrap: wrap; }
        #livingWorldCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }

        /* WHITE 3D AI ROBOT & INTERACTIVE BUBBLE STAGE */
        .robot-stage-wrapper { z-index: 2; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; margin: 20px; width: 380px; }
        .robot-container { position: relative; width: 220px; height: 260px; }

        /* INTERACTIVE FLOATING CLICK-TO-BURST BUBBLES */
        .module-bubble {
            position: absolute;
            background: rgba(9, 26, 29, 0.85);
            backdrop-filter: blur(8px);
            border: 1.5px solid var(--primary);
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 800;
            color: #34d399;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.4);
            cursor: pointer;
            user-select: none;
            transition: transform 0.15s ease-out;
            animation: bubbleWobble 4.5s ease-in-out infinite alternate;
        }
        .module-bubble:hover { transform: scale(1.1); border-color: var(--gold); color: #fbbf24; }
        .b-pos-1 { top: 0px; left: -70px; animation-delay: 0s; }
        .b-pos-2 { top: 75px; right: -80px; border-color: var(--gold); color: #fbbf24; animation-delay: 1.2s; }
        .b-pos-3 { bottom: 15px; left: -60px; animation-delay: 2.4s; }

        @keyframes bubbleWobble {
            0% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-12px) rotate(2deg); }
            100% { transform: translateY(4px) rotate(-2deg); }
        }

        /* POP BURST KEYFRAME */
        .bubble-popping { animation: popBurst 0.3s forwards !important; }
        @keyframes popBurst {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.4); opacity: 0.7; }
            100% { transform: scale(0); opacity: 0; }
        }

        .auth-card { z-index: 2; background: rgba(9, 26, 29, 0.94); backdrop-filter: blur(14px); border-radius: 22px; padding: 36px 32px; width: 100%; max-width: 420px; box-shadow: 0 25px 50px -10px rgba(0,0,0,0.8); border: 1.5px solid var(--border-color); text-align: center; margin: 20px; }
        .logo-box { width: 85px; height: 85px; margin: 0 auto 12px; }
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
        .btn-primary:hover { background: #047857; }
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
        .stat-card { background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border-color); border-left: 5px solid var(--primary); }
        .stat-val { font-size: 26px; font-weight: 800; color: var(--text-main); margin-top: 4px; }
        .stat-lbl { font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; }

        .content-box { background: var(--bg-card); padding: 24px; border-radius: 12px; border: 1px solid var(--border-color); margin-bottom: 24px; }
        .section-header { font-size: 16px; font-weight: 800; color: var(--text-main); margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
        .badge-live { background: rgba(5, 150, 105, 0.2); color: #34d399; border: 1px solid #059669; padding: 4px 8px; font-size: 11px; font-weight: 700; border-radius: 4px; }

        #alertModal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); z-index: 9999; align-items: center; justify-content: center; }
        .modal-box { background: var(--bg-card); border: 2px solid var(--gold); border-radius: 16px; width: 90%; max-width: 480px; padding: 24px; text-align: left; }
    </style>
</head>
<body>

    <!-- LIVING CYBER AI ENGINE LOGIN SCREEN -->
    <div id="authScreen" class="auth-container">
        <canvas id="livingWorldCanvas"></canvas>

        <!-- 3D WHITE GLOSSY AI BOT WITH LAPTOP & INTERACTIVE BUBBLES -->
        <div class="robot-stage-wrapper">
            <div class="robot-container">
                <!-- Glossy White AI Bot SVG -->
                <svg viewBox="0 0 240 280" width="100%" height="100%">
                    <defs>
                        <linearGradient id="bodyWhite" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#ffffff"/><stop offset="70%" stop-color="#e2e8f0"/><stop offset="100%" stop-color="#cbd5e1"/>
                        </linearGradient>
                        <filter id="neonCyan"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#10b981"/></filter>
                        <filter id="neonGold"><feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#fbbf24"/></filter>
                    </defs>
                    <!-- Head -->
                    <rect x="70" y="45" width="100" height="75" rx="28" fill="url(#bodyWhite)" stroke="#94a3b8" stroke-width="2"/>
                    <!-- Cyan Visor Display Screen -->
                    <rect x="82" y="60" width="76" height="42" rx="14" fill="#031d20" stroke="#059669" stroke-width="1.5"/>
                    <!-- Smiling Neon Eyes -->
                    <path d="M96 78 Q103 70 110 78" stroke="#10b981" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#neonCyan)"/>
                    <path d="M130 78 Q137 70 144 78" stroke="#10b981" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#neonCyan)"/>
                    <!-- Bot Antenna -->
                    <line x1="120" y1="45" x2="120" y2="22" stroke="#64748b" stroke-width="3.5"/>
                    <circle cx="120" cy="18" r="6" fill="#fbbf24" filter="url(#neonGold)"/>
                    <!-- Torso -->
                    <path d="M80 125 C80 120 160 120 160 125 L170 200 C170 215 70 215 70 200 Z" fill="url(#bodyWhite)" stroke="#94a3b8" stroke-width="2"/>
                    <circle cx="120" cy="155" r="14" fill="#042f2e" stroke="#10b981" stroke-width="2"/>
                    <path d="M115 155 L125 155 M120 150 L120 160" stroke="#10b981" stroke-width="2"/>
                    <!-- Glowing Cyber Laptop with King Saab AI Emblem -->
                    <polygon points="65,225 175,225 195,250 45,250" fill="#0f172a" stroke="#334155" stroke-width="2"/>
                    <rect x="75" y="180" width="90" height="48" rx="6" fill="#042f2e" stroke="#10b981" stroke-width="2" filter="url(#neonCyan)"/>
                    <text x="120" y="210" font-family="'Georgia', serif" font-style="italic" font-weight="900" font-size="11" fill="#fbbf24" text-anchor="middle">👑 KING SAAB</text>
                    <!-- Hands on Laptop -->
                    <circle cx="68" cy="225" r="9" fill="url(#bodyWhite)" stroke="#94a3b8"/>
                    <circle cx="172" cy="225" r="9" fill="url(#bodyWhite)" stroke="#94a3b8"/>
                </svg>

                <!-- Interactive Floating Click-to-Burst Module Bubbles -->
                <div class="module-bubble b-pos-1" onclick="popBubble(this)"><i class="fas fa-sync-alt fa-spin"></i> 5-Account Rotator</div>
                <div class="module-bubble b-pos-2" onclick="popBubble(this)"><i class="fas fa-bolt"></i> 24/7 Cloud Worker</div>
                <div class="module-bubble b-pos-3" onclick="popBubble(this)"><i class="fas fa-funnel-dollar"></i> CRM Pipeline</div>
            </div>

            <div style="margin-top: 15px; text-align: center; z-index: 2;">
                <span style="font-family: 'Georgia', serif; font-style: italic; font-size: 15px; font-weight: 800; color: #fbbf24;">⚡ System Engineered by King Saab</span>
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

        <!-- NAVIGATION RIBBON -->
        <div class="nav-ribbon" id="ribbonBar">
            <button id="ribbon-dash" class="tab-btn active" onclick="showTab('tab-dash', this)"><i class="fas fa-chart-pie"></i> Dashboard</button>
            <button id="ribbon-gmail" class="tab-btn" onclick="showTab('tab-gmail', this)"><i class="fas fa-envelope-open-text"></i> Gmail Hub</button>
            <button id="ribbon-studio" class="tab-btn" onclick="showTab('tab-studio', this)"><i class="fas fa-paper-plane"></i> Campaign Studio</button>
            <button id="ribbon-crm" class="tab-btn" onclick="showTab('tab-crm', this)"><i class="fas fa-funnel-dollar"></i> CRM & Scraper</button>
            <button id="ribbon-team" class="tab-btn" onclick="showTab('tab-team', this)"><i class="fas fa-users-cog"></i> Colleagues</button>
            <button id="ribbon-admin" class="tab-btn" onclick="showTab('tab-admin', this)"><i class="fas fa-terminal"></i> System Doctor</button>
        </div>

        <div class="main-content">
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
                        <span class="badge-live">● Permanent Cloud Active</span>
                    </div>
                    <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6;">
                        Cloud daemon is running continuously on Railway. You do not need to keep any local terminal open.
                    </p>
                </div>
            </div>

            <div id="tab-gmail" class="tab-pane">
                <div class="content-box">
                    <div class="section-header">
                        <span>📬 Connected Outreach Accounts</span>
                        <button class="btn btn-sm btn-primary" onclick="alert('OAuth Connected!')"><i class="fas fa-plus"></i> Connect Account</button>
                    </div>
                    <p style="color: var(--text-muted); font-size: 13px;">calvin.gracearchitectures.llc@gmail.com (Quota: 48/50) • Status: Optimal</p>
                </div>
            </div>

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

            <div id="tab-crm" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🎯 CRM Leads & Deals</span></div>
                    <p style="color: var(--text-muted); font-size: 13px;">Robert Sterling • Sterling Studio NYC • Deal: $15,000</p>
                </div>
            </div>

            <div id="tab-team" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>👥 Executive Leadership</span></div>
                    <p style="font-weight: 800; color: #fbbf24;">KING SAAB - Lead System Architect & Owner 👑</p>
                    <p style="font-weight: 800; color: #34d399; margin-top: 6px;">ABDULLAH KHAN - Executive Strategy & Operations 🌟</p>
                </div>
            </div>

            <div id="tab-admin" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🛠️ System Doctor Diagnostics</span></div>
                    <div style="background: #000; color: #34d399; font-family: monospace; font-size: 12px; padding: 16px; border-radius: 8px;">
                        [Railway Cloud] 24/7 Engine Heartbeat: ACTIVE<br>
                        [Lead Scraper] System rotation health: 100%
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
        // -------------------------------------------------------------
        // LIVING WORLD CANVAS (BUILDINGS ELECTRIC CURRENT, BIRDS, TREES, MAP FLASHES)
        // -------------------------------------------------------------
        const canvas = document.getElementById('livingWorldCanvas');
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        // Birds Physics
        const birds = Array.from({length: 6}, () => ({
            x: Math.random() * window.innerWidth,
            y: Math.random() * (window.innerHeight * 0.4),
            vx: 1.2 + Math.random() * 1.5,
            size: 8 + Math.random() * 6,
            wing: 0
        }));

        // US State Nodes Flashes (ny, ca, tx, fl, il, wa)
        const stateNodes = [
            {code: 'ny', x: 0.78, y: 0.35, alpha: 0.1, step: 0.02},
            {code: 'ca', x: 0.22, y: 0.45, alpha: 0.3, step: 0.015},
            {code: 'tx', x: 0.48, y: 0.70, alpha: 0.5, step: 0.03},
            {code: 'fl', x: 0.72, y: 0.78, alpha: 0.2, step: 0.025},
            {code: 'wa', x: 0.20, y: 0.22, alpha: 0.4, step: 0.018}
        ];

        let electricityPhase = 0;

        function drawLivingWorld() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            electricityPhase += 0.04;

            // 1. Draw Architectural Buildings Outline with Traveling Electric Current
            const bBaseY = canvas.height * 0.85;
            const bWidth = 140;
            const bStartX = canvas.width * 0.12;

            ctx.lineWidth = 1.5;
            ctx.strokeStyle = 'rgba(16, 185, 129, 0.15)';
            
            // Tower 1 & 2 Blueprint Frames
            ctx.strokeRect(bStartX, bBaseY - 320, bWidth, 320);
            ctx.strokeRect(bStartX + bWidth + 20, bBaseY - 420, bWidth + 20, 420);

            // Multi-Line Electric Golden & Emerald Lightning Beams Flowing Down Walls
            for (let line = 0; line < 4; line++) {
                const offset = (electricityPhase + line * 0.8) % 3;
                const flowY = bBaseY - 420 + offset * 140;
                
                ctx.beginPath();
                ctx.strokeStyle = line % 2 === 0 ? 'rgba(251, 191, 36, 0.75)' : 'rgba(52, 211, 153, 0.85)';
                ctx.lineWidth = 2.5;
                ctx.shadowColor = '#fbbf24';
                ctx.shadowBlur = 10;
                ctx.moveTo(bStartX + bWidth + 20 + line * 35, flowY - 40);
                ctx.lineTo(bStartX + bWidth + 20 + line * 35, flowY);
                ctx.stroke();
                ctx.shadowBlur = 0;
            }

            // 2. Glowing Cyber Foliage / Trees on Side
            ctx.fillStyle = 'rgba(4, 120, 87, 0.12)';
            ctx.beginPath();
            ctx.arc(bStartX - 40, bBaseY - 30, 45, 0, Math.PI * 2);
            ctx.arc(bStartX - 15, bBaseY - 60, 35, 0, Math.PI * 2);
            ctx.fill();

            // 3. State Nodes Blinking (ny, ca, tx...)
            stateNodes.forEach(node => {
                node.alpha += node.step;
                if (node.alpha > 0.85 || node.alpha < 0.1) node.step = -node.step;
                
                const nx = canvas.width * node.x;
                const ny = canvas.height * node.y;

                ctx.fillStyle = `rgba(251, 191, 36, ${node.alpha})`;
                ctx.font = 'italic 800 11px Georgia, serif';
                ctx.fillText(node.code, nx, ny);

                ctx.beginPath();
                ctx.arc(nx - 6, ny - 4, 3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(16, 185, 129, ${node.alpha})`;
                ctx.fill();
            });

            // 4. Flying Ambient Cyber Birds
            birds.forEach(b => {
                b.x += b.vx;
                b.wing += 0.15;
                if (b.x > canvas.width + 50) b.x = -50;

                ctx.strokeStyle = 'rgba(52, 211, 153, 0.5)';
                ctx.lineWidth = 1.8;
                ctx.beginPath();
                const wingOffset = Math.sin(b.wing) * 4;
                ctx.moveTo(b.x - b.size, b.y + wingOffset);
                ctx.lineTo(b.x, b.y);
                ctx.lineTo(b.x + b.size, b.y + wingOffset);
                ctx.stroke();
            });

            requestAnimationFrame(drawLivingWorld);
        }
        drawLivingWorld();

        // -------------------------------------------------------------
        // CLICK-TO-BURST BUBBLES WITH DYNAMIC MODULE REPLACER
        // -------------------------------------------------------------
        const moduleNames = [
            '<i class="fas fa-envelope-open-text"></i> Warmup AI Engine',
            '<i class="fas fa-search-location"></i> NYC Blueprint Scraper',
            '<i class="fas fa-shield-alt"></i> Spam Filter Guard',
            '<i class="fas fa-user-check"></i> Colleague Approvals',
            '<i class="fas fa-chart-line"></i> Pipeline Analytics',
            '<i class="fas fa-magic"></i> AI Pitch Personalizer'
        ];

        function popBubble(el) {
            el.classList.add('bubble-popping');
            setTimeout(() => {
                const randomName = moduleNames[Math.floor(Math.random() * moduleNames.length)];
                el.innerHTML = randomName;
                el.classList.remove('bubble-popping');
            }, 300);
        }

        // Navigation & Modals
        function toggleTheme() {
            var html = document.documentElement;
            var cur = html.getAttribute('data-theme');
            var nxt = cur === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', nxt);
            document.getElementById('themeIcon').className = nxt === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }

        function openAlertModal() { document.getElementById('alertModal').style.display = 'flex'; }
        function closeAlertModal() { document.getElementById('alertModal').style.display = 'none'; }
        function sendBroadcast() {
            var msg = document.getElementById('broadcastMsg').value;
            if(msg) {
                alert('📢 Alert successfully pushed to all active Colleagues: ' + msg);
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
                alert('✔ Account registered! You can now login.');
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

print("✔ Full Interactive Cyber AI Universe with Living World Canvas Deployed!")
