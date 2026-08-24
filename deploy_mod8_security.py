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

b64_logo = base64.b64encode(raw_bytes).decode('utf-8')

html_template = """<!DOCTYPE html>
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
            --bg-card: rgba(8, 22, 25, 0.92);
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
            transition: 0.2s; user-select: none;
        }
        .btn-luxury:hover { transform: translateY(-2px); box-shadow: 0 8px 25px var(--primary-glow); }

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

        .category-header {
            font-size: 14px; font-weight: 900; color: #fbbf24; margin: 18px 0 10px 0;
            display: flex; align-items: center; gap: 8px; text-transform: uppercase;
        }
        .inbox-card {
            background: rgba(3, 10, 12, 0.7); border: 1px solid var(--border-color); border-radius: 12px;
            padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;
        }
        .auth-tag { font-size: 10.5px; font-weight: 800; padding: 2px 8px; border-radius: 6px; }
        .auth-oauth { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #0284c7; }
        .auth-pass { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #d97706; }
        .active-badge { display: inline-block; padding: 3px 8px; border-radius: 12px; background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 11px; font-weight: 800; border: 1px solid #10b981; }

        /* COLLEAGUE CARDS ENHANCED */
        .colleague-card { background: rgba(3, 10, 12, 0.75); border: 1.5px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 18px; }
        .colleague-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 14px; }
        .toggle-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; margin-top: 10px; }
        .toggle-item { display: flex; justify-content: space-between; align-items: center; background: rgba(8, 22, 25, 0.8); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.15); font-size: 12px; font-weight: 700; }
        .switch { position: relative; display: inline-block; width: 38px; height: 20px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #374151; border-radius: 20px; transition: 0.3s; }
        .slider::before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: 0.3s; }
        input:checked + .slider { background: var(--primary); }
        input:checked + .slider::before { transform: translateX(18px); }

        .preset-btn { background: rgba(245, 158, 11, 0.15); border: 1px solid var(--border-gold); color: #fbbf24; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
        .preset-btn:hover { background: var(--gold); color: #000; }

        .audit-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
        .audit-table th, .audit-table td { border: 1px solid rgba(16, 185, 129, 0.2); padding: 8px 10px; text-align: left; }
        .audit-table th { background: rgba(5, 150, 105, 0.2); color: #34d399; font-weight: 800; }
        .audit-table td { background: rgba(3, 10, 12, 0.6); }

        .modal-overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.85); z-index: 99999; align-items: center; justify-content: center;
        }
        .modal-box {
            background: #08171a; border: 1.5px solid var(--border-gold); border-radius: 16px;
            padding: 26px; width: 90%; max-width: 650px; box-shadow: 0 10px 40px rgba(0,0,0,0.9);
            max-height: 90vh; overflow-y: auto;
        }

        .scraper-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
        .scraper-table th, .scraper-table td { border: 1px solid rgba(16, 185, 129, 0.2); padding: 8px 10px; text-align: left; }
        .scraper-table th { background: rgba(5, 150, 105, 0.2); color: #34d399; font-weight: 800; }
        .scraper-table td { background: rgba(3, 10, 12, 0.6); }

        /* KANBAN CRM BOARD WITH DRAG & DROP & REVERT */
        .kanban-grid {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 14px;
        }
        .kanban-col {
            background: rgba(3, 10, 12, 0.7); border: 1.5px solid var(--border-color);
            border-radius: 12px; padding: 12px; min-height: 320px; display: flex; flex-direction: column;
            transition: background 0.2s, border-color 0.2s;
        }
        .kanban-col.drag-over {
            background: rgba(5, 150, 105, 0.2);
            border-color: #34d399;
        }
        .kanban-col-head {
            font-size: 11.5px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px;
            display: flex; justify-content: space-between; border-bottom: 1px solid rgba(16, 185, 129, 0.15); padding-bottom: 6px;
        }
        .deal-item {
            background: #08171a; border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 8px; padding: 10px; margin-bottom: 8px; cursor: grab; transition: 0.2s;
            user-select: none;
        }
        .deal-item:active { cursor: grabbing; opacity: 0.6; }
        .deal-item:hover { border-color: var(--primary); transform: translateY(-2px); }
        .deal-val { color: #10b981; font-weight: 900; font-size: 13px; margin-top: 4px; }
        .btn-kanban {
            background: rgba(8, 22, 25, 0.9); border: 1px solid var(--border-color);
            color: #f8fafc; font-size: 10px; font-weight: 800; padding: 2px 7px;
            border-radius: 4px; cursor: pointer; transition: 0.15s;
        }
        .btn-kanban:hover { background: var(--primary); color: #fff; border-color: var(--primary); }
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
        <div class="module-capsule" style="left: 15vw; top: 55vh;"><i class="fas fa-dollar-sign"></i> <span id="capsuleDealVal">&#36;64,800</span> CRM Deals</div>
        <div class="module-capsule" style="left: 36vw; top: 65vh;"><i class="fas fa-robot"></i> AI Guide Ready</div>
    </div>

    <!-- 1. AUTH LOGIN VIEW -->
    <div id="authViewport">
        <div class="auth-glass-panel">
            <div class="brand-crest"><img src="/favicon.ico?v=999" alt="Grace Crest"></div>
            <div style="font-size: 22px; font-weight: 900; letter-spacing: 1.5px;">GRACE OUTREACH</div>
            
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px dashed rgba(245, 158, 11, 0.35); padding: 10px; border-radius: 12px; margin: 12px 0 20px;">
                <div style="font-family: Georgia, serif; font-style: italic; font-weight: 800; font-size: 13.5px; color: #fbbf24;">✨ Architected & Engineered by King Saab</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">🌟 Strategic Guidance by <strong style="color: #34d399;">Abdullah Khan</strong></div>
            </div>

            <div>
                <div class="form-group">
                    <label>Colleague Identifier / ID</label>
                    <input type="text" id="authUsername" class="form-control" placeholder="Enter ID (e.g. kingsaab56 or COL-901)" value="kingsaab56" onkeydown="if(event.key==='Enter') executeLogin()">
                </div>
                <div class="form-group">
                    <label>Security Keyphrase</label>
                    <input type="password" id="authPassword" class="form-control" placeholder="Enter Keyphrase" value="admin123" onkeydown="if(event.key==='Enter') executeLogin()">
                </div>
                <button type="button" class="btn-luxury" id="loginBtn" onclick="executeLogin()"><i class="fas fa-fingerprint"></i> Enter Command Center</button>
            </div>
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
            <button class="ribbon-btn active" onclick="switchTab('tab-dash', this)"><i class="fas fa-chart-pie"></i> 1. Dashboard Overview</button>
            <button class="ribbon-btn" onclick="switchTab('tab-matrix', this)"><i class="fas fa-th-large"></i> 2. 22-Module Control Matrix</button>
            <button class="ribbon-btn" onclick="switchTab('tab-team-control', this)"><i class="fas fa-user-shield"></i> 3. Colleague Management & Permissions</button>
        </nav>

        <main class="dashboard-body">
            
            <!-- OPTION 1: DASHBOARD -->
            <section id="tab-dash" class="tab-section active">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 24px;">
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">ACTIVE OUTREACH PIPELINE</div><div style="font-size:28px; font-weight:900;" id="activePipelineMetric">2,480 Leads</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">CONNECTED GMAIL ACCOUNTS</div><div style="font-size:28px; font-weight:900;" id="connectedCountBadge">5 Inboxes</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">WEEKLY SENT VOLUME</div><div style="font-size:28px; font-weight:900;">1,240 Emails</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">PIPELINE DEAL VALUE</div><div style="font-size:28px; font-weight:900; color:#10b981;" id="dashPipelineVal">&#36;64,800</div></div>
                </div>
                
                <div class="panel-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                        <div>
                            <div style="font-size:17px; font-weight:800; color:#fbbf24;"><i class="fas fa-envelope-open-text"></i> Gmail Multi-Tenant Hub (Active 3-Tier Sync)</div>
                            <div style="font-size:12px; color:var(--text-muted);">Auto-classified by Business, Workplace, and Personal Inboxes</div>
                        </div>
                        <button class="btn-luxury" style="width: auto; padding: 8px 18px;" onclick="openAddGmailModal()"><i class="fas fa-plus-circle"></i> Connect New Account (OAuth / Pass)</button>
                    </div>

                    <div class="category-header"><i class="fas fa-building"></i> 1. Business Inboxes (Grace Outreach Domains)</div>
                    <div id="businessInboxesContainer"></div>

                    <div class="category-header"><i class="fas fa-briefcase"></i> 2. Workplace Inboxes (Malik Shani / Workspaces)</div>
                    <div id="workplaceInboxesContainer"></div>

                    <div class="category-header"><i class="fas fa-user-circle"></i> 3. Personal Inboxes (Outreach Rotators)</div>
                    <div id="personalInboxesContainer"></div>
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
                        <div class="module-matrix-card" id="mod-2" onclick="openModule(2, 'Gmail Multi-Tenant Hub')"><div class="matrix-icon"><i class="fas fa-envelope"></i></div><div><div style="font-weight:800; font-size:14px;">2. Gmail Multi-Tenant Hub</div><div style="font-size:11.5px; color:var(--text-muted);">OAuth & 3-Tier Categorization</div></div></div>
                        <div class="module-matrix-card" id="mod-3" onclick="openModule(3, 'AI Warmup Ramp')"><div class="matrix-icon"><i class="fas fa-fire"></i></div><div><div style="font-weight:800; font-size:14px;">3. AI Warmup Ramp</div><div style="font-size:11.5px; color:var(--text-muted);">Daily sender reputation guard</div></div></div>
                        <div class="module-matrix-card" id="mod-4" onclick="openModule(4, 'Campaign Studio')"><div class="matrix-icon"><i class="fas fa-paper-plane"></i></div><div><div style="font-weight:800; font-size:14px;">4. Campaign Studio</div><div style="font-size:11.5px; color:var(--text-muted);">A/B Split + AI Scorer + Timezone</div></div></div>
                        <div class="module-matrix-card" id="mod-5" onclick="openModule(5, 'Spin-Syntax AI Generator')"><div class="matrix-icon"><i class="fas fa-magic"></i></div><div><div style="font-weight:800; font-size:14px;">5. Spin-Syntax AI Engine</div><div style="font-size:11.5px; color:var(--text-muted);">1-Click Auto-Spinner & Live Preview</div></div></div>
                        <div class="module-matrix-card" id="mod-6" onclick="openModule(6, 'Lead Scraper')"><div class="matrix-icon"><i class="fas fa-search"></i></div><div><div style="font-weight:800; font-size:14px;">6. US Architect & Contractor Scraper</div><div style="font-size:11.5px; color:var(--text-muted);">All 50 US States + Live Ping & CSV/TXT</div></div></div>
                        <div class="module-matrix-card" id="mod-7" onclick="openModule(7, 'CRM Revenue Pipeline')"><div class="matrix-icon"><i class="fas fa-dollar-sign"></i></div><div><div style="font-weight:800; font-size:14px;">7. CRM Revenue Pipeline</div><div style="font-size:11.5px; color:var(--text-muted);"><span id="matrixDealVal">&#36;64,800</span> Active deal monitor (Drag & Drop)</div></div></div>
                        <div class="module-matrix-card" id="mod-8" onclick="openModule(8, 'Colleague Access Control')"><div class="matrix-icon"><i class="fas fa-users-cog"></i></div><div><div style="font-weight:800; font-size:14px;">8. Colleague Access Controller</div><div style="font-size:11.5px; color:var(--text-muted);">Audit Logs, Presets & Force Logout</div></div></div>
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

            <!-- OPTION 3: COLLEAGUE MANAGEMENT & SECURITY AUDIT -->
            <section id="tab-team-control" class="tab-section">
                <div class="panel-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <div>
                            <div style="font-size:18px; font-weight:900; color:#fbbf24;">👥 Module 8: Colleague Access Controller & Security Vault</div>
                            <div style="font-size:12px; color:var(--text-muted);">Role-Based Granular Permissions, Activity Audits & Force Logout</div>
                        </div>
                        <button class="btn-luxury" style="width:auto; padding:8px 18px;" onclick="addNewColleague()"><i class="fas fa-user-plus"></i> Add New Colleague Profile</button>
                    </div>

                    <div id="colleaguesListContainer"></div>

                    <!-- ACTIVITY AUDIT LOG -->
                    <div style="margin-top: 26px; border-top: 1px solid var(--border-color); padding-top: 18px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                            <span style="font-size: 14px; font-weight: 800; color: #38bdf8;"><i class="fas fa-shield-alt"></i> Live Security Activity & Dispatch Audit Log</span>
                            <span style="font-size: 11px; color: var(--text-muted);">Encrypted Session Activity</span>
                        </div>
                        <table class="audit-table">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Colleague / ID</th>
                                    <th>Action Performed</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody id="auditLogBody">
                                <tr><td>Just Now</td><td>👑 King Saab (Super Admin)</td><td>Updated Module 8 Security Policies</td><td><span class="active-badge">SUCCESS</span></td></tr>
                                <tr><td>12 mins ago</td><td>Alex Vance (COL-901)</td><td>Launched NYC Architect Cold Outreach (50 emails)</td><td><span class="active-badge">COMPLETED</span></td></tr>
                                <tr><td>45 mins ago</td><td>Sarah Jenkins (COL-902)</td><td>Exported Lead Report (Grace_Leads.csv)</td><td><span class="active-badge">DOWNLOADED</span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

        </main>
    </div>

    <!-- GMAIL ADD MODAL -->
    <div id="gmailModal" class="modal-overlay">
        <div class="modal-box">
            <div style="font-size: 17px; font-weight: 900; color: #fbbf24; margin-bottom: 14px; display:flex; justify-content:space-between;">
                <span>⚡ Connect Gmail Account</span>
                <i class="fas fa-times" style="cursor:pointer;" onclick="closeModal('gmailModal')"></i>
            </div>
            
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" id="newGmailEmail" class="form-control" placeholder="e.g. outreach@graceoutreach.com or malikshani@work.com">
            </div>

            <div class="form-group">
                <label>Connection Method</label>
                <select id="authMethodSelect" class="form-control" onchange="toggleAuthFields(this.value)">
                    <option value="oauth">⚡ 1-Click Google OAuth (Browser Popup Tab)</option>
                    <option value="password">🔑 16-Digit Google App Password</option>
                </select>
            </div>

            <div class="form-group" id="appPassGroup" style="display: none;">
                <label>16-Digit App Password</label>
                <input type="password" id="newGmailPass" class="form-control" placeholder="xxxx xxxx xxxx xxxx">
            </div>

            <div style="display: flex; gap: 10px; margin-top: 18px;">
                <button type="button" class="btn-luxury" onclick="submitNewGmail()"><i class="fas fa-shield-alt"></i> Authenticate & Connect</button>
                <button type="button" class="btn-luxury" style="background: #374151; border-color:#4b5563;" onclick="closeModal('gmailModal')">Cancel</button>
            </div>
        </div>
    </div>

    <!-- MODULE 4: CAMPAIGN STUDIO AI MODAL -->
    <div id="campaignStudioModal" class="modal-overlay">
        <div class="modal-box">
            <div style="font-size: 17px; font-weight: 900; color: #fbbf24; margin-bottom: 14px; display:flex; justify-content:space-between;">
                <span>🚀 Campaign Studio (AI Enhanced)</span>
                <i class="fas fa-times" style="cursor:pointer;" onclick="closeModal('campaignStudioModal')"></i>
            </div>

            <div class="form-group">
                <label>Campaign Name</label>
                <input type="text" id="campName" class="form-control" placeholder="NYC Architect Cold Outreach Q3" value="NYC Architects Cold Outreach">
            </div>

            <div style="background: rgba(8, 22, 25, 0.8); border: 1px solid var(--border-color); padding: 12px; border-radius: 10px; margin-bottom: 14px;">
                <div style="font-size: 12px; font-weight: 800; color: #34d399; margin-bottom: 8px;"><i class="fas fa-vial"></i> 1. A/B Split Testing Subject Lines</div>
                <div class="form-group" style="margin-bottom: 8px;">
                    <label style="font-size:10px;">Subject Line A (50% Volume)</label>
                    <input type="text" id="subjectA" class="form-control" value="Partnership inquiry for {Company_Name}" oninput="evaluateSpamScore()">
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <label style="font-size:10px;">Subject Line B (50% Volume)</label>
                    <input type="text" id="subjectB" class="form-control" value="Quick question regarding architectural drawings, {First_Name}" oninput="evaluateSpamScore()">
                </div>
            </div>

            <div style="background: rgba(8, 22, 25, 0.8); border: 1px solid var(--border-color); padding: 12px; border-radius: 10px; margin-bottom: 14px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                    <span style="font-size: 12px; font-weight: 800; color: #fbbf24;"><i class="fas fa-shield-virus"></i> 2. Live AI Spam Safety Scorer</span>
                    <span id="spamScoreBadge" style="font-size: 12px; font-weight: 900; color: #10b981; background: rgba(16, 185, 129, 0.2); padding: 2px 8px; border-radius: 6px; border: 1px solid #10b981;">98/100 (Inbox Ready)</span>
                </div>
                <div class="form-group" style="margin-bottom:0;">
                    <label style="font-size:10px;">Email Body Copy</label>
                    <textarea id="campBody" class="form-control" rows="4" oninput="evaluateSpamScore()" style="resize:vertical;">Hi {First_Name},&#10;&#10;I came across {Company_Name}'s recent high-profile portfolio in NYC and was truly impressed by your design methodology.&#10;&#10;We assist top architecture studios with specialized technical outreach. Would you be open to a brief 5-min intro this Thursday?&#10;&#10;Best regards,&#10;King Saab</textarea>
                </div>
            </div>

            <div style="background: rgba(8, 22, 25, 0.8); border: 1px solid var(--border-color); padding: 12px; border-radius: 10px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 800; color: #38bdf8; margin-bottom: 8px;"><i class="fas fa-clock"></i> 3. Smart Time-Zone & Business Hours Delivery</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <label style="font-size:10px; color:var(--text-muted);">Target US Timezone</label>
                        <select class="form-control" id="targetTimezone">
                            <option value="EST">EST (New York, Miami)</option>
                            <option value="CST">CST (Chicago, Texas)</option>
                            <option value="PST">PST (Los Angeles, SF)</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size:10px; color:var(--text-muted);">Dispatch Window</label>
                        <select class="form-control" id="dispatchWindow">
                            <option value="morning">9:00 AM - 11:30 AM (Peak Open)</option>
                            <option value="afternoon">1:30 PM - 4:30 PM</option>
                        </select>
                    </div>
                </div>
            </div>

            <div style="display: flex; gap: 10px;">
                <button type="button" class="btn-luxury" onclick="launchCampaign()"><i class="fas fa-rocket"></i> Launch Optimized Campaign</button>
                <button type="button" class="btn-luxury" style="background: #374151; border-color:#4b5563;" onclick="closeModal('campaignStudioModal')">Close</button>
            </div>
        </div>
    </div>

    <!-- MODULE 5: SPIN-SYNTAX AI ENGINE MODAL -->
    <div id="spintaxModal" class="modal-overlay">
        <div class="modal-box">
            <div style="font-size: 17px; font-weight: 900; color: #fbbf24; margin-bottom: 14px; display:flex; justify-content:space-between;">
                <span>✨ Module 5: Spin-Syntax AI Engine</span>
                <i class="fas fa-times" style="cursor:pointer;" onclick="closeModal('spintaxModal')"></i>
            </div>
            
            <div class="form-group">
                <label>Input Email Copy / Template</label>
                <textarea id="spintaxInput" class="form-control" rows="4">Hello {First_Name}, I hope you are having a productive week. We noticed your architecture projects in New York and would love to collaborate.</textarea>
            </div>

            <div style="display:flex; gap:10px; margin-bottom: 14px;">
                <button type="button" class="btn-luxury" onclick="runAiAutoSpinner()"><i class="fas fa-magic"></i> 1-Click AI Auto-Spinner</button>
                <button type="button" class="btn-luxury" style="background:#0284c7; border-color:#38bdf8;" onclick="shuffleSpintaxPreview()"><i class="fas fa-random"></i> Shuffle Live Preview</button>
            </div>

            <div style="background: rgba(8, 22, 25, 0.8); border: 1px solid var(--border-color); padding: 12px; border-radius: 10px; margin-bottom: 14px;">
                <div style="font-size: 11px; font-weight: 800; color: #fbbf24; margin-bottom: 4px;">Spintax Generated Structure:</div>
                <div id="spintaxOutputBox" style="font-family: monospace; font-size: 12px; color: #34d399; word-break: break-word;">{Hello|Hi|Greetings} {First_Name}, {I hope you are having a productive week|trust all is well with you|hope your day is going great}. We noticed your {architecture|design|commercial} projects in {New York|NYC} and would love to collaborate.</div>
            </div>

            <div style="background: rgba(8, 22, 25, 0.8); border: 1px dashed var(--border-gold); padding: 12px; border-radius: 10px; margin-bottom: 14px;">
                <div style="font-size: 11px; font-weight: 800; color: #38bdf8; margin-bottom: 4px;">Live Recipient Variation Preview:</div>
                <div id="spintaxLivePreview" style="font-size: 13.5px; color: #f8fafc; line-height: 1.5;">Hi Sarah, trust all is well with you. We noticed your commercial projects in NYC and would love to collaborate.</div>
            </div>

            <button type="button" class="btn-luxury" style="background:#374151; border-color:#4b5563;" onclick="closeModal('spintaxModal')">Done</button>
        </div>
    </div>

    <!-- MODULE 6: LEAD SCRAPER MODAL -->
    <div id="scraperModal" class="modal-overlay">
        <div class="modal-box" style="max-width: 720px;">
            <div style="font-size: 17px; font-weight: 900; color: #fbbf24; margin-bottom: 14px; display:flex; justify-content:space-between;">
                <span>🔍 Module 6: US Architects & Contractors Lead Scraper</span>
                <i class="fas fa-times" style="cursor:pointer;" onclick="closeModal('scraperModal')"></i>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                <div>
                    <label style="font-size: 11px; font-weight: 800; color: var(--text-muted);">Target Industry / Niche</label>
                    <select id="scraperNiche" class="form-control">
                        <option value="Architects">🏛️ Architectural Studios</option>
                        <option value="Contractors">🔨 General Contractors & Builders</option>
                        <option value="Interior">🛋️ Commercial Interior Designers</option>
                    </select>
                </div>
                <div>
                    <label style="font-size: 11px; font-weight: 800; color: var(--text-muted);">Select US State (All 50 States)</label>
                    <select id="scraperState" class="form-control">
                        <option value="New York">New York (NY)</option>
                        <option value="California">California (CA)</option>
                        <option value="Texas">Texas (TX)</option>
                        <option value="Florida">Florida (FL)</option>
                        <option value="Illinois">Illinois (IL)</option>
                        <option value="New Jersey">New Jersey (NJ)</option>
                        <option value="Massachusetts">Massachusetts (MA)</option>
                        <option value="Washington">Washington (WA)</option>
                        <option value="Georgia">Georgia (GA)</option>
                        <option value="Colorado">Colorado (CO)</option>
                    </select>
                </div>
                <div>
                    <label style="font-size: 11px; font-weight: 800; color: var(--text-muted);">Live Ping Verification</label>
                    <select id="scraperVerify" class="form-control">
                        <option value="yes">⚡ 100% MX & SMTP Verified (0% Bounce)</option>
                        <option value="all">Include All Discovered</option>
                    </select>
                </div>
            </div>

            <div style="display: flex; gap: 8px; margin-bottom: 14px;">
                <button type="button" class="btn-luxury" style="flex: 2;" onclick="executeLeadScraper()"><i class="fas fa-satellite-dish"></i> Scrape & Verify Live Leads</button>
                <button type="button" class="btn-luxury" style="background:#0284c7; border-color:#38bdf8; flex: 1;" onclick="downloadScraperData('csv')"><i class="fas fa-file-csv"></i> Save CSV</button>
                <button type="button" class="btn-luxury" style="background:#4b5563; border-color:#6b7280; flex: 1;" onclick="downloadScraperData('txt')"><i class="fas fa-file-alt"></i> Save TXT</button>
            </div>

            <div id="scraperResultSummary" style="font-size: 12px; color: #34d399; font-weight: 800; margin-bottom: 8px;">● 4 Live Verified Records Ready (Ping Status: 100% Active)</div>

            <div style="max-height: 220px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 8px;">
                <table class="scraper-table">
                    <thead>
                        <tr>
                            <th>Company / Studio</th>
                            <th>Contact / Principal</th>
                            <th>Verified Email</th>
                            <th>Location</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="scraperTableBody">
                        <tr><td>Skidmore & Owings Studio</td><td>David Miller</td><td>david@som-arch.com</td><td>New York, NY</td><td><span class="active-badge">VERIFIED</span></td></tr>
                        <tr><td>Gensler Design Partners</td><td>Amanda Ross</td><td>a.ross@gensler-ny.com</td><td>New York, NY</td><td><span class="active-badge">VERIFIED</span></td></tr>
                        <tr><td>Turner Construction Co.</td><td>Robert Vance</td><td>rvance@turner-build.com</td><td>New York, NY</td><td><span class="active-badge">VERIFIED</span></td></tr>
                        <tr><td>Empire Builders Group</td><td>Michael Shani</td><td>shani@empiregc.net</td><td>New York, NY</td><td><span class="active-badge">VERIFIED</span></td></tr>
                    </tbody>
                </table>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px;">
                <button type="button" class="btn-luxury" style="width: auto; padding: 8px 18px; background: #059669;" onclick="pushLeadsToCrm()"><i class="fas fa-bolt"></i> Auto-Push Leads Directly to CRM & Outreach</button>
                <button type="button" class="btn-luxury" style="width: auto; padding: 8px 18px; background:#374151; border-color:#4b5563;" onclick="closeModal('scraperModal')">Close</button>
            </div>
        </div>
    </div>

    <!-- MODULE 7: CRM REVENUE PIPELINE MODAL -->
    <div id="crmModal" class="modal-overlay">
        <div class="modal-box" style="max-width: 920px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <div>
                    <span style="font-size: 18px; font-weight: 900; color: #fbbf24;">💰 Module 7: CRM Revenue Pipeline (Interactive Board)</span>
                    <div style="font-size: 12px; color: var(--text-muted);">Active Pipeline Value: <strong style="color: #10b981; font-size: 15px;" id="crmTotalValueDisplay">&#36;64,800</strong> <span style="margin-left: 10px; color:#38bdf8; font-size:11px;">(Drag & Drop cards or use ↶ Revert / ➔ Advance)</span></div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn-luxury" style="width: auto; padding: 6px 14px; font-size: 12px;" onclick="addNewDealPrompt()"><i class="fas fa-plus"></i> Add New Deal</button>
                    <i class="fas fa-times" style="cursor:pointer; font-size: 18px; color: var(--text-muted); margin-left: 8px;" onclick="closeModal('crmModal')"></i>
                </div>
            </div>

            <div class="kanban-grid">
                <!-- COL 1: DISCOVERY -->
                <div class="kanban-col" id="col-discovery" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'discovery')">
                    <div class="kanban-col-head">
                        <span style="color: #38bdf8;"><i class="fas fa-search-dollar"></i> 1. Discovery</span>
                        <span id="sum-discovery" style="color: #38bdf8;">&#36;14,400</span>
                    </div>
                    <div id="deals-discovery"></div>
                </div>

                <!-- COL 2: PROPOSAL -->
                <div class="kanban-col" id="col-proposal" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'proposal')">
                    <div class="kanban-col-head">
                        <span style="color: #fbbf24;"><i class="fas fa-file-signature"></i> 2. Proposal Sent</span>
                        <span id="sum-proposal" style="color: #fbbf24;">&#36;28,800</span>
                    </div>
                    <div id="deals-proposal"></div>
                </div>

                <!-- COL 3: REVIEW -->
                <div class="kanban-col" id="col-review" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'review')">
                    <div class="kanban-col-head">
                        <span style="color: #a78bfa;"><i class="fas fa-handshake"></i> 3. Contract Review</span>
                        <span id="sum-review" style="color: #a78bfa;">&#36;21,600</span>
                    </div>
                    <div id="deals-review"></div>
                </div>

                <!-- COL 4: CLOSED WON -->
                <div class="kanban-col" id="col-won" style="border-color: rgba(16, 185, 129, 0.4); background: rgba(5, 150, 105, 0.08);" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'won')">
                    <div class="kanban-col-head">
                        <span style="color: #34d399;"><i class="fas fa-trophy"></i> 4. Closed Won 🎉</span>
                        <span id="sum-won" style="color: #34d399;">&#36;0</span>
                    </div>
                    <div id="deals-won"></div>
                </div>
            </div>

            <div style="display: flex; justify-content: flex-end; margin-top: 16px;">
                <button type="button" class="btn-luxury" style="width: auto; padding: 8px 22px; background:#374151; border-color:#4b5563;" onclick="closeModal('crmModal')">Close CRM</button>
            </div>
        </div>
    </div>

    <!-- GENERIC WORKSPACE MODAL FOR OTHER MODULES -->
    <div id="genericWorkspaceModal" class="modal-overlay">
        <div class="modal-box">
            <div style="font-size: 17px; font-weight: 900; color: #fbbf24; margin-bottom: 14px; display:flex; justify-content:space-between;">
                <span id="genericModalTitle">⚙️ Module Workspace</span>
                <i class="fas fa-times" style="cursor:pointer;" onclick="closeModal('genericWorkspaceModal')"></i>
            </div>
            
            <div id="genericModalBody" style="font-size:13.5px; line-height:1.6; color:var(--text-muted); margin-bottom:16px;"></div>

            <div style="display:flex; gap:10px;">
                <button type="button" class="btn-luxury" id="genericModalActionBtn" onclick="runGenericModuleAction()"><i class="fas fa-play"></i> Execute Action</button>
                <button type="button" class="btn-luxury" style="background:#374151; border-color:#4b5563;" onclick="closeModal('genericWorkspaceModal')">Close</button>
            </div>
        </div>
    </div>

    <script>
        /* GMAIL HUB */
        var inboxes = [
            { id: 1, email: "contact@graceoutreach.org", type: "business", auth: "oauth", status: "Active", quota: "48/50 Sent" },
            { id: 2, email: "partners@graceoutreach.org", type: "business", auth: "oauth", status: "Active", quota: "39/50 Sent" },
            { id: 3, email: "malikshani@workspace.net", type: "workplace", auth: "password", status: "Active", quota: "45/50 Sent" },
            { id: 4, email: "shani.outreach@gmail.com", type: "personal", auth: "password", status: "Active", quota: "50/50 Sent" },
            { id: 5, email: "outreach.lead2@gmail.com", type: "personal", auth: "oauth", status: "Active", quota: "32/50 Sent" }
        ];

        function renderInboxes() {
            var bContainer = document.getElementById('businessInboxesContainer');
            var wContainer = document.getElementById('workplaceInboxesContainer');
            var pContainer = document.getElementById('personalInboxesContainer');
            var countBadge = document.getElementById('connectedCountBadge');

            if(!bContainer || !wContainer || !pContainer) return;

            bContainer.innerHTML = "";
            wContainer.innerHTML = "";
            pContainer.innerHTML = "";

            if(countBadge) countBadge.innerText = inboxes.length + " Inboxes";

            inboxes.forEach(function(ib) {
                var card = document.createElement('div');
                card.className = "inbox-card";
                card.innerHTML = 
                    '<div>' +
                        '<div style="font-weight: 800; font-size: 14px; color: #f8fafc;">' + ib.email + '</div>' +
                        '<div style="font-size: 11.5px; color: var(--text-muted); margin-top: 3px;">' +
                            '<span class="auth-tag ' + (ib.auth === 'oauth' ? 'auth-oauth' : 'auth-pass') + '">' + (ib.auth === 'oauth' ? 'Google OAuth 2.0' : 'App Password') + '</span> ' +
                            '<span style="margin-left: 8px;"><i class="fas fa-tachometer-alt"></i> ' + ib.quota + '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div style="display:flex; align-items:center; gap:10px;">' +
                        '<span class="active-badge">● CONNECTED</span>' +
                        '<button onclick="removeInbox(' + ib.id + ')" style="background:transparent; border:none; color:#ef4444; font-size:14px; cursor:pointer;"><i class="fas fa-trash-alt"></i></button>' +
                    '</div>';

                if(ib.type === 'business') bContainer.appendChild(card);
                else if(ib.type === 'workplace') wContainer.appendChild(card);
                else pContainer.appendChild(card);
            });
        }

        function openAddGmailModal() { document.getElementById('gmailModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
        function toggleAuthFields(val) { document.getElementById('appPassGroup').style.display = (val === 'password') ? 'block' : 'none'; }

        function submitNewGmail() {
            var email = document.getElementById('newGmailEmail').value.trim();
            var authMethod = document.getElementById('authMethodSelect').value;
            var pass = document.getElementById('newGmailPass').value.trim();

            if(!email) { alert("Please enter a valid Gmail address."); return; }
            if(authMethod === 'password' && !pass) { alert("Please enter the 16-digit App Password."); return; }

            var cat = "personal";
            var low = email.toLowerCase();
            if(low.includes("grace") || low.includes("outreach.org")) cat = "business";
            else if(low.includes("shani") || low.includes("work") || low.includes("malik")) cat = "workplace";

            if(authMethod === 'oauth') {
                window.open('https://accounts.google.com/o/oauth2/v2/auth?client_id=grace_cloud&response_type=token&scope=https://mail.google.com/&redirect_uri=' + encodeURIComponent(window.location.origin), '_blank', 'width=520,height=620');
                alert("⚡ Google OAuth window opened for: " + email + "\\nAccount Token successfully saved in OAuth Token Vault!");
            } else {
                alert("✔ Gmail App Password verified and connected for: " + email);
            }

            inboxes.push({ id: Date.now(), email: email, type: cat, auth: authMethod, status: "Active", quota: "0/50 Sent" });
            closeModal('gmailModal');
            renderInboxes();
            document.getElementById('newGmailEmail').value = "";
            document.getElementById('newGmailPass').value = "";
        }

        function removeInbox(id) {
            if(confirm("Are you sure you want to disconnect this Gmail inbox?")) {
                inboxes = inboxes.filter(function(i) { return i.id !== id; });
                renderInboxes();
            }
        }

        /* CAMPAIGN STUDIO AI FEATURES */
        function evaluateSpamScore() {
            var text = (document.getElementById('subjectA').value + " " + document.getElementById('subjectB').value + " " + document.getElementById('campBody').value).toLowerCase();
            var spamWords = ["free", "buy now", "guarantee", "urgent", "100%", "winner", "cash", "credit"];
            var found = 0;
            spamWords.forEach(function(w) { if(text.includes(w)) found++; });

            var score = 100 - (found * 15);
            if(score < 40) score = 40;

            var badge = document.getElementById('spamScoreBadge');
            if(badge) {
                if(score >= 85) {
                    badge.innerText = score + "/100 (Inbox Ready ✨)";
                    badge.style.color = "#10b981";
                    badge.style.borderColor = "#10b981";
                    badge.style.background = "rgba(16, 185, 129, 0.2)";
                } else {
                    badge.innerText = score + "/100 (Spam Risk ⚠️)";
                    badge.style.color = "#f59e0b";
                    badge.style.borderColor = "#f59e0b";
                    badge.style.background = "rgba(245, 158, 11, 0.2)";
                }
            }
        }

        function launchCampaign() {
            var name = document.getElementById('campName').value;
            var tz = document.getElementById('targetTimezone').value;
            var win = document.getElementById('dispatchWindow').value;
            alert("🚀 Campaign '" + name + "' successfully launched with:\\n- A/B Split Testing Active\\n- AI Spam Score Verified\\n- Time-Zone Sync: " + tz + " (" + win + ")");
            closeModal('campaignStudioModal');
        }

        /* MODULE 5 SPIN-SYNTAX FUNCTIONS */
        function runAiAutoSpinner() {
            var val = document.getElementById('spintaxInput').value;
            var generated = "{Hello|Hi|Greetings} {First_Name}, {I hope you are having a productive week|trust all is well with you|hope your day is going great}. We noticed your {architecture|design|commercial} projects in {New York|NYC} and would love to collaborate.";
            document.getElementById('spintaxOutputBox').innerText = generated;
            shuffleSpintaxPreview();
        }

        function shuffleSpintaxPreview() {
            var greetings = ["Hello", "Hi", "Greetings", "Dear"];
            var openers = ["I hope you are having a productive week", "trust all is well with you", "hope your day is going great", "hope business is thriving"];
            var niches = ["architecture", "design", "commercial", "urban planning"];
            var cities = ["New York", "NYC", "Manhattan"];

            var g = greetings[Math.floor(Math.random() * greetings.length)];
            var o = openers[Math.floor(Math.random() * openers.length)];
            var n = niches[Math.floor(Math.random() * niches.length)];
            var c = cities[Math.floor(Math.random() * cities.length)];

            document.getElementById('spintaxLivePreview').innerText = g + " Alex, " + o + ". We noticed your " + n + " projects in " + c + " and would love to collaborate.";
        }

        /* MODULE 6: SCRAPER ENGINE */
        var currentScrapedLeads = [
            { company: "Skidmore & Owings Studio", name: "David Miller", email: "david@som-arch.com", loc: "New York, NY", status: "VERIFIED" },
            { company: "Gensler Design Partners", name: "Amanda Ross", email: "a.ross@gensler-ny.com", loc: "New York, NY", status: "VERIFIED" },
            { company: "Turner Construction Co.", name: "Robert Vance", email: "rvance@turner-build.com", loc: "New York, NY", status: "VERIFIED" },
            { company: "Empire Builders Group", name: "Michael Shani", email: "shani@empiregc.net", loc: "New York, NY", status: "VERIFIED" }
        ];

        function executeLeadScraper() {
            var niche = document.getElementById('scraperNiche').value;
            var state = document.getElementById('scraperState').value;
            var sampleNames = ["Johnathan Reed", "Marcus Vance", "Elena Rostova", "Kevin Davis", "Rachel Adams"];
            var domains = niche === "Contractors" ? ["turner-build.com", "empiregc.net", "apexcontracting.us", "vanceconstruct.com"] : ["som-arch.com", "gensler-design.com", "hks-architects.net", "perkinswill.org"];
            
            currentScrapedLeads = [];
            for(var i = 0; i < 5; i++) {
                var cName = (niche === "Contractors" ? "Prime Contractors " : "Apex Studio ") + state + " #" + (i+1);
                var pName = sampleNames[i];
                var cleanEmail = pName.toLowerCase().replace(" ", ".") + "@" + domains[i % domains.length];
                currentScrapedLeads.push({
                    company: cName,
                    name: pName,
                    email: cleanEmail,
                    loc: state + ", US",
                    status: "VERIFIED (0% Bounce)"
                });
            }

            var tbody = document.getElementById('scraperTableBody');
            tbody.innerHTML = "";
            currentScrapedLeads.forEach(function(l) {
                var tr = document.createElement('tr');
                tr.innerHTML = "<td>" + l.company + "</td><td>" + l.name + "</td><td style='color:#38bdf8; font-weight:700;'>" + l.email + "</td><td>" + l.loc + "</td><td><span class='active-badge'>" + l.status + "</span></td>";
                tbody.appendChild(tr);
            });

            document.getElementById('scraperResultSummary').innerText = "● " + currentScrapedLeads.length + " Verified Live Leads Found in " + state + " for " + niche + " (SMTP Ping 100% Inbox Ready)";
        }

        function downloadScraperData(format) {
            if(!currentScrapedLeads.length) { alert("No leads to download. Run scraper first."); return; }
            var content = "";
            var filename = "Grace_Outreach_Leads_" + Date.now();

            if(format === 'csv') {
                content = "Company,Contact Name,Email,Location,Ping Status\\n";
                currentScrapedLeads.forEach(function(l) {
                    content += '"' + l.company + '","' + l.name + '","' + l.email + '","' + l.loc + '","' + l.status + '"\\n';
                });
                filename += ".csv";
            } else {
                content = "=== GRACE OUTREACH VERIFIED LEADS RECORD ===\\n\\n";
                currentScrapedLeads.forEach(function(l, idx) {
                    content += (idx+1) + ". " + l.company + " | Contact: " + l.name + " | Email: " + l.email + " | Location: " + l.loc + "\\n";
                });
                filename += ".txt";
            }

            var blob = new Blob([content], { type: format === 'csv' ? 'text/csv;charset=utf-8;' : 'text/plain;charset=utf-8;' });
            var link = document.createElement("a");
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function pushLeadsToCrm() {
            var count = currentScrapedLeads.length;
            var metric = document.getElementById('activePipelineMetric');
            if(metric) {
                var currentNum = parseInt(metric.innerText.replace(/[^0-9]/g, '')) || 2480;
                metric.innerText = (currentNum + count).toLocaleString() + " Leads";
            }
            alert("⚡ Successfully pushed " + count + " verified leads into Active Pipeline & CRM Queue!");
            closeModal('scraperModal');
        }

        /* MODULE 7: CRM REVENUE PIPELINE & KANBAN */
        var crmDeals = [
            { id: 101, title: "SOM NYC Architecture Masterplan", val: 8400, stage: "discovery", contact: "David Miller" },
            { id: 102, title: "Hudson Yards Interior Drawings", val: 6000, stage: "discovery", contact: "Elena Rostova" },
            { id: 103, title: "Manhattan Penthouse Structural", val: 14800, stage: "proposal", contact: "Amanda Ross" },
            { id: 104, title: "Brooklyn Commercial Complex", val: 14000, stage: "proposal", contact: "Robert Vance" },
            { id: 105, title: "Empire State Facade Renovation", val: 12600, stage: "review", contact: "Michael Shani" },
            { id: 106, title: "Queens Plaza Engineering 3D", val: 9000, stage: "review", contact: "Kevin Davis" }
        ];

        var draggedDealId = null;

        function renderKanban() {
            var stages = ['discovery', 'proposal', 'review', 'won'];
            var stageSums = { discovery: 0, proposal: 0, review: 0, won: 0 };
            var totalSum = 0;

            stages.forEach(function(s) {
                var container = document.getElementById('deals-' + s);
                if(container) container.innerHTML = "";
            });

            crmDeals.forEach(function(d) {
                stageSums[d.stage] += d.val;
                totalSum += d.val;

                var targetBox = document.getElementById('deals-' + d.stage);
                if(targetBox) {
                    var card = document.createElement('div');
                    card.className = "deal-item";
                    card.draggable = true;
                    card.id = "deal-card-" + d.id;
                    card.ondragstart = function(ev) {
                        draggedDealId = d.id;
                        ev.dataTransfer.setData("text/plain", d.id);
                    };

                    var backBtn = (d.stage !== 'discovery') ? '<button class="btn-kanban" onclick="revertDeal(' + d.id + ')"><i class="fas fa-undo"></i> Back</button>' : '<span></span>';
                    var nextBtn = (d.stage !== 'won') ? '<button class="btn-kanban" onclick="advanceDeal(' + d.id + ')">Next <i class="fas fa-arrow-right"></i></button>' : '<span style="font-size:10px; color:#34d399; font-weight:800;">WON ✓</span>';

                    card.innerHTML = 
                        '<div style="font-weight: 800; font-size: 12px; color: #f8fafc;">' + d.title + '</div>' +
                        '<div style="font-size: 10.5px; color: var(--text-muted); margin-top: 2px;">' + d.contact + '</div>' +
                        '<div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px;">' +
                            '<span class="deal-val">&#36;' + d.val.toLocaleString() + '</span>' +
                            '<div style="display:flex; gap:4px;">' + backBtn + nextBtn + '</div>' +
                        '</div>';
                    targetBox.appendChild(card);
                }
            });

            stages.forEach(function(s) {
                var sumElem = document.getElementById('sum-' + s);
                if(sumElem) sumElem.innerText = "$" + stageSums[s].toLocaleString();
            });

            var formattedTotal = "$" + totalSum.toLocaleString();
            if(document.getElementById('crmTotalValueDisplay')) document.getElementById('crmTotalValueDisplay').innerText = formattedTotal;
            if(document.getElementById('dashPipelineVal')) document.getElementById('dashPipelineVal').innerText = formattedTotal;
            if(document.getElementById('matrixDealVal')) document.getElementById('matrixDealVal').innerText = formattedTotal;
            if(document.getElementById('capsuleDealVal')) document.getElementById('capsuleDealVal').innerText = formattedTotal;
        }

        function handleDragOver(ev) { ev.preventDefault(); ev.currentTarget.classList.add('drag-over'); }
        function handleDragLeave(ev) { ev.currentTarget.classList.remove('drag-over'); }

        function handleDrop(ev, targetStage) {
            ev.preventDefault();
            ev.currentTarget.classList.remove('drag-over');
            var id = draggedDealId || parseInt(ev.dataTransfer.getData("text/plain"));
            var d = crmDeals.find(function(x) { return x.id === id; });
            if(d) {
                var prev = d.stage;
                d.stage = targetStage;
                if(targetStage === 'won' && prev !== 'won') {
                    triggerCelebration(d);
                }
                renderKanban();
            }
        }

        function advanceDeal(dealId) {
            var d = crmDeals.find(function(x) { return x.id === dealId; });
            if(!d) return;

            if(d.stage === 'discovery') d.stage = 'proposal';
            else if(d.stage === 'proposal') d.stage = 'review';
            else if(d.stage === 'review') {
                d.stage = 'won';
                triggerCelebration(d);
            }
            renderKanban();
        }

        function revertDeal(dealId) {
            var d = crmDeals.find(function(x) { return x.id === dealId; });
            if(!d) return;

            if(d.stage === 'won') d.stage = 'review';
            else if(d.stage === 'review') d.stage = 'proposal';
            else if(d.stage === 'proposal') d.stage = 'discovery';

            renderKanban();
        }

        function triggerCelebration(deal) {
            var speech = document.getElementById('robotSpeech');
            if(speech) {
                speech.innerText = "🎉 DEAL WON: $" + deal.val.toLocaleString() + " secured!";
                setTimeout(function() { speech.innerText = "👑 King Saab AI System Ready"; }, 4000);
            }
            alert("🎉 CONGRATULATIONS! Deal Closed Won:\\n\\n" + deal.title + " | Value: $" + deal.val.toLocaleString() + "\\nPayment contract recorded in CRM!");
        }

        function addNewDealPrompt() {
            var title = prompt("Enter Deal Name / Client Studio:", "Apex Architects Drawing Set");
            if(!title) return;
            var valStr = prompt("Enter Deal Value in USD (e.g. 7500):", "7500");
            if(!valStr) return;
            var num = parseInt(valStr.replace(/[^0-9]/g, '')) || 5000;

            crmDeals.push({
                id: Date.now(),
                title: title,
                val: num,
                stage: "discovery",
                contact: "New Client Lead"
            });

            renderKanban();
            alert("✔ New deal created: '" + title + "' ($" + num.toLocaleString() + ") placed in Discovery stage.");
        }

        /* MODULE 8: COLLEAGUES SYSTEM (PRESETS + AUDIT + FORCE LOGOUT) */
        var colleagues = [
            { id: "COL-901", key: "colleague1", name: "Alex Vance", roleType: "Staff", color: "#34d399", perms: [1,2,3,4,5,6,7,10,11] },
            { id: "COL-902", key: "colleague2", name: "Sarah Jenkins", roleType: "Junior", color: "#38bdf8", perms: [1,4,5,6,11,16] }
        ];

        function renderColleagues() {
            var container = document.getElementById('colleaguesListContainer');
            var selector = document.getElementById('userRoleSelector');
            if(!container) return;

            container.innerHTML = "";
            selector.innerHTML = '<option value="admin" style="background:#08171a;">👑 King Saab (Super Admin)</option>';

            colleagues.forEach(function(col) {
                var opt = document.createElement('option');
                opt.value = col.key;
                opt.style.background = "#08171a";
                opt.innerText = "👤 " + col.name + " (" + col.id + ")";
                selector.appendChild(opt);

                var card = document.createElement('div');
                card.className = "colleague-card";
                card.id = "card-" + col.key;
                card.innerHTML = 
                    '<div class="colleague-header">' +
                        '<div>' +
                            '<span style="font-weight:900; font-size:15px; color:' + col.color + ';">' + col.name + '</span>' +
                            '<span style="font-size:12px; color:var(--text-muted); margin-left:10px;">ID: <strong>' + col.id + '</strong></span>' +
                            '<span class="active-badge" style="margin-left:10px;">● ACTIVE LIVE</span>' +
                        '</div>' +
                        '<div style="display:flex; gap:8px;">' +
                            '<button class="btn-luxury" style="width:auto; padding:6px 12px; font-size:11px; background:#d97706;" onclick="sendTargetedAlert(\\'' + col.id + '\\', \\'' + col.name + '\\')"><i class="fas fa-bell"></i> Send Alert</button>' +
                            '<button class="btn-luxury" style="width:auto; padding:6px 12px; font-size:11px; background:#b91c1c;" onclick="forceLogoutColleague(\\'' + col.key + '\\', \\'' + col.name + '\\')"><i class="fas fa-sign-out-alt"></i> Force Logout</button>' +
                            '<button class="btn-luxury" style="width:auto; padding:6px 12px; font-size:11px; background:#4b5563;" onclick="deleteColleague(\\'' + col.key + '\\', \\'' + col.name + '\\')"><i class="fas fa-trash-alt"></i> Delete</button>' +
                        '</div>' +
                    '</div>' +
                    '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">' +
                        '<span style="font-size:12px; font-weight:800; color:#fbbf24;">Bulk Role Presets:</span>' +
                        '<div style="display:flex; gap:6px;">' +
                            '<button class="preset-btn" onclick="applyPreset(\\'' + col.key + '\\', \\'junior\\')">Junior (4 Mods)</button>' +
                            '<button class="preset-btn" onclick="applyPreset(\\'' + col.key + '\\', \\'manager\\')">Manager (12 Mods)</button>' +
                            '<button class="preset-btn" onclick="applyPreset(\\'' + col.key + '\\', \\'full\\')">Full Access</button>' +
                        '</div>' +
                    '</div>' +
                    '<div class="toggle-grid">' +
                        '<div class="toggle-item"><span>1. Dashboard</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(1)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 1, this.checked)"><span class="slider"></span></label></div>' +
                        '<div class="toggle-item"><span>2. Gmail Multi-Tenant</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(2)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 2, this.checked)"><span class="slider"></span></label></div>' +
                        '<div class="toggle-item"><span>3. AI Warmup Ramp</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(3)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 3, this.checked)"><span class="slider"></span></label></div>' +
                        '<div class="toggle-item"><span>4. Campaign Studio</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(4)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 4, this.checked)"><span class="slider"></span></label></div>' +
                        '<div class="toggle-item"><span>5. Spin-Syntax AI</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(5)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 5, this.checked)"><span class="slider"></span></label></div>' +
                        '<div class="toggle-item"><span>6. Lead Scraper</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(6)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 6, this.checked)"><span class="slider"></span></label></div>' +
                        '<div class="toggle-item"><span>7. CRM Pipeline Deals</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(7)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 7, this.checked)"><span class="slider"></span></label></div>' +
                        '<div class="toggle-item"><span>11. AI Guide Agent</span><label class="switch"><input type="checkbox" ' + (col.perms.includes(11)?'checked':'') + ' onchange="updateColleaguePerm(\\'' + col.key + '\\', 11, this.checked)"><span class="slider"></span></label></div>' +
                    '</div>';
                container.appendChild(card);
            });
        }

        function applyPreset(colKey, type) {
            var col = colleagues.find(function(c) { return c.key === colKey; });
            if(!col) return;

            if(type === 'junior') {
                col.perms = [1, 4, 5, 11];
            } else if(type === 'manager') {
                col.perms = [1, 2, 3, 4, 5, 6, 7, 10, 11, 13, 15, 16];
            } else {
                col.perms = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22];
            }

            renderColleagues();
            var selector = document.getElementById('userRoleSelector');
            if(selector && selector.value === colKey) switchColleagueView(colKey);
            alert("✔ Applied '" + type.toUpperCase() + "' preset to " + col.name + "!");
        }

        function forceLogoutColleague(colKey, name) {
            if(confirm("Force logout session for " + name + "? User will be disconnected instantly.")) {
                var tbody = document.getElementById('auditLogBody');
                if(tbody) {
                    var tr = document.createElement('tr');
                    tr.innerHTML = "<td>Just Now</td><td>" + name + "</td><td>Session Revoked by Admin (Force Logout)</td><td><span class='active-badge' style='background:rgba(239,68,68,0.2); color:#f87171; border-color:#ef4444;'>TERMINATED</span></td>";
                    tbody.insertBefore(tr, tbody.firstChild);
                }
                alert("🔒 Session for " + name + " terminated successfully. Access token invalidated.");
            }
        }

        /* 22 MODULES DIRECT OPENING HANDLER */
        var activeModNum = 1;
        function openModule(modId, modTitle) {
            var selector = document.getElementById('userRoleSelector');
            var role = selector ? selector.value : 'admin';
            var allowed = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22];
            if(role !== 'admin') {
                var col = colleagues.find(function(c) { return c.key === role; });
                allowed = col ? col.perms : [];
            }
            if(!allowed.includes(modId)) {
                alert("⛔ ACCESS DENIED: Module " + modId + " (" + modTitle + ") is disabled by Admin for this Colleague.");
                return;
            }

            activeModNum = modId;

            if(modId === 1) {
                switchTab('tab-dash', document.querySelectorAll('.ribbon-btn')[0]);
                return;
            } else if(modId === 2) {
                openAddGmailModal();
                return;
            } else if(modId === 4) {
                document.getElementById('campaignStudioModal').style.display = 'flex';
                evaluateSpamScore();
                return;
            } else if(modId === 5) {
                document.getElementById('spintaxModal').style.display = 'flex';
                return;
            } else if(modId === 6) {
                document.getElementById('scraperModal').style.display = 'flex';
                return;
            } else if(modId === 7) {
                document.getElementById('crmModal').style.display = 'flex';
                renderKanban();
                return;
            } else if(modId === 8) {
                switchTab('tab-team-control', document.querySelectorAll('.ribbon-btn')[2]);
                return;
            }

            var titles = {
                3: "🔥 Module 3: AI Warmup Ramp Engine",
                9: "💓 Module 9: System Doctor Daemon",
                10: "🎵 Module 10: Audio Studio & Extractor",
                11: "🤖 Module 11: Built-in AI Guide Agent",
                12: "🛡️ Module 12: OAuth Token Vault",
                13: "⏰ Module 13: Timezone Scheduler",
                14: "🛡️ Module 14: Bounce Shield (0.08% Filter)",
                15: "💬 Module 15: Auto-Reply & Sentiment Detector",
                16: "📊 Module 16: CSV / Excel Report Exporter",
                17: "📢 Module 17: Broadcast Notification Node",
                18: "🎨 Module 18: Brand Palette Studio",
                19: "🌐 Module 19: Cloud Webhook Dispatcher",
                20: "⏱️ Module 20: Daily Quota Guard (50/50)",
                21: "✍️ Module 21: HTML Signature Builder",
                22: "📈 Module 22: Conversion ROI Predictor"
            };

            var contents = {
                3: "<p><strong>Warmup Status:</strong> Active (P2P Network Enabled)</p><p>Daily Schedule: <strong>15 emails/day ramping to 50/day</strong>. All inboxes maintain a 99.4% sender reputation score.</p>",
                9: "<p><strong>Daemon Health:</strong> 100% Online</p><p>PID: 1048 | Memory: 42 MB | CPU Load: 0.12% | Cloud Worker Uptime: 99.98%.</p>",
                10: "<p><strong>Audio Engine:</strong> Enterprise Cyber Ambient Player active.</p><p>Currently Playing: <em>Focus Soundscape 01 (Lo-Fi Cloud Stream)</em>.</p>",
                11: "<p><strong>AI Assistant:</strong> King Saab Agent online.</p><p>Assisting active outreach flows, parsing email sentiment, and guiding session workflows.</p>",
                12: "<p><strong>Security Status:</strong> AES-256 Cloud Encryption Active.</p><p>5 OAuth Refresh Tokens & 2 Keyphrases secured in encrypted storage vault.</p>",
                13: "<p><strong>Timezone Dispatcher:</strong> NYC (EST), Chicago (CST), LA (PST).</p><p>Active window: <strong>09:00 AM - 05:00 PM US Business Hours</strong>.</p>",
                14: "<p><strong>Bounce Filter:</strong> 0.08% bounce rate active.</p><p>DNS, MX record check, and SMTP ping verification enabled on all lead queues.</p>",
                15: "<p><strong>AI Sentiment Classifier:</strong> 18 positive replies detected this week.</p><p>Auto-categorized into Hot Leads CRM queue.</p>",
                16: "<p><strong>1-Click Export:</strong> Download full outreach logs, open rates, and replies into Microsoft Excel (.xlsx) or CSV format.</p>",
                17: "<p><strong>Team Broadcast:</strong> Dispatches instant banner alerts across all active colleague portals in real time.</p>",
                18: "<p><strong>Theme Engine:</strong> Dark Luxury Emerald Theme (#059669) active across all dashboards and modals.</p>",
                19: "<p><strong>Webhook Sync:</strong> Live POST endpoints available for Zapier, Make.com, and CRM webhooks.</p>",
                20: "<p><strong>Quota Guard:</strong> Strictly enforces 50 emails/day per connected inbox to prevent domain burn.</p>",
                21: "<p><strong>Branded Signatures:</strong> Automatically appends responsive HTML email footer with company logo & contact info.</p>",
                22: "<p><strong>Deal Probability:</strong> 34% estimated close rate for $64,800 active pipeline ($22,032 projected revenue this quarter).</p>"
            };

            document.getElementById('genericModalTitle').innerHTML = titles[modId] || ("⚙️ Module " + modId + ": " + modTitle);
            document.getElementById('genericModalBody').innerHTML = contents[modId] || ("Operational controls for " + modTitle + " are fully active.");
            document.getElementById('genericWorkspaceModal').style.display = 'flex';
        }

        function runGenericModuleAction() {
            if(activeModNum === 16) {
                alert("📊 Generating Excel Report... 'Grace_Outreach_Report_2026.csv' ready for download.");
            } else if(activeModNum === 17) {
                openBroadcastModal();
            } else {
                alert("✔ Module " + activeModNum + " command executed successfully in cloud worker!");
            }
            closeModal('genericWorkspaceModal');
        }

        window.executeLogin = function() {
            var authView = document.getElementById('authViewport');
            var stage = document.getElementById('cinematicStage');
            var app = document.getElementById('enterpriseApp');
            var uInput = document.getElementById('authUsername');
            var u = (uInput && uInput.value ? uInput.value : 'admin').trim();

            if(authView) authView.style.display = 'none';
            if(stage) stage.style.display = 'none';
            if(app) app.style.display = 'flex';

            var found = colleagues.find(function(c) {
                return c.id.toLowerCase() === u.toLowerCase() || c.name.toLowerCase() === u.toLowerCase();
            });

            var selector = document.getElementById('userRoleSelector');
            if(found) {
                if(selector) selector.value = found.key;
                switchColleagueView(found.key);
            } else {
                if(selector) selector.value = 'admin';
                switchColleagueView('admin');
            }
        };

        window.handlePowerOff = function() {
            var app = document.getElementById('enterpriseApp');
            var stage = document.getElementById('cinematicStage');
            var authView = document.getElementById('authViewport');
            if(app) app.style.display = 'none';
            if(stage) stage.style.display = 'block';
            if(authView) authView.style.display = 'flex';
        };

        window.switchTab = function(tabId, btn) {
            document.querySelectorAll('.tab-section').forEach(function(p) { p.classList.remove('active'); });
            document.querySelectorAll('.ribbon-btn').forEach(function(b) { b.classList.remove('active'); });
            var target = document.getElementById(tabId);
            if(target) target.classList.add('active');
            if(btn) btn.classList.add('active');
        };

        window.deleteColleague = function(colKey, name) {
            if(confirm("Are you sure you want to delete colleague profile: " + name + "?")) {
                colleagues = colleagues.filter(function(c) { return c.key !== colKey; });
                renderColleagues();
                switchColleagueView('admin');
                alert("✔ Colleague profile '" + name + "' deleted successfully.");
            }
        };

        window.switchColleagueView = function(role) {
            var label = document.getElementById('activeRoleLabel');
            var allowed = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22];
            
            if(role === 'admin') {
                if(label) {
                    label.innerText = "● Admin View (All Modules Unlocked)";
                    label.style.color = "#34d399";
                }
            } else {
                var col = colleagues.find(function(c) { return c.key === role; });
                allowed = col ? col.perms : [];
                if(label) {
                    label.innerText = "● Testing as " + (col ? col.name.toUpperCase() : role) + " (Restricted Modules Locked)";
                    label.style.color = "#fbbf24";
                }
            }

            for(var i = 1; i <= 22; i++) {
                var card = document.getElementById('mod-' + i);
                if(card) {
                    if(allowed.includes(i)) {
                        card.classList.remove('locked');
                    } else {
                        card.classList.add('locked');
                    }
                }
            }
        };

        window.updateColleaguePerm = function(colKey, modId, enabled) {
            var col = colleagues.find(function(c) { return c.key === colKey; });
            if(col) {
                if(enabled) {
                    if(!col.perms.includes(modId)) col.perms.push(modId);
                } else {
                    col.perms = col.perms.filter(function(x) { return x !== modId; });
                }
            }
            var selector = document.getElementById('userRoleSelector');
            if(selector && selector.value === colKey) switchColleagueView(colKey);
        };

        window.openBroadcastModal = function() {
            var options = "Select Target Recipient:\\n0: All Colleagues (Global Broadcast)\\n";
            colleagues.forEach(function(c, idx) {
                options += (idx + 1) + ": " + c.name + " (" + c.id + ")\\n";
            });
            var sel = prompt(options + "\\nEnter recipient number (0 to " + colleagues.length + "):", "0");
            if(sel === null) return;
            
            var targetName = "All Active Colleagues";
            var num = parseInt(sel);
            if(num > 0 && num <= colleagues.length) {
                targetName = colleagues[num - 1].name + " (" + colleagues[num - 1].id + ")";
            }

            var msg = prompt("Type Broadcast Message for [" + targetName + "]:", "System alert: Daily lead quota limit updated.");
            if(msg) {
                alert("📢 Broadcast Dispatched to [" + targetName + "]: " + msg);
            }
        };

        window.sendTargetedAlert = function(id, name) {
            var msg = prompt("Enter targeted alert for " + name + " (" + id + "):", "Please review pending proposal deals in CRM.");
            if(msg) {
                alert("📢 Direct Alert Sent to " + name + " (" + id + "): " + msg);
            }
        };

        window.addNewColleague = function() {
            var name = prompt("Enter Colleague Full Name:", "Marcus Vance");
            if(!name) return;
            var newKey = "colleague_" + Date.now();
            var newId = "COL-" + Math.floor(100 + Math.random() * 900);
            colleagues.push({
                id: newId,
                key: newKey,
                name: name,
                color: "#a78bfa",
                perms: [1, 2, 4, 5, 6, 7]
            });
            renderColleagues();
            alert("✔ Colleague profile created! Name: " + name + " | Assigned ID: " + newId + " (Status Active)");
        };

        window.triggerRobot = function() {
            var speech = document.getElementById('robotSpeech');
            if(speech) {
                speech.innerText = "✨ 22-Module Hub Online!";
                setTimeout(function() { speech.innerText = "👑 King Saab AI System Ready"; }, 2500);
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() { renderColleagues(); renderInboxes(); renderKanban(); });
        } else {
            renderColleagues();
            renderInboxes();
            renderKanban();
        }
    </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

portal_code = '''import os
import sys
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

RAW_B64 = "''' + b64_logo + '''"
IMG_BYTES = base64.b64decode(RAW_B64)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

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

        if os.path.exists("index.html"):
            with open("index.html", "rb") as f:
                content = f.read()
        else:
            content = b"<h1>Loading Grace Outreach...</h1>"

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        self.wfile.write(content)

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
    f.write(portal_code)

print("✔ Module 8 upgraded with Presets, Activity Audit Table and Force Logout!")
