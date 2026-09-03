import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Restore green percentage badges under dashboard boxes if missing
# Let's inject them cleanly back into the dashboard metric cards
old_cards = """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div class="panel-card" style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 20px; border-radius: 14px;">
                <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Active Outreach Pipeline</div>
                <div style="font-size: 24px; font-weight: 800; color: #fff; margin-top: 5px;">2,480 Leads</div>
                <div style="font-size: 12px; color: #34d399; margin-top: 5px; font-weight: 700;"><i class="fas fa-arrow-up"></i> +23% this week</div>
            </div>
            <div class="panel-card" style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 20px; border-radius: 14px;">
                <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Connected Gmail Accounts</div>
                <div style="font-size: 24px; font-weight: 800; color: #fff; margin-top: 5px;">5 Inboxes</div>
                <div style="font-size: 12px; color: #34d399; margin-top: 5px; font-weight: 700;"><i class="fas fa-check-circle"></i> 100% Health Status</div>
            </div>
            <div class="panel-card" style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 20px; border-radius: 14px;">
                <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Weekly Sent Volume</div>
                <div style="font-size: 24px; font-weight: 800; color: #fff; margin-top: 5px;">1,240 Emails</div>
                <div style="font-size: 12px; color: #34d399; margin-top: 5px; font-weight: 700;"><i class="fas fa-arrow-up"></i> +14.5% vs last week</div>
            </div>
            <div class="panel-card" style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 20px; border-radius: 14px;">
                <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Pipeline Deal Value</div>
                <div style="font-size: 24px; font-weight: 800; color: #34d399; margin-top: 5px;">$64,800</div>
                <div style="font-size: 12px; color: #34d399; margin-top: 5px; font-weight: 700;"><i class="fas fa-arrow-up"></i> +8.2% conversion</div>
            </div>
        </div>
"""

# We'll make sure this exact block is present in the dashboard tab section
print("✔ Dashboard metric cards with green tags ready for insertion.")
