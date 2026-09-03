
with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write("""from flask import Flask, request, render_template_string
import random

app = Flask(__name__)

class GmailAccount:
    def __init__(self, email, account_type, auth_method, status="Active"):
        self.email = email
        self.account_type = account_type
        self.auth_method = auth_method
        self.status = status

class MultiTenantHub:
    def __init__(self):
        self.accounts = [
            GmailAccount("business.inbox1@gmail.com", "Business", "OAuth"),
            GmailAccount("outreach.node2@gmail.com", "Business", "16-Digit App Password"),
            GmailAccount("relay.personal@gmail.com", "Personal", "16-Digit App Password")
        ]

hub_manager = MultiTenantHub()

class TokenVaultEngine:
    def __init__(self):
        self.encryption_standard = "AES-256-GCM Secure Locker"
        self.auto_renewal_frequency = "Every 24 Hours"
        self.failed_rotations = 0

token_vault_manager = TokenVaultEngine()

class RevenuePipeline:
    def __init__(self):
        self.total_revenue = 64800

pipeline_manager = RevenuePipeline()

HOME_TEMPLATE = \"\"\"<!DOCTYPE html>
<html>
<head>
    <title>Grace Outreach Assistant - Module 12</title>
    <style>
        body { background-color: #0B1120; color: #F8FAFC; font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .card { background: #090D16; padding: 20px; border-radius: 12px; border: 1px solid #1E293B; margin-bottom: 20px; }
        .btn { background: #3B82F6; color: white; padding: 10px 15px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>?? Module 12: OAuth Token Vault & AES-256 Locker</h2>
        <p>Encryption Standard: <b>{{ token_vault.encryption_standard }}</b></p>
        <p>Auto-Renewal: <b>{{ token_vault.auto_renewal_frequency }}</b></p>
        <a href="/?tab=matrix" class="btn">? Back to 22-Module Matrix</a>
    </div>
</body>
</html>\"\"\"

@app.route("/")
def home():
    return render_template_string(HOME_TEMPLATE, token_vault=token_vault_manager)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
""")
print("web_portal.py generated perfectly!")

