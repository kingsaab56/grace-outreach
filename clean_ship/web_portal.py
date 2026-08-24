import os
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

APP_HTML = '''<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="emerald">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Grace Outreach Assistant | Enterprise AI Command Center</title>
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
            --bg-card: rgba(8, 22, 25, 0.85);
            --bg-card-solid: #08171a;
            --bg-nav: rgba(3, 20, 23, 0.95);
            --border-color: rgba(16, 185, 129, 0.2);
            --border-gold: rgba(245, 158, 11, 0.3);
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --card-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8);
        }

        [data-theme="light"] {
            --bg-body: #f0fdf4;
            --bg-card: rgba(255, 255, 255, 0.9);
            --bg-card-solid: #ffffff;
            --bg-nav: rgba(255, 255, 255, 0.95);
            --border-color: rgba(5, 150, 105, 0.2);
            --border-gold: rgba(217, 119, 6, 0.3);
            --text-main: #0f172a;
            --text-muted: #475569;
            --card-shadow: 0 15px 30px -5px rgba(0, 0, 0, 0.1);
        }

        [data-accent="gold"] { --primary: #d97706; --primary-glow: rgba(217, 119, 6, 0.45); --primary-dark: #78350f; }
        [data-accent="cyan"] { --primary: #0891b2; --primary-glow: rgba(8, 145, 178, 0.45); --primary-dark: #164e63; }
        [data-accent="royal"] { --primary: #2563eb; --primary-glow: rgba(37, 99, 235, 0.45); --primary-dark: #1e3a8a; }
        [data-accent="purple"] { --primary: #9333ea; --primary-glow: rgba(147, 51, 234, 0.45); --primary-dark: #581c87; }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; overflow-x: hidden; position: relative; }

        /* CINEMATIC STAGE */
        #cinematicStage {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: 1;
            overflow: hidden;
            pointer-events: none;
            transition: transform 1.2s ease, opacity 1s ease;
        }

        #worldCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }

        .hologram-emblem {
            position: absolute;
            top: 48%; left: 50%;
            transform: translate(-50%, -50%);
            width: min(650px, 80vw);
            height: min(650px, 80vw);
            opacity: 0.18;
            pointer-events: none;
            filter: drop-shadow(0 0 45px var(--primary-glow));
            animation: holoPulse 12s ease-in-out infinite alternate;
        }

        @keyframes holoPulse {
            0% { transform: translate(-50%, -50%) rotate(0deg) scale(0.96); opacity: 0.14; }
            100% { transform: translate(-50%, -50%) rotate(3deg) scale(1.03); opacity: 0.22; }
        }

        .robot-interactive-actor {
            position: absolute;
            bottom: 4%; left: 18%;
            width: 230px; height: 290px;
            pointer-events: auto;
            cursor: pointer;
            z-index: 10;
            transition: transform 0.4s ease-out;
            filter: drop-shadow(0 20px 25px rgba(0, 0, 0, 0.7));
        }
        .robot-interactive-actor:hover { transform: scale(1.04) translateY(-6px); }

        .robot-speech-balloon {
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
            box-shadow: 0 0 20px var(--primary-glow);
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        .robot-speech-balloon::after {
            content: ''; position: absolute;
            bottom: -6px; left: 50%; transform: translateX(-50%);
            border-width: 6px 6px 0; border-style: solid;
            border-color: var(--primary) transparent; display: block; width: 0;
        }

        .module-capsule {
            position: absolute;
            background: rgba(4, 24, 28, 0.75);
            backdrop-filter: blur(10px);
            border: 1.5px solid var(--primary);
            padding: 9px 18px;
            border-radius: 24px;
            font-size: 12px;
            font-weight: 800;
            color: #34d399;
            box-shadow: 0 0 20px var(--primary-glow);
            cursor: pointer;
            user-select: none;
            pointer-events: auto;
            z-index: 15;
            transition: transform 0.2s;
            animation: capsuleWobble 6s ease-in-out infinite alternate;
        }
        .module-capsule:hover {
            transform: scale(1.15) !important;
            border-color: var(--gold);
            color: #fbbf24;
            box-shadow: 0 0 25px var(--gold-glow);
        }
        @keyframes capsuleWobble {
            0% { transform: translate(0, 0) rotate(0deg); }
            50% { transform: translate(6px, -14px) rotate(2deg); }
            100% { transform: translate(-6px, 8px) rotate(-2deg); }
        }

        /* AUTH VIEWPORT */
        #authViewport {
            position: relative;
            z-index: 20;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 40px 8vw;
            transition: opacity 0.8s ease, transform 0.8s ease;
        }

        .auth-glass-panel {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1.5px solid var(--border-color);
            border-radius: 24px;
            padding: 40px 36px;
            width: 100%;
            max-width: 440px;
            box-shadow: var(--card-shadow);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .auth-glass-panel::before {
            content: ''; position: absolute;
            top: 0; left: 0; right: 0; height: 3px;
            background: var(--gold-gradient);
        }

        .brand-crest { width: 78px; height: 78px; margin: 0 auto 12px; filter: drop-shadow(0 0 15px var(--primary-glow)); }
        .auth-title { font-size: 23px; font-weight: 900; letter-spacing: 1.5px; color: var(--text-main); }
        
        .signature-banner {
            background: rgba(245, 158, 11, 0.08);
            border: 1px dashed var(--border-gold);
            padding: 10px 14px;
            border-radius: 12px;
            margin: 14px 0 22px;
        }
        .sig-architect {
            font-family: Georgia, serif;
            font-style: italic;
            font-weight: 800;
            font-size: 13.5px;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sig-executive { font-size: 11px; color: var(--text-muted); margin-top: 4px; font-weight: 600; }
        .sig-executive strong { color: #34d399; }

        .form-group { text-align: left; margin-bottom: 16px; }
        .form-group label { display: block; font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; }
        .form-control {
            width: 100%;
            padding: 12px 15px;
            background: rgba(3, 10, 12, 0.6);
            border: 1.5px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-main);
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .form-control:focus { border-color: var(--primary); box-shadow: 0 0 12px var(--primary-glow); }

        .btn-luxury {
            width: 100%;
            padding: 13px 20px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border: 1px solid var(--primary);
            border-radius: 10px;
            color: #ffffff;
            font-size: 13.5px;
            font-weight: 800;
            letter-spacing: 0.5px;
            cursor: pointer;
            box-shadow: 0 6px 20px var(--primary-glow);
            transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .btn-luxury:hover { transform: translateY(-2px); box-shadow: 0 10px 25px var(--primary-glow); background: var(--primary); }

        /* ENTERPRISE DASHBOARD */
        #enterpriseApp {
            display: none;
            position: relative;
            z-index: 30;
            min-height: 100vh;
            flex-direction: column;
            background: var(--bg-body);
            opacity: 0;
            transition: opacity 0.8s ease-in-out;
        }

        .top-navbar {
            background: var(--bg-nav);
            border-bottom: 2px solid var(--border-gold);
            padding: 12px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky; top: 0; z-index: 100;
        }
        .brand-meta-box { display: flex; align-items: center; gap: 14px; }
        .brand-meta-box svg { width: 40px; height: 40px; }
        .nav-app-title { font-size: 17px; font-weight: 900; letter-spacing: 0.5px; }
        .nav-app-credits { font-size: 11.5px; margin-top: 2px; }
        .nav-app-credits .dev { font-family: Georgia, serif; font-style: italic; font-weight: 800; color: #fbbf24; }
        .nav-app-credits .advisor { color: #6ee7b7; font-weight: 600; }

        .nav-actions { display: flex; align-items: center; gap: 12px; }
        .btn-broadcast {
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
            border: 1px solid var(--gold);
            color: #ffffff;
            padding: 9px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex; align-items: center; gap: 8px;
            box-shadow: 0 4px 15px var(--gold-glow);
        }
        .btn-power-off {
            background: #dc2626;
            border: 1px solid #ef4444;
            color: #ffffff;
            padding: 9px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex; align-items: center; gap: 6px;
            transition: transform 0.2s, background 0.2s;
        }
        .btn-power-off:hover { transform: scale(1.05); background: #b91c1c; }

        .nav-ribbon-bar {
            background: var(--bg-card-solid);
            border-bottom: 1px solid var(--border-color);
            padding: 8px 28px;
            display: flex;
            gap: 8px;
            overflow-x: auto;
            align-items: center;
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
            white-space: nowrap;
            transition: all 0.2s;
            display: inline-flex; align-items: center; gap: 8px;
        }
        .ribbon-btn:hover, .ribbon-btn.active {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
            box-shadow: 0 4px 15px var(--primary-glow);
        }

        .dashboard-body { padding: 28px 28px; max-width: 1400px; margin: 0 auto; width: 100%; flex: 1; }
        .tab-section { display: none; }
        .tab-section.active { display: block; }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 18px;
            margin-bottom: 24px;
        }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 5px solid var(--primary);
            border-radius: 14px;
            padding: 22px 20px;
            box-shadow: var(--card-shadow);
        }
        .metric-label { font-size: 11.5px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }
        .metric-value { font-size: 28px; font-weight: 900; color: var(--text-main); margin-top: 6px; }

        .panel-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
        }
        .panel-header {
            font-size: 16.5px;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 18px;
            display: flex; justify-content: space-between; align-items: center;
        }

        .audio-preset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin-top: 14px; }
        .audio-card { background: rgba(3, 10, 12, 0.6); border: 1.5px solid var(--border-color); padding: 16px; border-radius: 10px; cursor: pointer; text-align: center; transition: all 0.2s; }
        .audio-card:hover, .audio-card.active { border-color: var(--gold); box-shadow: 0 0 15px var(--gold-glow); background: rgba(245, 158, 11, 0.08); }
        .audio-card i { font-size: 22px; color: var(--gold); margin-bottom: 8px; }

        .color-palette { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
        .color-chip { width: 34px; height: 34px; border-radius: 50%; cursor: pointer; border: 2px solid #ffffff; transition: transform 0.2s; }
        .color-chip:hover { transform: scale(1.15); }

        .toggle-line { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border-color); }
        .switch { position: relative; display: inline-block; width: 44px; height: 22px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #374151; border-radius: 24px; transition: 0.3s; }
        .slider::before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: 0.3s; }
        input:checked + .slider { background: var(--primary); }
        input:checked + .slider::before { transform: translateX(22px); }

        @media (max-width: 900px) {
            #authViewport { justify-content: center; padding: 20px; }
            .robot-interactive-actor { left: 5%; bottom: 2%; transform: scale(0.75); }
        }
    </style>
</head>
<body>

    <audio id="bgAudioPlayer" loop style="display:none;"></audio>

    <!-- CINEMATIC BACKGROUND WORLD -->
    <div id="cinematicStage">
        <canvas id="worldCanvas"></canvas>

        <div class="hologram-emblem">
            <svg viewBox="0 0 512 512" width="100%" height="100%">
                <defs>
                    <linearGradient id="holoGold" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#fef08a"/><stop offset="50%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#b45309"/>
                    </linearGradient>
                    <linearGradient id="holoEmerald" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#34d399"/><stop offset="50%" stop-color="#059669"/><stop offset="100%" stop-color="#064e3b"/>
                    </linearGradient>
                </defs>
                <rect x="20" y="20" width="472" height="472" rx="90" fill="none" stroke="url(#holoGold)" stroke-width="4" stroke-dasharray="16,8"/>
                <circle cx="256" cy="256" r="210" fill="none" stroke="url(#holoEmerald)" stroke-width="2"/>
                <path d="M180 300 L180 180 L225 135 L225 300 Z" fill="url(#holoEmerald)"/>
                <path d="M240 300 L240 90 L285 55 L285 300 Z" fill="url(#holoEmerald)"/>
                <path d="M300 120 L355 185 L355 300 L320 300 L320 235 L300 235 Z" fill="url(#holoGold)"/>
                <text x="256" y="380" font-family="-apple-system, sans-serif" font-weight="900" font-size="44" fill="#f3f4f6" text-anchor="middle" letter-spacing="8">GRACE</text>
                <text x="256" y="418" font-family="-apple-system, sans-serif" font-weight="700" font-size="20" fill="#fbbf24" text-anchor="middle" letter-spacing="10">OUTREACH</text>
            </svg>
        </div>

        <div class="robot-interactive-actor" id="robotActor" onclick="triggerRobotInteraction()">
            <div class="robot-speech-balloon" id="robotSpeech">👑 King Saab System Ready</div>
            <svg viewBox="0 0 240 310" width="100%" height="100%">
                <defs>
                    <linearGradient id="cyberHead" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#cbd5e1"/>
                    </linearGradient>
                </defs>
                <rect x="68" y="45" width="104" height="78" rx="28" fill="url(#cyberHead)" stroke="#94a3b8" stroke-width="2"/>
                <rect x="80" y="60" width="80" height="44" rx="16" fill="#021a1d" stroke="#059669" stroke-width="2"/>
                <path id="robotEyeL" d="M94 80 Q102 72 110 80" stroke="#10b981" stroke-width="3.5" fill="none" stroke-linecap="round"/>
                <path id="robotEyeR" d="M130 80 Q138 72 146 80" stroke="#10b981" stroke-width="3.5" fill="none" stroke-linecap="round"/>
                <line x1="120" y1="45" x2="120" y2="18" stroke="#64748b" stroke-width="3.5"/>
                <circle cx="120" cy="14" r="6.5" fill="#fbbf24"/>
                <path d="M75 130 C75 122 165 122 165 130 L175 210 C175 228 65 228 65 210 Z" fill="url(#cyberHead)" stroke="#94a3b8" stroke-width="2"/>
                <rect x="70" y="190" width="100" height="52" rx="6" fill="#022c22" stroke="#10b981" stroke-width="2"/>
                <text x="120" y="222" font-family="'Georgia', serif" font-style="italic" font-weight="900" font-size="11.5" fill="#fbbf24" text-anchor="middle">👑 KING SAAB</text>
            </svg>
        </div>

        <div id="capsuleContainer"></div>
    </div>

    <!-- 1. AUTH LOGIN VIEW -->
    <div id="authViewport">
        <div class="auth-glass-panel">
            <div class="brand-crest">
                <svg viewBox="0 0 100 100" width="100%" height="100%">
                    <rect width="100" height="100" rx="22" fill="#032024" stroke="#10b981" stroke-width="3"/>
                    <rect x="6" y="6" width="88" height="88" rx="18" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,2"/>
                    <path d="M32 65 L32 44 L44 32 L44 65 Z" fill="#059669"/>
                    <path d="M48 65 L48 24 L60 14 L60 65 Z" fill="#059669"/>
                    <path d="M64 32 L78 46 L78 65 L68 65 L68 54 L64 54 Z" fill="#f59e0b"/>
                    <text x="50" y="78" font-family="-apple-system, sans-serif" font-weight="900" font-size="10" fill="#ffffff" text-anchor="middle" letter-spacing="2">GRACE</text>
                    <text x="50" y="88" font-family="-apple-system, sans-serif" font-weight="700" font-size="6" fill="#fbbf24" text-anchor="middle" letter-spacing="1.5">OUTREACH</text>
                </svg>
            </div>
            <div class="auth-title">GRACE OUTREACH</div>
            
            <div class="signature-banner">
                <div class="sig-architect">✨ Architected & Engineered by King Saab</div>
                <div class="sig-executive">🌟 Executive Strategic Guidance by <strong>Abdullah Khan</strong></div>
            </div>

            <form id="loginForm" onsubmit="handleAuthSubmit(event)">
                <div class="form-group">
                    <label>Colleague Identifier / ID</label>
                    <input type="text" id="authUsername" class="form-control" placeholder="kingsaab56" value="kingsaab56" required>
                </div>
                <div class="form-group">
                    <label>Security Keyphrase</label>
                    <input type="password" id="authPassword" class="form-control" placeholder="••••••••" value="admin56" required>
                </div>
                <button type="submit" class="btn-luxury" id="loginBtn">
                    <i class="fas fa-fingerprint"></i> Enter Command Center
                </button>
                <div style="margin-top: 18px; font-size: 12px; color: var(--text-muted);">
                    Grace Outreach Assistant Cloud Hub • 24/7 Verified
                </div>
            </form>
        </div>
    </div>

    <!-- 2. ENTERPRISE APP DASHBOARD -->
    <div id="enterpriseApp">
        <header class="top-navbar">
            <div class="brand-meta-box">
                <svg viewBox="0 0 100 100">
                    <rect width="100" height="100" rx="20" fill="#032024" stroke="#10b981" stroke-width="3"/>
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
                <button class="btn-broadcast" onclick="alert('📢 Broadcast Alert Sent Across All Active Nodes.')"><i class="fas fa-bullhorn"></i> Broadcast Alert</button>
                <button class="btn-power-off" onclick="handlePowerOff()" title="Power Off / Logout"><i class="fas fa-power-off"></i> Power Off</button>
            </div>
        </header>

        <nav class="nav-ribbon-bar">
            <button id="ribbon-tab-dash" class="ribbon-btn active" onclick="switchTab('tab-dash', this)"><i class="fas fa-chart-pie"></i> Dashboard</button>
            <button id="ribbon-tab-gmail" class="ribbon-btn" onclick="switchTab('tab-gmail', this)"><i class="fas fa-envelope-open-text"></i> Gmail Hub</button>
            <button id="ribbon-tab-studio" class="ribbon-btn" onclick="switchTab('tab-studio', this)"><i class="fas fa-paper-plane"></i> Campaign Studio</button>
            <button id="ribbon-tab-crm" class="ribbon-btn" onclick="switchTab('tab-crm', this)"><i class="fas fa-funnel-dollar"></i> CRM Pipeline</button>
            <button id="ribbon-tab-team" class="ribbon-btn" onclick="switchTab('tab-team', this)"><i class="fas fa-users-cog"></i> Colleagues</button>
            <button id="ribbon-tab-doctor" class="ribbon-btn" onclick="switchTab('tab-doctor', this)"><i class="fas fa-terminal"></i> System Doctor</button>
            <button id="ribbon-tab-custom" class="ribbon-btn" onclick="switchTab('tab-custom', this)"><i class="fas fa-sliders-h"></i> Settings & Audio</button>
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
                        <div class="metric-value" style="color:#10b981;">,800</div>
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
                        <button class="btn-luxury" style="width:auto; padding:8px 16px;" onclick="alert('OAuth Connected!')"><i class="fas fa-plus"></i> Connect Account</button>
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
                    <p style="color:var(--text-muted); font-size:14px;">Robert Sterling • Sterling Studio NYC • Deal: ,000</p>
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

            <!-- 7. SETTINGS & AUDIO STUDIO -->
            <section id="tab-custom" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header">
                        <span>🎵 Ambient Background Music & Audio Extractor</span>
                        <button class="btn-luxury" style="width:auto; padding:6px 14px;" onclick="toggleAudioPlayback()"><i id="audioBtnIcon" class="fas fa-play"></i> <span id="audioBtnText">Play Music</span></button>
                    </div>

                    <div style="margin-bottom: 18px;">
                        <label style="font-size:12px; font-weight:800; text-transform:uppercase; color:var(--text-muted);">1. Select Ambient Soundscape Preset</label>
                        <div class="audio-preset-grid">
                            <div class="audio-card active" onclick="selectPresetAudio('cyber', this)">
                                <i class="fas fa-robot"></i>
                                <div style="font-weight:800; font-size:13px;">Cyber Matrix</div>
                                <div style="font-size:11px; color:var(--text-muted);">110Hz Sine Chill Atmosphere</div>
                            </div>
                            <div class="audio-card" onclick="selectPresetAudio('deep', this)">
                                <i class="fas fa-satellite"></i>
                                <div style="font-weight:800; font-size:13px;">Deep Sci-Fi</div>
                                <div style="font-size:11px; color:var(--text-muted);">75Hz Cosmic Resonator</div>
                            </div>
                            <div class="audio-card" onclick="selectPresetAudio('chill', this)">
                                <i class="fas fa-wave-square"></i>
                                <div style="font-weight:800; font-size:13px;">Enterprise Pulse</div>
                                <div style="font-size:11px; color:var(--text-muted);">Harmonic Ambient Wave</div>
                            </div>
                        </div>
                    </div>

                    <div style="border-top:1px solid var(--border-color); padding-top:16px;">
                        <label style="font-size:12px; font-weight:800; text-transform:uppercase; color:var(--text-muted);">2. Upload Custom Audio or Extract Sound from Video (.mp3, .wav, .mp4, .webm)</label>
                        <div style="display:flex; gap:12px; margin-top:8px; flex-wrap:wrap;">
                            <input type="file" id="mediaUploadInput" class="form-control" style="flex:1; min-width:240px;" accept="audio/*,video/*" onchange="handleMediaUpload(event)">
                            <button class="btn-luxury" style="width:auto;" onclick="document.getElementById('mediaUploadInput').click()"><i class="fas fa-file-audio"></i> Choose File</button>
                        </div>
                        <p style="font-size:11.5px; color:var(--text-muted); margin-top:6px;">Upload any video or audio file; the portal will instantly extract and loop it across your sessions.</p>
                    </div>
                </div>

                <div class="panel-card">
                    <div class="panel-header">
                        <span>🎨 Theme & Accent Customization</span>
                        <button class="btn-luxury" style="width:auto; padding:6px 14px;" onclick="toggleThemeMode()"><i id="themeIcon" class="fas fa-sun"></i> Toggle Theme</button>
                    </div>
                    <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 12px;">Choose brand accent color palette:</p>
                    <div class="color-palette">
                        <div class="color-chip" style="background:#059669;" onclick="setAccentTheme('emerald')" title="Emerald"></div>
                        <div class="color-chip" style="background:#d97706;" onclick="setAccentTheme('gold')" title="Gold"></div>
                        <div class="color-chip" style="background:#0891b2;" onclick="setAccentTheme('cyan')" title="Cyan"></div>
                        <div class="color-chip" style="background:#2563eb;" onclick="setAccentTheme('royal')" title="Royal Blue"></div>
                        <div class="color-chip" style="background:#9333ea;" onclick="setAccentTheme('purple')" title="Purple"></div>
                    </div>
                </div>

                <div class="panel-card">
                    <div class="panel-header"><span>🎛️ Navigation Ribbon Buttons</span></div>
                    <div class="toggle-line"><span>Dashboard Tab</span><label class="switch"><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-dash', this.checked)"><span class="slider"></span></label></div>
                    <div class="toggle-line"><span>Gmail Hub Tab</span><label class="switch"><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-gmail', this.checked)"><span class="slider"></span></label></div>
                    <div class="toggle-line"><span>Campaign Studio Tab</span><label class="switch"><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-studio', this.checked)"><span class="slider"></span></label></div>
                    <div class="toggle-line"><span>CRM Pipeline Tab</span><label class="switch"><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-crm', this.checked)"><span class="slider"></span></label></div>
                    <div class="toggle-line"><span>Colleagues Tab</span><label class="switch"><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-team', this.checked)"><span class="slider"></span></label></div>
                    <div class="toggle-line"><span>System Doctor Tab</span><label class="switch"><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-doctor', this.checked)"><span class="slider"></span></label></div>
                </div>
            </section>
        </main>
    </div>

    <script>
        const canvas = document.getElementById('worldCanvas');
        const ctx = canvas.getContext('2d');
        let width, height;

        function setCanvasSize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        setCanvasSize();
        window.addEventListener('resize', setCanvasSize);

        const birds = Array.from({ length: 7 }, () => ({
            x: Math.random() * window.innerWidth,
            y: Math.random() * (window.innerHeight * 0.38),
            vx: 1.2 + Math.random() * 1.6,
            vy: (Math.random() - 0.5) * 0.4,
            size: 9 + Math.random() * 6,
            wingPhase: Math.random() * Math.PI * 2
        }));

        let lightningTime = 0;
        function renderLivingScene() {
            ctx.clearRect(0, 0, width, height);
            lightningTime += 0.04;

            const grad = ctx.createLinearGradient(0, 0, 0, height);
            grad.addColorStop(0, '#02090b');
            grad.addColorStop(1, '#051b1f');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, width, height);

            const baseY = height * 0.90;
            const bWidth = 140;
            const bStartX = width * 0.10;

            ctx.strokeStyle = 'rgba(5, 150, 105, 0.2)';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(bStartX, baseY - 340, bWidth, 340);
            ctx.strokeRect(bStartX + bWidth + 24, baseY - 460, bWidth + 40, 460);

            birds.forEach(b => {
                b.x += b.vx;
                b.y += b.vy;
                b.wingPhase += 0.18;
                if(b.x > width + 60) b.x = -60;
                if(b.y < 30 || b.y > height * 0.5) b.vy *= -1;

                ctx.strokeStyle = 'rgba(52, 211, 153, 0.65)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                const wingOffset = Math.sin(b.wingPhase) * 5;
                ctx.moveTo(b.x - b.size, b.y + wingOffset);
                ctx.lineTo(b.x, b.y);
                ctx.lineTo(b.x + b.size, b.y + wingOffset);
                ctx.stroke();
            });

            requestAnimationFrame(renderLivingScene);
        }
        renderLivingScene();

        const initialCapsules = [
            { title: "5-Account Rotator", icon: "fa-sync fa-spin", x: 12, y: 35 },
            { title: "24/7 Cloud Worker", icon: "fa-bolt", x: 34, y: 25 },
            { title: "CRM Deal Pipeline", icon: "fa-funnel-dollar", x: 15, y: 55 },
            { title: "Warmup AI Guardian", icon: "fa-shield-alt", x: 36, y: 65 }
        ];
        const capsuleContainer = document.getElementById('capsuleContainer');
        initialCapsules.forEach(cap => {
            const el = document.createElement('div');
            el.className = 'module-capsule';
            el.style.left = cap.x + 'vw';
            el.style.top = cap.y + 'vh';
            el.innerHTML = '<i class="fas ' + cap.icon + '"></i> ' + cap.title;
            capsuleContainer.appendChild(el);
        });

        function triggerRobotInteraction() {
            const speech = document.getElementById('robotSpeech');
            speech.innerText = "✨ Command Center Online!";
            setTimeout(() => { speech.innerText = "👑 King Saab AI System Ready"; }, 2500);
        }

        /* 1. AUTH LOGIN SUBMIT */
        function handleAuthSubmit(e) {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing Environment...';

            setTimeout(() => {
                const stage = document.getElementById('cinematicStage');
                const authView = document.getElementById('authViewport');
                const appView = document.getElementById('enterpriseApp');

                stage.style.transform = 'scale(1.2)';
                stage.style.opacity = '0';
                authView.style.opacity = '0';
                authView.style.transform = 'translateY(-20px)';

                setTimeout(() => {
                    authView.style.display = 'none';
                    stage.style.display = 'none';
                    appView.style.display = 'flex';
                    setTimeout(() => { appView.style.opacity = '1'; }, 50);
                    btn.innerHTML = '<i class="fas fa-fingerprint"></i> Enter Command Center';
                }, 600);
            }, 700);
        }

        /* 2. POWER OFF / LOGOUT (RETURNS CLEANLY TO LOGIN VIEW) */
        function handlePowerOff() {
            const stage = document.getElementById('cinematicStage');
            const authView = document.getElementById('authViewport');
            const appView = document.getElementById('enterpriseApp');

            appView.style.opacity = '0';
            setTimeout(() => {
                appView.style.display = 'none';
                stage.style.display = 'block';
                authView.style.display = 'flex';
                
                setTimeout(() => {
                    stage.style.transform = 'scale(1)';
                    stage.style.opacity = '1';
                    authView.style.opacity = '1';
                    authView.style.transform = 'translateY(0)';
                }, 50);
            }, 400);
        }

        function switchTab(tabId, btn) {
            document.querySelectorAll('.tab-section').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.ribbon-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            if(btn) btn.classList.add('active');
        }

        function toggleRibbonItem(ribbonBtnId, visible) {
            const el = document.getElementById(ribbonBtnId);
            if(el) el.style.display = visible ? 'inline-flex' : 'none';
        }

        function setAccentTheme(accent) {
            document.documentElement.setAttribute('data-accent', accent);
            localStorage.setItem('grace_accent', accent);
        }

        function toggleThemeMode() {
            const cur = document.documentElement.getAttribute('data-theme');
            const next = cur === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            const icon = document.getElementById('themeIcon');
            if(icon) icon.className = next === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }

        /* AUDIO SYSTEM */
        let audioCtx = null;
        let isAudioPlaying = false;
        let activeOsc = null;
        let currentPreset = 'cyber';
        const player = document.getElementById('bgAudioPlayer');

        function initAudioContext() {
            if(!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if(audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function selectPresetAudio(presetName, el) {
            document.querySelectorAll('.audio-card').forEach(c => c.classList.remove('active'));
            if(el) el.classList.add('active');
            currentPreset = presetName;
            
            if(!player.paused) player.pause();
            if(isAudioPlaying) {
                stopPresetSynth();
                playPresetSynth();
            }
        }

        function playPresetSynth() {
            initAudioContext();
            activeOsc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            
            if(currentPreset === 'cyber') {
                activeOsc.type = 'sine';
                activeOsc.frequency.setValueAtTime(110, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.015, audioCtx.currentTime);
            } else if(currentPreset === 'deep') {
                activeOsc.type = 'triangle';
                activeOsc.frequency.setValueAtTime(75, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.02, audioCtx.currentTime);
            } else {
                activeOsc.type = 'sine';
                activeOsc.frequency.setValueAtTime(140, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.012, audioCtx.currentTime);
            }

            activeOsc.connect(gain);
            gain.connect(audioCtx.destination);
            activeOsc.start();
        }

        function stopPresetSynth() {
            if(activeOsc) {
                try { activeOsc.stop(); } catch(e){}
                activeOsc = null;
            }
        }

        function toggleAudioPlayback() {
            initAudioContext();
            const btnIcon = document.getElementById('audioBtnIcon');
            const btnText = document.getElementById('audioBtnText');

            if(!isAudioPlaying) {
                if(player.src && player.src !== '') {
                    player.play();
                } else {
                    playPresetSynth();
                }
                isAudioPlaying = true;
                if(btnIcon) btnIcon.className = 'fas fa-pause';
                if(btnText) btnText.innerText = 'Pause Music';
            } else {
                if(!player.paused) player.pause();
                stopPresetSynth();
                isAudioPlaying = false;
                if(btnIcon) btnIcon.className = 'fas fa-play';
                if(btnText) btnText.innerText = 'Play Music';
            }
        }

        function handleMediaUpload(e) {
            const file = e.target.files[0];
            if(file) {
                stopPresetSynth();
                const fileURL = URL.createObjectURL(file);
                player.src = fileURL;
                player.play();
                isAudioPlaying = true;
                const btnIcon = document.getElementById('audioBtnIcon');
                const btnText = document.getElementById('audioBtnText');
                if(btnIcon) btnIcon.className = 'fas fa-pause';
                if(btnText) btnText.innerText = 'Playing: ' + file.name.substring(0, 14) + '...';
                alert('✔ Audio extracted & actively playing: ' + file.name);
            }
        }

        const savedAccent = localStorage.getItem('grace_accent');
        if(savedAccent) document.documentElement.setAttribute('data-accent', savedAccent);
    </script>
</body>
</html>'''

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
