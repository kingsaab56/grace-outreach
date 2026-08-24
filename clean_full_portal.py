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
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#e8ede9"/></linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#fef08a"/><stop offset="50%" stop-color="#d97706"/><stop offset="100%" stop-color="#b45309"/></linearGradient>
    <linearGradient id="emerald" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#065f46"/><stop offset="50%" stop-color="#047857"/><stop offset="100%" stop-color="#022c22"/></linearGradient>
  </defs>
  <rect width="512" height="512" rx="100" fill="url(#bg)" stroke="#047857" stroke-width="12"/>
  <rect x="20" y="20" width="472" height="472" rx="85" fill="none" stroke="url(#gold)" stroke-width="6"/>
  <path d="M190 280 L190 180 L230 140 L230 280 Z" fill="url(#emerald)"/>
  <path d="M245 280 L245 100 L285 70 L285 280 Z" fill="url(#emerald)"/>
  <path d="M270 70 L285 70 L285 100 L270 100 Z" fill="url(#gold)"/>
  <path d="M300 130 L350 190 L350 280 L320 280 L320 230 L300 230 Z" fill="url(#gold)"/>
  <text x="256" y="350" font-family="Arial, sans-serif" font-weight="900" font-size="44" fill="#022c22" text-anchor="middle" letter-spacing="8">GRACE</text>
  <text x="256" y="390" font-family="Arial, sans-serif" font-weight="700" font-size="22" fill="#047857" text-anchor="middle" letter-spacing="10">OUTREACH</text>
  <line x1="120" y1="415" x2="392" y2="415" stroke="url(#gold)" stroke-width="3"/>
  <text x="256" y="445" font-family="Georgia, serif" font-style="italic" font-size="19" fill="#78350f" text-anchor="middle">Developed by King Saab</text>
</svg>"""

FULL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Outreach Assistant | Cloud Control Center</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #064e3b; color: #1f2937; min-height: 100vh; display: flex; flex-direction: column; }
        
        .auth-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background: linear-gradient(135deg, #022c22 0%, #064e3b 100%); }
        .auth-card { background: #ffffff; border-radius: 16px; padding: 36px 30px; width: 100%; max-width: 440px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4); text-align: center; }
        .logo-box { width: 85px; height: 85px; margin: 0 auto 12px; }
        .logo-box svg { width: 100%; height: 100%; }
        .auth-title { font-size: 22px; font-weight: 800; color: #022c22; letter-spacing: 0.5px; }
        .auth-sub { font-size: 13px; color: #b45309; font-weight: 700; margin-bottom: 20px; }
        
        .input-group { text-align: left; margin-bottom: 14px; }
        .input-group label { display: block; font-size: 11px; font-weight: 800; color: #374151; margin-bottom: 5px; text-transform: uppercase; }
        .input-group input, .input-group select, .input-group textarea { width: 100%; padding: 11px 13px; border: 1.5px solid #d1d5db; border-radius: 8px; font-size: 14px; outline: none; }
        .input-group input:focus { border-color: #047857; box-shadow: 0 0 0 3px rgba(4, 120, 87, 0.2); }
        
        .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 14px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        .btn-primary { background: linear-gradient(135deg, #047857 0%, #065f46 100%); color: #ffffff; }
        .btn-primary:hover { background: #022c22; }
        
        .app-container { display: none; min-height: 100vh; flex-direction: column; background: #f3f4f6; }
        .navbar { background: #022c22; color: #ffffff; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #d97706; }
        .nav-brand { display: flex; align-items: center; gap: 12px; }
        .nav-brand svg { width: 42px; height: 42px; }
        .nav-title { font-size: 18px; font-weight: 800; color: #ffffff; letter-spacing: 1px; }
        .nav-sub { font-size: 11px; color: #fbbf24; font-weight: 600; }
        
        .nav-tabs { display: flex; gap: 8px; }
        .tab-btn { background: transparent; border: none; color: #d1fae5; padding: 8px 16px; font-size: 13px; font-weight: 700; cursor: pointer; border-radius: 6px; }
        .tab-btn.active, .tab-btn:hover { background: #047857; color: #ffffff; }
        
        .main-content { padding: 24px; max-width: 1200px; margin: 0 auto; width: 100%; flex: 1; }
        .tab-pane { display: none; }
        .tab-pane.active { display: block; }
        
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border-left: 5px solid #047857; }
        .stat-val { font-size: 26px; font-weight: 800; color: #022c22; }
        .stat-lbl { font-size: 12px; color: #6b7280; font-weight: 700; text-transform: uppercase; }
        
        .content-box { background: #ffffff; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 24px; }
        .section-header { font-size: 16px; font-weight: 800; color: #022c22; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
        .badge { padding: 4px 8px; font-size: 11px; font-weight: 700; border-radius: 4px; }
        .badge-live { background: #d1fae5; color: #065f46; }
    </style>
</head>
<body>

    <div id="authScreen" class="auth-container">
        <div class="auth-card">
            <div class="logo-box">__LOGO_PLACEHOLDER__</div>
            <div class="auth-title">GRACE OUTREACH</div>
            <div class="auth-sub">Developed by King Saab</div>

            <div id="loginForm">
                <div class="input-group">
                    <label>Username / Colleague ID</label>
                    <input type="text" id="loginUser" placeholder="kingsaab56" value="kingsaab56">
                </div>
                <div class="input-group">
                    <label>Password</label>
                    <input type="password" id="loginPass" placeholder="••••••••" value="admin56">
                </div>
                <button class="btn btn-primary" onclick="login()">Sign In to Dashboard</button>
                <p style="margin-top: 14px; font-size: 12px; color: #4b5563;">
                    New Colleague? <a href="#" onclick="toggleAuth(true)" style="color: #047857; font-weight: 700;">Register Account</a>
                </p>
            </div>

            <div id="registerForm" style="display: none;">
                <div class="input-group">
                    <label>Full Name</label>
                    <input type="text" id="regName" placeholder="e.g. Ali Ahmed">
                </div>
                <div class="input-group">
                    <label>Email</label>
                    <input type="email" id="regEmail" placeholder="name@gracearchitectures.com">
                </div>
                <div class="input-group">
                    <label>Secret Passcode</label>
                    <input type="password" id="regCode" placeholder="Enter 'grace'">
                </div>
                <button class="btn btn-primary" onclick="register()">Create Account</button>
                <p style="margin-top: 14px; font-size: 12px; color: #4b5563;">
                    Already have an account? <a href="#" onclick="toggleAuth(false)" style="color: #047857; font-weight: 700;">Sign In</a>
                </p>
            </div>
        </div>
    </div>

    <div id="appScreen" class="app-container">
        <div class="navbar">
            <div class="nav-brand">
                __LOGO_PLACEHOLDER__
                <div>
                    <div class="nav-title">GRACE OUTREACH ASSISTANT</div>
                    <div class="nav-sub">Cloud Hub 24/7 Active • Developed by King Saab</div>
                </div>
            </div>
            <div class="nav-tabs">
                <button class="tab-btn active" onclick="showTab('tab-dash', this)"><i class="fas fa-chart-line"></i> Dashboard</button>
                <button class="tab-btn" onclick="showTab('tab-studio', this)"><i class="fas fa-paper-plane"></i> Campaign Studio</button>
                <button class="tab-btn" onclick="showTab('tab-crm', this)"><i class="fas fa-funnel-dollar"></i> CRM Pipeline</button>
                <button class="tab-btn" onclick="showTab('tab-team', this)"><i class="fas fa-users"></i> Colleagues</button>
                <button class="tab-btn" onclick="logout()" style="background: #991b1b;"><i class="fas fa-sign-out-alt"></i> Logout</button>
            </div>
        </div>

        <div class="main-content">
            <div id="tab-dash" class="tab-pane active">
                <div class="grid-stats">
                    <div class="stat-card">
                        <div class="stat-lbl">Active Outreach Pipeline</div>
                        <div class="stat-val">2,480</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Emails Sent (This Week)</div>
                        <div class="stat-val">650</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Positive Reply Rate</div>
                        <div class="stat-val">18.4%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Deals in Pipeline</div>
                        <div class="stat-val">$48,500</div>
                    </div>
                </div>

                <div class="content-box">
                    <div class="section-header">
                        <span>⚡ Live Outreach Engine Status</span>
                        <span class="badge badge-live">● System 24/7 Online</span>
                    </div>
                    <p style="color: #4b5563; font-size: 14px; line-height: 1.6;">
                        Cloud container is actively monitoring scheduled campaigns, handling automated follow-ups, and managing Colleague activities in real time.
                    </p>
                </div>
            </div>

            <div id="tab-studio" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🚀 Launch New Campaign</span></div>
                    <div class="input-group">
                        <label>Campaign Name</label>
                        <input type="text" placeholder="e.g. Q3 Architecture Firms Outreach">
                    </div>
                    <div class="input-group">
                        <label>Target Audience / Category</label>
                        <select>
                            <option>Commercial Real Estate Developers</option>
                            <option>Residential Architects (USA / UK)</option>
                            <option>Interior Design Studios</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Email Pitch / Template</label>
                        <textarea rows="4" placeholder="Hello, we noticed your recent architectural projects..."></textarea>
                    </div>
                    <button class="btn btn-primary" onclick="alert('✔ Campaign Queued & Ready to Run!')">Queue & Launch Campaign</button>
                </div>
            </div>

            <div id="tab-crm" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>🎯 CRM Deal Pipeline</span></div>
                    <p style="color: #6b7280; font-size: 13px; margin-bottom: 12px;">Track your lead conversions and stages.</p>
                    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
                        <tr style="background: #f9fafb; border-bottom: 2px solid #e5e7eb;">
                            <th style="padding: 10px;">Contact</th>
                            <th style="padding: 10px;">Company</th>
                            <th style="padding: 10px;">Stage</th>
                            <th style="padding: 10px;">Value</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 10px; font-weight: 700;">John Carter</td>
                            <td style="padding: 10px;">Carter Architecture NYC</td>
                            <td style="padding: 10px;"><span class="badge badge-live">Proposal Sent</span></td>
                            <td style="padding: 10px; font-weight: 700; color: #047857;">$12,000</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 10px; font-weight: 700;">Sarah Jenkins</td>
                            <td style="padding: 10px;">Apex Urban Living</td>
                            <td style="padding: 10px;"><span class="badge badge-live">Pitch Opened</span></td>
                            <td style="padding: 10px; font-weight: 700; color: #047857;">$8,500</td>
                        </tr>
                    </table>
                </div>
            </div>

            <div id="tab-team" class="tab-pane">
                <div class="content-box">
                    <div class="section-header"><span>👥 Team & Colleague Activity</span></div>
                    <p style="color: #6b7280; font-size: 13px; margin-bottom: 12px;">Colleagues registered under company passcode 'grace'.</p>
                    <div style="background: #f9fafb; padding: 14px; border-radius: 8px; border-left: 4px solid #047857;">
                        <div style="font-weight: 800; color: #022c22;">Admin: KING SAAB (Active)</div>
                        <div style="font-size: 12px; color: #6b7280;">calvin.gracearchitectures.llc@gmail.com</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
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
                alert('Please enter valid credentials.');
            }
        }

        function register() {
            var code = document.getElementById('regCode').value;
            if(code.toLowerCase() === 'grace') {
                alert('✔ Account successfully registered! You can now login.');
                toggleAuth(false);
            } else {
                alert('❌ Invalid Secret Passcode! Contact King Saab for access.');
            }
        }

        function logout() {
            document.getElementById('appScreen').style.display = 'none';
            document.getElementById('authScreen').style.display = 'flex';
        }

        function showTab(tabId, el) {
            var panes = document.getElementsByClassName('tab-pane');
            for(var i=0; i<panes.length; i++) panes[i].classList.remove('active');
            
            var btns = document.getElementsByClassName('tab-btn');
            for(var j=0; j<btns.length; j++) btns[j].classList.remove('active');
            
            document.getElementById(tabId).classList.add('active');
            el.classList.add('active');
        }
    </script>
</body>
</html>""".replace("__LOGO_PLACEHOLDER__", SVG_LOGO)

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
        self.wfile.write(FULL_HTML.encode('utf-8'))

    def do_POST(self):
        self.do_GET()

def run():
    server = HTTPServer((HOST, PORT), GraceRequestHandler)
    print(f"✔ Grace Cloud Server listening on http://{HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
''')

print("✔ Cleaned web_portal.py successfully created!")
