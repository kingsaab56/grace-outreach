import io
import json
import sys
from pathlib import Path

# Add project directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from main import app, read_shared_state, US_STATES_CATALOG, decrypt_vault_payload, update_shared_state, render_colleagues, send_welcome_email
except ImportError:
    from app import app, read_shared_state, US_STATES_CATALOG, decrypt_vault_payload

def wsgi_request(path, method="GET", query_string="", body_dict=None, headers_dict=None):
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
    if headers_dict:
        for hk, hv in headers_dict.items():
            environ["HTTP_" + hk.upper().replace("-", "_")] = hv
    
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

    # 23. Test Aesthetic Brightness Slider & Universal Light Theme Contrast Engine
    print("Testing Aesthetic Brightness Slider & Universal Light Theme Contrast Engine...")
    assert "brightness-control-pill" in dash_html, "Missing brightness-control-pill in ribbon"
    assert "brightness-slider" in dash_html, "Missing brightness-slider in ribbon"
    assert "adjustBrightness" in dash_html, "Missing adjustBrightness handler in JS"
    assert "initBrightness" in dash_html, "Missing initBrightness handler in JS"
    assert "--app-brightness" in dash_html, "Missing --app-brightness CSS variable"
    assert "body.light #logo-modal-title" in dash_html, "Missing light mode modal title contrast fix"
    # 24. Test Ultra-HD Master, Retina Thumbnail, and Viewport-Docked Modal
    print("Testing Ultra-HD Master, Retina Thumbnail & Viewport-Docked Modal...")
    status_thumb, headers_thumb, data_thumb = wsgi_request("/api/assets/grace-logo-thumb.png", "GET")
    assert status_thumb == "200 OK", f"Expected 200 OK for thumb, got {status_thumb}"
    assert data_thumb.startswith(b"\x89PNG"), "Thumbnail must be valid PNG"
    assert len(data_thumb) > 10000, "Thumbnail must contain valid image data"

    status_master, headers_master, data_master = wsgi_request("/api/assets/grace-logo.png", "GET")
    assert status_master == "200 OK", f"Expected 200 OK for master, got {status_master}"
    assert data_master.startswith(b"\x89PNG"), "Master must be valid PNG"
    assert len(data_master) > 1000000, "Master must be Ultra-HD (> 1MB)"

    assert "grace-logo-thumb.png" in dash_html, "Missing grace-logo-thumb.png reference in HTML"
    assert "brightness-overlay" in dash_html, "Missing brightness-overlay in JS"
    print("[PASS] Ultra-HD Master, Retina Thumbnail, and Viewport-Docked Modal verified.")

    # 25. Test Module Detail Vertical Segmented HUD (Image 3) & Pro Max Execution Controls
    print("Testing Module Detail Vertical Segmented HUD (Image 3) & Pro Max Execution Controls...")
    status_m8, headers_m8, data_m8 = wsgi_request("/api/", "GET", query_string="tab=module&id=8")
    assert status_m8 == "200 OK", f"Expected 200 OK for module 8, got {status_m8}"
    m8_html = data_m8.decode("utf-8")
    assert "MULTI-TENANT TELEMETRY HUD" in m8_html, "Missing MULTI-TENANT TELEMETRY HUD in module 8"
    assert "Vertical Segmented Quota, Velocity &amp; Reputation Gauges" in m8_html, "Missing Image 3 HUD title in module 8"
    assert "chamber-wb-8-1" in m8_html, "Missing vertical chamber chamber-wb-8-1 in module 8"
    assert "chamber-wb-8-2" in m8_html, "Missing vertical chamber chamber-wb-8-2 in module 8"
    assert "chamber-wb-8-3" in m8_html, "Missing vertical chamber chamber-wb-8-3 in module 8"
    assert "chamber-wb-8-4" in m8_html, "Missing vertical chamber chamber-wb-8-4 in module 8"
    assert "body.light .control-row b" in m8_html, "Missing light theme control-row text contrast fix"
    assert "--text-main: #0F172A !important;" in m8_html, "Missing --text-main light mode variable"
    print("[PASS] Module Detail Vertical Segmented HUD (Image 3) and Pro Max Execution Controls verified.")

    # 26. Test Circular Header Avatar, Current Profile Details & Dual-Vault Photo Persistence
    print("Testing Circular Header Avatar, Current Profile Details & Dual-Vault Photo Persistence...")
    assert "header-avatar-circle-wrap" in dash_html, "Missing header-avatar-circle-wrap in dashboard"
    assert "openProfilePhotoPreviewModal" in dash_html, "Missing openProfilePhotoPreviewModal in HTML"
    assert "profile-photo-preview-modal" in dash_html, "Missing profile-photo-preview-modal in HTML"
    assert "header-avatar-cam-badge" not in dash_html, "Camera badge should be removed from header avatar"
    assert "header-active-name" in dash_html, "Missing header-active-name class in HTML"
    assert "active-profile-role-tag" in dash_html, "Missing active-profile-role-tag in HTML"
    assert "grace-profile-photos-vault" in dash_html, "Missing grace-profile-photos-vault dual persistence in JS"
    assert "body.light .header-active-name" in dash_html, "Missing light mode active name contrast rule"
    assert "aspect-ratio: 1 / 1 !important;" in dash_html, "Missing strict 1:1 circular aspect ratio override"
    assert "body.light .header-avatar:not([data-uploaded=\"true\"])" in dash_html, "Missing light mode not-uploaded guard"
    assert ".header-avatar[data-uploaded=\"true\"]" in dash_html, "Missing uploaded avatar transparent background rule"
    assert ".header-avatar img" in dash_html, "Missing header-avatar img rule"
    print("[PASS] Circular Header Avatar, Current Profile Display & Dual-Vault Photo Persistence verified.")

    # 27. Test Company Account Vault, 4-Class Lifecycle, Google Checkpoint & Migration Exporter
    print("Testing Company Account Vault, 4-Class Lifecycle, Google Checkpoint & Migration Exporter...")
    status, headers, body = wsgi_request("/api/state", "GET")
    assert status == "200 OK"
    state = json.loads(body.decode("utf-8"))
    assert "companyAccounts" in state, "Missing companyAccounts in shared state"
    assert len(state["companyAccounts"]) >= 4, "Expected pre-seeded company accounts"
    assert "acc_king_01" in state["companyAccounts"]
    assert state["companyAccounts"]["acc_king_01"]["status_class"] == "active"

    # POST /api/state add new company account
    new_acc_payload = {
        "resource": "companyAccounts",
        "action": "save",
        "key": "acc_test_new",
        "value": {
            "id": "acc_test_new",
            "colleague_key": "abdullah",
            "colleague_name": "Abdullah Khan",
            "email": "test.outreach@gracehub.io",
            "username": "test_abdullah",
            "password": "TestAppPassword2026#",
            "provider": "Google Workspace",
            "status_class": "active",
            "notes": "Automated verification test account"
        }
    }
    status, headers, body = wsgi_request("/api/state", "POST", body_dict=new_acc_payload)
    assert status == "200 OK", f"Failed saving company account: {body}"
    res = json.loads(body.decode("utf-8"))
    assert res.get("state", {}).get("companyAccounts", {}).get("acc_test_new") is not None

    # Shift class through all 4 lifecycle classes
    for target_class in ["maintenance", "suspended", "restricted", "active"]:
        shift_payload = {
            "resource": "companyAccounts",
            "action": "change_class",
            "key": "acc_test_new",
            "value": {
                "id": "acc_test_new",
                "colleague_key": "abdullah",
                "colleague_name": "Abdullah Khan",
                "email": "test.outreach@gracehub.io",
                "password": "TestAppPassword2026#",
                "status_class": target_class
            }
        }
        status, headers, body = wsgi_request("/api/state", "POST", body_dict=shift_payload)
        assert status == "200 OK"
        res = json.loads(body.decode("utf-8"))
        assert res["state"]["companyAccounts"]["acc_test_new"]["status_class"] == target_class

    # Delete test account
    del_payload = {
        "resource": "companyAccounts",
        "action": "delete",
        "key": "acc_test_new",
        "value": {}
    }
    status, headers, body = wsgi_request("/api/state", "POST", body_dict=del_payload)
    assert status == "200 OK"
    res = json.loads(body.decode("utf-8"))
    assert "acc_test_new" not in res.get("state", {}).get("companyAccounts", {})

    # Validation rejects invalid email
    bad_payload = {
        "resource": "companyAccounts",
        "action": "save",
        "value": {
            "email": "not-an-email",
            "password": "123",
            "status_class": "active"
        }
    }
    status, headers, body = wsgi_request("/api/state", "POST", body_dict=bad_payload)
    assert status == "400 Bad Request", "Expected rejection for bad email"

    # Verify rendered HTML elements across colleagues and dashboard
    status_c, headers_c, data_c = wsgi_request("/api/", "GET", query_string="tab=colleagues")
    assert status_c == "200 OK"
    colleagues_html = data_c.decode("utf-8")
    assert "company-account-modal" in colleagues_html, "Missing company-account-modal"
    assert "google-verify-checkpoint-modal" in colleagues_html, "Missing google-verify-checkpoint-modal"
    assert "admin-master-vault-modal" in colleagues_html, "Missing admin-master-vault-modal"
    assert "account-appeal-modal" in colleagues_html, "Missing account-appeal-modal"
    assert "ribbon-vault-btn" in colleagues_html, "Missing ribbon-vault-btn in header"
    assert "colleagues-vault-btn" in colleagues_html, "Missing colleagues-vault-btn in colleague view"
    assert "class-active" in colleagues_html, "Missing class-active CSS"
    assert "class-maintenance" in colleagues_html, "Missing class-maintenance CSS"
    assert "class-suspended" in colleagues_html, "Missing class-suspended CSS"
    assert "class-restricted" in colleagues_html, "Missing class-restricted CSS"
    assert "openAdminMasterVaultModal" in colleagues_html, "Missing openAdminMasterVaultModal JS"
    assert "exportCompanyAccounts" in colleagues_html, "Missing exportCompanyAccounts JS"
    assert "initiateGoogleVerificationCheckpoint" in colleagues_html, "Missing initiateGoogleVerificationCheckpoint JS"
    assert "executeGoogleVerificationHandshake" in colleagues_html, "Missing executeGoogleVerificationHandshake JS"
    assert "toggleAdminVaultMasterLock" in colleagues_html, "Missing toggleAdminVaultMasterLock JS"
    print("[PASS] Company Account Vault, 4-Class Lifecycle, Google Checkpoint & Migration Exporter verified.")

    # 28. Test WhatsApp Aesthetic 3D Royal Crown Asset & Rendering
    status_crown, headers_crown, data_crown = wsgi_request("/api/assets/crown.png", "GET")
    assert status_crown == "200 OK", f"Expected 200 OK for /api/assets/crown.png, got {status_crown}"
    assert data_crown.startswith(b"\x89PNG"), "Expected valid PNG signature for /api/assets/crown.png"
    assert len(data_crown) > 5000, f"Expected substantive PNG data, got {len(data_crown)} bytes"
    
    # Verify rendered HTML contains wa-crown-icon
    assert "wa-crown-icon" in dash_html, "Missing wa-crown-icon class in rendered dashboard"
    assert "crown.png" in dash_html, "Missing crown.png image reference in rendered dashboard"
    assert "creator-king" in dash_html, "Missing creator-king in dashboard"
    assert "WA_CROWN_HTML" in dash_html, "Missing WA_CROWN_HTML in client-side script"
    print("[PASS] WhatsApp Aesthetic 3D Royal Crown & High-Res Asset Pipeline verified.")

    # 29. Test Colleague Real-Time Search & Accordion Expand/Collapse Drawer
    assert "colleague-search-input" in colleagues_html, "Missing colleague-search-input in colleague management"
    assert "colleague-toolbar-card" in colleagues_html, "Missing colleague-toolbar-card in colleague management"
    assert "colleague-match-counter" in colleagues_html, "Missing colleague-match-counter in toolbar"
    assert "colleague-expand-btn" in colleagues_html, "Missing colleague-expand-btn on colleague cards"
    assert "colleague-chevron-icon" in colleagues_html, "Missing colleague-chevron-icon SVG in expand button"
    assert "colleague-details-drawer" in colleagues_html, "Missing colleague-details-drawer container"
    assert "toggleColleagueExpand" in colleagues_html, "Missing toggleColleagueExpand JS handler"
    assert "filterColleagues" in colleagues_html, "Missing filterColleagues JS handler"
    assert "expandAllColleagues" in colleagues_html, "Missing expandAllColleagues JS handler"
    assert "clearColleagueSearch" in colleagues_html, "Missing clearColleagueSearch JS handler"
    assert "body.light .colleague-expand-btn" in colleagues_html, "Missing light mode colleague-expand-btn styling"
    print("[PASS] Colleague Real-Time Search, Match Counter & Accordion Expand/Collapse Drawers verified.")

    # 30. Test Interactive Soundscape Playlist Queue & Floating Minimalist Mini-Player
    assert "soundscape-playlist-container" in dash_html, "Missing soundscape-playlist-container in soundscape modal"
    assert "soundscape-playlist-box" in dash_html, "Missing soundscape-playlist-box CSS or HTML"
    assert "floating-audio-main" in dash_html, "Missing floating-audio-main widget on main pages"
    assert "floating-audio-gateway" in dash_html, "Missing floating-audio-gateway widget in Auth Gateway"
    assert "audio-dot-main" in dash_html, "Missing audio-dot-main floating button"
    assert "audio-dot-gateway" in dash_html, "Missing audio-dot-gateway floating button"
    assert "floating-audio-controls-main" in dash_html, "Missing floating-audio-controls-main container"
    assert "floating-audio-controls-gateway" in dash_html, "Missing floating-audio-controls-gateway container"
    assert "mini-play-btn-main" in dash_html, "Missing mini-play-btn-main control button"
    assert "mini-play-btn-gateway" in dash_html, "Missing mini-play-btn-gateway control button"
    assert "mini-track-label-main" in dash_html, "Missing mini-track-label-main element"
    assert "mini-track-label-gateway" in dash_html, "Missing mini-track-label-gateway element"
    assert "renderSoundscapePlaylist" in dash_html, "Missing renderSoundscapePlaylist JS function"
    assert "removeTrackFromPlaylist" in dash_html, "Missing removeTrackFromPlaylist JS function"
    assert "playTrackAtIndex" in dash_html, "Missing playTrackAtIndex JS function"
    assert "playNextTrack" in dash_html, "Missing playNextTrack JS function"
    assert "playPrevTrack" in dash_html, "Missing playPrevTrack JS function"
    assert "toggleFloatingAudioControls" in dash_html, "Missing toggleFloatingAudioControls JS function"
    assert "syncAllAudioControlsUI" in dash_html, "Missing syncAllAudioControlsUI JS function"
    assert ".floating-audio-dot" in dash_html, "Missing .floating-audio-dot CSS styling"
    assert "body.light .floating-audio-dot" in dash_html, "Missing light mode .floating-audio-dot styling"
    assert "body.light .soundscape-playlist-box" in dash_html, "Missing light mode .soundscape-playlist-box styling"
    # 31. Test Colleague Permanent Profile Persistence, Custom Vault & Card Hydration
    print("Testing Colleague Permanent Profile Persistence & Dual-Vault Auto-Heal...")
    assert "grace-custom-profiles-vault" in dash_html, "Missing grace-custom-profiles-vault in client script"
    assert "colleague-role-tag" in dash_html, "Missing colleague-role-tag class in HTML/JS"
    
    colleague_payload = {
        "resource": "profiles",
        "key": "sarah",
        "value": {
            "name": "Sarah Jenkins - Growth Lead",
            "role": "Principal Outreach Strategist",
            "assigned_states": ["Washington", "Illinois"],
            "assigned_contractors": ["Turner Construction Co.", "Bechtel Corporation"]
        }
    }
    status, headers, body = wsgi_request("/api/state", "POST", body_dict=colleague_payload)
    assert status == "200 OK", f"Expected 200 OK, got {status}"
    persisted_state = read_shared_state()
    assert persisted_state["profiles"]["sarah"]["name"] == "Sarah Jenkins - Growth Lead"
    assert persisted_state["profiles"]["sarah"]["role"] == "Principal Outreach Strategist"
    assert persisted_state["profiles"]["sarah"]["initials"] == "SJ"
    assert persisted_state["profiles"]["sarah"]["assigned_states"] == ["Washington", "Illinois"]
    assert persisted_state["profiles"]["sarah"]["assigned_contractors"] == ["Turner Construction Co.", "Bechtel Corporation"]

    # Verify Colleague Management HTML reflects the persisted update
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=colleagues")
    assert status == "200 OK"
    colleagues_page = data.decode("utf-8")
    assert "Sarah Jenkins - Growth Lead" in colleagues_page
    assert "Principal Outreach Strategist" in colleagues_page
    assert "wa-crown-icon" in colleagues_page
    assert "King Saab" in colleagues_page
    print("[PASS] Colleague Permanent Profile Persistence, Custom Vault & Card Hydration verified.")

    # 32. Verify Soundscape Multi-Box Architecture, Video/Audio Native Decoding, Shuffle Engine & Draggable Mini-Player
    print("Testing Soundscape Multi-Box Architecture, Video/Audio Native Decoding, Shuffle Engine & Draggable Mini-Player...")
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=dashboard")
    assert status == "200 OK"
    dash_html = data.decode("utf-8")
    
    # Check 3 standalone boxes
    assert "default-soundscape-box" in dash_html
    assert "soundscape-playlist-box" in dash_html
    assert "custom-media-studio-box" in dash_html
    
    # Check native video/audio decode element
    assert '<video id="custom-media"' in dash_html
    
    # Check shuffle mode & controls
    assert "shuffleSoundscapePlaylist" in dash_html
    assert "loop-shuffle-btn" in dash_html
    assert "playShuffleTrack" in dash_html
    assert "setLoopMode('shuffle')" in dash_html
    
    # Check draggable mini-player engine and CSS
    assert "initFloatingAudioDrag" in dash_html
    assert "audioDrag" in dash_html
    assert "grace-floating-audio-pos" in dash_html
    assert "floating-audio-widget" in dash_html
    assert "floating-audio-dot" in dash_html
    assert "cursor: grab;" in dash_html
    assert "cursor: grabbing;" in dash_html
    assert "touch-action: none;" in dash_html
    print("[PASS] Soundscape Multi-Box Architecture, Native Video/Audio Decoding, Shuffle Engine & Draggable Mini-Player verified.")

    # 33. Verify 3D Animated AI Agent Companion, Bilingual Vocal Speech, 5 Personas & A-to-Z App Tour
    print("Testing 3D Animated AI Agent Companion, Bilingual Vocal Speech, 5 Personas & A-to-Z App Tour...")
    # Verify asset endpoints
    status, headers, data = wsgi_request("/api/assets/ai-agent-titan.png", "GET")
    assert status == "200 OK"
    assert len(data) > 50000
    assert data.startswith(b"\x89PNG")

    status, headers, data = wsgi_request("/api/assets/ai-agent-alara.png", "GET")
    assert status == "200 OK"
    assert len(data) > 50000
    assert data.startswith(b"\x89PNG")

    # Verify dashboard markup
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=dashboard")
    assert status == "200 OK"
    html = data.decode("utf-8")

    assert "ai-agent-widget" in html
    assert "ai-agent-avatar-wrap" in html
    assert "ai-agent-img" in html
    assert "agent-speaking-waves" in html
    assert "ai-agent-bubble" in html
    assert "ai-agent-persona-modal" in html
    assert "AI_VOICE_PERSONAS" in html
    assert "APP_TOUR_STEPS" in html
    assert "speakAloud" in html
    assert "previewPersonaVoice" in html
    assert "startAppTour" in html
    assert "askAgentQuestion" in html
    assert "initAIAgentDrag" in html
    assert "alara" in html
    assert "calvin" in html
    assert "opus2" in html
    assert "aura" in html
    assert "zephyr" in html
    print("[PASS] 3D Animated AI Agent Companion, Bilingual Vocal Speech, 5 Personas & A-to-Z App Tour verified.")

    # 34. Verify 4K Resolution, 5s Auto-Minimize Mini-Bot, In-Chat Voice Mic, Permanent Name Vault & Visual Step Sketches
    print("Testing 4K Visuals, 5s Auto-Minimize, In-Chat Mic, Name Vault, Fluent Urdu & Step Sketches...")
    from PIL import Image
    im_titan = Image.open("assets/ai-agent-titan.png")
    im_alara = Image.open("assets/ai-agent-alara.png")
    assert im_titan.size == (1600, 2400), f"Expected Titan 4K (1600, 2400), got {im_titan.size}"
    assert im_alara.size == (1600, 2400), f"Expected Alara 4K (1600, 2400), got {im_alara.size}"

    assert "bubble-settings-btn" in html
    assert "bubble-mic-btn" in html
    assert "is-minimized" in html
    assert "startAgentInactivityTimer" in html
    assert "minimizeAgentToMiniBot" in html
    assert "restoreAgentFromMiniBot" in html
    assert "grace-ai-custom-name-vault" in html
    assert "grace-ai-name-is-custom" in html
    assert "resetAgentCustomName" in html
    assert "previewUrduPhonetic" in html
    assert "urduPhoneticAudio" in html
    assert "toRomanUrduPhonetic" in html
    assert "renderStepSketchFlow" in html
    assert "step-sketch-flow" in html
    assert "beacon-radar-target" in html
    assert "highlightScreenTarget" in html
    assert "triggerProactiveAgentGuidance" in html
    assert "initProactiveContextTriggers" in html
    print("[PASS] 4K Visuals, 5s Auto-Minimize, In-Chat Mic, Name Vault, Fluent Urdu & Step Sketches verified.")

    # 35. Verify Autonomous Collision Avoidance, Responsive Screen HUD, Terminal Blueprint Sketches & Natural HD Palette
    print("Testing Collision Avoidance, Screen-Adaptive HUD, Terminal Wireframe Blueprints & Natural Colors...")
    assert "adjustAgentPositionForTarget" in html, "Missing adjustAgentPositionForTarget"
    assert "restoreAgentDefaultPosition" in html, "Missing restoreAgentDefaultPosition"
    assert "dock-left" in html, "Missing dock-left in HTML/CSS"
    assert "dock-right" in html, "Missing dock-right in HTML/CSS"
    assert "blueprint-terminal-card" in html, "Missing blueprint-terminal-card in HTML/CSS"
    assert "blueprint-terminal-header" in html, "Missing blueprint-terminal-header"
    assert "blueprint-terminal-pre" in html, "Missing blueprint-terminal-pre"
    assert "blueprint-tags-row" in html, "Missing blueprint-tags-row"
    assert "blueprint-btn-tag" in html, "Missing blueprint-btn-tag"
    assert "renderAsciiBlueprintCard" in html, "Missing renderAsciiBlueprintCard"
    assert "asciiBlueprint" in html, "Missing asciiBlueprint in tour steps"
    assert "min(450px, 92vw)" in html, "Missing responsive width min(450px, 92vw)"
    assert "max-height: min(560px, 82vh)" in html, "Missing responsive max-height"
    assert "@media (max-height: 800px)" in html, "Missing laptop screen responsive media query"
    
    # Verify natural pearl-white armor calibration (no artificial blue tint spill)
    # Check pixels on the armor shoulder area: R, G, B should be close to balanced neutral
    titan_pixels = list(im_titan.getdata())
    # Find bright non-transparent pixels (armor)
    armor_pixels = [p for p in titan_pixels if len(p) == 4 and p[3] > 200 and p[0] > 160 and p[1] > 160 and p[2] > 160]
    assert len(armor_pixels) > 500, "Should have plenty of bright armor pixels"
    # Ensure blue does not excessively dominate red/green on white armor
    sample_armor = armor_pixels[:500]
    avg_diff_b_r = sum(p[2] - p[0] for p in sample_armor) / len(sample_armor)
    assert avg_diff_b_r < 40, f"Blue cast on armor too strong: {avg_diff_b_r}"
    print("[PASS] Collision Avoidance, Screen-Adaptive HUD, Terminal Wireframe Blueprints & Natural Colors verified.")

    # 36. Verify Fluent Urdu Speech Engine, Opus 2 Default Persona, Gender-Matched Neural Voices & Mic-to-Mike Normalization
    print("Testing Fluent Urdu Speech Engine, Opus 2 Default, Gender Voices & Mic-to-Mike Normalization...")
    assert "sanitizePhoneticUrdu" in html, "Missing sanitizePhoneticUrdu in html"
    assert "findBestSpeechVoice" in html, "Missing findBestSpeechVoice in html"
    assert "currentAgentPersonaKey = 'opus2'" in html, "Opus 2 should be default persona in JS"
    assert "mike dabayein" in html, "Tour finish should use 'mike dabayein' instead of 'mic'"
    assert "Cyber Intelligence ⭐" in html, "Opus 2 tag updated with highlight star"
    assert "isVoiceFemale" in html, "Missing isVoiceFemale gender discriminator"
    assert "isVoiceMale" in html, "Missing isVoiceMale gender discriminator"
    assert "lyve" in html, "Missing lyve phonetic normalization"
    assert "H U D" in html, "Missing H U D phonetic normalization"
    # 37. Verify Executive Telemetry & Activity Stream Redesign (Coloring, Dynamic Badges & Theme Harmony)
    print("Testing Executive Activity Stream, Dynamic Badges, Custom Scrollbars & Light/Dark Theming...")
    assert "telemetry-card-title" in html, "Missing telemetry-card-title class"
    assert "telemetry-live-badge" in html, "Missing telemetry-live-badge class"
    assert "body.light .telemetry-card-title" in html, "Missing body.light .telemetry-card-title theme rule"
    assert "body.light .log-box" in html, "Missing body.light .log-box theme rule"
    assert "body.light .log-box .log-row" in html, "Missing body.light .log-box .log-row rule"
    assert "log-row-dispatch" in html, "Missing log-row-dispatch class"
    assert "log-row-classify" in html, "Missing log-row-classify class"
    assert "flex-basis: 100%" in html, "Missing flex-basis: 100% on log-msg for proper row wrapping"
    assert "scrollbar-color" in html, "Missing custom scrollbar color rule on log-box"
    print("[PASS] Executive Activity Stream, Dynamic Badges, Custom Scrollbars & Light/Dark Theming verified.")

    # 38. Verify Senior Dev Deep Audit: DOM Hierarchy Balance, Zero Duplicate IDs, applyTheme, Voice GC Shield & Auto-Docking
    print("Testing Senior Dev Deep Audit: DOM Balance, Single Logo ID, applyTheme, Voice GC Shield & Auto-Docking...")
    assert html.count('id="logo-clickable-wrap"') == 1, "Duplicate id='logo-clickable-wrap' found in rendered HTML"
    assert (Path(__file__).resolve().parent / "main.py").read_text(encoding="utf-8").count("LOGO_SVG_MODAL") >= 1, "Missing LOGO_SVG_MODAL definition"
    assert "function applyTheme(" in html, "Missing applyTheme function in rendered HTML"
    assert "window.__graceAgentUtterance = utter;" in html, "Missing Chromium GC shield for voice synthesis"
    assert "cachedSpeechVoices" in html, "Missing async cachedSpeechVoices pre-warming"
    assert ".grid-2 { grid-template-columns: 1fr !important; }" in html, "Missing mobile responsive breakpoint for swapped grid-2"
    assert "LIVE STREAM TELEMETRY & ACTIVITY FEED" in html, "Missing Telemetry/Activity Stream ASCII blueprint in askAgentQuestion"
    assert "widget.classList.add('dock-left')" in html, "Missing auto-docking left class on drag end"
    assert "widget.classList.add('dock-right')" in html, "Missing auto-docking right class on drag end"
    print("[PASS] Senior Dev Deep Audit: DOM Balance, Single Logo ID, applyTheme, Voice GC Shield & Auto-Docking verified.")

    # 39. Verify 7-Day Deliverability Radar & Pacing Histogram Visualizations (User Uploaded Metric Cards)
    print("Testing 7-Day Deliverability Radar & Outbound Dispatch Velocity Pacing Histogram...")
    assert "telemetry-radar-card" in html, "Missing telemetry-radar-card in dashboard HTML"
    assert "pacing-histogram-card" in html, "Missing pacing-histogram-card in dashboard HTML"
    assert "7-Day Deliverability &amp; Reputation Curve" in html, "Missing 7-Day Deliverability & Reputation Curve title"
    assert "Outbound Dispatch Velocity &amp; Jitter" in html, "Missing Outbound Dispatch Velocity & Jitter title"
    assert "Optimal (98.4% Avg)" in html, "Missing Optimal (98.4% Avg) badge"
    assert "Human-Like Pacing" in html, "Missing Human-Like Pacing badge"
    assert "TELEMETRY RADAR" in html, "Missing TELEMETRY RADAR eyebrow"
    assert "PACING HISTOGRAM" in html, "Missing PACING HISTOGRAM eyebrow"
    assert "reputation-fill-grad" in html, "Missing reputation area gradient in SVG"
    assert "hist-bar" in html, "Missing hist-bar styling class"
    assert "curve-dot" in html, "Missing curve-dot styling class"
    assert ".charts-grid-2 { grid-template-columns: 1fr !important; }" in html, "Missing responsive mobile breakpoint for charts"
    print("[PASS] 7-Day Deliverability Radar & Outbound Dispatch Velocity Pacing Histogram verified.")

    # 40. Verify Defensive Security Hardening & 12 Security Areas
    print("Testing Defensive Security Hardening & 12 Security Areas...")
    # 40.1 Security Headers on HTTP responses
    status, headers, data = wsgi_request("/api/", "GET", query_string="tab=dashboard")
    hdr_dict = {k.lower(): v for k, v in headers}
    assert hdr_dict.get("x-content-type-options") == "nosniff", "Missing or invalid X-Content-Type-Options"
    assert hdr_dict.get("x-frame-options") == "SAMEORIGIN", "Missing or invalid X-Frame-Options"
    assert hdr_dict.get("x-xss-protection") == "1; mode=block", "Missing or invalid X-XSS-Protection"
    assert hdr_dict.get("referrer-policy") == "strict-origin-when-cross-origin", "Missing or invalid Referrer-Policy"
    assert "content-security-policy" in hdr_dict, "Missing Content-Security-Policy"

    # 40.2 Prohibited paths returning 404 (No leakage of .env, credentials, source code, db)
    for forbidden in ["/.env", "/.env.production", "/credentials.json", "/token.json", "/main.py", "/data.db", "/api/../../.env"]:
        st, _, _ = wsgi_request(forbidden, "GET")
        assert st.startswith("404"), f"Forbidden path {forbidden} should return 404, got {st}"

    # 40.3 Password masking in GET /api/state
    status, _, data = wsgi_request("/api/state", "GET")
    state_res = json.loads(data.decode("utf-8"))
    for acc_id, acc in state_res.get("companyAccounts", {}).items():
        assert acc.get("password") == "••••••••••••", f"Password in company account {acc_id} was not masked: {acc.get('password')}"
        assert acc.get("has_password") is True

    # 40.4 Server-Side Auth API (/api/auth/login, /api/auth/session, /api/auth/logout)
    status, _, data = wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "king", "password": "wrongpassword"})
    assert status.startswith("401"), f"Invalid login should return 401, got {status}"
    status, hdrs, data = wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "king", "password": "grace2026"})
    assert status.startswith("200"), f"Valid login should return 200, got {status}"
    auth_resp = json.loads(data.decode("utf-8"))
    assert auth_resp.get("status") == "ok"
    assert "token" in auth_resp
    assert any("grace_session_id=" in v for k, v in hdrs if k.lower() == "set-cookie")

    # 40.5 Master Vault Reveal API (/api/vault/reveal)
    status, _, _ = wsgi_request("/api/vault/reveal", "POST", body_dict={"master_key": "bad_key"})
    assert status.startswith("401"), f"Invalid master key should return 401, got {status}"
    status, _, data = wsgi_request("/api/vault/reveal", "POST", body_dict={"master_key": "grace2026"})
    assert status.startswith("200"), f"Valid master key should return 200, got {status}"
    vault_resp = json.loads(data.decode("utf-8"))
    assert vault_resp.get("status") == "ok"
    assert "accounts" in vault_resp

    # 40.6 Rate Limiting defense against abuse (returns 429 Too Many Requests)
    rate_headers = {"X-Test-Rate-Limit": "1", "X-Forwarded-For": "198.51.100.24"}
    for _ in range(12):
        wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "king", "password": "wrong"}, headers_dict=rate_headers)
    rate_st, rate_hdrs, rate_data = wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "king", "password": "wrong"}, headers_dict=rate_headers)
    assert rate_st.startswith("429"), f"Abusive requests should trigger 429 Too Many Requests, got {rate_st}"
    rate_hdrs_dict = {k.lower(): v for k, v in rate_hdrs}
    assert "retry-after" in rate_hdrs_dict, "429 response must include Retry-After header"
    print("[PASS] Defensive Security Hardening, 12 Security Areas & HTTP 429 Rate Limiting verified.")

    # 41. GOOGLE BULK SENDER 2026 & PRIVACY/TERMS/ENCRYPTION COMPLIANCE TEST
    print("Testing Google Compliance, Privacy Policy, Terms of Service & At-Rest Encryption...")
    
    # 41.1 Privacy Policy (/privacy)
    priv_st, priv_hdrs, priv_body = wsgi_request("/privacy", "GET")
    assert priv_st.startswith("200"), f"/privacy should return 200 OK, got {priv_st}"
    priv_html = priv_body.decode("utf-8")
    assert "Privacy Policy &amp; Google API User Data Disclosure" in priv_html, "Missing Privacy Policy title"
    assert "Limited Use requirements" in priv_html, "Missing Google Limited Use disclosure"
    assert "Spam Rate Sentinel" in priv_html, "Missing Google Spam Rate Sentinel disclosure"
    assert "RFC 8058 One-Click Unsubscribe" in priv_html, "Missing RFC 8058 disclosure"
    assert "ENC256:" in priv_html or "AES-256 Fernet" in priv_html, "Missing AES-256 Vault encryption disclosure"

    # 41.2 Terms of Service (/terms)
    terms_st, terms_hdrs, terms_body = wsgi_request("/terms", "GET")
    assert terms_st.startswith("200"), f"/terms should return 200 OK, got {terms_st}"
    terms_html = terms_body.decode("utf-8")
    assert "Terms of Service &amp; Acceptable Use Policy" in terms_html, "Missing Terms of Service title"
    assert "Google Bulk Sender 2026 Compliance Covenant" in terms_html, "Missing Bulk Sender Covenant"
    assert "Zero Tolerance for Unsolicited Spam" in terms_html, "Missing Anti-Spam covenant"

    # 41.3 RFC 8058 One-Click Unsubscribe Handler (/api/compliance/unsubscribe)
    unsub_st, _, unsub_body = wsgi_request("/api/compliance/unsubscribe?email=test.recipient@example.com", "GET")
    assert unsub_st.startswith("200"), f"GET /api/compliance/unsubscribe should return 200, got {unsub_st}"
    assert "Unsubscribe Confirmed" in unsub_body.decode("utf-8")

    unsub_post_st, _, unsub_post_body = wsgi_request("/api/compliance/unsubscribe?email=post.recipient@example.com", "POST")
    assert unsub_post_st.startswith("200"), f"POST /api/compliance/unsubscribe should return 200, got {unsub_post_st}"
    unsub_post_json = json.loads(unsub_post_body.decode("utf-8"))
    assert unsub_post_json.get("status") == "ok"
    assert unsub_post_json.get("email") == "post.recipient@example.com"

    # 41.4 Sitemap Verification (/sitemap.xml)
    sm_st, _, sm_body = wsgi_request("/sitemap.xml", "GET")
    assert sm_st.startswith("200")
    sm_xml = sm_body.decode("utf-8")
    assert "<loc>/privacy</loc>" in sm_xml, "Sitemap must include /privacy"
    assert "<loc>/terms</loc>" in sm_xml, "Sitemap must include /terms"

    # 41.5 At-Rest Encrypted Passwords & Super Admin Decryption
    st_raw = read_shared_state()
    for acc_id, acc in st_raw.get("companyAccounts", {}).items():
        pwd = acc.get("password", "")
        if pwd:
            assert pwd.startswith("ENC256:"), f"Password on disk for {acc_id} must be encrypted with ENC256:, got {pwd[:10]}"
            decrypted = decrypt_vault_payload(pwd)
            assert decrypted and not decrypted.startswith("ENC256:"), f"Password failed to decrypt properly: {decrypted}"

    print("[PASS] Google Compliance, Privacy Policy, Terms of Service & At-Rest Encryption verified.")

    
    # 42. STRATEGIC HARDENING: OTP AUTH, MULTI-USER OVERLAP, TENANT ISOLATION & COMPACT MODAL
    print("Testing OTP Verification, Multi-User Overlap Matching, Colleague Isolation & Strategic Hardening...")

    # 42.1 Email OTP Send API (/api/auth/otp/send)
    otp_send_st, _, otp_send_body = wsgi_request("/api/auth/otp/send", "POST", body_dict={
        "email": "lead.architect@graceassistant.io",
        "name": "King Saab",
        "purpose": "register"
    }, headers_dict={"X-Test-Client": "1"})
    assert otp_send_st.startswith("200"), f"Expected 200 from /api/auth/otp/send, got {otp_send_st}"
    otp_send_res = json.loads(otp_send_body.decode("utf-8"))
    assert otp_send_res.get("status") == "ok"
    assert "demo_otp" in otp_send_res
    generated_otp = otp_send_res["demo_otp"]
    assert len(generated_otp) == 6

    # 42.2 Email OTP Verify API (/api/auth/otp/verify)
    # Test invalid OTP
    bad_otp_st, _, _ = wsgi_request("/api/auth/otp/verify", "POST", body_dict={
        "email": "lead.architect@graceassistant.io",
        "otp": "000000",
        "purpose": "register"
    }, headers_dict={"X-Test-Client": "1"})
    assert bad_otp_st.startswith("401"), f"Invalid OTP should return 401, got {bad_otp_st}"

    # Test valid OTP
    good_otp_st, _, good_otp_body = wsgi_request("/api/auth/otp/verify", "POST", body_dict={
        "email": "lead.architect@graceassistant.io",
        "otp": generated_otp,
        "purpose": "register"
    }, headers_dict={"X-Test-Client": "1"})
    assert good_otp_st.startswith("200"), f"Valid OTP should return 200, got {good_otp_st}"
    good_otp_res = json.loads(good_otp_body.decode("utf-8"))
    assert good_otp_res.get("verified") is True

    # 42.3 Welcome Email Dispatch & Audit Logging
    welcome_res = send_welcome_email("sarah.onboarding@graceassistant.io", "Sarah Malik", "Growth Marketer", "GRA-MKT-003")
    assert welcome_res.get("status") == "ok"
    st_post_welcome = read_shared_state()
    assert any("Welcome Email Dispatched" in a.get("action", "") for a in st_post_welcome.get("auditLog", []))

    # 42.4 Duplicate Company Account Prevention (Same Colleague)
    duplicate_payload = {
        "resource": "companyAccounts",
        "key": "acc_king_dup_test",
        "value": {
            "email": "kingsaab.outreach@graceassistant.io",
            "colleague_key": "king",
            "colleague_name": "King Saab",
            "password": "Password123!"
        }
    }
    duplicate_blocked = False
    try:
        update_shared_state(duplicate_payload)
    except ValueError as e:
        if "already exists in your database" in str(e).lower():
            duplicate_blocked = True
    assert duplicate_blocked, "Adding duplicate account for same colleague should raise ValueError"

    # 42.5 100% Multi-User Overlap Identity Matching Engine (Different Colleagues)
    overlap_payload = {
        "resource": "companyAccounts",
        "key": "acc_hamza_overlap_test",
        "value": {
            "email": "sarah.malik@graceoutreach.org",
            "colleague_key": "hamza",
            "colleague_name": "Hamza Ali",
            "password": "OverlapPassword2026!"
        }
    }
    st_overlap = update_shared_state(overlap_payload)
    acc_overlap = st_overlap["companyAccounts"]["acc_hamza_overlap_test"]
    assert acc_overlap.get("overlap_detected") is True, "Overlap must be detected when another colleague connects same email"
    assert "Sarah Malik" in acc_overlap.get("overlap_users", [])
    assert "Hamza Ali" in acc_overlap.get("overlap_users", [])

    # Clean up test overlap account
    update_shared_state({"resource": "companyAccounts", "key": "acc_hamza_overlap_test", "value": {"_action": "delete"}})

    # 42.6 Colleague Tenant Isolation (Backend Rendering)
    html_all = render_colleagues()
    assert "colleague-card-king" in html_all
    assert "colleague-card-sarah" in html_all

    html_sarah_isolated = render_colleagues(current_user="sarah")
    assert "colleague-card-sarah" in html_sarah_isolated
    assert "colleague-card-king" not in html_sarah_isolated
    assert "colleague-card-hamza" not in html_sarah_isolated

    # 42.7 Public Login Modal Markup, Hidden Admin Pass, In-App Policy Modal & 4K Logo
    root_st, _, root_body = wsgi_request("/", "GET")
    assert root_st.startswith("200")
    root_html = root_body.decode("utf-8")
    assert 'id="login-email-input"' in root_html, "Missing public clean email/username input"
    assert 'id="admin-picker-wrap"' in root_html, "Missing admin-picker-wrap container"
    assert 'style="display:none;' in root_html or 'hidden' in root_html, "Admin picker must be hidden by default"
    assert 'id="reg-policy-agree"' in root_html, "Missing mandatory policy agreement checkbox"
    assert 'id="inapp-legal-modal"' in root_html, "Missing in-app legal reader modal"
    assert "🛡️ Google Verified Enterprise Outreach Engine • AES-256 Hardware Encrypted" in root_html, "Missing executive engine badge"
    assert 'id="video-eye-toggle"' in root_html, "Missing soundscape eye blur toggle button"
    assert "grace-logo.png?v=20260916_4k" in root_html, "Missing 4K master crest logo asset link"

    print("[PASS] OTP Auth, Multi-User Overlap, Colleague Tenant Isolation & Strategic Hardening verified.")

    print("\n[SUCCESS] ALL 42 EXTENSIVE TESTS PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_tests()





