"""
Enhanced OAuth Controller with Persistent Chrome User Data Directory
"""

import os
import sys
import json
import shutil
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import Flow
from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error, highlight

VAULT_DIR = os.path.abspath("./tokens_vault_backup")
ACCOUNTS_DIR = os.path.abspath("./accounts")
CRED_FILE = os.path.abspath("./credentials.json")

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(ACCOUNTS_DIR, exist_ok=True)

AUTH_CODE_RECEIVED = None
SERVER_INSTANCE = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global AUTH_CODE_RECEIVED
        query = urlparse(self.path).query
        params = parse_qs(query)
        if "code" in params:
            AUTH_CODE_RECEIVED = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authentication Complete!</h1><p>You can close this tab and return to the console.</p>")
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authentication Failed</h1><p>No code received.</p>")

    def log_message(self, format, *args):
        pass


def backup_token(email, token_file_path):
    if token_file_path and os.path.exists(token_file_path):
        sanitized = email.replace("@", "_at_").replace(".", "_")
        dest = os.path.join(VAULT_DIR, f"vault_token_{sanitized}.json")
        shutil.copy2(token_file_path, dest)
        return dest
    return None


def _find_chrome_path():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return "chrome"


def _launch_chrome_with_profile(profile_name, url):
    chrome_exe = _find_chrome_path()
    user_data_dir = os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data")
    try:
        cmd = [
            chrome_exe,
            f'--user-data-dir={user_data_dir}',
            f'--profile-directory={profile_name}',
            url
        ]
        subprocess.Popen(cmd)
        return True
    except Exception:
        import webbrowser
        webbrowser.open(url)
        return False


def get_pending_oauth_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT gmail, 
                   GROUP_CONCAT(DISTINCT profile_name) as profiles, 
                   MAX(oauth_connected) as is_conn,
                   MAX(token_file) as token_path
            FROM gmail_accounts
            GROUP BY gmail
            ORDER BY gmail ASC
            """
        )
        all_acc = cursor.fetchall()
        
        pending = []
        connected = []
        
        for acc in all_acc:
            email, profs, is_conn, tok_path = acc
            has_tok = tok_path and os.path.exists(tok_path)
            
            sanitized = email.replace("@", "_at_").replace(".", "_")
            vault_tok = os.path.join(VAULT_DIR, f"vault_token_{sanitized}.json")
            if not has_tok and os.path.exists(vault_tok):
                has_tok = True
                tok_path = vault_tok
                cursor.execute("UPDATE gmail_accounts SET oauth_connected = 1, token_file = ? WHERE gmail = ?", (vault_tok, email))
                conn.commit()

            if is_conn == 1 and has_tok:
                connected.append({"email": email, "profiles": profs, "token": tok_path})
            else:
                pending.append({"email": email, "profiles": profs})
                
        return pending, connected
    finally:
        conn.close()


def connect_oauth_flow_for_account(email, profile_name):
    global AUTH_CODE_RECEIVED, SERVER_INSTANCE
    AUTH_CODE_RECEIVED = None

    if not os.path.exists(CRED_FILE):
        print(error("credentials.json not found in project directory!"))
        return False

    first_profile = profile_name.split(",")[0].strip() if "," in profile_name else profile_name
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    port = 50948
    redirect_uri = f"http://localhost:{port}/"

    flow = Flow.from_client_secrets_file(
        CRED_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    auth_url, _ = flow.authorization_url(
        prompt='consent',
        access_type='offline',
        login_hint=email
    )

    print(f"\n{Colors.CYAN}➔ Target Email   :{Colors.RESET} {Colors.BOLD}{email}{Colors.RESET}")
    print(f"{Colors.CYAN}➔ Linked Profile :{Colors.RESET} {first_profile}")
    print(f"{Colors.GREEN}➔ Launching Chrome with Persistent User Data...{Colors.RESET}")
    print(f"{Colors.YELLOW}ℹ Press Ctrl + C anytime in console if you wish to cancel and return.{Colors.RESET}\n")

    _launch_chrome_with_profile(first_profile, auth_url)

    try:
        SERVER_INSTANCE = HTTPServer(("localhost", port), OAuthCallbackHandler)
    except Exception:
        SERVER_INSTANCE = HTTPServer(("localhost", 0), OAuthCallbackHandler)
        port = SERVER_INSTANCE.server_address[1]
        flow.redirect_uri = f"http://localhost:{port}/"

    server_thread = threading.Thread(target=SERVER_INSTANCE.serve_forever, daemon=True)
    server_thread.start()

    try:
        max_wait = 90
        start_time = time.time()
        while AUTH_CODE_RECEIVED is None:
            if time.time() - start_time > max_wait:
                print(warning("Authorization timed out (90s)."))
                break
            time.sleep(0.3)
    except KeyboardInterrupt:
        print(f"\n{warning('Cancelled by user! Returning cleanly...')}")
        SERVER_INSTANCE.shutdown()
        return False

    SERVER_INSTANCE.shutdown()

    if not AUTH_CODE_RECEIVED:
        print(error("Failed to receive authentication code."))
        return False

    try:
        flow.fetch_token(code=AUTH_CODE_RECEIVED)
        creds = flow.credentials

        sanitized = email.replace("@", "_at_").replace(".", "_")
        prof_folder = os.path.join(ACCOUNTS_DIR, first_profile)
        os.makedirs(prof_folder, exist_ok=True)
        token_path = os.path.join(prof_folder, f"token_{sanitized}.json")

        with open(token_path, 'w') as tf:
            tf.write(creds.to_json())

        backup_token(email, token_path)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE gmail_accounts
            SET oauth_connected = 1, token_file = ?, updated_at = CURRENT_TIMESTAMP
            WHERE gmail = ?
            """,
            (token_path, email)
        )
        conn.commit()
        conn.close()

        print(f"\n{success(f'Account {email} CONNECTED & LOCKED IN VAULT successfully!')}\n")
        return True
    except Exception as e:
        print(error(f"Error saving token: {e}"))
        return False


def oauth_vault_manager_menu():
    while True:
        pending, connected = get_pending_oauth_accounts()
        
        print_banner("OAUTH DEDUPLICATED VAULT HUB", "🔑")
        print(f" {Colors.GREEN}✔ Connected Unique Accounts :{Colors.RESET} {len(connected)}")
        print(f" {Colors.YELLOW}⚠ Pending Authentication   :{Colors.RESET} {len(pending)}\n")

        if pending:
            print(f"{Colors.BOLD}{'#':<4} │ {'Pending Email (Single Auth)':<40} │ {'Assigned Profile'}{Colors.RESET}")
            print(f"{Colors.CYAN}{'─' * 75}{Colors.RESET}")
            for idx, acc in enumerate(pending, start=1):
                print(f"{idx:<4} │ {acc['email']:<40} │ {acc['profiles']}")
            print(f"{Colors.CYAN}{'─' * 75}{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}🎉 All accounts are fully CONNECTED and SECURED in Vault!{Colors.RESET}\n")

        print(f"\n {Colors.GREEN}[1-{len(pending)}]{Colors.RESET} Select an account number to Connect (1-by-1)")
        print(f" {Colors.CYAN}[V]{Colors.RESET}     View Connected Accounts Details")
        print(f" {Colors.RED}[0]{Colors.RESET}     Back to Campaign Menu")
        print(f"{Colors.CYAN}{'═' * 75}{Colors.RESET}")

        try:
            choice = input(f"{Colors.YELLOW}Select Option: {Colors.RESET}").strip().upper()
        except KeyboardInterrupt:
            break

        if choice == "0":
            break
        elif choice == "V":
            print_banner("CONNECTED VAULT ACCOUNTS", "🔒")
            for idx, acc in enumerate(connected, start=1):
                print(f" {idx:<3} │ {acc['email']:<40} │ {acc['profiles']:<20} │ {Colors.GREEN}LOCKED IN VAULT ✔{Colors.RESET}")
            print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}")
            input("\nPress Enter to continue...")
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(pending):
                target = pending[idx - 1]
                connect_oauth_flow_for_account(target["email"], target["profiles"])
            else:
                print(error("Invalid Account Number."))
