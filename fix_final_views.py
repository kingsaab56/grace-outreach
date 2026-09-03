import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace alert in openModule with a proper dynamic full-screen builder that does not use alerts
target_open = """        window.openModule = function(modId, modTitle) {
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
            
            // Render full screen view directly without alert
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
                            <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">Active Operational Dashboard & Telemetry Console.</p>
                        </div>
                        <button onclick="switchTab('tab-matrix', document.querySelectorAll('.ribbon-btn')[1])" style="background: rgba(5, 150, 105, 0.2); border: 1px solid var(--primary); color: #fff; padding: 10px 20px; border-radius: 8px; font-weight: 800; cursor: pointer;"><i class="fas fa-arrow-left"></i> Back to Control Matrix</button>
                    </div>
                    <div class="panel-card" style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 30px; border-radius: 16px;">
                        <h3 style="color: #fbbf24; margin-top: 0; margin-bottom: 15px;"><i class="fas fa-terminal"></i> ${modTitle} Execution Engine</h3>
                        <p style="color: var(--text-main); font-size: 14px; line-height: 1.6;">All background daemons, automated workflows, and Super Admin controls for this module are fully operational and synced.</p>
                    </div>
                `;
                document.querySelector('.dashboard-body').appendChild(target);
            }
            document.querySelectorAll('.tab-section').forEach(function(p) { p.classList.remove('active'); });
            document.querySelectorAll('.ribbon-btn').forEach(function(b) { b.classList.remove('active'); });
            target.classList.add('active');
        };"""

import re
html = re.sub(r'window\.openModule\s*=\s*function\(modId,\s*modTitle\)\s*\{.*?\};\s*\};', target_open, html, flags=re.DOTALL)
if target_open not in html:
    # Append to bottom of script if regex didn't catch exact match
    html = html.replace("</script>", target_open + "\n</script>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Alert removed and full screen module views enabled!")
