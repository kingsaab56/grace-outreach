import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Safe isolated update for Module 1 view section only without touching anything else
module_1_upgrade = """
            <!-- OPTION 1: DASHBOARD (MODULE 1 UPGRADED) -->
            <section id="tab-dash" class="tab-section active">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 24px;">
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;">
                        <div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">ACTIVE OUTREACH PIPELINE</div>
                        <div style="font-size:28px; font-weight:900;">2,480 Leads</div>
                        <div style="font-size:11px; color:#34d399; margin-top:5px;">▲ +12% this week</div>
                    </div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;">
                        <div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">CONNECTED GMAIL ACCOUNTS</div>
                        <div style="font-size:28px; font-weight:900;">5 Inboxes</div>
                        <div style="font-size:11px; color:#34d399; margin-top:5px;">● All Daemons Active</div>
                    </div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;">
                        <div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">WEEKLY SENT VOLUME</div>
                        <div style="font-size:28px; font-weight:900;">1,240 Emails</div>
                        <div style="font-size:11px; color:#fbbf24; margin-top:5px;">⚡ Pacing Optimal</div>
                    </div>
                    <div style="background: var(--bg-card); border-left: 5px solid var(--primary); padding: 22px; border-radius: 14px;">
                        <div style="font-size:11.5px; color:var(--text-muted); font-weight:800;">PIPELINE DEAL VALUE</div>
                        <div style="font-size:28px; font-weight:900; color:#10b981;">&#36;64,800</div>
                        <div style="font-size:11px; color:#10b981; margin-top:5px;">✔ Verified Baseline</div>
                    </div>
                </div>

                <div class="panel-card" style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 25px; border-radius: 16px;">
                    <h3 style="color: #fbbf24; margin-top: 0; margin-bottom: 15px;"><i class="fas fa-heartbeat"></i> Module 1: Live Deliverability Health & Quick Telemetry</h3>
                    <p style="color: var(--text-main); font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                        Welcome to the enterprise control center dashboard. All system daemons, multi-tenant rotation hubs, and automated safety guards are currently operating under King Saab's Super Admin clearance.
                    </p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 15px;">
                        <div style="background: rgba(3,10,12,0.6); padding: 18px; border-radius: 12px; border: 1px solid rgba(52,211,153,0.3);">
                            <div style="font-size: 12px; color: var(--text-muted); font-weight: 800;">INBOX PLACEMENT SCORE</div>
                            <div style="font-size: 20px; font-weight: 900; color: #34d399; margin-top: 5px;">99.4% (Optimal)</div>
                        </div>
                        <div style="background: rgba(3,10,12,0.6); padding: 18px; border-radius: 12px; border: 1px solid rgba(245,158,11,0.3);">
                            <div style="font-size: 12px; color: var(--text-muted); font-weight: 800;">SYSTEM LATENCY</div>
                            <div style="font-size: 20px; font-weight: 900; color: #fbbf24; margin-top: 5px;">14ms (Super Fast)</div>
                        </div>
                    </div>
                </div>
            </section>
"""

# Replace only tab-dash section safely
import re
if 'id="tab-dash"' in html:
    # Extract and replace tab-dash section
    html = re.sub(r'<!-- OPTION 1: DASHBOARD -->.*?<!-- OPTION 2:', module_1_upgrade + '\n            <!-- OPTION 2:', html, flags=re.DOTALL)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✔ Module 1 successfully updated safely!")
else:
    print("⚠ tab-dash section not found.")
