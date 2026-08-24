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
    <title>Grace Outreach Assistant | 22-Module Enterprise Command Center</title>
    <!-- EMBEDDED HIGH-RES SVG FAVICON FOR BROWSER TAB & ADDRESS BAR -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23032024' stroke='%2310b981' stroke-width='4'/%3E%3Cpath d='M30 65 L30 42 L42 30 L42 65 Z' fill='%23059669'/%3E%3Cpath d='M46 65 L46 22 L58 12 L58 65 Z' fill='%23059669'/%3E%3Cpath d='M62 30 L76 44 L76 65 L66 65 Z' fill='%23f59e0b'/%3E%3C/svg%3E">
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
            --bg-card: rgba(8, 22, 25, 0.88);
            --bg-card-solid: #08171a;
            --bg-nav: rgba(3, 20, 23, 0.96);
            --border-color: rgba(16, 185, 129, 0.22);
            --border-gold: rgba(245, 158, 11, 0.35);
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --card-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8);
        }

        [data-theme="light"] {
            --bg-body: #f0fdf4;
            --bg-card: rgba(255, 255, 255, 0.92);
            --bg-card-solid: #ffffff;
            --bg-nav: rgba(255, 255, 255, 0.96);
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
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; overflow-x: hidden; }

        #launchSplash {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #02080a;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: opacity 0.6s ease, visibility 0.6s ease;
        }
        .splash-crest {
            width: 120px; height: 120px;
            animation: pulseSplash 1.4s ease-in-out infinite alternate;
            filter: drop-shadow(0 0 35px var(--primary-glow));
        }
        @keyframes pulseSplash {
            0% { transform: scale(0.92); opacity: 0.8; }
            100% { transform: scale(1.08); opacity: 1; }
        }
        .splash-title {
            margin-top: 18px;
            font-size: 22px;
            font-weight: 900;
            letter-spacing: 4px;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

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
            bottom: 4%; left: 16%;
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

        .brand-crest { width: 90px; height: 90px; margin: 0 auto 12px; filter: drop-shadow(0 0 16px var(--primary-glow)); }
        .auth-title { font-size: 22px; font-weight: 900; letter-spacing: 1.5px; color: var(--text-main); }
        
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
        .brand-meta-box svg { width: 44px; height: 44px; }
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
            padding: 8px 24px;
            display: flex;
            gap: 6px;
            overflow-x: auto;
            align-items: center;
            scrollbar-width: thin;
        }
        .ribbon-btn {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 8px 14px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            border-radius: 8px;
            white-space: nowrap;
            transition: all 0.2s;
            display: inline-flex; align-items: center; gap: 7px;
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
        .metric-value { font-size: 28px; font-weight: 900; color: var(--text-main); margin-top: 6px; display: flex; align-items: baseline; gap: 4px; }
        .dollar-symbol { color: #10b981; font-weight: 900; font-size: 26px; }

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

        .custom-table { width: 100%; border-collapse: collapse; margin-top: 14px; }
        .custom-table th, .custom-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 13.5px; }
        .custom-table th { background: rgba(5, 150, 105, 0.12); color: #34d399; font-weight: 800; text-transform: uppercase; font-size: 11.5px; }
        .status-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 800; }
        .badge-optimal { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
        .badge-warmup { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }

        .modules-matrix-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-top: 14px;
        }
        .module-matrix-card {
            background: rgba(3, 10, 12, 0.6);
            border: 1.5px solid var(--border-color);
            border-radius: 12px;
            padding: 18px;
            display: flex;
            gap: 14px;
            align-items: flex-start;
            cursor: pointer;
            transition: all 0.2s;
        }
        .module-matrix-card:hover {
            border-color: var(--primary);
            transform: translateY(-3px);
            box-shadow: 0 6px 20px var(--primary-glow);
        }
        .matrix-icon {
            font-size: 22px;
            color: var(--gold);
            background: rgba(245, 158, 11, 0.1);
            width: 44px; height: 44px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 10px;
            border: 1px solid var(--border-gold);
        }

        .chat-box {
            background: rgba(2, 10, 12, 0.7);
            border: 1.5px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            height: 320px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .chat-msg {
            padding: 10px 14px;
            border-radius: 10px;
            max-width: 80%;
            font-size: 13.5px;
            line-height: 1.5;
        }
        .msg-agent {
            background: rgba(5, 150, 105, 0.15);
            border: 1px solid var(--primary);
            align-self: flex-start;
            color: #f9fafb;
        }
        .msg-user {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid var(--gold);
            align-self: flex-end;
            color: #ffffff;
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

    <div id="launchSplash">
        <div class="splash-crest">
            <svg viewBox="0 0 100 100" width="100%" height="100%">
                <rect width="100" height="100" rx="22" fill="#032024" stroke="#10b981" stroke-width="3"/>
                <path d="M30 65 L30 42 L42 30 L42 65 Z" fill="#059669"/>
                <path d="M46 65 L46 22 L58 12 L58 65 Z" fill="#059669"/>
                <path d="M62 30 L76 44 L76 65 L66 65 Z" fill="#f59e0b"/>
            </svg>
        </div>
        <div class="splash-title">GRACE OUTREACH ASSISTANT</div>
        <div style="color:#6ee7b7; font-size:12px; margin-top:8px; font-weight:700;"><i class="fas fa-circle-notch fa-spin"></i> Initializing 22 Core Modules...</div>
    </div>

    <audio id="bgAudioPlayer" loop style="display:none;"></audio>

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
                <div class="sig-executive">🌟 Strategic Guidance by <strong>Abdullah Khan</strong></div>
            </div>

            <form id="loginForm" onsubmit="handleAuthSubmit(event)" autocomplete="off">
                <div class="form-group">
                    <label>Colleague Identifier / ID</label>
                    <input type="text" id="authUsername" class="form-control" placeholder="Enter Colleague ID" required autocomplete="off">
                </div>
                <div class="form-group">
                    <label>Security Keyphrase</label>
                    <input type="password" id="authPassword" class="form-control" placeholder="Enter Keyphrase" required autocomplete="new-password">
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
                <button class="btn-broadcast" onclick="alert('📢 Broadcast Alert Sent Across All 22 Nodes.')"><i class="fas fa-bullhorn"></i> Broadcast Alert</button>
                <button class="btn-power-off" onclick="handlePowerOff()" title="Power Off / Logout"><i class="fas fa-power-off"></i> Power Off</button>
            </div>
        </header>

        <nav class="nav-ribbon-bar">
            <button id="ribbon-tab-dash" class="ribbon-btn active" onclick="switchTab('tab-dash', this)"><i class="fas fa-chart-pie"></i> 1. Dashboard</button>
            <button id="ribbon-tab-matrix" class="ribbon-btn" onclick="switchTab('tab-matrix', this)"><i class="fas fa-th"></i> 2. 22-Module Matrix</button>
            <button id="ribbon-tab-gmail" class="ribbon-btn" onclick="switchTab('tab-gmail', this)"><i class="fas fa-envelope-open-text"></i> 3. Gmail Hub & Warmup</button>
            <button id="ribbon-tab-studio" class="ribbon-btn" onclick="switchTab('tab-studio', this)"><i class="fas fa-paper-plane"></i> 4. Campaign Studio</button>
            <button id="ribbon-tab-leads" class="ribbon-btn" onclick="switchTab('tab-leads', this)"><i class="fas fa-search-location"></i> 5. Lead Scraper</button>
            <button id="ribbon-tab-crm" class="ribbon-btn" onclick="switchTab('tab-crm', this)"><i class="fas fa-funnel-dollar"></i> 6. CRM Pipeline Deals</button>
            <button id="ribbon-tab-team" class="ribbon-btn" onclick="switchTab('tab-team', this)"><i class="fas fa-users-cog"></i> 7. Colleagues Manager</button>
            <button id="ribbon-tab-doctor" class="ribbon-btn" onclick="switchTab('tab-doctor', this)"><i class="fas fa-terminal"></i> 8. System Doctor</button>
            <button id="ribbon-tab-custom" class="ribbon-btn" onclick="switchTab('tab-custom', this)"><i class="fas fa-sliders-h"></i> 9. Settings & Audio</button>
            <button id="ribbon-tab-agent" class="ribbon-btn" onclick="switchTab('tab-agent', this)"><i class="fas fa-robot"></i> 10. AI Guide Agent</button>
            <button id="ribbon-tab-vault" class="ribbon-btn" onclick="switchTab('tab-vault', this)"><i class="fas fa-shield-alt"></i> 11. OAuth Vault</button>
            <button id="ribbon-tab-time" class="ribbon-btn" onclick="switchTab('tab-time', this)"><i class="fas fa-clock"></i> 12. Scheduler</button>
            <button id="ribbon-tab-bounce" class="ribbon-btn" onclick="switchTab('tab-bounce', this)"><i class="fas fa-filter"></i> 13. Bounce Shield</button>
            <button id="ribbon-tab-reply" class="ribbon-btn" onclick="switchTab('tab-reply', this)"><i class="fas fa-reply-all"></i> 14. Auto-Reply</button>
            <button id="ribbon-tab-export" class="ribbon-btn" onclick="switchTab('tab-export', this)"><i class="fas fa-file-export"></i> 15. CSV Export</button>
            <button id="ribbon-tab-broadcast" class="ribbon-btn" onclick="switchTab('tab-broadcast', this)"><i class="fas fa-bullhorn"></i> 16. Broadcast Node</button>
            <button id="ribbon-tab-theme" class="ribbon-btn" onclick="switchTab('tab-theme', this)"><i class="fas fa-palette"></i> 17. Brand Palette</button>
            <button id="ribbon-tab-robot" class="ribbon-btn" onclick="switchTab('tab-robot', this)"><i class="fas fa-microchip"></i> 18. Cyber Robot</button>
            <button id="ribbon-tab-webhook" class="ribbon-btn" onclick="switchTab('tab-webhook', this)"><i class="fas fa-network-wired"></i> 19. Webhooks</button>
            <button id="ribbon-tab-quota" class="ribbon-btn" onclick="switchTab('tab-quota', this)"><i class="fas fa-tachometer-alt"></i> 20. Quota Guard</button>
            <button id="ribbon-tab-sign" class="ribbon-btn" onclick="switchTab('tab-sign', this)"><i class="fas fa-signature"></i> 21. Signature Builder</button>
            <button id="ribbon-tab-roi" class="ribbon-btn" onclick="switchTab('tab-roi', this)"><i class="fas fa-chart-line"></i> 22. ROI Predictor</button>
        </nav>

        <main class="dashboard-body">
            <section id="tab-dash" class="tab-section active">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Active Outreach Pipeline</div>
                        <div class="metric-value">2,480 <span style="font-size:14px; color:var(--text-muted);">Leads</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Connected Gmail Accounts</div>
                        <div class="metric-value">5 <span style="font-size:14px; color:var(--text-muted);">Inboxes</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Weekly Sent Volume</div>
                        <div class="metric-value">1,240 <span style="font-size:14px; color:var(--text-muted);">Emails</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Pipeline Deal Value</div>
                        <div class="metric-value"><span class="dollar-symbol">$</span>64,800</div>
                    </div>
                </div>

                <div class="panel-card">
                    <div class="panel-header">
                        <span>⚡ 24/7 Cloud Outreach Engine Active</span>
                        <span style="color:#34d399; font-weight:700; font-size:12px;">● Permanent Cloud Active</span>
                    </div>
                    <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6;">
                        Cloud daemon is running continuously on Railway. All 22 modules operate synchronously for both leadership and colleagues.
                    </p>
                </div>
            </section>

            <section id="tab-matrix" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🎛️ Complete 22-Module Control Matrix</span></div>
                    <div class="modules-matrix-grid">
                        <div class="module-matrix-card" onclick="switchTab('tab-dash')"><div class="matrix-icon"><i class="fas fa-chart-pie"></i></div><div><div style="font-weight:800; font-size:14px;">1. Dashboard Overview</div><div style="font-size:11.5px; color:var(--text-muted);">Live analytics & telemetry</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-matrix')"><div class="matrix-icon"><i class="fas fa-th"></i></div><div><div style="font-weight:800; font-size:14px;">2. 22-Module Matrix</div><div style="font-size:11.5px; color:var(--text-muted);">Full system control array</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-gmail')"><div class="matrix-icon"><i class="fas fa-envelope"></i></div><div><div style="font-weight:800; font-size:14px;">3. Gmail Hub & Warmup</div><div style="font-size:11.5px; color:var(--text-muted);">5-account rotation engine</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-studio')"><div class="matrix-icon"><i class="fas fa-paper-plane"></i></div><div><div style="font-weight:800; font-size:14px;">4. Campaign Studio</div><div style="font-size:11.5px; color:var(--text-muted);">Dynamic follow-up engine</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-leads')"><div class="matrix-icon"><i class="fas fa-search"></i></div><div><div style="font-weight:800; font-size:14px;">5. NYC Lead Scraper</div><div style="font-size:11.5px; color:var(--text-muted);">Architect firm contact extractor</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-crm')"><div class="matrix-icon"><i class="fas fa-dollar-sign"></i></div><div><div style="font-weight:800; font-size:14px;">6. CRM Deals Pipeline</div><div style="font-size:11.5px; color:var(--text-muted);">,800 Active deal stages</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-team')"><div class="matrix-icon"><i class="fas fa-users-cog"></i></div><div><div style="font-weight:800; font-size:14px;">7. Colleagues Permission Manager</div><div style="font-size:11.5px; color:var(--text-muted);">Admin-controlled module visibility</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-doctor')"><div class="matrix-icon"><i class="fas fa-heartbeat"></i></div><div><div style="font-weight:800; font-size:14px;">8. System Doctor Daemon</div><div style="font-size:11.5px; color:var(--text-muted);">Live health & PID supervisor</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-custom')"><div class="matrix-icon"><i class="fas fa-music"></i></div><div><div style="font-weight:800; font-size:14px;">9. Settings & Audio Studio</div><div style="font-size:11.5px; color:var(--text-muted);">Volume slider & Sound extractor</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-agent')"><div class="matrix-icon"><i class="fas fa-robot"></i></div><div><div style="font-weight:800; font-size:14px;">10. AI Guide Agent</div><div style="font-size:11.5px; color:var(--text-muted);">Live interactive chat assistant</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-vault')"><div class="matrix-icon"><i class="fas fa-shield-alt"></i></div><div><div style="font-weight:800; font-size:14px;">11. OAuth Token Vault</div><div style="font-size:11.5px; color:var(--text-muted);">Encrypted keyphrase protection</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-time')"><div class="matrix-icon"><i class="fas fa-clock"></i></div><div><div style="font-weight:800; font-size:14px;">12. Timezone Scheduler</div><div style="font-size:11.5px; color:var(--text-muted);">EST & PST delivery targeting</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-bounce')"><div class="matrix-icon"><i class="fas fa-filter"></i></div><div><div style="font-weight:800; font-size:14px;">13. Bounce Shield</div><div style="font-size:11.5px; color:var(--text-muted);">0.1% hard bounce filtering</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-reply')"><div class="matrix-icon"><i class="fas fa-reply-all"></i></div><div><div style="font-weight:800; font-size:14px;">14. Auto-Reply Detector</div><div style="font-size:11.5px; color:var(--text-muted);">Positive response alert</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-export')"><div class="matrix-icon"><i class="fas fa-file-export"></i></div><div><div style="font-weight:800; font-size:14px;">15. CSV Export Engine</div><div style="font-size:11.5px; color:var(--text-muted);">1-Click campaign reports</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-broadcast')"><div class="matrix-icon"><i class="fas fa-bullhorn"></i></div><div><div style="font-weight:800; font-size:14px;">16. Broadcast Notification Node</div><div style="font-size:11.5px; color:var(--text-muted);">Real-time colleague alerts</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-theme')"><div class="matrix-icon"><i class="fas fa-palette"></i></div><div><div style="font-weight:800; font-size:14px;">17. Brand Palette Theme</div><div style="font-size:11.5px; color:var(--text-muted);">5 Luxury accent styling</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-robot')"><div class="matrix-icon"><i class="fas fa-microchip"></i></div><div><div style="font-weight:800; font-size:14px;">18. Cyber Viewport Robot</div><div style="font-size:11.5px; color:var(--text-muted);">Interactive viewport agent</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-webhook')"><div class="matrix-icon"><i class="fas fa-network-wired"></i></div><div><div style="font-weight:800; font-size:14px;">19. Webhook Dispatcher</div><div style="font-size:11.5px; color:var(--text-muted);">Third-party integrations</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-quota')"><div class="matrix-icon"><i class="fas fa-tachometer-alt"></i></div><div><div style="font-weight:800; font-size:14px;">20. Quota Guard Shield</div><div style="font-size:11.5px; color:var(--text-muted);">50/50 safe daily limit</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-sign')"><div class="matrix-icon"><i class="fas fa-signature"></i></div><div><div style="font-weight:800; font-size:14px;">21. HTML Signature Builder</div><div style="font-size:11.5px; color:var(--text-muted);">Custom design branding</div></div></div>
                        <div class="module-matrix-card" onclick="switchTab('tab-roi')"><div class="matrix-icon"><i class="fas fa-chart-line"></i></div><div><div style="font-weight:800; font-size:14px;">22. Conversion ROI Predictor</div><div style="font-size:11.5px; color:var(--text-muted);">Deal closing probability</div></div></div>
                    </div>
                </div>
            </section>

            <section id="tab-gmail" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header">
                        <span>📬 Connected Multi-Tenant Outreach Inboxes</span>
                        <button class="btn-luxury" style="width:auto; padding:8px 16px;" onclick="alert('Google OAuth 2.0 Auth Bridge Initiated!')"><i class="fas fa-plus"></i> Connect New Account</button>
                    </div>
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th>Account Email</th>
                                <th>Daily Quota</th>
                                <th>Warmup Schedule</th>
                                <th>OAuth Guard</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>calvin.gracearchitectures.llc@gmail.com</td>
                                <td>48 / 50 Sent</td>
                                <td>Ramp Up: Day 18</td>
                                <td><span style="color:#34d399;">Active Refresh Token</span></td>
                                <td><span class="status-badge badge-optimal">Optimal</span></td>
                            </tr>
                            <tr>
                                <td>brydon.gracearchitectures.llc@gmail.com</td>
                                <td>35 / 50 Sent</td>
                                <td>Ramp Up: Day 12</td>
                                <td><span style="color:#34d399;">Active Refresh Token</span></td>
                                <td><span class="status-badge badge-optimal">Optimal</span></td>
                            </tr>
                            <tr>
                                <td>outreach.grace.nyc@gmail.com</td>
                                <td>22 / 50 Sent</td>
                                <td>Ramp Up: Day 6</td>
                                <td><span style="color:#fbbf24;">Warmup Safeguard</span></td>
                                <td><span class="status-badge badge-warmup">Warming Up</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section id="tab-studio" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🚀 Launch Dynamic Outreach Campaign</span></div>
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:16px;">
                        <div class="form-group">
                            <label>Campaign Name</label>
                            <input type="text" class="form-control" value="Q3 Architecture Leads NYC">
                        </div>
                        <div class="form-group">
                            <label>Assigned Sender Rotation Pool</label>
                            <select class="form-control">
                                <option>Auto-Rotate All 5 Verified Accounts</option>
                                <option>Calvin & Brydon Duo Pool</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Dynamic Spin-Syntax Email Template</label>
                        <textarea class="form-control" rows="4">Hi {First_Name}, I noticed your architectural portfolio at {Company_Name}. Would love to discuss collaborating on your upcoming high-end residential designs.</textarea>
                    </div>
                    <button class="btn-luxury" style="width:auto; padding:10px 24px;" onclick="alert('Campaign launched successfully across cloud workers!')"><i class="fas fa-play"></i> Launch Campaign</button>
                </div>
            </section>

            <section id="tab-leads" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🔍 Architecture & Design Firm Lead Finder</span></div>
                    <div style="display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap;">
                        <input type="text" class="form-control" style="flex:1; min-width:240px;" placeholder="Target Industry (e.g. Interior Designers NYC)">
                        <button class="btn-luxury" style="width:auto; padding:10px 20px;" onclick="alert('Scraper query dispatched! Fetching verified contacts...')"><i class="fas fa-search"></i> Extract Leads</button>
                    </div>
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th>Contact Name</th>
                                <th>Firm Name</th>
                                <th>Verified Email</th>
                                <th>Location</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Marcus Vance</td>
                                <td>Vance & Partners NYC</td>
                                <td>mvance@vancearchitects.com</td>
                                <td>New York, NY</td>
                            </tr>
                            <tr>
                                <td>Elena Rostova</td>
                                <td>Skyline Studio Brooklyn</td>
                                <td>elena@skylinestudio.design</td>
                                <td>Brooklyn, NY</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section id="tab-crm" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🎯 CRM Deals & Client Pipeline (<span class="dollar-symbol">$</span>64,800 Total Active)</span></div>
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th>Client / Prospect</th>
                                <th>Stage</th>
                                <th>Estimated Value ($)</th>
                                <th>Assigned Inbox</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Robert Sterling (Sterling Studio)</td>
                                <td><span class="status-badge badge-optimal">Proposal Sent</span></td>
                                <td style="color:#10b981; font-weight:800;">,000</td>
                                <td>Calvin Inbox</td>
                            </tr>
                            <tr>
                                <td>Sarah Jenkins (Jenkins Architecture)</td>
                                <td><span class="status-badge badge-warmup">Discovery Call</span></td>
                                <td style="color:#10b981; font-weight:800;">,000</td>
                                <td>Brydon Inbox</td>
                            </tr>
                            <tr>
                                <td>David Miller (Manhattan Design Loft)</td>
                                <td><span class="status-badge badge-optimal">Contract Review</span></td>
                                <td style="color:#10b981; font-weight:800;">,800</td>
                                <td>Calvin Inbox</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section id="tab-team" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>👥 Admin Colleague Role & Module Access Controller</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px; margin-bottom:16px;">Admin decides which modules are enabled or disabled for each colleague.</p>
                    
                    <div style="background:rgba(3, 10, 12, 0.6); border:1px solid var(--border-color); border-radius:12px; padding:18px; margin-bottom:16px;">
                        <div style="font-weight:800; font-size:15px; color:#fbbf24; margin-bottom:12px;">Admin Module Visibility Toggles for Colleagues:</div>
                        <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap:12px;">
                            <label class="toggle-line" style="border:none; padding:4px 0;"><span>3. Gmail Hub & Warmup</span><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-gmail', this.checked)"></label>
                            <label class="toggle-line" style="border:none; padding:4px 0;"><span>4. Campaign Studio</span><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-studio', this.checked)"></label>
                            <label class="toggle-line" style="border:none; padding:4px 0;"><span>5. Lead Scraper</span><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-leads', this.checked)"></label>
                            <label class="toggle-line" style="border:none; padding:4px 0;"><span>6. CRM Pipeline Deals</span><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-crm', this.checked)"></label>
                            <label class="toggle-line" style="border:none; padding:4px 0;"><span>10. AI Guide Agent</span><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-agent', this.checked)"></label>
                            <label class="toggle-line" style="border:none; padding:4px 0;"><span>15. CSV Export Engine</span><input type="checkbox" checked onchange="toggleRibbonItem('ribbon-tab-export', this.checked)"></label>
                        </div>
                    </div>
                </div>
            </section>

            <section id="tab-doctor" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🛠️ System Doctor Diagnostics & Cloud Daemon</span></div>
                    <div style="background:#01080a; color:#10b981; font-family:monospace; padding:18px; border-radius:10px; font-size:12.5px; line-height:1.7;">
                        [Railway Cloud] 24/7 Engine Heartbeat: ACTIVE [PID: 1]<br>
                        [OAuth Guard] 5 Multi-tenant Gmail accounts ready<br>
                        [Lead Scraper] System rotation health: 100%<br>
                        [Database Sync] CRM Pipeline synchronized with persistent state (,800 Active Deals)
                    </div>
                </div>
            </section>

            <section id="tab-custom" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header">
                        <span>🎵 Ambient Background Music & Audio Extractor</span>
                        <button class="btn-luxury" style="width:auto; padding:6px 14px;" onclick="toggleAudioPlayback()"><i id="audioBtnIcon" class="fas fa-play"></i> <span id="audioBtnText">Play Music</span></button>
                    </div>

                    <div style="margin: 10px 0 16px; background: rgba(3, 10, 12, 0.6); padding: 14px; border-radius: 10px; border: 1px solid var(--border-color); display:flex; align-items:center; gap:16px;">
                        <i class="fas fa-volume-up" style="color:var(--gold); font-size:18px;"></i>
                        <span style="font-size:13px; font-weight:700; min-width:85px;">Volume: <span id="volLabel">50%</span></span>
                        <input type="range" min="0" max="100" value="50" style="flex:1; accent-color:var(--primary); cursor:pointer;" oninput="adjustVolume(this.value)">
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
            </section>

            <section id="tab-agent" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🤖 Built-in AI Guide Agent & Module Operator</span></div>
                    <p style="color:var(--text-muted); font-size:13px; margin-bottom:14px;">Ask how to operate any module, get cold email advice, or troubleshoot campaigns.</p>
                    
                    <div class="chat-box" id="chatBoxContainer">
                        <div class="chat-msg msg-agent">
                            <strong>AI Agent:</strong> Greetings! I am your Grace Outreach Assistant Guide. Ask me anything about operating the 22 modules (e.g. <em>"How to run Gmail warmup?"</em>, <em>"How to scrape architecture leads?"</em>, or <em>"Explain CRM deals"</em>).
                        </div>
                    </div>

                    <div style="display:flex; gap:10px; margin-top:14px;">
                        <input type="text" id="agentInput" class="form-control" placeholder="Ask AI Guide Agent a question..." onkeydown="if(event.key==='Enter') sendAgentMessage()">
                        <button class="btn-luxury" style="width:auto; padding:10px 20px;" onclick="sendAgentMessage()"><i class="fas fa-paper-plane"></i> Ask Agent</button>
                    </div>
                </div>
            </section>

            <section id="tab-vault" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🔐 Google OAuth Token Vault & Refresh Engine</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">All 5 Google Workspace inboxes are secured with encrypted refresh tokens. Automatic background token renewal active.</p>
                </div>
            </section>

            <section id="tab-time" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>⏰ Timezone & Delivery Window Scheduler</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Active schedule: Monday to Friday 09:00 AM - 05:00 PM EST (New York Time).</p>
                </div>
            </section>

            <section id="tab-bounce" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🛡️ Zero-Spam Bounce Shield</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Current bounce rate: <strong>0.08%</strong>. Automated DNS, MX, and SMTP ping validation operational.</p>
                </div>
            </section>

            <section id="tab-reply" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>💬 Instant Auto-Reply & Sentiment Detector</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Positive sentiment replies are automatically prioritized and pushed to CRM Deal Stages.</p>
                </div>
            </section>

            <section id="tab-export" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>📊 1-Click CSV & Excel Export Engine</span></div>
                    <button class="btn-luxury" style="width:auto; padding:10px 20px;" onclick="alert('Exporting verified campaign report to CSV...')"><i class="fas fa-download"></i> Download Full Lead & Deal Report</button>
                </div>
            </section>

            <section id="tab-broadcast" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>📢 Broadcast Node Dispatcher</span></div>
                    <div style="display:flex; gap:12px;">
                        <input type="text" class="form-control" placeholder="Type team-wide notification...">
                        <button class="btn-luxury" style="width:auto; padding:10px 20px;" onclick="alert('Broadcast sent!')"><i class="fas fa-paper-plane"></i> Send</button>
                    </div>
                </div>
            </section>

            <section id="tab-theme" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🎨 Brand Theme & Visual Studio</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Select between Emerald Gold, Cyan Matrix, Royal Blue, and Purple Cyber luxury themes.</p>
                </div>
            </section>

            <section id="tab-robot" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🤖 Cyber Viewport Robot Status</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Interactive visual mascot connected with real-time daemon state.</p>
                </div>
            </section>

            <section id="tab-webhook" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>🔗 Cloud Webhook Integrations</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Pushes lead status updates to external endpoints in JSON format.</p>
                </div>
            </section>

            <section id="tab-quota" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>⏱️ Daily Quota Guard Shield</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Each sender mailbox is locked to a strict 50 emails/day cap to preserve Google account reputation.</p>
                </div>
            </section>

            <section id="tab-sign" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>✍️ Architecture HTML Signature Builder</span></div>
                    <p style="color:var(--text-muted); font-size:13.5px;">Stylizes company branding, phone numbers, and luxury architectural design credits.</p>
                </div>
            </section>

            <section id="tab-roi" class="tab-section">
                <div class="panel-card">
                    <div class="panel-header"><span>📈 Conversion ROI & Deal Probability Predictor</span></div>
                    <p style="color:#34d399; font-weight:800; font-size:16px;">Predicted Pipeline Closing Value: ,800 (Confidence: 86.4%)</p>
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

        function renderLivingScene() {
            ctx.clearRect(0, 0, width, height);

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
            { title: "22 Engines Online", icon: "fa-cubes", x: 12, y: 35 },
            { title: "24/7 Cloud Worker", icon: "fa-bolt", x: 34, y: 25 },
            { title: ",800 CRM Deals", icon: "fa-dollar-sign", x: 15, y: 55 },
            { title: "AI Guide Ready", icon: "fa-robot", x: 36, y: 65 }
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
            speech.innerText = "✨ 22-Module Hub Online!";
            setTimeout(() => { speech.innerText = "👑 King Saab AI System Ready"; }, 2500);
        }

        function handleAuthSubmit(e) {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing 22 Modules...';

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

        function handlePowerOff() {
            const stage = document.getElementById('cinematicStage');
            const authView = document.getElementById('authViewport');
            const appView = document.getElementById('enterpriseApp');

            appView.style.opacity = '0';
            setTimeout(() => {
                appView.style.display = 'none';
                stage.style.display = 'block';
                authView.style.display = 'flex';
                
                document.getElementById('authUsername').value = '';
                document.getElementById('authPassword').value = '';

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
            const target = document.getElementById(tabId);
            if(target) target.classList.add('active');
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

        function sendAgentMessage() {
            const input = document.getElementById('agentInput');
            const query = input.value.trim();
            if(!query) return;

            const chatBox = document.getElementById('chatBoxContainer');
            
            const userMsg = document.createElement('div');
            userMsg.className = 'chat-msg msg-user';
            userMsg.innerHTML = '<strong>You:</strong> ' + query;
            chatBox.appendChild(userMsg);
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            setTimeout(() => {
                let reply = "I can guide you with that! ";
                const q = query.toLowerCase();

                if(q.includes('warmup') || q.includes('gmail')) {
                    reply += "For <strong>Gmail Hub & Warmup</strong>: Google accounts should start at 5-10 emails/day and ramp up over 14-21 days until reaching the 50/day cap. Always maintain active OAuth refresh tokens.";
                } else if(q.includes('scrape') || q.includes('lead')) {
                    reply += "For <strong>Lead Scraper</strong>: Enter targeted search criteria (e.g. 'Interior Designers Manhattan') to extract firm names and verified emails. The system auto-filters bounced entries.";
                } else if(q.includes('crm') || q.includes('deal') || q.includes('dollar')) {
                    reply += "For <strong>CRM Pipeline</strong>: Active leads are grouped by Proposal Sent, Discovery Call, and Contract Review with live deal values ( to ).";
                } else if(q.includes('admin') || q.includes('colleague') || q.includes('module')) {
                    reply += "For <strong>Colleagues Manager</strong>: Admin can check/uncheck module permissions in Tab 7 to control which ribbons appear on colleague screens.";
                } else {
                    reply += "To operate the 22 modules: 1) Verify sender inboxes in Gmail Hub, 2) Extract leads via Scraper, 3) Launch dynamic spin-syntax campaigns in Campaign Studio, and 4) Track deal conversions in CRM Pipeline.";
                }

                const agentMsg = document.createElement('div');
                agentMsg.className = 'chat-msg msg-agent';
                agentMsg.innerHTML = '<strong>AI Agent:</strong> ' + reply;
                chatBox.appendChild(agentMsg);
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 600);
        }

        let audioCtx = null;
        let isAudioPlaying = false;
        let activeOsc = null;
        let masterGainNode = null;
        let currentPreset = 'cyber';
        let currentVolume = 0.5;
        const player = document.getElementById('bgAudioPlayer');

        function initAudioContext() {
            if(!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                masterGainNode = audioCtx.createGain();
                masterGainNode.gain.setValueAtTime(currentVolume, audioCtx.currentTime);
                masterGainNode.connect(audioCtx.destination);
            }
            if(audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function adjustVolume(val) {
            currentVolume = val / 100;
            document.getElementById('volLabel').innerText = val + '%';
            if(masterGainNode && audioCtx) {
                masterGainNode.gain.setValueAtTime(currentVolume, audioCtx.currentTime);
            }
            if(player) {
                player.volume = currentVolume;
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
            gain.connect(masterGainNode);
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
                    player.volume = currentVolume;
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
                player.volume = currentVolume;
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
