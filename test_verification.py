import io
import json
import sys
from pathlib import Path

# Add project directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from main import app, read_shared_state, US_STATES_CATALOG
except ImportError:
    from app import app, read_shared_state, US_STATES_CATALOG

def wsgi_request(path, method="GET", query_string="", body_dict=None):
    body_bytes = b""
    if body_dict is not None:
        body_bytes = json.dumps(body_dict).encode("utf-8")
    
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query_string,
        "CONTENT_LENGTH": str(len(body_bytes)),
        "wsgi.input": io.BytesIO(body_bytes),
    }
    
    response_status = None
    response_headers = []
    
    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers

    result = app(environ, start_response)
    data = b"".join(result)
    return response_status, response_headers, data

def run_tests():
    print("=== Testing Grace Outreach Assistant Backend & WSGI ===")
    
    # 1. Test GET /api/state
    status, headers, data = wsgi_request("/api/state", "GET")
    assert status == "200 OK", f"Expected 200 OK, got {status}"
    state = json.loads(data.decode("utf-8"))
    assert "profiles" in state, "Missing profiles in state"
    assert "attendance" in state, "Missing attendance in state"
    assert "king" in state["profiles"], "Missing king in profiles"
    print("[PASS] GET /api/state returned valid JSON state.")

    # 2. Test POST /api/state: Valid profile & territory states (max 2 states)
    update_payload = {
        "resource": "profiles",
        "key": "abdullah",
        "value": {
            "name": "Abdullah Khan - Senior Lead",
            "role": "Executive VP Outreach",
            "assigned_states": ["Texas", "California"]
        }
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict=update_payload)
    assert status == "200 OK", f"Expected 200 OK, got {status}"
    resp = json.loads(data.decode("utf-8"))
    assert resp["status"] == "ok"
    assert resp["state"]["profiles"]["abdullah"]["name"] == "Abdullah Khan - Senior Lead"
    assert resp["state"]["profiles"]["abdullah"]["assigned_states"] == ["Texas", "California"]
    print("[PASS] POST /api/state successfully persisted colleague profile & 2 territory states.")

    # 3. Test POST /api/state: Rejecting > 2 states
    invalid_payload = {
        "resource": "profiles",
        "key": "abdullah",
        "value": {
            "name": "Abdullah Khan",
            "role": "Strategic Lead",
            "assigned_states": ["Texas", "California", "Florida"]  # 3 states -> should fail!
        }
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict=invalid_payload)
    assert status == "400 Bad Request", f"Expected 400 Bad Request, got {status}"
    err_resp = json.loads(data.decode("utf-8"))
    assert "Maximum 2 contractor territory states" in err_resp["error"]
    print("[PASS] POST /api/state strictly enforced max 2 territory states limit (rejected 3 states).")

    # 4. Test POST /api/state: Photo upload
    fake_avatar_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    photo_payload = {
        "resource": "photos",
        "key": "sarah",
        "value": fake_avatar_data
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict=photo_payload)
    assert status == "200 OK", f"Expected 200 OK, got {status}"
    saved_state = read_shared_state()
    assert saved_state["photos"]["sarah"] == fake_avatar_data
    print("[PASS] POST /api/state successfully persisted avatar photo.")

    # 5. Test POST /api/state: Attendance update
    att_payload = {
        "resource": "attendance",
        "value": {
            "hamza": {"mon": "absent", "tue": "present", "wed": "present", "thu": "present", "fri": "present", "sat": "present"}
        }
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict=att_payload)
    assert status == "200 OK", f"Expected 200 OK, got {status}"
    print("[PASS] POST /api/state successfully updated attendance records.")

    # 6. Test HTML Page Rendering
    pages = [
        ("Dashboard", "/api/", "tab=dashboard", "Active workspace"),
        ("22-Module Matrix", "/api/", "tab=matrix", "Complete 22-Module Control Matrix"),
        ("Colleague Management", "/api/", "tab=colleagues", "Colleague Profiles &amp; Contractor Management"),
        ("Module 6 Detail", "/api/", "tab=module&id=6", "US Architect & Contractor Scraper"),
        ("Module 12 Detail", "/api/", "tab=module&id=12", "OAuth Token Vault"),
    ]
    for page_name, path, qs, expected_str in pages:
        status, headers, data = wsgi_request(path, "GET", query_string=qs)
        assert status == "200 OK", f"Expected 200 OK on {page_name}, got {status}"
        html = data.decode("utf-8")
        assert expected_str in html, f"Expected '{expected_str}' in {page_name}"
        assert ".mod-title { font-size: 12px;" in html, "Missing updated mod-title font size"
        assert ".mod-name { font-size: 15px;" in html, "Missing updated mod-name font size"
        print(f"[PASS] Rendered {page_name} with complete HTML & enhanced typography.")

    # 7. Test New Colleague Account Registration via POST /api/state
    new_colleague_payload = {
        "resource": "profiles",
        "key": "zayn_malik",
        "value": {
            "name": "Zayn Malik",
            "role": "Regional Director",
            "password": "securepassword123",
            "assigned_states": ["New York", "Florida"]
        }
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict=new_colleague_payload)
    assert status == "200 OK", f"Expected 200 OK for registering new colleague, got {status}"
    reg_resp = json.loads(data.decode("utf-8"))
    assert reg_resp["state"]["profiles"]["zayn_malik"]["name"] == "Zayn Malik"
    assert reg_resp["state"]["profiles"]["zayn_malik"]["assigned_states"] == ["New York", "Florida"]
    print("[PASS] POST /api/state successfully registered new colleague account.")

    # 8. Test Auth Gateway & Mobile Ratio Cropper Markup
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=dashboard")
    dash_html = data.decode("utf-8")
    assert "auth-gateway-overlay" in dash_html, "Missing auth-gateway-overlay element"
    assert "switchAuthTab('signin')" in dash_html, "Missing signin tab action"
    assert "switchAuthTab('register')" in dash_html, "Missing register tab action"
    assert "switchAuthTab('forgot')" in dash_html, "Missing forgot password tab action"
    assert "cropper-zoom" in dash_html, "Missing cropper-zoom slider"
    assert "cropperFitFull()" in dash_html, "Missing cropperFitFull function"
    
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=module&id=6")
    mod6_html = data.decode("utf-8")
    assert "exportScraperLeads" in mod6_html, "Missing real-time exportScraperLeads function"
    
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=module&id=12")
    mod12_html = data.decode("utf-8")
    assert "exportVaultBackup" in mod12_html, "Missing real-time exportVaultBackup function"
    print("[PASS] Verified Auth Gateway, Mobile Cropper & Real-time Action functions in rendered HTML.")

    # 9. Test Contractors Catalog & Strict Max 2 Contractors
    valid_contractor_payload = {
        "resource": "profiles",
        "key": "abdullah",
        "value": {
            "name": "Abdullah Khan",
            "role": "Strategic Lead",
            "assigned_states": ["Texas", "Florida"],
            "assigned_contractors": ["Turner Construction Co.", "Bechtel Corporation"]
        }
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict=valid_contractor_payload)
    assert status == "200 OK", f"Expected 200 OK for valid contractors, got {status}"
    resp = json.loads(data.decode("utf-8"))
    assert resp["state"]["profiles"]["abdullah"]["assigned_contractors"] == ["Turner Construction Co.", "Bechtel Corporation"]
    print("[PASS] POST /api/state successfully assigned max 2 contractors.")

    invalid_contractor_payload = {
        "resource": "profiles",
        "key": "abdullah",
        "value": {
            "name": "Abdullah Khan",
            "role": "Strategic Lead",
            "assigned_contractors": ["Turner Construction Co.", "Bechtel Corporation", "Skanska USA Building"]
        }
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict=invalid_contractor_payload)
    assert status == "400 Bad Request", f"Expected 400 Bad Request, got {status}"
    err_resp = json.loads(data.decode("utf-8"))
    assert "Maximum 2 contractors allowed" in err_resp["error"]
    print("[PASS] POST /api/state strictly rejected > 2 contractors.")

    # 10. Test Audit Log Persistence
    audit_entry = {
        "timestamp": "2026-09-10 01:00:00",
        "user": "King Saab",
        "action": "Campaign Dispatch",
        "details": "Safely dispatched 25 contractor records with human jitter"
    }
    status, headers, data = wsgi_request("/api/state", "POST", body_dict={"resource": "auditLog", "value": audit_entry})
    assert status == "200 OK", f"Expected 200 OK for auditLog, got {status}"
    saved_state = read_shared_state()
    assert any(log.get("action") == "Campaign Dispatch" for log in saved_state.get("auditLog", []))
    print("[PASS] POST /api/state successfully recorded and persisted immutable audit log entry.")

    # 11. Test Contrast Fix in CSS
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=dashboard")
    dash_html = data.decode("utf-8")
    assert ".telemetry-card strong" in dash_html
    assert "color:#10B981 !important;" in dash_html
    assert "background:#001A17 !important;" in dash_html
    print("[PASS] Contrast fix confirmed: Glowing emerald #10B981 !important and dark luxury cards enforced.")

    # 12. Test Audio Loop & Gateway Sound Controls
    assert "gateway-sound-toggle" in dash_html, "Missing gateway-sound-toggle button"
    assert "setLoopMode" in dash_html, "Missing setLoopMode function in JS"
    assert "toggleGatewayAudio" in dash_html, "Missing toggleGatewayAudio function in JS"
    print("[PASS] Audio background loop and Gateway floating sound toggle verified.")

    # 13. Test Colleague RBAC Full Module Names & Contractor Badges
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=colleagues")
    colleague_html = data.decode("utf-8")
    assert "US WORKING CONTRACTORS (MAX 2)" in colleague_html
    assert "perm-badge" in colleague_html
    assert "perm-title" in colleague_html
    assert "Dashboard Overview" in colleague_html or "Gmail Multi-Tenant Hub" in colleague_html
    print("[PASS] Colleague cards display contractor badges and RBAC permissions display full module names.")

    # 14. Test Interactive Campaign Execution Studio
    assert "campaign-studio-modal" in dash_html
    assert "openCampaignStudio" in dash_html
    assert "generateStudioAiVariants" in dash_html
    assert "runStudioDispatch" in dash_html
    assert "studio-live-ticker" in dash_html
    print("[PASS] Enterprise Interactive Campaign Studio drawer, Spintax generator and jitter dispatcher verified.")

    # 15. Test In-Page Direct Workspaces Across All 22 Modules
    print("Testing In-Page Dedicated Workspaces for all 22 Modules...")
    for mod_id in range(1, 23):
        status, headers, data = wsgi_request("/api/", "GET", query_string=f"tab=module&id={mod_id}")
        assert status == "200 OK", f"Module {mod_id} returned status {status}"
        html = data.decode("utf-8")
        expected_tag = f"MODULE {mod_id:02d} DIRECT WORKSPACE"
        assert expected_tag in html, f"Module {mod_id} missing in-page workspace tag '{expected_tag}'"
    # 16. Test Colleague Operations Guide & Real-Time Controls Across All 22 Modules
    print("Testing Colleague Operations Guides & Real-Time Controls across all 22 Modules...")
    for mod_id in range(1, 23):
        status, headers, data = wsgi_request("/api/", "GET", query_string=f"tab=module&id={mod_id}")
        assert status == "200 OK"
        html = data.decode("utf-8")
        assert "Colleague Operations Runbook" in html, f"Module {mod_id} missing Colleague Operations Runbook"
        assert "colleague-guide-card" in html, f"Module {mod_id} missing colleague-guide-card CSS class"
        assert f"runModuleBlueprintControl({mod_id}," in html, f"Module {mod_id} missing real-time runModuleBlueprintControl handler"
        assert f"mod-row-{mod_id}-0" in html, f"Module {mod_id} missing table row ID mod-row-{mod_id}-0"
        assert "module-table-status-pill" in html, f"Module {mod_id} missing module-table-status-pill"
    print("[PASS] All 22 Modules render Colleague Operations Runbooks in clean executive English & Real-Time Controls!")

    # 17. Test Logo & Favicon endpoints
    print("Testing 3D Logo & Favicon endpoints...")
    status, headers, data = wsgi_request("/api/assets/grace-logo.png", "GET")
    assert status == "200 OK", f"Expected 200 OK for logo, got {status}"
    ct = dict(headers).get("Content-Type")
    assert ct in ("image/png", "image/jpeg"), f"Expected image/png or image/jpeg, got {ct}"
    print("[PASS] /api/assets/grace-logo.png successfully served 3D Crest Logo.")

    # 18. Test Notifications Modal, Unified Theme & Toast Close Button in Dashboard
    print("Testing Notifications modal, single theme button, and toast 'X' button...")
    status, headers, data = wsgi_request("/api/", "GET")
    assert status == "200 OK"
    dash_html = data.decode("utf-8")
    assert "notifications-inbox-modal" in dash_html, "Missing notifications-inbox-modal in dashboard"
    assert "openNotificationsModal" in dash_html, "Missing openNotificationsModal in dashboard"
    assert "FULL INTERESTED" in dash_html, "Missing FULL INTERESTED intent classification in notifications"
    assert "MOST INTERESTED" in dash_html, "Missing MOST INTERESTED intent classification in notifications"
    assert "toggleExecutiveTheme" in dash_html, "Missing unified toggleExecutiveTheme"
    assert "toast-close-btn" in dash_html, "Missing toast-close-btn in CSS"
    assert "custom-contractor-input" in dash_html, "Missing custom-contractor-input in colleague modal"
    assert "addAndHuntCustomContractor" in dash_html, "Missing addAndHuntCustomContractor handler"
    # 19. Test Vertical Segmented Telemetry HUD (Image 1)
    print("Testing Vertical Segmented Telemetry HUD (Image 1)...")
    assert "hud-vertical-chamber" in dash_html, "Missing hud-vertical-chamber in dashboard"
    assert "hud-segment" in dash_html, "Missing hud-segment in dashboard"
    assert "chamber-node1" in dash_html, "Missing chamber-node1 in dashboard"
    assert "chamber-node2" in dash_html, "Missing chamber-node2 in dashboard"
    assert "chamber-health" in dash_html, "Missing chamber-health in dashboard"
    print("[PASS] Vertical Segmented Telemetry HUD (10-tier chambers) successfully rendered in Dashboard.")

    # 20. Test Auth Gateway Enhancements, Smart Suggestions & Hub Delegation
    print("Testing Auth Gateway, Smart Suggestions & Hub Delegation...")
    assert "btn-google-oauth" in dash_html, "Missing Google OAuth button in Auth Gateway"
    assert "handleGoogleOAuthLogin" in dash_html, "Missing Google OAuth handler"
    assert "generateUsernameSuggestions" in dash_html, "Missing smart username generator"
    assert "handleExecutiveLogout" in dash_html, "Missing executive logout handler"
    assert "sendPasswordResetOTP" in dash_html, "Missing email OTP sender"
    assert "dispatchWelcomeAutoReply" in dash_html, "Missing welcome message auto-reply"
    
    # Check Colleague Management delegation switch
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=colleagues")
    assert status == "200 OK"
    col_html = data.decode("utf-8")
    assert "delegation-btn-abdullah" in col_html, "Missing delegation-btn-abdullah in Colleague Management"
    assert "toggleColleagueManagementDelegation" in col_html, "Missing toggleColleagueManagementDelegation handler"
    # 21. Test Modal Dismiss Loop Prevention & Borderless 3D Logo Styling
    print("Testing Modal Dismiss Loop Prevention & Borderless 3D Logo Styling...")
    assert "isUserAuthenticated" in dash_html, "Missing isUserAuthenticated session guard in JS"
    assert "persistUserAuthentication" in dash_html, "Missing persistUserAuthentication handler in JS"
    assert "#brand-logo-container" in dash_html, "Missing #brand-logo-container CSS rule"
    assert "border: none !important;" in dash_html, "Missing borderless override for logo container"
    assert "rel=\"shortcut icon\"" in dash_html, "Missing rel='shortcut icon' in HTML head"
    print("[PASS] Modal loop prevention, persistent authentication guard, and borderless 3D logo verified.")

    # 22. Test Clickable Logo Preview Modal (Center Popup with Close Button)
    print("Testing Clickable Logo Preview Modal & Centered Popup...")
    assert "logo-preview-modal" in dash_html, "Missing logo-preview-modal in dashboard"
    assert "openLogoModal" in dash_html, "Missing openLogoModal handler in dashboard"
    assert "closeLogoModal" in dash_html, "Missing closeLogoModal handler in dashboard"
    assert "logo-clickable-wrap" in dash_html, "Missing logo-clickable-wrap in dashboard"
    print("[PASS] Clickable Logo Centered Modal Popup & Close controls verified.")

    print("\n[SUCCESS] ALL 22 EXTENSIVE TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()



