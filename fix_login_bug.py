import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix the executeLogin function explicitly in index.html
old_login = """        window.executeLogin = function() {
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
        };"""

# Ensure executeLogin is bulletproof and properly defined
new_login = """        window.executeLogin = function() {
            var authView = document.getElementById('authViewport');
            var stage = document.getElementById('cinematicStage');
            var app = document.getElementById('enterpriseApp');
            var uInput = document.getElementById('authUsername');
            var u = (uInput && uInput.value ? uInput.value : 'kingsaab56').trim();

            if(authView) authView.style.display = 'none';
            if(stage) stage.style.display = 'none';
            if(app) app.style.display = 'flex';

            if(typeof colleagues !== 'undefined') {
                var found = colleagues.find(function(c) {
                    return c.id.toLowerCase() === u.toLowerCase() || c.name.toLowerCase() === u.toLowerCase();
                });
                var selector = document.getElementById('userRoleSelector');
                if(found) {
                    if(selector) selector.value = found.key;
                    if(typeof switchColleagueView === 'function') switchColleagueView(found.key);
                } else {
                    if(selector) selector.value = 'admin';
                    if(typeof switchColleagueView === 'function') switchColleagueView('admin');
                }
            }
        };"""

if old_login in html:
    html = html.replace(old_login, new_login)
else:
    # Append or force-fix executeLogin inside script
    html = html.replace("window.executeLogin", "window.executeLogin_old")
    html = html.replace("</script>", new_login + "\n</script>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Login execution function repaired!")
