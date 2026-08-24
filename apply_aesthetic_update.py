import os

with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
    f.write('''import os
import sys
import json
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

SVG_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f0fdf4"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#b45309"/>
    </linearGradient>
    <linearGradient id="emerald" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981"/>
      <stop offset="50%" stop-color="#047857"/>
      <stop offset="100%" stop-color="#064e3b"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.25"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="100" fill="url(#bg)" stroke="#10b981" stroke-width="10"/>
  <rect x="20" y="20" width="472" height="472" rx="85" fill="none" stroke="url(#gold)" stroke-width="5"/>
  <g filter="url(#shadow)">
    <path d="M185 270 L185 180 L225 140 L225 270 Z" fill="url(#emerald)"/>
    <path d="M238 270 L238 100 L278 70 L278 270 Z" fill="url(#emerald)"/>
    <path d="M265 70 L278 70 L278 100 L265 100 Z" fill="url(#gold)"/>
    <path d="M290 120 L340 180 L340 270 L310 270 L310 225 L290 225 Z" fill="url(#gold)"/>
  </g>
  <text x="256" y="340" font-family="'Segoe UI', Arial, sans-serif" font-weight="900" font-size="44" fill="#064e3b" text-anchor="middle" letter-spacing="8">GRACE</text>
  <text x="256" y="380" font-family="'Segoe UI', Arial, sans-serif" font-weight="700" font-size="22" fill="#047857" text-anchor="middle" letter-spacing="10">OUTREACH</text>
  <line x1="100" y1="405" x2="412" y2="405" stroke="url(#gold)" stroke-width="3.5" stroke-linecap="round"/>
  <text x="256" y="440" font-family="Georgia, serif" font-style="italic" font-size="18" fill="#b45309" text-anchor="middle">Developed by King Saab</text>
</svg>"""

B64_SVG = base64.b64encode(SVG_LOGO.encode('utf-8')).decode('utf-8')

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Enterprise Admin Panel</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,__B64_SVG__">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #047857;
            --primary-hover: #065f46;
            --gold: #f59e0b;
            --gold-gradient: linear-gradient(135deg, #fef08a 0%, #f59e0b 50%, #d97706 100%);
            --bg-body: #0b1315;
            --bg-card: #132225;
            --bg-nav: #061719;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border-color: #1e3a3f;
            --card-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
        }

        [data-theme="light"] {
            --primary: #047857;
            --primary-hover: #065f46;
            --gold: #b45309;
            --gold-gradient: linear-gradient(135deg, #d97706 0%, #b45309 100%);
            --bg-body: #f3f4f6;
            --bg-card: #ffffff;
            --bg-nav: #022c22;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --border-color: #e5e7eb;
            --card-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; transition: background 0.2s, color 0.2s; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }

        /* Auth Screen */
        .auth-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background: linear-gradient(135deg, #022c22 0%, #064e3b 100%); }
        .auth-card { background: var(--bg-card); border-radius: 20px; padding: 40px 32px; width: 100%; max-width: 450px; box-shadow: var(--card-shadow); border: 1px solid var(--border-color); text-align: center; }
        
        .logo-box { width: 95px; height: 95px; margin: 0 auto 16px; border-radius: 18px; overflow: hidden; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.25); background: #ffffff; display: flex; align-items: center; justify-content: center; padding: 4px; }
        .logo-box svg { width: 100%; height: 100%; display: block; }
        
        .auth-title { font-size: 24px; font-weight: 900; color: var(--text-main); letter-spacing: 1px; }
        
        /* Aesthetic Credits Banner */
        .aesthetic-badge {
            background: rgba(245, 158, 11, 0.1);
            border: 1px dashed #f59e0b;
            padding: 8px 12px;
            border-radius: 10px;
            margin: 14px 0 20px 0;
            display: inline-block;
            width: 100%;
        }
        .dev-credit { font-family: "Georgia", serif; font-style: italic; font-size: 13px; font-weight: 700; background: var(--gold-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .appreciation-credit { font-size: 11px; color: var(--text-muted); margin-top: 4px; font-weight: 600; }
        .appreciation-credit strong { color: #10b981; }

        .input-group { text-align: left; margin-bottom: 14px; }
        .input-group label { display: block; font-size: 11px; font-weight: 800; color: var(--text-muted); margin-bottom: 5px; text-transform: uppercase; }
        .input-group input, .input-group select, .input-group textarea { width: 100%; padding: 11px 13px; background: var(--bg-body); color: var(--text-main); border: 1.5px solid var(--border-color); border-radius: 8px; font-size: 14px; outline: none; }
        .input-group input:focus, .input-group select:focus, .input-group textarea:focus { border-color: var(--primary); }

        .btn { padding: 10px 18px; border: none; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-primary { background: var(--primary); color: #ffffff; width: 100%; }
        .btn-primary:hover { background: var(--primary-hover); }
        .btn-sm { padding: 6px 12px; font-size: 12px; width: auto; }
        .btn-gold { background: var(--gold); color: #ffffff; }

        /* Dashboard Layout */
        .app-container { display: none; min-height: 100vh; flex-direction: column; }
        .navbar { background: var(--bg-nav); color: #ffffff; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid var(--gold); }
        .nav-brand { display: flex; align-items: center; gap: 14px; }
        
        .nav-logo-box { width: 48px; height: 48px; border-radius: 12px; background: #ffffff; padding: 3px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .nav-logo-box svg { width: 100%; height: 100%; display: block; }
        
        .nav-title { font-size: 18px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .nav-sub { font-size: 11px; margin-top: 2px; }
        .nav-dev { font-family: "Georgia", serif; font-style: italic; font-weight: 700; color: #fbbf24; }
        .nav-mentor { color: #a7f3d0; font-weight: 600; }

        .nav-actions { display: flex; align-items: center; gap: 10px; }
        .theme-toggle-btn { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #ffffff; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 700; }
        .theme-toggle-btn:hover { background: rgba(255,255,255,0.2); }

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
        .badge-live { background: rgba(4, 120, 87, 0.2); color: #10b981; border: 1px solid #047857; }
        .badge-gold { background: rgba(217, 119, 6, 0.2); color: #f59e0b; border: 1px solid #d97706; }

        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; margin-top: 12px; }
        th { background: var(--bg-body); padding: 12px; border-bottom: 2px solid var(--border-color); color: var(--text-muted); text-transform: uppercase; font-size: 11px; }
        td { padding: 12px; border-bottom: 1px solid var(--border-color); color: var(--text-main); }
        
        .chip-picker { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
        .color-chip { width: 34px; height: 34px; border-radius: 50%; cursor: pointer; border: 2px solid #ffffff; box-shadow: 0 0 5px rgba(0,0,0,0.3); }
        
        .toggle-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border-color); }
        .toggle-switch { position: relative; display: inline-block; width: 44px; height: 24px; }
        .toggle-switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #4b5563; transition: .3s; border-radius: 24px; }
        .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; }
        input:checked + .slider { background-color: var(--primary); }
        input:checked + .slider:before { transform: translateX(20px); }
    </style>
</head>
<body>

    <!-- AUTH SCREEN -->
    <div id="authScreen" class="auth-container">
        <div class="auth-card">
            <div class="logo-box">__SVG_LOGO__</div>
            <div class="auth-title">GRACE OUTREACH</div>
            
            <!-- Aesthetic Recognition Banner -->
            <div class="aesthetic-badge">
                <div class="dev-credit">✨ Architected & Engineered by King Saab</div>
                <div class="appreciation-credit">🌟 Executive Strategic Guidance by <strong>Abdullah Khan</strong></div>
            </div>

            <div id="loginForm">
                <div class="input-group">
                    <label>Username / Colleague ID</label>
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
                <button class="theme-toggle-btn" onclick="toggleTheme()"><i id="themeIcon" class="fas fa-sun"></i> Theme</button>
                <button class="theme-toggle-btn" onclick="showTab('tab-custom', null)"><i class="fas fa-sliders-h"></i> Personalize</button>
                <button class="btn btn-sm btn-gold" onclick="logout()"><i class="fas fa-power-off"></i></button>
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
            <button id="ribbon-custom" class="tab-btn" onclick="showTab('tab-custom', this)"><i class="fas fa-palette"></i> Personalization</button>
        </div>

        <div class="main-content">
            
            <!-- 1. DASHBOARD OVERVIEW -->
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
                        <span>⚡ Enterprise System Status</span>
                        <span class="badge badge-live">● Cloud Active 24/7</span>
                    </div>
                    <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6;">
                        Outreach rotation engine is actively load-balancing queries across verified accounts. Follow-up sequences and lead trackers are automated.
                    </p>
                </div>
            </div>

            <!-- 2. GMAIL ACCOUNTS HUB -->
            <div id="tab-gmail" class="tab-pane">
                <div class="content-box">
                    <div class="section-header">
                        <span>📬 Connected Outreach Accounts</span>
                        <button class="btn btn-sm btn-primary" onclick="alert('OAuth Connection Flow Triggered')"><i class="fas fa-plus"></i> Connect New Account</button>
                    </div>
                    <table>
                        <tr>
                            <th>Account Email</th>
                            <th>Daily Quota</th>
                            <th>Warmup Status</th>
                            <th>Health</th>
                            <th>Action</th>
                        </tr>
                        <tr>
                            <td><strong>calvin.gracearchitectures.llc@gmail.com</strong></td>
                            <td>48 / 50 sent</td>
                            <td><span class="badge badge-live">Optimal (100%)</span></td>
                            <td><span class="badge badge-live">Active</span></td>
                            <td><button class="btn btn-sm" style="background: #374151; color:#fff;" onclick="alert('Account settings opened')">Manage</button></td>
                        </tr>
                        <tr>
                            <td><strong>outreach.team@gracearchitectures.com</strong></td>
                            <td>32 / 50 sent</td>
                            <td><span class="badge badge-live">Optimal (98%)</span></td>
                            <td><span class="badge badge-live">Active</span></td>
                            <td><button class="btn btn-sm" style="background: #374151; color:#fff;" onclick="alert('Account settings opened')">Manage</button></td>
                        </tr>
                    </table>
                </div>
            </div>

            <!-- 3. CAMPAIGN STUDIO -->
            <div id="tab-studio" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🚀 Launch Custom Outreach Campaign</span></div>
                    <div class="input-group">
                        <label>Campaign Title</label>
                        <input type="text" placeholder="e.g. Q3 High-Ticket Architectural Developers">
                    </div>
                    <div class="input-group">
                        <label>Upload Leads CSV</label>
                        <input type="file" accept=".csv" style="padding: 8px;">
                    </div>
                    <div class="input-group">
                        <label>Email Pitch Body</label>
                        <textarea rows="4" placeholder="Hi {{First_Name}}, I saw your recent architectural blueprint in {{City}}..."></textarea>
                    </div>
                    <button class="btn btn-primary" onclick="alert('✔ Campaign Queued in Cloud Rotation Engine!')"><i class="fas fa-rocket"></i> Queue & Dispatch Campaign</button>
                </div>
            </div>

            <!-- 4. CRM & PIPELINE -->
            <div id="tab-crm" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🎯 Live Deals & Conversion Funnel</span></div>
                    <table>
                        <tr>
                            <th>Lead Contact</th>
                            <th>Company</th>
                            <th>Status</th>
                            <th>Estimated Value</th>
                        </tr>
                        <tr>
                            <td><strong>Robert Sterling</strong></td>
                            <td>Sterling Studio Architects NYC</td>
                            <td><span class="badge badge-live">Call Scheduled</span></td>
                            <td style="color: #10b981; font-weight:800;">$15,000</td>
                        </tr>
                        <tr>
                            <td><strong>Elena Rostova</strong></td>
                            <td>Apex Urban Form London</td>
                            <td><span class="badge badge-gold">Proposal Review</span></td>
                            <td style="color: #10b981; font-weight:800;">$24,000</td>
                        </tr>
                    </table>
                </div>
            </div>

            <!-- 5. COLLEAGUES -->
            <div id="tab-team" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>👥 Colleague Activity & Approvals</span></div>
                    <div style="background: var(--bg-body); padding: 14px; border-radius: 8px; border-left: 4px solid var(--primary); margin-bottom: 10px;">
                        <div style="font-weight: 800; color: var(--text-main);">KING SAAB (Lead Architect & Developer) 👑</div>
                        <div style="font-size: 12px; color: var(--text-muted);">calvin.gracearchitectures.llc@gmail.com • Access: Master System Owner</div>
                    </div>
                    <div style="background: var(--bg-body); padding: 14px; border-radius: 8px; border-left: 4px solid var(--gold); margin-bottom: 10px;">
                        <div style="font-weight: 800; color: var(--text-main);">ABDULLAH KHAN (Executive Strategy & Growth) 🌟</div>
                        <div style="font-size: 12px; color: var(--text-muted);">Grace Architectures Leadership • Role: Advisory & Operations Lead</div>
                    </div>
                </div>
            </div>

            <!-- 6. SYSTEM DOCTOR / ADMIN CONTROLS -->
            <div id="tab-admin" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🛠️ System Doctor & Maintenance</span></div>
                    <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
                        <button class="btn btn-sm btn-primary" onclick="alert('Database Schema Synced!')"><i class="fas fa-sync"></i> Sync DB Tables</button>
                        <button class="btn btn-sm btn-gold" onclick="alert('Profiles Backup Generated!')"><i class="fas fa-file-archive"></i> Backup Profiles</button>
                        <button class="btn btn-sm" style="background:#dc2626; color:#fff;" onclick="alert('Queue Cleared!')"><i class="fas fa-trash-alt"></i> Reset Queue</button>
                    </div>
                    <label style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--text-muted);">Live Terminal Console Output</label>
                    <div style="background: #000000; color: #10b981; font-family: monospace; font-size: 12px; padding: 16px; border-radius: 8px; margin-top: 6px; line-height: 1.5;">
                        [Cloud Daemon] Live active on port 8080<br>
                        [OAuth Guard] 5 Multi-tenant Gmail accounts ready<br>
                        [Lead Scraper] Outreach worker heartbeat verified (0 errors)
                    </div>
                </div>
            </div>

            <!-- 7. PERSONALIZATION STUDIO -->
            <div id="tab-custom" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🎨 Theme & Color Personalization</span></div>
                    <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 12px;">Choose your primary brand accent or pick a custom palette.</p>
                    <div class="chip-picker">
                        <div class="color-chip" style="background: #047857;" title="Emerald Classic" onclick="setAccent('#047857', '#065f46')"></div>
                        <div class="color-chip" style="background: #d97706;" title="Royal Gold" onclick="setAccent('#d97706', '#b45309')"></div>
                        <div class="color-chip" style="background: #2563eb;" title="Ocean Blue" onclick="setAccent('#2563eb', '#1d4ed8')"></div>
                        <div class="color-chip" style="background: #7c3aed;" title="Imperial Purple" onclick="setAccent('#7c3aed', '#6d28d9')"></div>
                        <div class="color-chip" style="background: #e11d48;" title="Ruby Red" onclick="setAccent('#e11d48', '#be123c')"></div>
                    </div>
                </div>

                <div class="content-box">
                    <div class="section-header"><span>🎛️ Navigation Ribbon Buttons (Add / Remove)</span></div>
                    <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 12px;">Enable or disable navigation buttons from your main top ribbon.</p>
                    
                    <div class="toggle-row">
                        <span><i class="fas fa-chart-pie" style="width: 24px;"></i> Dashboard Tab</span>
                        <label class="toggle-switch">
                            <input type="checkbox" checked onchange="toggleRibbon('ribbon-dash', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="toggle-row">
                        <span><i class="fas fa-envelope-open-text" style="width: 24px;"></i> Gmail Hub Tab</span>
                        <label class="toggle-switch">
                            <input type="checkbox" checked onchange="toggleRibbon('ribbon-gmail', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="toggle-row">
                        <span><i class="fas fa-paper-plane" style="width: 24px;"></i> Campaign Studio Tab</span>
                        <label class="toggle-switch">
                            <input type="checkbox" checked onchange="toggleRibbon('ribbon-studio', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="toggle-row">
                        <span><i class="fas fa-funnel-dollar" style="width: 24px;"></i> CRM & Scraper Tab</span>
                        <label class="toggle-switch">
                            <input type="checkbox" checked onchange="toggleRibbon('ribbon-crm', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="toggle-row">
                        <span><i class="fas fa-users-cog" style="width: 24px;"></i> Colleagues Tab</span>
                        <label class="toggle-switch">
                            <input type="checkbox" checked onchange="toggleRibbon('ribbon-team', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="toggle-row">
                        <span><i class="fas fa-terminal" style="width: 24px;"></i> System Doctor Tab</span>
                        <label class="toggle-switch">
                            <input type="checkbox" checked onchange="toggleRibbon('ribbon-admin', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        function toggleTheme() {
            var html = document.documentElement;
            var current = html.getAttribute('data-theme');
            var next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            document.getElementById('themeIcon').className = next === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            localStorage.setItem('grace_theme', next);
        }

        function setAccent(color, hover) {
            document.documentElement.style.setProperty('--primary', color);
            document.documentElement.style.setProperty('--primary-hover', hover);
            localStorage.setItem('grace_accent', color);
        }

        function toggleRibbon(id, show) {
            var el = document.getElementById(id);
            if(el) {
                el.style.display = show ? 'inline-flex' : 'none';
            }
        }

        function toggleAuth(showRegister) {
            document.getElementById('loginForm').style.display = showRegister ? 'none' : 'block';
            document.getElementById('registerForm').style.display = showRegister ? 'block' : 'none';
        }

        function login() {
            var u = document.getElementById('loginUser').value;
            var p = document.getElementById('loginPass').value;
            if(u && p) {
                document.getElementById('authScreen').style.display = 'none';
                document.getElementById('appScreen').style.display = 'flex';
            } else {
                alert('Please enter your credentials.');
            }
        }

        function register() {
            var code = document.getElementById('regCode').value;
            if(code.toLowerCase() === 'grace') {
                alert('✔ Colleague Registered Successfully! You can now log in.');
                toggleAuth(false);
            } else {
                alert('❌ Invalid Secret Passcode! Contact King Saab.');
            }
        }

        function logout() {
            document.getElementById('appScreen').style.display = 'none';
            document.getElementById('authScreen').style.display = 'flex';
        }

        function showTab(tabId, btn) {
            var panes = document.getElementsByClassName('tab-pane');
            for(var i=0; i<panes.length; i++) panes[i].classList.remove('active');

            var btns = document.getElementsByClassName('tab-btn');
            for(var j=0; j<btns.length; j++) btns[j].classList.remove('active');

            document.getElementById(tabId).classList.add('active');
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
    print(f"✔ Grace Cloud Server listening on http://{HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
''')

print("✔ Aesthetic Logo Visibility & Appreciation credits applied successfully!")
