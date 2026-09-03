import os

# Clean, robust index.html reset with 100% working global functions
clean_html = """<!DOCTYPE html>
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
            width: 100%; padding: 14px 20px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border: 1px solid var(--primary); border-radius: 10px; color: #ffffff;
            font-size: 14px; font-weight: 800; cursor: pointer; box-shadow: 0 6px 20px var(--primary-glow);
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
                    <input type="text" id="authUsername" class="form-control" value="kingsaab56">
                </div>
                <div class="form-group">
                    <label>Security Keyphrase</label>
                    <input type="password" id="authPassword" class="form-control" value="admin123">
                </div>
                <button type="button" class="btn-luxury" onclick="executeLogin()"><i class="fas fa-fingerprint"></i> Enter Command Center</button>
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
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">ACTIVE OUTREACH PIPELINE</div><div style="font-size:28px; font-weight:900;">2,480 Leads</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">CONNECTED GMAIL ACCOUNTS</div><div style="font-size:28px; font-weight:900;">5 Inboxes</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">WEEKLY SENT VOLUME</div><div style="font-size:28px; font-weight:900;">1,240 Emails</div></div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;"><div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">PIPELINE DEAL VALUE</div><div style="font-size:28px; font-weight:900; color:#10b981;">&#36;64,800</div></div>
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
                    <div id="colleaguesListContainer"></div>
                </div>
            </section>

        </main>
    </div>

    <script>
        window.executeLogin = function() {
            document.getElementById('authViewport').style.display = 'none';
            document.getElementById('cinematicStage').style.display = 'none';
            document.getElementById('enterpriseApp').style.display = 'flex';
        };

        window.handlePowerOff = function() {
            document.getElementById('enterpriseApp').style.display = 'none';
            document.getElementById('cinematicStage').style.display = 'block';
            document.getElementById('authViewport').style.display = 'flex';
        };

        window.switchTab = function(tabId, btn) {
            document.querySelectorAll('.tab-section').forEach(function(p) { p.classList.remove('active'); });
            document.querySelectorAll('.ribbon-btn').forEach(function(b) { b.classList.remove('active'); });
            var target = document.getElementById(tabId);
            if(target) target.classList.add('active');
            if(btn) btn.classList.add('active');
        };

        window.openModule = function(modId, modTitle) {
            var tabId = "tab-mod-view-" + modId;
            var target = document.getElementById(tabId);
            if(!target) {
                target = document.createElement("div");
                target.id = tabId;
                target.className = "tab-section";
                target.style.cssText = "padding: 30px; background: var(--bg-body); min-height: 90vh; position: relative; z-index: 50;";
                target.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 15px;">
                        <div>
                            <h2 style="color: #34d399; margin: 0; font-size: 22px;"><i class="fas fa-microchip"></i> Module ${modId}: ${modTitle}</h2>
                            <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">Enterprise Operational Dashboard & Live Execution Engine.</p>
                        </div>
                        <button onclick="switchTab('tab-matrix', document.querySelectorAll('.ribbon-btn')[1])" style="background: rgba(5, 150, 105, 0.2); border: 1px solid var(--primary); color: #fff; padding: 10px 20px; border-radius: 8px; font-weight: 800; cursor: pointer;"><i class="fas fa-arrow-left"></i> Back to Control Matrix</button>
                    </div>
                    <div class="panel-card" style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 30px; border-radius: 16px;">
                        <h3 style="color: #fbbf24; margin-top: 0; margin-bottom: 15px;"><i class="fas fa-terminal"></i> Live Module Telemetry & Controls</h3>
                        <p style="color: var(--text-main); font-size: 14px; line-height: 1.6;">You are now inside <strong>${modTitle}</strong>. Module specific parameters, active telemetry streams, and execution tools are now fully online.</p>
                    </div>
                `;
                document.querySelector('.dashboard-body').appendChild(target);
            }
            document.querySelectorAll('.tab-section').forEach(function(p) { p.classList.remove('active'); });
            document.querySelectorAll('.ribbon-btn').forEach(function(b) { b.classList.remove('active'); });
            target.classList.add('active');
        };

        window.openBroadcastModal = function() {
            alert("📢 Broadcast Notification Dispatched to All Active Colleague Portals.");
        };

        window.addNewColleague = function() {
            alert("✔ New Colleague Profile successfully added to system database.");
        };
    </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(clean_html)

print("✔ Clean robust index.html created!")
