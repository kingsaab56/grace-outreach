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

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

APP_HTML = \'\'\'<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="emerald">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Enterprise Command Center</title>
    
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
            padding: 8px 24px; display: flex; gap: 10px; align-items: center;
        }
        .ribbon-btn {
            background: transparent; border: 1px solid transparent; color: var(--text-muted);
            padding: 10px 20px; font-size: 13.5px; font-weight: 800; cursor: pointer; border-radius: 8px; white-space: nowrap;
            display: inline-flex; align-items: center; gap: 8px; transition: 0.2s;
        }
        .ribbon-btn:hover, .ribbon-btn.active { background: var(--primary); color: #ffffff; box-shadow: 0 4px 15px var(--primary-glow); }

        .dashboard-body { padding: 28px 28px; max-width: 1400px; margin: 0 auto; width: 100%; flex: 1; }
        .tab-section { display: none; }
        .tab-section.active { display: block; }
        .panel-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 16px; padding: 26px; margin-bottom: 24px; }

        .modules-matrix-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-top: 14px;
        }
        .module-matrix-card {
            background: rgba(3, 10, 12, 0.6); border: 1.5px solid var(--border-color); border-radius: 12px;
            padding: 18px; display: flex; gap: 14px; align-items: flex-start; cursor: pointer; transition: all 0.2s;
        }
        .module-matrix-card:hover {
            border-color: var(--primary); transform: translateY(-3px); box-shadow: 0 6px 20px var(--primary-glow);
        }
        .module-matrix-card.locked {
            opacity: 0.45; filter: grayscale(1); cursor: not-allowed; border-color: rgba(239, 68, 68, 0.4);
        }
        .matrix-icon {
            font-size: 22px; color: var(--gold); background: rgba(245, 158, 11, 0.1); width: 44px; height: 44px;
            display: flex; align-items: center; justify-content: center; border-radius: 10px; border: 1px solid var(--border-gold);
        }

        .colleague-card {
            background: rgba(3, 10, 12, 0.75); border: 1.5px solid var(--border-color);
            border-radius: 14px; padding: 20px; margin-bottom: 18px;
        }
        .colleague-header {
            display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px; margin-bottom: 14px;
        }
        .toggle-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; margin-top: 10px;
        }
        .toggle-item {
            display: flex; justify-content: space-between; align-items: center; background: rgba(8, 22, 25, 0.8);
            padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.15); font-size: 12px; font-weight: 700;
        }
        .switch { position: relative; display: inline-block; width: 38px; height: 20px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #374151; border-radius: 20px; transition: 0.3s; }
        .slider::before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: 0.3s; }
        input:checked + .slider { background: var(--primary); }
        input:checked + .slider::before { transform: translateX(18px); }

        .active-badge { display: inline-block; padding: 3px 8px; border-radius: 12px; background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 11px; font-weight: 800; border: 1px solid #10b981; }
    </style>
</head>
<body>

    <div id="cinematicStage">
        <canvas id="worldCanvas"></canvas>
        <div class="hologram-emblem"><img src="/favicon.ico?v=999" alt="Grace Hologram"></div>

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
        <div class="module-capsule" style="left: 15vw; top: 55vh;"><i class="fas fa-dollar-sign"></i> &#36;64,800 CRM Deals</div>
        <div class="module-capsule" style="left: 36vw; top: 65vh;"><i class="fas fa-robot"></i> AI Guide Ready</div>
    </div>

    <!-- 1. AUTH LOGIN (INSTANT ZERO-BLOCK OPENING) -->
    <div id="authViewport">
        <div class="auth-glass-panel">
            <div class="brand-crest"><img src="/favicon.ico?v=999" alt="Grace Crest"></div>
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

    <!-- 2. ENTERPRISE APP VIEW -->
    <div id="enterpriseApp">
        <header class="top-navbar">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div class="nav-logo-thumb"><img src="/favicon.ico?v=999" alt="Grace Logo"></div>
                <div>
                    <div style="font-size: 17px; font-weight: 900;">GRACE OUTREACH ASSISTANT</div>
                    <div style="font-size: 11.5px;"><span style="color: #fbbf24; font-style: italic;">⚡ Built by King Saab</span> | <span style="color: #6ee7b7;">🌟 Strategic Guidance by Abdullah Khan</span></div>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="background: rgba(3, 10, 12, 0.8); padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border-gold); display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 11.5px; color: var(--text-muted); font-weight: 700;">Active Session:</span>
                    <select id="userRoleSelector" onchange="switchColleagueView(this.value)" style="background: transparent; color: #fbbf24; border: none; font-weight: 800; font-size: 12px; outline: none; cursor: pointer;">
                        <option value="admin" style="background:#08171a;">👑 King Saab (Super Admin)</option>
                    </select>
                </div>

                <button style="background: linear-gradient(135deg, #d97706, #b45309); border:none; color:#fff; padding:9px 18px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="openBroadcastModal()"><i class="fas fa-bullhorn"></i> Broadcast Alert</button>
                <button style="background: #dc2626; border:none; color:#fff; padding:9px 16px; border-radius:8px; font-weight:800; cursor:pointer;" onclick="handlePowerOff()"><i class="fas fa-power-off"></i> Power Off</button>
            </div>
        </header>

        <nav class="nav-ribbon-bar">
            <button class="ribbon-btn active" onclick="switchTab(\'tab-dash\', this)"><i class="fas fa-chart-pie"></i> 1. Dashboard Overview</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-matrix\', this)"><i class="fas fa-th-large"></i> 2. 22-Module Control Matrix</button>
            <button class="ribbon-btn" onclick="switchTab(\'tab-team-control\', this)"><i class="fas fa-user-shield"></i> 3. Colleague Management & Permissions</button>
        </nav>

        <main class="dashboard-body">
            
            <!-- OPTION 1: DASHBOARD -->
            <section id="tab-dash" class="tab-section active">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 24px;">
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">ACTIVE OUTREACH PIPELINE</div><div style="font-size:28px; font-weight:900;">2,480 Leads</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">CONNECTED GMAIL ACCOUNTS</div><div style="font-size:28px; font-weight:900;">5 Inboxes</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">WEEKLY SENT VOLUME</div><div style="font-size:28px; font-weight:900;">1,240 Emails</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">PIPELINE DEAL VALUE</div><div style="font-size:28px; font-weight:900; color:#10b981;">&#36;64,800</div></div>
                </div>
                <div class="panel-card">
                    <div style="font-size:16.5px; font-weight:800; margin-bottom:10px; color:#fbbf24;">⚡ 24/7 Cloud Outreach Engine Active</div>
                    <p style="color:var(--text-muted); font-size:14px; line-height:1.6;">Cloud daemon is running continuously on Railway. Total Pipeline Value verified at &#36;64,800 across active stages.</p>
                </div>
            </section>

            <!-- OPTION 2: 22 MODULES MATRIX -->
            <section id="tab-matrix" class="tab-section">
                <div class="panel-card">
                    <div style="font-size:17px; font-weight:800; margin-bottom:14px; display:flex; justify-content:space-between;">
                        <span>🎛️ Complete 22-Module Functional Matrix</span>
                        <span id="activeRoleLabel" style="font-size:12px; color:#34d399; font-weight:700;">● Admin View (All Modules Unlocked)</span>
                    </div>
                    
                    <div class="modules-matrix-grid" id="matrixContainer">
                        <div class="module-matrix-card" id="mod-1" onclick="openModule(1, 'Dashboard Overview')"><div class="matrix-icon"><i class="fas fa-chart-pie"></i></div><div><div style="font-weight:800; font-size:14px;">1. Dashboard Overview</div><div style="font-size:11.5px; color:var(--text-muted);">Live analytics & telemetry</div></div></div>
                        <div class="module-matrix-card" id="mod-2" onclick="openModule(2, 'Gmail Multi-Tenant Hub')"><div class="matrix-icon"><i class="fas fa-envelope"></i></div><div><div style="font-weight:800; font-size:14px;">2. Gmail Multi-Tenant Hub</div><div style="font-size:11.5px; color:var(--text-muted);">5-account rotation engine</div></div></div>
                        <div class="module-matrix-card" id="mod-3" onclick="openModule(3, 'AI Warmup Ramp')"><div class="matrix-icon"><i class="fas fa-fire"></i></div><div><div style="font-weight:800; font-size:14px;">3. AI Warmup Ramp</div><div style="font-size:11.5px; color:var(--text-muted);">Daily sender reputation guard</div></div></div>
                        <div class="module-matrix-card" id="mod-4" onclick="openModule(4, 'Campaign Studio')"><div class="matrix-icon"><i class="fas fa-paper-plane"></i></div><div><div style="font-weight:800; font-size:14px;">4. Campaign Studio</div><div style="font-size:11.5px; color:var(--text-muted);">Dynamic follow-up launcher</div></div></div>
                        <div class="module-matrix-card" id="mod-5" onclick="openModule(5, 'Spin-Syntax AI Generator')"><div class="matrix-icon"><i class="fas fa-magic"></i></div><div><div style="font-weight:800; font-size:14px;">5. Spin-Syntax AI Engine</div><div style="font-size:11.5px; color:var(--text-muted);">Spam-free copy variation</div></div></div>
                        <div class="module-matrix-card" id="mod-6" onclick="openModule(6, 'Lead Scraper')"><div class="matrix-icon"><i class="fas fa-search"></i></div><div><div style="font-weight:800; font-size:14px;">6. Lead Scraper</div><div style="font-size:11.5px; color:var(--text-muted);">Architect firm contact finder</div></div></div>
                        <div class="module-matrix-card" id="mod-7" onclick="openModule(7, 'CRM Revenue Pipeline')"><div class="matrix-icon"><i class="fas fa-dollar-sign"></i></div><div><div style="font-weight:800; font-size:14px;">7. CRM Revenue Pipeline</div><div style="font-size:11.5px; color:var(--text-muted);">&#36;64,800 Active deal monitor</div></div></div>
                        <div class="module-matrix-card" id="mod-8" onclick="openModule(8, 'Colleague Access Control')"><div class="matrix-icon"><i class="fas fa-users-cog"></i></div><div><div style="font-weight:800; font-size:14px;">8. Colleague Access Controller</div><div style="font-size:11.5px; color:var(--text-muted);">Permission toggles manager</div></div></div>
                        <div class="module-matrix-card" id="mod-9" onclick="openModule(9, 'System Doctor Daemon')"><div class="matrix-icon"><i class="fas fa-heartbeat"></i></div><div><div style="font-weight:800; font-size:14px;">9. System Doctor Daemon</div><div style="font-size:11.5px; color:var(--text-muted);">Live health & PID supervisor</div></div></div>
                        <div class="module-matrix-card" id="mod-10" onclick="openModule(10, 'Audio Studio & Extractor')"><div class="matrix-icon"><i class="fas fa-music"></i></div><div><div style="font-weight:800; font-size:14px;">10. Audio Studio & Extractor</div><div style="font-size:11.5px; color:var(--text-muted);">Soundscape & ambient media</div></div></div>
                        <div class="module-matrix-card" id="mod-11" onclick="openModule(11, 'Built-in AI Guide Agent')"><div class="matrix-icon"><i class="fas fa-robot"></i></div><div><div style="font-weight:800; font-size:14px;">11. Built-in AI Guide Agent</div><div style="font-size:11.5px; color:var(--text-muted);">Interactive portal assistant</div></div></div>
                        <div class="module-matrix-card" id="mod-12" onclick="openModule(12, 'OAuth Token Vault')"><div class="matrix-icon"><i class="fas fa-shield-alt"></i></div><div><div style="font-weight:800; font-size:14px;">12. OAuth Token Vault</div><div style="font-size:11.5px; color:var(--text-muted);">Encrypted keyphrase protection</div></div></div>
                        <div class="module-matrix-card" id="mod-13" onclick="openModule(13, 'Timezone Scheduler')"><div class="matrix-icon"><i class="fas fa-clock"></i></div><div><div style="font-weight:800; font-size:14px;">13. Timezone Scheduler</div><div style="font-size:11.5px; color:var(--text-muted);">EST & PST smart dispatching</div></div></div>
                        <div class="module-matrix-card" id="mod-14" onclick="openModule(14, 'Bounce Shield')"><div class="matrix-icon"><i class="fas fa-filter"></i></div><div><div style="font-weight:800; font-size:14px;">14. Bounce Shield</div><div style="font-size:11.5px; color:var(--text-muted);">0.08% bounce filtering</div></div></div>
                        <div class="module-matrix-card" id="mod-15" onclick="openModule(15, 'Auto-Reply Detector')"><div class="matrix-icon"><i class="fas fa-reply-all"></i></div><div><div style="font-weight:800; font-size:14px;">15. Auto-Reply Detector</div><div style="font-size:11.5px; color:var(--text-muted);">Positive sentiment alerts</div></div></div>
                        <div class="module-matrix-card" id="mod-16" onclick="openModule(16, 'CSV / Excel Export')"><div class="matrix-icon"><i class="fas fa-file-export"></i></div><div><div style="font-weight:800; font-size:14px;">16. CSV / Excel Exporter</div><div style="font-size:11.5px; color:var(--text-muted);">1-Click campaign reports</div></div></div>
                        <div class="module-matrix-card" id="mod-17" onclick="openModule(17, 'Broadcast Notification Node')"><div class="matrix-icon"><i class="fas fa-bullhorn"></i></div><div><div style="font-weight:800; font-size:14px;">17. Broadcast Notification Node</div><div style="font-size:11.5px; color:var(--text-muted);">Real-time colleague alerts</div></div></div>
                        <div class="module-matrix-card" id="mod-18" onclick="openModule(18, 'Brand Palette Studio')"><div class="matrix-icon"><i class="fas fa-palette"></i></div><div><div style="font-weight:800; font-size:14px;">18. Brand Palette Studio</div><div style="font-size:11.5px; color:var(--text-muted);">Luxury theme customization</div></div></div>
                        <div class="module-matrix-card" id="mod-19" onclick="openModule(19, 'Cloud Webhook Dispatcher')"><div class="matrix-icon"><i class="fas fa-network-wired"></i></div><div><div style="font-weight:800; font-size:14px;">19. Cloud Webhook Dispatcher</div><div style="font-size:11.5px; color:var(--text-muted);">Third-party JSON triggers</div></div></div>
                        <div class="module-matrix-card" id="mod-20" onclick="openModule(20, 'Daily Quota Guard')"><div class="matrix-icon"><i class="fas fa-tachometer-alt"></i></div><div><div style="font-weight:800; font-size:14px;">20. Daily Quota Guard</div><div style="font-size:11.5px; color:var(--text-muted);">50/50 safe account limits</div></div></div>
                        <div class="module-matrix-card" id="mod-21" onclick="openModule(21, 'HTML Signature Builder')"><div class="matrix-icon"><i class="fas fa-signature"></i></div><div><div style="font-weight:800; font-size:14px;">21. HTML Signature Builder</div><div style="font-size:11.5px; color:var(--text-muted);">Professional design layout</div></div></div>
                        <div class="module-matrix-card" id="mod-22" onclick="openModule(22, 'Conversion ROI Predictor')"><div class="matrix-icon"><i class="fas fa-chart-line"></i></div><div><div style="font-weight:800; font-size:14px;">22. Conversion ROI Predictor</div><div style="font-size:11.5px; color:var(--text-muted);">Deal closing probability model</div></div></div>
                    </div>
                </div>
            </section>

            <!-- OPTION 3: COLLEAGUE MANAGEMENT -->
            <section id="tab-team-control" class="tab-section">
                <div class="panel-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <div style="font-size:17px; font-weight:800; color:#fbbf24;">👥 Colleague Multi-User Management & Module Access</div>
                        <button class="btn-luxury" style="width:auto; padding:8px 18px;" onclick="addNewColleague()"><i class="fas fa-user-plus"></i> Add New Colleague Profile</button>
                    </div>
                    <p style="color:var(--text-muted); font-size:13.5px; margin-bottom:20px;">Admin can configure individual module permissions, delete colleague profiles, and send targeted alert notifications.</p>

                    <div id="colleaguesListContainer"></div>
                </div>
            </section>

        </main>
    </div>

    <script>
        window.addEventListener('DOMContentLoaded', () => {
            renderColleagues();
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

        let colleagues = [
            { id: "COL-901", key: "colleague1", name: "Alex Vance", color: "#34d399", perms: [1,2,3,4,7,10,11] },
            { id: "COL-902", key: "colleague2", name: "Sarah Jenkins", color: "#38bdf8", perms: [1,4,5,6,11,16] }
        ];

        function renderColleagues() {
            const container = document.getElementById('colleaguesListContainer');
            const selector = document.getElementById('userRoleSelector');
            if(!container) return;

            container.innerHTML = "";
            selector.innerHTML = '<option value="admin" style="background:#08171a;">👑 King Saab (Super Admin)</option>';

            colleagues.forEach(col => {
                const opt = document.createElement('option');
                opt.value = col.key;
                opt.style.background = "#08171a";
                opt.innerText = "👤 " + col.name + " (" + col.id + ")";
                selector.appendChild(opt);

                const card = document.createElement('div');
                card.className = "colleague-card";
                card.id = "card-" + col.key;
                card.innerHTML = `
                    <div class="colleague-header">
                        <div>
                            <span style="font-weight:900; font-size:15px; color:${col.color};">${col.name}</span>
                            <span style="font-size:12px; color:var(--text-muted); margin-left:10px;">ID: <strong>${col.id}</strong></span>
                            <span class="active-badge" style="margin-left:10px;">● ACTIVE LIVE</span>
                        </div>
                        <div style="display:flex; gap:8px;">
                            <button class="btn-luxury" style="width:auto; padding:6px 14px; font-size:12px; background:#d97706;" onclick="sendTargetedAlert('${col.id}', '${col.name}')"><i class="fas fa-bell"></i> Send Alert</button>
                            <button class="btn-luxury" style="width:auto; padding:6px 14px; font-size:12px; background:#dc2626;" onclick="deleteColleague('${col.key}', '${col.name}')"><i class="fas fa-trash-alt"></i> Delete</button>
                        </div>
                    </div>
                    <div style="font-size:12.5px; font-weight:800; color:#fbbf24; margin-bottom:6px;">Module Permissions for ${col.name}:</div>
                    <div class="toggle-grid">
                        <div class="toggle-item"><span>1. Dashboard</span><label class="switch"><input type="checkbox" ${col.perms.includes(1)?'checked':''} onchange="updateColleaguePerm('${col.key}', 1, this.checked)"><span class="slider"></span></label></div>
                        <div class="toggle-item"><span>2. Gmail Multi-Tenant</span><label class="switch"><input type="checkbox" ${col.perms.includes(2)?'checked':''} onchange="updateColleaguePerm('${col.key}', 2, this.checked)"><span class="slider"></span></label></div>
                        <div class="toggle-item"><span>3. AI Warmup Ramp</span><label class="switch"><input type="checkbox" ${col.perms.includes(3)?'checked':''} onchange="updateColleaguePerm('${col.key}', 3, this.checked)"><span class="slider"></span></label></div>
                        <div class="toggle-item"><span>4. Campaign Studio</span><label class="switch"><input type="checkbox" ${col.perms.includes(4)?'checked':''} onchange="updateColleaguePerm('${col.key}', 4, this.checked)"><span class="slider"></span></label></div>
                        <div class="toggle-item"><span>5. Spin-Syntax AI</span><label class="switch"><input type="checkbox" ${col.perms.includes(5)?'checked':''} onchange="updateColleaguePerm('${col.key}', 5, this.checked)"><span class="slider"></span></label></div>
                        <div class="toggle-item"><span>6. Lead Scraper</span><label class="switch"><input type="checkbox" ${col.perms.includes(6)?'checked':''} onchange="updateColleaguePerm('${col.key}', 6, this.checked)"><span class="slider"></span></label></div>
                        <div class="toggle-item"><span>7. CRM Pipeline Deals</span><label class="switch"><input type="checkbox" ${col.perms.includes(7)?'checked':''} onchange="updateColleaguePerm('${col.key}', 7, this.checked)"><span class="slider"></span></label></div>
                        <div class="toggle-item"><span>11. AI Guide Agent</span><label class="switch"><input type="checkbox" ${col.perms.includes(11)?'checked':''} onchange="updateColleaguePerm('${col.key}', 11, this.checked)"><span class="slider"></span></label></div>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        function deleteColleague(colKey, name) {
            if(confirm("Are you sure you want to delete colleague profile: " + name + "? All permissions and active session will be terminated.")) {
                colleagues = colleagues.filter(c => c.key !== colKey);
                renderColleagues();
                switchColleagueView('admin');
                alert("✔ Colleague profile '" + name + "' deleted successfully.");
            }
        }

        function switchColleagueView(role) {
            const label = document.getElementById('activeRoleLabel');
            let allowed = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22];
            
            if(role === 'admin') {
                label.innerText = "● Admin View (All Modules Unlocked)";
                label.style.color = "#34d399";
            } else {
                const col = colleagues.find(c => c.key === role);
                allowed = col ? col.perms : [];
                label.innerText = "● Testing as " + (col ? col.name.toUpperCase() : role) + " (Restricted Modules Locked)";
                label.style.color = "#fbbf24";
            }

            for(let i = 1; i <= 22; i++) {
                const card = document.getElementById('mod-' + i);
                if(card) {
                    if(allowed.includes(i)) {
                        card.classList.remove('locked');
                    } else {
                        card.classList.add('locked');
                    }
                }
            }
        }

        function updateColleaguePerm(colKey, modId, enabled) {
            const col = colleagues.find(c => c.key === colKey);
            if(col) {
                if(enabled) {
                    if(!col.perms.includes(modId)) col.perms.push(modId);
                } else {
                    col.perms = col.perms.filter(x => x !== modId);
                }
            }
            const currentSelected = document.getElementById('userRoleSelector').value;
            if(currentSelected === colKey) switchColleagueView(colKey);
        }

        function openModule(modId, modTitle) {
            const role = document.getElementById('userRoleSelector').value;
            let allowed = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22];
            if(role !== 'admin') {
                const col = colleagues.find(c => c.key === role);
                allowed = col ? col.perms : [];
            }
            if(!allowed.includes(modId)) {
                alert("⛔ ACCESS DENIED: Module " + modId + " (" + modTitle + ") is disabled by Admin for this Colleague.");
                return;
            }
            alert("✔ Opening Module " + modId + ": " + modTitle);
        }

        function openBroadcastModal() {
            let options = "Select Target Recipient:\\n0: All Colleagues (Global Broadcast)\\n";
            colleagues.forEach((c, idx) => {
                options += (idx + 1) + ": " + c.name + " (" + c.id + ")\\n";
            });
            const sel = prompt(options + "\\nEnter recipient number (0 to " + colleagues.length + "):", "0");
            if(sel === null) return;
            
            let targetName = "All Active Colleagues";
            const num = parseInt(sel);
            if(num > 0 && num <= colleagues.length) {
                targetName = colleagues[num - 1].name + " (" + colleagues[num - 1].id + ")";
            }

            const msg = prompt("Type Broadcast Message for [" + targetName + "]:", "System alert: Daily lead quota limit updated.");
            if(msg) {
                alert("📢 Broadcast Dispatched to [" + targetName + "]: " + msg);
            }
        }

        function sendTargetedAlert(id, name) {
            const msg = prompt("Enter targeted alert for " + name + " (" + id + "):", "Please review pending proposal deals in CRM.");
            if(msg) {
                alert("📢 Direct Alert Sent to " + name + " (" + id + "): " + msg);
            }
        }

        function addNewColleague() {
            const name = prompt("Enter Colleague Full Name:", "Marcus Vance");
            if(!name) return;
            const newKey = "colleague_" + Date.now();
            const newId = "COL-" + Math.floor(100 + Math.random() * 900);
            colleagues.push({
                id: newId,
                key: newKey,
                name: name,
                color: "#a78bfa",
                perms: [1, 2, 4, 6]
            });
            renderColleagues();
            alert("✔ Colleague profile created! Name: " + name + " | Assigned ID: " + newId + " (Status Active)");
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

print("✔ Generated clean instant web_portal.py without splash delay!")
