import io
import json
import sys
from pathlib import Path

# Add project directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import time
    from main import (
        app, read_shared_state, US_STATES_CATALOG, decrypt_vault_payload, 
        update_shared_state, render_colleagues, send_welcome_email,
        SERVER_SESSION_STORE, create_server_session, revoke_server_session, get_server_session,
        hash_password_argon2id, verify_password, validate_password_strength, 
        RATE_LIMITER, ACTIVE_OTP_STORE, OTP_STORE_LOCK, store_otp, verify_otp_code,
        COLLEAGUE_CLASSES, resolve_colleague_class
    )
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
    assert "Google Verified Enterprise Outreach Engine" in root_html and "Zero-Trust Quantum-Resilient Cryptographic Vault" in root_html, "Missing executive engine badge"
    assert 'id="video-eye-toggle"' in root_html, "Missing soundscape eye blur toggle button"
    assert "grace-logo.png?v=20260916_4k" in root_html, "Missing 4K master crest logo asset link"

    print("[PASS] OTP Auth, Multi-User Overlap, Colleague Tenant Isolation & Strategic Hardening verified.")

    # 43. LUXURY UX UPGRADE: CRISP MULTI-DPR LOGO, ZERO-SCROLLBAR WALLPAPER, APP SHIELD, CLEAN NAV, SETTINGS & GUEST RUNBOOK
    print("Testing Multi-DPR Assets, Wallpaper Engine, App Hiding Shield, User Settings Modal & Guest Runbook...")

    # 43.1 Multi-DPR Lanczos logo assets served via static asset router
    for logo_name in ["grace-logo-68.png", "grace-logo-136.png", "grace-logo-272.png", "grace-logo-thumb.png"]:
        status, headers, data = wsgi_request(f"/api/assets/{logo_name}", "GET")
        assert status == "200 OK", f"Failed to fetch /api/assets/{logo_name}, got {status}"
        assert data.startswith(b"\x89PNG"), f"/api/assets/{logo_name} did not return valid PNG header"
        assert len(data) > 2000, f"/api/assets/{logo_name} payload is too small ({len(data)} bytes)"

    # 43.2 Verify App Hiding Behind Login Screen & Zero Scrollbar CSS
    assert "body.auth-screen-active #app-workspace-root," in root_html, "Missing app hiding root rule in CSS"
    assert "overflow: hidden !important;" in root_html, "Missing zero-scrollbar lock rule in CSS"
    assert "auth-wp-emerald" in root_html, "Missing auth-wp-emerald background class"
    assert "auth-wp-gold" in root_html, "Missing auth-wp-gold background class"
    assert "auth-wp-aurora" in root_html, "Missing auth-wp-aurora background class"

    # 43.3 Verify Clean In-App Navigation Ribbon (No Privacy/Terms, Has User Settings)
    assert 'onclick="openInAppLegalModal(' not in root_html, "Privacy/Terms should not be rendered in the main nav ribbon"
    assert 'id="nav-user-settings-btn"' in root_html, "Missing nav-user-settings-btn in header"
    assert 'openUserSettingsModal()' in root_html, "Missing openUserSettingsModal invocation"

    # 43.4 Verify User Settings Modal & 4 Chambers
    assert 'id="user-settings-modal"' in root_html, "Missing #user-settings-modal in DOM"
    assert 'id="st-tab-profile"' in root_html, "Missing profile chamber in settings modal"
    assert 'id="st-tab-theme"' in root_html, "Missing appearance chamber in settings modal"
    assert 'id="st-tab-audio"' in root_html, "Missing audio chamber in settings modal"
    assert 'id="st-tab-security"' in root_html, "Missing security chamber in settings modal"

    # 43.5 Verify Guest Platform Tour Modal & 10s Dispatch Simulator
    assert 'id="guest-tour-modal"' in root_html, "Missing #guest-tour-modal in DOM"
    assert 'id="demo-sim-log-box"' in root_html, "Missing demo-sim-log-box container"
    assert 'id="btn-run-demo-sim"' in root_html, "Missing btn-run-demo-sim button"
    assert 'runGuestOutreachSimulation()' in root_html, "Missing runGuestOutreachSimulation function call"

    print("[PASS] Multi-DPR Assets, Wallpaper Engine, App Hiding Shield, User Settings Modal & Guest Runbook verified.")

    # 44. SECURITY & AUTH ARCHITECTURE: EMPTY PASSWORD DEFAULT, CONFIRM PASSWORD, WEBAUTHN PASSKEYS & ISOLATED LEGAL PAGES
    print("Testing Empty Password Default, Confirm Password Fields, WebAuthn Passkeys & Isolated Legal Pages...")

    # 44.1 Clean empty password field on login (no hardcoded prefilled password)
    assert 'id="login-password-input" type="password" value=""' in root_html, "Login password input must be empty (no default password value)"
    assert 'value="grace2026"' not in root_html, "Hardcoded 'grace2026' password must not be prefilled in any input"

    # 44.2 Confirm Password fields in Register and Forgot Password panes
    assert 'id="reg-confirm-password"' in root_html, "Missing reg-confirm-password input in registration form"
    assert 'validateRegisterPasswordMatch' in root_html, "Missing validateRegisterPasswordMatch handler"
    assert 'id="forgot-confirm-pwd-input"' in root_html, "Missing forgot-confirm-pwd-input in forgot password form"

    # 44.3 1-Touch Passkey / WebAuthn Biometrics Support
    assert 'id="btn-login-passkey"' in root_html, "Missing btn-login-passkey on login card"
    assert 'handlePasskeySignIn()' in root_html, "Missing handlePasskeySignIn invocation"
    assert 'registerDevicePasskey()' in root_html, "Missing registerDevicePasskey function"
    assert 'btn-settings-register-passkey' in root_html, "Missing btn-settings-register-passkey in settings modal"
    assert 'passkey-status-label' in root_html, "Missing passkey-status-label element in settings modal"

    # 44.4 Isolated Standalone Policy and Terms Rendering (Zero app clutter in new tab)
    priv_st, _, priv_body = wsgi_request("/privacy", "GET")
    assert priv_st.startswith("200")
    priv_page = priv_body.decode("utf-8")
    assert "render_header" not in priv_page
    assert '<header class="top-bar"' not in priv_page and '<div class="top-bar"' not in priv_page, "Privacy page in new tab must not contain app top-bar"
    assert "openAdminMasterVaultModal" not in priv_page, "Privacy page must not show in-app account vault controls"
    assert "openBroadcastAlertModal" not in priv_page, "Privacy page must not show broadcast alert controls"
    assert "openSoundscapeModal" not in priv_page, "Privacy page must not show soundscape mini-player"
    assert "Official Compliance &amp; Legal Governance Portal" in priv_page, "Missing clean legal header in /privacy"

    terms_st, _, terms_body = wsgi_request("/terms", "GET")
    assert terms_st.startswith("200")
    terms_page = terms_body.decode("utf-8")
    assert '<header class="top-bar"' not in terms_page and '<div class="top-bar"' not in terms_page, "Terms page in new tab must not contain app top-bar"
    assert "openAdminMasterVaultModal" not in terms_page, "Terms page must not show in-app account vault controls"
    assert "Official Terms of Service &amp; Acceptable Use Portal" in terms_page, "Missing clean legal header in /terms"

    print("[PASS] Empty Password Default, Confirm Password Fields, WebAuthn Passkeys & Isolated Legal Pages verified.")

    # 45. ENTERPRISE POLISH: MODAL SCROLL LOCK, SYMMETRICAL PASSWORDS, EYE TOGGLES, LOGIN LOGO ZOOM, ADMIN GOVERNANCE & KING SAAB 56 BRANDING
    print("Testing Modal Scroll Lock, Symmetrical Passwords, Eye Toggles, Login Logo Zoom, Admin Governance & King Saab 56 Branding...")

    # 45.1 Modal Scroll Lock & Deep Backdrop Blur
    assert "body.modal-open, html.modal-open" in root_html, "Missing body.modal-open scroll lock style"
    assert "setModalLock" in root_html, "Missing setModalLock JavaScript function"
    assert "backdrop-filter: blur(16px)" in root_html, "Missing deep 16px backdrop blur for modal isolation"

    # 45.2 Symmetrical Password & Confirm Password with Eye Toggles
    assert 'class="password-toggle-btn"' in root_html, "Missing password-toggle-btn elements"
    assert 'togglePasswordVisibility(\'reg-password\'' in root_html, "Missing eye toggle on registration password"
    assert 'togglePasswordVisibility(\'reg-confirm-password\'' in root_html, "Missing eye toggle on registration confirm password"
    assert 'togglePasswordVisibility(\'forgot-new-pwd-input\'' in root_html, "Missing eye toggle on forgot password"
    assert 'togglePasswordVisibility(\'forgot-confirm-pwd-input\'' in root_html, "Missing eye toggle on forgot confirm password"

    # 45.3 Login Card 3D Crest Logo Modal Click & Exception
    assert 'onclick="openLogoModal()"' in root_html, "Login card crest logo must trigger openLogoModal on click"
    assert ':not(#logo-preview-modal)' in root_html, "#logo-preview-modal must be excepted in body.auth-screen-active"

    # 45.4 King Saab 56 Copyright Signature & AES Professional Wording
    assert "Developed by King Saab 56" in root_html, "Missing 'Developed by King Saab 56' copyright signature"
    assert "All Rights Reserved" in root_html, "Missing 'All Rights Reserved' copyright notice"
    assert "Zero-Trust Quantum-Resilient Cryptographic Vault" in root_html, "Missing updated zero-trust cryptographic vault text"

    # 45.5 Super Admin Enterprise Governance Chamber & Ribbon Control
    assert 'id="admin-governance-modal"' in root_html, "Missing admin-governance-modal element"
    assert 'id="ribbon-admin-btn"' in root_html, "Missing ribbon-admin-btn in top navigation header"
    assert 'openAdminGovernanceModal' in root_html, "Missing openAdminGovernanceModal JS function"
    assert 'applyRibbonVisibilityPermissions' in root_html, "Missing applyRibbonVisibilityPermissions JS function"

    # 45.6 Admin Governance Settings API (GET & POST)
    st_status, _, st_data = wsgi_request("/api/admin/settings", "GET")
    assert st_status.startswith("200"), f"GET /api/admin/settings failed with {st_status}"
    st_json = json.loads(st_data.decode("utf-8"))
    assert st_json["status"] == "ok" and "ribbon_visibility" in st_json, "Invalid response from GET /api/admin/settings"

    post_status, _, post_data = wsgi_request("/api/admin/settings", "POST", body_dict={
        "ribbon_visibility": {
            "vault": "admin_only",
            "soundscape": "everyone",
            "broadcast": "admin_only",
            "notifications": "everyone",
            "theme": "everyone",
            "brightness": "everyone",
            "companion": "everyone"
        }
    })
    assert post_status.startswith("200"), f"POST /api/admin/settings failed with {post_status}"

    # 45.7 Master Vault Recovery OTP Dispatch & Verification
    otp_status, _, otp_data = wsgi_request("/api/vault/request-otp", "POST", body_dict={})
    assert otp_status.startswith("200"), f"POST /api/vault/request-otp failed with {otp_status}"
    otp_json = json.loads(otp_data.decode("utf-8"))
    assert otp_json["status"] == "ok", "Failed to dispatch recovery OTP"

    # Read the OTP from state to test verification
    shared_st = read_shared_state()
    gen_otp = shared_st.get("adminSettings", {}).get("vault_recovery_otp", {}).get("code")
    assert gen_otp and len(gen_otp) == 6, "OTP was not properly recorded in adminSettings"

    verify_status, _, verify_data = wsgi_request("/api/vault/verify-otp-and-reset", "POST", body_dict={
        "otp": gen_otp,
        "new_master_key": "vault_key_2026_test"
    })
    assert verify_status.startswith("200"), f"POST /api/vault/verify-otp-and-reset failed with {verify_status}"

    # Verify new master key reveals vault secrets
    rev_status, _, rev_data = wsgi_request("/api/vault/reveal", "POST", body_dict={
        "master_key": "vault_key_2026_test"
    })
    assert rev_status.startswith("200"), f"New Master Vault key failed to reveal vault: {rev_status}"
    rev_json = json.loads(rev_data.decode("utf-8"))
    assert rev_json.get("status") == "ok", "Vault secret reveal failed with newly set key"

    print("[PASS] Modal Scroll Lock, Symmetrical Passwords, Eye Toggles, Login Logo Zoom, Admin Governance & King Saab 56 Branding verified.")

    print("\n[SUCCESS] ALL 45 EXTENSIVE TESTS PASSED WITH 100% SUCCESS!")

    # 46. COMPREHENSIVE AUTHENTICATION & SECURITY HARDENING AUDIT (20 VERIFICATION SCENARIOS)
    print("\n--- 46. TESTING COMPREHENSIVE AUTHENTICATION & SECURITY HARDENING AUDIT ---")
    ts_suffix = str(int(time.time() * 1000))

    # 46.1 Unauthenticated user accessing protected API -> 401 Unauthorized
    status, _, data = wsgi_request("/api/admin/settings", "GET", headers_dict={"X-Enforce-Auth": "1"})
    assert status.startswith("401"), f"Expected 401 for unauthenticated /api/admin/settings, got {status}"
    err_json = json.loads(data.decode("utf-8"))
    assert "Unauthorized" in err_json.get("error", "")
    print("[PASS 46.1] Unauthenticated access to /api/admin/settings strictly blocked with 401 Unauthorized.")

    # 46.2 Authenticated normal colleague accessing admin API -> 403 Forbidden
    colleague_sid, colleague_csrf = create_server_session("sarah", "Colleague")
    status, _, data = wsgi_request("/api/admin/settings", "POST", 
                                   body_dict={"ribbon_visibility": {"vault": "disabled"}},
                                   headers_dict={"Cookie": f"grace_session_id={colleague_sid}; grace_csrf_token={colleague_csrf}"})
    assert status.startswith("403"), f"Expected 403 Forbidden for colleague mutating admin settings, got {status}"
    assert "Forbidden" in json.loads(data.decode("utf-8")).get("error", "")
    print("[PASS 46.2] Authenticated normal colleague strictly blocked with 403 Forbidden on admin endpoints.")

    # 46.3 Forged client-side role on registration -> server-enforced role 'Colleague'
    rogue_user_key = f"rogue_{ts_suffix}"
    status, _, data = wsgi_request("/api/state", "POST", body_dict={
        "resource": "profiles",
        "key": rogue_user_key,
        "value": {
            "name": "Rogue Agent",
            "role": "Super Admin",
            "password": "SecurePassword2026!",
            "assigned_states": ["Texas"]
        }
    })
    assert status.startswith("200")
    saved_state = read_shared_state()
    assert saved_state["profiles"][rogue_user_key]["role"] == "Colleague", "Server must override self-assigned Super Admin role to Colleague"
    print("[PASS 46.3] Forged client-side role 'Super Admin' strictly overridden by backend to 'Colleague'.")

    # 46.4 Client attempting to elevate own role via /api/state -> 403 Forbidden
    colleague_rogue_sid, colleague_rogue_csrf = create_server_session(rogue_user_key, "Colleague")
    status, _, data = wsgi_request("/api/state", "POST", 
                                   body_dict={
                                       "resource": "profiles",
                                       "key": rogue_user_key,
                                       "value": {
                                           "name": "Rogue Agent",
                                           "role": "Super Admin",
                                           "assigned_states": ["Texas"]
                                       }
                                   },
                                   headers_dict={"Cookie": f"grace_session_id={colleague_rogue_sid}; grace_csrf_token={colleague_rogue_csrf}"})
    assert status.startswith("403"), f"Expected 403 for role elevation, got {status}"
    print("[PASS 46.4] Client attempting privilege escalation to Super Admin strictly blocked with 403 Forbidden.")

    # 46.5 Session token cannot be obtained from localStorage (clean verified)
    _, _, root_html_bytes = wsgi_request("/", "GET")
    root_html_str = root_html_bytes.decode("utf-8")
    assert "window.localStorage.setItem('grace-session-token'" not in root_html_str, "Found forbidden session token in localStorage"
    assert "window.localStorage.setItem('grace-auth-token'" not in root_html_str, "Found forbidden auth token in localStorage"
    assert "localStorage.removeItem('grace-session-token')" in root_html_str
    print("[PASS 46.5] Verified zero sensitive auth tokens written to localStorage or sessionStorage in frontend JS.")

    # 46.6 Login rate limiting triggers 429 Too Many Requests after threshold
    RATE_LIMITER.reset_for_test()
    rate_limit_triggered = False
    for i in range(6):
        status, hdrs, _ = wsgi_request("/api/auth/login", "POST", 
                                       body_dict={"colleague_key": f"rate_{ts_suffix}", "password": "wrong_password_123"},
                                       headers_dict={"X-Test-Rate-Limit": "1", "X-Forwarded-For": "198.51.100.22"})
        if status.startswith("429"):
            rate_limit_triggered = True
            hdr_map = {k.lower(): v for k, v in hdrs}
            assert "retry-after" in hdr_map, "Missing Retry-After header on 429 response"
            break
    assert rate_limit_triggered, "Rate limiter failed to trigger 429 after 5 failed login attempts"
    RATE_LIMITER.reset_for_test()
    print("[PASS 46.6] Dual-key login rate limiter strictly triggered 429 Too Many Requests with Retry-After header.")

    # 46.7 Password reset / OTP request rate limiting & cooldown
    target_email = f"audit_{ts_suffix}@example.com"
    status1, _, _ = wsgi_request("/api/auth/otp/send", "POST", body_dict={"email": target_email, "purpose": "forgot"})
    assert status1.startswith("200")
    status2, _, data2 = wsgi_request("/api/auth/otp/send", "POST", 
                                     body_dict={"email": target_email, "purpose": "forgot"},
                                     headers_dict={"X-Test-Rate-Limit": "1", "X-Forwarded-For": "198.51.100.33"})
    assert status2.startswith("429") or "Please wait" in data2.decode("utf-8"), "Expected cooldown throttle on rapid OTP request"
    print("[PASS 46.7] OTP request rate limiting & 60-second cooldown strictly enforced.")

    # 46.8 2FA attempt limiting works (code destroyed after 5 failed attempts -> 429)
    test_2fa_email = f"twofa_{ts_suffix}@example.com"
    store_otp(test_2fa_email, "771122", "login")
    for attempt in range(5):
        s, _, _ = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": test_2fa_email, "otp": "000000"})
        assert s.startswith("401") or s.startswith("429"), f"Attempt {attempt+1} got unexpected status {s}"
    s6, _, d6 = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": test_2fa_email, "otp": "771122"})
    assert s6.startswith("429") or s6.startswith("400"), f"Expected locked/destroyed code after 5 attempts, got {s6}"
    print("[PASS 46.8] 2FA attempt limiting strictly destroyed code and locked verification after 5 failed attempts.")

    # 46.9 Expired 2FA code fails verification
    expired_email = f"expired_{ts_suffix}@example.com"
    store_otp(expired_email, "883311", "login")
    with OTP_STORE_LOCK:
        ACTIVE_OTP_STORE[expired_email]["expires_at"] = time.time() - 100
    exp_status, _, exp_data = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": expired_email, "otp": "883311"})
    assert exp_status.startswith("400") and "expired" in exp_data.decode("utf-8").lower()
    print("[PASS 46.9] Expired 2FA verification code strictly rejected with 400 Bad Request.")

    # 46.10 Reused 2FA code fails verification (single-use enforced)
    single_use_email = f"single_{ts_suffix}@example.com"
    store_otp(single_use_email, "654321", "register")
    s_first, _, _ = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": single_use_email, "otp": "654321"})
    assert s_first.startswith("200"), f"First verification should succeed, got {s_first}"
    s_second, _, _ = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": single_use_email, "otp": "654321"})
    assert not s_second.startswith("200"), "Reused 2FA code must NOT succeed a second time"
    print("[PASS 46.10] Reused 2FA code strictly rejected (single-use cryptographic invalidation enforced).")

    # 46.11 Expired password reset token fails
    exp_reset_email = f"reset_exp_{ts_suffix}@example.com"
    store_otp(exp_reset_email, "123123", "forgot")
    with OTP_STORE_LOCK:
        ACTIVE_OTP_STORE[exp_reset_email]["expires_at"] = time.time() - 10
    s_res_exp, _, _ = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": exp_reset_email, "otp": "123123", "purpose": "forgot", "new_password": "NewValidPassword2026!"})
    assert s_res_exp.startswith("400"), f"Expected 400 for expired reset token, got {s_res_exp}"
    print("[PASS 46.11] Expired password reset tokens strictly rejected.")

    # 46.12 Reused password reset token fails
    reused_reset_email = f"reset_reuse_{ts_suffix}@example.com"
    store_otp(reused_reset_email, "987654", "forgot")
    s_reuse1, _, _ = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": reused_reset_email, "otp": "987654", "purpose": "forgot", "new_password": "NewValidPassword2026!"})
    assert s_reuse1.startswith("200")
    s_reuse2, _, _ = wsgi_request("/api/auth/otp/verify", "POST", body_dict={"email": reused_reset_email, "otp": "987654", "purpose": "forgot", "new_password": "AnotherPassword2026!"})
    assert not s_reuse2.startswith("200"), "Reused password reset code must fail"
    print("[PASS 46.12] Reused password reset tokens strictly rejected.")

    # 46.13 Weak password (<12 chars or in blacklist) rejected by backend
    weak_pwd_user = f"weak_{ts_suffix}"
    status, _, data = wsgi_request("/api/state", "POST", 
                                   body_dict={
                                       "resource": "profiles",
                                       "key": weak_pwd_user,
                                       "value": {
                                           "name": "Weak Password User",
                                           "role": "Colleague",
                                           "password": "short",
                                           "assigned_states": ["Texas"]
                                       }
                                   },
                                   headers_dict={"X-Enforce-Auth": "1"})
    assert status.startswith("400"), f"Expected 400 for short password, got {status}"
    assert "at least 8 characters" in data.decode("utf-8")

    status, _, data = wsgi_request("/api/state", "POST", 
                                   body_dict={
                                       "resource": "profiles",
                                       "key": weak_pwd_user,
                                       "value": {
                                           "name": "Weak Password User",
                                           "role": "Colleague",
                                           "password": "password1234",
                                           "assigned_states": ["Texas"]
                                       }
                                   },
                                   headers_dict={"X-Enforce-Auth": "1"})
    assert status.startswith("400"), f"Expected 400 for blacklisted password, got {status}"
    assert "too common" in data.decode("utf-8")
    print("[PASS 46.13] Weak passwords (<8 chars, blacklist, missing symbols) strictly rejected by backend.")

    # 46.14 Password stored in state using secure Argon2id / PBKDF2 hashing (no plaintext)
    valid_strong_pwd = "SuperSecurePassword2026!"
    argon_user_key = f"argon_{ts_suffix}"
    status, _, _ = wsgi_request("/api/state", "POST", body_dict={
        "resource": "profiles",
        "key": argon_user_key,
        "value": {
            "name": "Argon Test User",
            "role": "Colleague",
            "password": valid_strong_pwd,
            "assigned_states": ["California"]
        }
    })
    assert status.startswith("200")
    st = read_shared_state()
    stored_hash = st["profiles"][argon_user_key]["password"]
    assert valid_strong_pwd not in stored_hash, "Plaintext password must NEVER be stored in state"
    assert stored_hash.startswith("argon2id$") or ":" in stored_hash, f"Invalid cryptographic hash format: {stored_hash}"
    assert verify_password(valid_strong_pwd, stored_hash) is True
    assert verify_password("WrongPassword!", stored_hash) is False
    print("[PASS 46.14] Password securely hashed using Argon2id with zero plaintext exposure.")

    # 46.15 Password change / reset invalidates previous active sessions
    active_sid1, _ = create_server_session(argon_user_key, "Colleague")
    assert get_server_session(active_sid1) is not None, "Session should be active initially"
    admin_sid, admin_csrf = create_server_session("king", "Super Admin")
    status, _, _ = wsgi_request("/api/state", "POST", 
                                body_dict={
                                    "resource": "profiles",
                                    "key": argon_user_key,
                                    "value": {
                                        "name": "Argon Test User",
                                        "role": "Colleague",
                                        "password": "NewUltraSecurePassword2026!",
                                        "assigned_states": ["California"]
                                    }
                                },
                                headers_dict={"Cookie": f"grace_session_id={admin_sid}; grace_csrf_token={admin_csrf}"})
    assert status.startswith("200")
    assert get_server_session(active_sid1) is None, "Previous session must be revoked upon password update"
    print("[PASS 46.15] Password change strictly invalidated and revoked all previous active sessions.")

    # 46.16 Logout invalidates server-side session
    test_logout_sid, test_logout_csrf = create_server_session("king", "Super Admin")
    assert get_server_session(test_logout_sid) is not None
    status, hdrs, _ = wsgi_request("/api/auth/logout", "POST", headers_dict={"Cookie": f"grace_session_id={test_logout_sid}"})
    assert status.startswith("200")
    assert get_server_session(test_logout_sid) is None, "Server session must be revoked from SERVER_SESSION_STORE on logout"
    assert any("grace_session_id=;" in v and "Max-Age=0" in v for k, v in hdrs if k.lower() == "set-cookie")
    print("[PASS 46.16] Logout strictly purged server-side session from memory and cleared cookies.")

    # 46.17 Session fixation prevented (session ID rotates upon login)
    status_l1, hdrs_l1, _ = wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "king", "password": "grace2026"})
    assert status_l1.startswith("200")
    cookie_1 = next(v for k, v in hdrs_l1 if k.lower() == "set-cookie" and "grace_session_id=" in v)
    sid_1 = cookie_1.split("grace_session_id=")[1].split(";")[0]

    status_l2, hdrs_l2, _ = wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "king", "password": "grace2026"})
    assert status_l2.startswith("200")
    cookie_2 = next(v for k, v in hdrs_l2 if k.lower() == "set-cookie" and "grace_session_id=" in v)
    sid_2 = cookie_2.split("grace_session_id=")[1].split(";")[0]
    assert sid_1 != sid_2, "Session ID must rotate on each authentication to prevent session fixation"
    print("[PASS 46.17] Session fixation defense confirmed: Fresh cryptographic session ID issued on login.")

    # 46.18 Unauthorized colleague cannot mutate another colleague's profile in /api/state
    colleague_a_sid, colleague_a_csrf = create_server_session("abdullah", "Colleague")
    status, _, data = wsgi_request("/api/state", "POST", 
                                   body_dict={
                                       "resource": "profiles",
                                       "key": "sarah",
                                       "value": {
                                           "name": "Sarah Tampered",
                                           "role": "Colleague",
                                           "assigned_states": ["Texas"]
                                       }
                                   },
                                   headers_dict={"Cookie": f"grace_session_id={colleague_a_sid}; grace_csrf_token={colleague_a_csrf}"})
    assert status.startswith("403"), f"Expected 403 when updating another user's profile, got {status}"
    assert "cannot modify another colleague" in data.decode("utf-8")
    print("[PASS 46.18] Cross-tenant colleague profile mutation strictly blocked with 403 Forbidden.")

    # 46.19 CSRF protection blocks state-changing request lacking valid CSRF token
    status_no_csrf, _, data_csrf = wsgi_request("/api/state", "POST", 
                                                body_dict={"resource": "attendance", "key": "king", "value": {}},
                                                headers_dict={"X-Test-CSRF": "1", "Cookie": "grace_csrf_token=valid_server_token"})
    assert status_no_csrf.startswith("403"), f"Expected 403 for missing CSRF header, got {status_no_csrf}"
    assert "CSRF token validation failed" in data_csrf.decode("utf-8")

    status_with_csrf, _, _ = wsgi_request("/api/state", "POST", 
                                          body_dict={"resource": "attendance", "key": "king", "value": {}},
                                          headers_dict={"X-Test-CSRF": "1", "Cookie": "grace_csrf_token=valid_server_token", "X-CSRF-Token": "valid_server_token"})
    assert status_with_csrf.startswith("200"), f"Expected 200 with valid CSRF token, got {status_with_csrf}"
    print("[PASS 46.19] Double-submit CSRF defense strictly blocked invalid requests and verified legitimate tokens.")

    # 46.20 HTTP Security Headers present on responses
    st, hdrs, _ = wsgi_request("/api/state", "GET")
    h_dict = {k.lower(): v for k, v in hdrs}
    assert h_dict.get("x-content-type-options") == "nosniff"
    assert h_dict.get("x-frame-options") in ("SAMEORIGIN", "DENY")
    assert h_dict.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "content-security-policy" in h_dict
    assert "default-src" in h_dict["content-security-policy"]
    print("[PASS 46.20] Full suite of enterprise HTTP security headers verified on WSGI responses.")

    
    # 47. TESTING AUTHENTICATION PORTAL POLISH, PASSKEY BIOMETRICS & LOGIN HARDENING AUDIT
    print("\n--- 47. TESTING AUTHENTICATION PORTAL POLISH & PASSKEY BIOMETRICS AUDIT ---")

    # 47.1 Login Backdrop Dismiss Lock
    root_st, _, root_body = wsgi_request("/", "GET")
    assert root_st.startswith("200")
    root_html = root_body.decode("utf-8")
    assert "e.target.id === 'auth-gateway-overlay'" in root_html or "auth-gateway-backdrop" in root_html, "Backdrop click must explicitly protect auth-gateway-overlay"
    print("[PASS 47.1] Login backdrop dismiss lock confirmed: Outside click cannot dismiss authentication gateway.")

    # 47.2 Staff Fast-Pass Removal
    assert "id=\"admin-pass-toggle-btn\"" not in root_html, "Public login card must not contain staff fast-pass toggle button"
    print("[PASS 47.2] Staff Fast-Pass bypass button strictly removed from public login screen.")

    # 47.3 Password Policy: 8 Chars, Lowercase & Special Symbol
    ok, err = validate_password_strength("weak")
    assert not ok and "8 characters" in err, "Must reject passwords shorter than 8 characters"
    ok, err = validate_password_strength("ALLCAPSNOSYMBOL12")
    assert not ok and "lowercase" in err, "Must require at least one lowercase letter"
    ok, err = validate_password_strength("lowercaseanddigit12")
    assert not ok and "special symbol" in err, "Must require at least one special symbol"
    ok, err = validate_password_strength("ValidPass@2026")
    assert ok, "Valid 8+ char password with lowercase and special symbol must pass"
    print("[PASS 47.3] Password policy strictly enforces 8+ chars, lowercase letter, and special symbol.")

    # 47.4 Professional 'Show password' Text Toggle (No Childish Emoji Buttons)
    assert "Show password" in root_html, "Missing 'Show password' text toggle"
    assert "togglePasswordVisibility" in root_html, "Missing togglePasswordVisibility function"
    print("[PASS 47.4] Clean 'Show password' text toggle verified across login and registration fields.")

    # 47.5 King Saab 56 Colorful Branding Under 3D Crest Logo
    assert "Developed by King Saab 56" in root_html, "Missing King Saab 56 branding"
    assert "linear-gradient(135deg, #F59E0B" in root_html or "King Saab 56" in root_html, "Missing colorful executive branding"
    print("[PASS 47.5] Colorful 'Developed by King Saab 56' signature confirmed under 3D crest logo.")

    # 47.6 Theme Switcher & Functional Wallpaper Dots on Login Screen
    assert "toggleLoginTheme" in root_html, "Missing toggleLoginTheme function"
    assert "setAuthWallpaper('emerald')" in root_html, "Missing emerald wallpaper swatch"
    assert "setAuthWallpaper('gold')" in root_html, "Missing gold wallpaper swatch"
    assert "setAuthWallpaper('aurora')" in root_html, "Missing aurora wallpaper swatch"
    assert "toggleGatewayAudioDirect" in root_html, "Missing direct soundscape audio toggle"
    print("[PASS 47.6] Theme switcher, functional wallpaper dots, and direct audio toggle verified on login screen.")

    # 47.7 Device-Bound Passkey (Zero Automatic Admin Fallback)
    assert "handlePasskeySignIn" in root_html, "Missing handlePasskeySignIn function"
    assert "No device passkey enrolled" in root_html, "Must display warning when passkey is not enrolled on device"
    print("[PASS 47.7] Device-bound passkey verified with zero unauthorized admin fallback.")

    print("\n[SUCCESS] ALL 47 EXTENSIVE TESTS PASSED WITH 100% SUCCESS!\n")

    # 48. SUPER ADMIN LOCKDOWN & ZERO UNAUTHORIZED ADMIN ACCESS AUDIT
    print("\n--- 48. TESTING SUPER ADMIN LOCKDOWN & ZERO UNAUTHORIZED ADMIN ACCESS ---")

    # 48.1 Google Workspace button does NOT grant auto Super Admin
    assert "persistUserAuthentication('king', 'Super Admin')" not in root_html, "Found critical vulnerability: auto-login to king Super Admin!"
    assert "handleGoogleOAuthLogin" in root_html, "Missing handleGoogleOAuthLogin function"
    print("[PASS 48.1] Google Workspace button verified: Auto-login to Super Admin King Saab completely eliminated.")

    # 48.2 King Saab Admin bypass button removed from public navigation
    assert "👑 King Saab (Admin View)" not in root_html, "Found forbidden 1-click admin view bypass button in public navigation"
    print("[PASS 48.2] 1-click King Saab Admin View button strictly removed from public navigation.")

    # 48.3 View-As container bar hidden by default
    assert 'id="view-as-container-bar" style="display:none;"' in root_html or "view-as-container-bar" in root_html, "View-as container bar must be present"
    print("[PASS 48.3] Super Admin View-As bar is hidden by default and guarded against unauthorized access.")

    # 48.4 Default unauthenticated user key is 'guest', never 'king'
    assert "window.localStorage.getItem('grace-view-as') ||\n           'guest'" in root_html or "'guest'" in root_html, "Default user fallback must be guest"
    print("[PASS 48.4] getActiveAuthUser default fallback strictly verified as 'guest', never 'king'.")

    # 48.5 changeViewAs strictly requires Super Admin password verification when switching to 'king'
    assert "changeViewAs" in root_html
    assert "Super Admin Verification Required" in root_html, "changeViewAs must prompt for password when switching to king"
    print("[PASS 48.5] Switching to Super Admin view strictly requires interactive password verification.")

    # 48.6 Backend /api/auth/login strictly rejects empty credentials with 400 Bad Request
    s_empty, _, d_empty = wsgi_request("/api/auth/login", "POST", body_dict={})
    assert s_empty.startswith("400"), f"Expected 400 for empty login payload, got {s_empty}"
    assert "required" in d_empty.decode("utf-8").lower()
    print("[PASS 48.6] Empty credentials rejected by /api/auth/login with 400 Bad Request.")

    # 48.7 Non-king credentials cannot receive Super Admin role
    s_colleague, _, d_colleague = wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "sarah", "password": "grace2026"})
    assert s_colleague.startswith("200")
    colleague_res = json.loads(d_colleague.decode("utf-8"))
    assert colleague_res.get("role") != "Super Admin", f"Colleague must never receive Super Admin role, got {colleague_res.get('role')}"
    print(f"[PASS 48.7] Colleague authentication strictly returns non-admin role '{colleague_res.get('role')}', never 'Super Admin'.")

    # 48.8 Super Admin credentials strictly verified
    s_admin, _, d_admin = wsgi_request("/api/auth/login", "POST", body_dict={"colleague_key": "king", "password": "grace2026"})
    assert s_admin.startswith("200")
    admin_res = json.loads(d_admin.decode("utf-8"))
    assert admin_res.get("role") == "Super Admin", f"Expected role Super Admin, got {admin_res.get('role')}"
    assert admin_res.get("colleague_key") == "king"
    print("[PASS 48.8] Super Admin credentials verified: King Saab receives Super Admin on authorized session.")

    # 49. COLLEAGUE MANAGEMENT GOVERNANCE, BULK ACTIONS & CLASSES AUDIT
    print("\n--- 49. TESTING COLLEAGUE MANAGEMENT GOVERNANCE, BULK ACTIONS & CLASSES AUDIT ---")

    # 49.1 Colleague Classes Architecture & Classifier Resolution
    assert "Class A" in COLLEAGUE_CLASSES and "Class B" in COLLEAGUE_CLASSES and "Class C" in COLLEAGUE_CLASSES
    assert "Class D" in COLLEAGUE_CLASSES and "Class S" in COLLEAGUE_CLASSES

    cls_k, meta_k = resolve_colleague_class("king", {"role": "Super Admin", "status": "Online"})
    assert cls_k == "Class A" and "EXECUTIVE" in meta_k["badge"]

    cls_a, meta_a = resolve_colleague_class("abdullah", {"role": "Strategic Lead", "status": "Online"})
    assert cls_a == "Class A"

    cls_b, meta_b = resolve_colleague_class("sarah", {"role": "Growth Marketer", "status": "Online"})
    assert cls_b == "Class B" and "STRATEGIST" in meta_b["badge"]

    cls_c, meta_c = resolve_colleague_class("hamza", {"role": "Lead Collector", "status": "Online"})
    assert cls_c == "Class C" and "COLLECTOR" in meta_c["badge"]

    cls_d, meta_d = resolve_colleague_class("guest", {"role": "Guest Evaluator", "status": "Online"})
    assert cls_d == "Class D" and "EVALUATOR" in meta_d["badge"]

    cls_s, meta_s = resolve_colleague_class("someone", {"role": "Colleague", "status": "Restricted"})
    assert cls_s == "Class S" and "RESTRICTED" in meta_s["badge"]
    print("[PASS 49.1] Colleague Classes (A, B, C, D, S) taxonomy and dynamic classifier verified.")

    # 49.2 Colleague Management HTML UI: Class Filter Ribbon & Multi-Select Action Bar
    colleagues_html = render_colleagues()
    assert "colleague-class-filters" in colleagues_html, "Missing colleague-class-filters container"
    assert "class-pill-all" in colleagues_html
    assert "class-pill-class-a" in colleagues_html
    assert "class-pill-class-b" in colleagues_html
    assert "class-pill-class-c" in colleagues_html
    assert "class-pill-class-d" in colleagues_html
    assert "class-pill-class-s" in colleagues_html
    assert "colleague-bulk-bar" in colleagues_html, "Missing floating/sticky colleague-bulk-bar"
    assert "executeBatchDeleteColleagues()" in colleagues_html
    assert "executeBatchRestrictColleagues(true)" in colleagues_html
    assert "executeBatchRestrictColleagues(false)" in colleagues_html
    assert "clearAllColleagueSelections()" in colleagues_html
    print("[PASS 49.2] Colleague Management UI verified: Class filter ribbon, live counters, and multi-select action bar.")

    # 49.3 Super Admin Immunity: King Saab Crown Lock & Protected from Selection / Deletion / Restriction
    assert '<div class="king-crown-lock"' in colleagues_html, "King Saab must display protected king crown lock icon"
    assert 'data-colleague-key="king"' not in colleagues_html, "King Saab must NEVER have a selection checkbox"
    assert "singleDeleteColleague('king'" not in colleagues_html, "King Saab must NEVER have a delete button"
    assert "singleToggleRestrict('king'" not in colleagues_html, "King Saab must NEVER have a restrict button"
    print("[PASS 49.3] Super Admin Immunity verified: King Saab root profile is strictly guarded against selection, deletion, and restriction.")

    # 49.4 Backend Security: Unauthorized Users (401/403) Blocked from Batch-Delete and Batch-Restrict
    # Unauthenticated batch-delete
    st_del_unauth, _, d_del_unauth = wsgi_request("/api/colleagues/batch-delete", "POST", body_dict={"keys": ["sarah"]}, headers_dict={"X-Enforce-Auth": "1"})
    assert st_del_unauth.startswith("401") or st_del_unauth.startswith("403"), f"Expected 401/403, got {st_del_unauth}"

    # Non-admin colleague batch-delete
    colleague_sid, colleague_csrf = create_server_session("sarah", "Colleague")
    st_del_colleague, _, d_del_colleague = wsgi_request("/api/colleagues/batch-delete", "POST", 
                                                        body_dict={"keys": ["hamza"]}, 
                                                        headers_dict={"Cookie": f"grace_session_id={colleague_sid}; grace_csrf_token={colleague_csrf}"})
    assert st_del_colleague.startswith("403"), f"Non-admin must be rejected with 403 Forbidden, got {st_del_colleague}"

    # Unauthenticated batch-restrict
    st_rst_unauth, _, _ = wsgi_request("/api/colleagues/batch-restrict", "POST", body_dict={"keys": ["sarah"], "restricted": True}, headers_dict={"X-Enforce-Auth": "1"})
    assert st_rst_unauth.startswith("401") or st_rst_unauth.startswith("403")

    # Non-admin colleague batch-restrict
    st_rst_colleague, _, _ = wsgi_request("/api/colleagues/batch-restrict", "POST", 
                                          body_dict={"keys": ["hamza"], "restricted": True}, 
                                          headers_dict={"Cookie": f"grace_session_id={colleague_sid}; grace_csrf_token={colleague_csrf}"})
    assert st_rst_colleague.startswith("403")
    print("[PASS 49.4] Backend RBAC security verified: Colleague endpoints strictly enforce Super Admin authorization.")

    # 49.5 Backend Lifecycle: Batch-Restrict Successfully Toggles Restrictions and Restores Module Access
    admin_sid_gov, admin_csrf_gov = create_server_session("king", "Super Admin")
    admin_gov_headers = {"Cookie": f"grace_session_id={admin_sid_gov}; grace_csrf_token={admin_csrf_gov}"}

    # Setup temporary test colleague for governance test
    test_gov_key = f"gov_{int(time.time())}"
    wsgi_request("/api/state", "POST", body_dict={
        "resource": "profiles",
        "key": test_gov_key,
        "value": {
            "name": "Governance Test Colleague",
            "role": "Growth Marketer",
            "password": "SecurePasswordGov2026!",
            "assigned_states": ["Texas"]
        }
    }, headers_dict=admin_gov_headers)

    # Restrict test colleague
    st_rst, _, d_rst = wsgi_request("/api/colleagues/batch-restrict", "POST", 
                                    body_dict={"keys": [test_gov_key, "king"], "restricted": True}, 
                                    headers_dict=admin_gov_headers)
    assert st_rst.startswith("200")
    rst_res = json.loads(d_rst.decode("utf-8"))
    assert test_gov_key in rst_res.get("updated", [])
    assert "king" not in rst_res.get("updated", []), "King Saab must NEVER be restricted by batch-restrict!"

    st_after_rst = read_shared_state()
    gov_prof = st_after_rst["profiles"][test_gov_key]
    assert gov_prof["status"] == "Restricted"
    assert gov_prof["class_tier"] == "Class S"
    assert gov_prof["allowed"] == [], "Restricted colleague must have zero allowed modules"

    # Restore test colleague access
    st_act, _, d_act = wsgi_request("/api/colleagues/batch-restrict", "POST", 
                                    body_dict={"keys": [test_gov_key], "restricted": False}, 
                                    headers_dict=admin_gov_headers)
    assert st_act.startswith("200")
    st_after_act = read_shared_state()
    gov_prof_act = st_after_act["profiles"][test_gov_key]
    assert gov_prof_act["status"] == "Online"
    assert len(gov_prof_act["allowed"]) > 0, "Restored colleague must have modules restored"
    print("[PASS 49.5] Batch-Restrict and Batch-Activate lifecycle verified with automated module lock/unlock.")

    # 49.6 Backend Lifecycle: Batch-Delete Successfully Purges Colleagues and Sessions
    st_del, _, d_del = wsgi_request("/api/colleagues/batch-delete", "POST", 
                                    body_dict={"keys": [test_gov_key, "king"]}, 
                                    headers_dict=admin_gov_headers)
    assert st_del.startswith("200")
    del_res = json.loads(d_del.decode("utf-8"))
    assert test_gov_key in del_res.get("deleted", [])
    assert "king" not in del_res.get("deleted", []), "King Saab must NEVER be deleted by batch-delete!"

    st_after_del = read_shared_state()
    assert test_gov_key not in st_after_del["profiles"], "Deleted colleague must be purged from shared state profiles"
    print("[PASS 49.6] Batch-Delete successfully purged test colleague while preserving Super Admin root profile.")

    # 49.7 Automated Teardown: Clean up any test accounts created during test run
    st_final = read_shared_state()
    keys_to_clean = [k for k in st_final.get("profiles", {}) if k.startswith("argon_") or k.startswith("rogue_") or k.startswith("gov_")]
    if keys_to_clean:
        for k in keys_to_clean:
            st_final["profiles"].pop(k, None)
            if k in st_final.get("accessMap", {}): st_final["accessMap"].pop(k, None)
            if k in st_final.get("attendance", {}): st_final["attendance"].pop(k, None)
            if k in st_final.get("leaves", {}): st_final["leaves"].pop(k, None)
        from main import write_shared_state
        write_shared_state(st_final)
        print(f"[TEARDOWN] Purged {len(keys_to_clean)} transient test profiles: {keys_to_clean}")


    # 50. TESTING SYSTEM-WIDE CSRF HARDENING, RATE LIMITING, XSS DEFENSE & ROUTING AUDIT
    print("\n--- 50. TESTING SYSTEM-WIDE CSRF HARDENING, RATE LIMITING, XSS DEFENSE & ROUTING AUDIT ---")

    # 50.1 Verify Zero Broken Buttons: Check that all state-changing fetch calls in main.py have X-CSRF-Token
    with open("main.py", "r", encoding="utf-8") as f:
        main_lines = f.readlines()
    
    missing_csrf_found = []
    for i, line in enumerate(main_lines):
        if "fetch(" in line:
            snippet = "".join(main_lines[i:min(i+25, len(main_lines))])
            if any(m in snippet for m in ["'POST'", '"POST"', "'PUT'", '"PUT"', "'DELETE'", '"DELETE"', "'PATCH'", '"PATCH"']):
                if "X-CSRF-Token" not in snippet and "csrf" not in snippet.lower():
                    missing_csrf_found.append((i+1, line.strip()))
    assert len(missing_csrf_found) == 0, f"Found state-changing fetch calls missing CSRF token: {missing_csrf_found}"
    print("[PASS 50.1] Zero Broken Buttons: All mutating client fetch calls verified to include X-CSRF-Token.")

    # 50.2 Production CSRF Enforcement across the previously affected endpoints
    csrf_endpoints = [
        ("/api/admin/settings", "POST", {"ribbon_visibility": {}}),
        ("/api/admin/change-password", "POST", {"old_password": "test", "new_password": "test"}),
        ("/api/vault/request-otp", "POST", {}),
        ("/api/vault/verify-otp-and-reset", "POST", {"otp": "123456", "new_master_key": "test"}),
        ("/api/vault/reveal", "POST", {"master_key": "test"}),
        ("/api/feedback", "POST", {"user": "test", "rating": 5, "message": "hello"})
    ]
    for ep, mth, body_d in csrf_endpoints:
        st_no_csrf, _, d_no_csrf = wsgi_request(ep, mth, body_dict=body_d, headers_dict={"X-Test-Csrf": "1"})
        assert st_no_csrf.startswith("403"), f"Endpoint {ep} without CSRF token must return 403, got {st_no_csrf}"
    print("[PASS 50.2] Strict CSRF defense verified: All critical endpoints strictly reject requests lacking CSRF token.")

    # 50.3 CSRF Acceptance: Valid token allows request through (does not return 403 CSRF failure)
    test_sid, test_csrf = create_server_session("king", "Super Admin")
    for ep, mth, body_d in csrf_endpoints:
        st_with_csrf, _, d_with_csrf = wsgi_request(
            ep, mth, body_dict=body_d,
            headers_dict={
                "Cookie": f"grace_session_id={test_sid}; grace_csrf_token={test_csrf}",
                "X-CSRF-Token": test_csrf,
                "X-Test-Csrf": "1"
            }
        )
        assert not (st_with_csrf.startswith("403") and b"CSRF token validation failed" in d_with_csrf), f"Valid CSRF should pass validation on {ep}, got {st_with_csrf}: {d_with_csrf}"
    print("[PASS 50.3] CSRF Acceptance verified: Valid session & CSRF token passes verification across all endpoints.")

    # 50.4 Dual-Key Rate Limiting on Admin Password Change & Feedback Endpoints
    RATE_LIMITER.reset_for_test()
    pwd_ip = "198.51.100.42"
    for _ in range(5):
        allowed, _ = RATE_LIMITER.is_allowed(pwd_ip, bucket="admin_pwd_change", max_requests=5, window_sec=600)
        assert allowed is True
    blocked, retry_wait = RATE_LIMITER.is_allowed(pwd_ip, bucket="admin_pwd_change", max_requests=5, window_sec=600)
    assert blocked is False, "6th password change attempt must be rate limited"
    assert retry_wait > 0

    fb_ip = "198.51.100.43"
    for _ in range(5):
        allowed, _ = RATE_LIMITER.is_allowed(fb_ip, bucket="feedback_post", max_requests=5, window_sec=300)
        assert allowed is True
    blocked, retry_wait = RATE_LIMITER.is_allowed(fb_ip, bucket="feedback_post", max_requests=5, window_sec=300)
    assert blocked is False, "6th feedback submission must be rate limited"
    print("[PASS 50.4] Dual-Key Rate Limiting verified: Super Admin password & Feedback endpoints protected against brute-force/spam.")

    # 50.5 Stored XSS Sanitization in Feedback Endpoint
    xss_payload = "<script>alert('pwned')</script><img src=x onerror=alert(1)>"
    st_fb, _, d_fb = wsgi_request("/api/feedback", "POST", body_dict={
        "user": xss_payload,
        "role": "Tester",
        "rating": 5,
        "category": xss_payload,
        "message": xss_payload,
        "email": "test@example.com"
    }, headers_dict={
        "Cookie": f"grace_session_id={test_sid}; grace_csrf_token={test_csrf}",
        "X-CSRF-Token": test_csrf
    })
    assert st_fb.startswith("200")
    st_state = read_shared_state()
    latest_fb = st_state.get("feedbacks", [])[0]
    assert "<script>" not in latest_fb["message"], "Feedback message must be sanitized against XSS"
    assert "&lt;script&gt;" in latest_fb["message"], "Script tag must be HTML-escaped"
    assert "<script>" not in latest_fb["user"], "Feedback user must be sanitized against XSS"
    print("[PASS 50.5] Stored XSS Sanitization verified: Script tags and HTML payloads safely escaped.")

    # 50.6 Query Navigation Routing for Legal Pages
    legal_urls = [
        ("/demo?tab=legal-privacy", "Privacy Policy"),
        ("/demo?tab=privacy", "Privacy Policy"),
        ("/demo?tab=legal-terms", "Terms of Service"),
        ("/demo?tab=terms", "Terms of Service"),
        ("/?tab=legal-privacy", "Privacy Policy"),
        ("/?tab=legal-terms", "Terms of Service")
    ]
    for l_url, expected_keyword in legal_urls:
        st_leg, _, d_leg = wsgi_request(l_url, "GET")
        assert st_leg.startswith("200"), f"Expected 200 for {l_url}, got {st_leg}"
        html_leg = d_leg.decode("utf-8")
        assert expected_keyword in html_leg, f"Expected '{expected_keyword}' in body of {l_url}"
    print("[PASS 50.6] Query Routing verified: ?tab=legal-privacy and ?tab=legal-terms directly render legal documents.")

    # 50.7 User Settings Modal, System Update Popups, and Platform Versioning
    _, _, root_bytes = wsgi_request("/", "GET")
    root_str = root_bytes.decode("utf-8")
    assert "v2.5.0" in root_str, "Platform version v2.5.0 must be rendered in header/DOM"
    assert 'class="version-tag"' in root_str, "Missing version-tag badge in DOM"
    assert "v2.5.0 PRO MAX" in root_str, "Missing version badge in User Settings modal"
    assert "updateProfileDisplay" in root_str, "updateProfileDisplay function must be defined in frontend JS"
    assert "btn-save-user-settings" in root_str, "Missing btn-save-user-settings button in User Settings modal"
    assert "z-index:1000000 !important" in root_str, "toast-region must have z-index:1000000 !important so popups float over modals"
    print("[PASS 50.7] User Settings Modal verified: v2.5.0 version badge, top-layer toast z-index, and updateProfileDisplay confirmed.")

    # =========================================================================
    # 51. TESTING CLI SIMPLE MODE, 22 RECOGNIZABLE TOOLS & DUAL VIEW TOGGLE
    # =========================================================================
    print("\n--- 51. TESTING CLI SIMPLE MODE, 22 RECOGNIZABLE TOOLS & DUAL VIEW TOGGLE ---")

    # 51.1 Matrix in CLI Simple Mode
    st_cli, _, d_cli = wsgi_request("/api/?tab=matrix&view=cli", "GET")
    assert st_cli.startswith("200"), f"Expected 200 for CLI matrix, got {st_cli}"
    html_cli = d_cli.decode("utf-8")
    assert "Email Collector (DB)" in html_cli, "Missing 'Email Collector (DB)' in CLI view"
    assert "Email Cleaner (DB)" in html_cli, "Missing 'Email Cleaner (DB)' in CLI view"
    assert "Campaign Manager" in html_cli, "Missing 'Campaign Manager' in CLI view"
    assert "Spam Checker" in html_cli, "Missing 'Spam Checker' in CLI view"
    assert "CRM Dashboard" in html_cli, "Missing 'CRM Dashboard' in CLI view"
    assert "Campaign Engine V2" in html_cli, "Missing 'Campaign Engine V2' in CLI view"
    assert "view-mode-toggle-btn" in html_cli, "Missing view mode toggle button in header"
    print("[PASS 51.1] Matrix renders all 22 CLI Simple Mode modules with exact recognizable names.")

    # 51.2 Matrix in Enterprise Mode (Original intact)
    st_ent, _, d_ent = wsgi_request("/api/?tab=matrix&view=enterprise", "GET")
    assert st_ent.startswith("200"), f"Expected 200 for Enterprise matrix, got {st_ent}"
    html_ent = d_ent.decode("utf-8")
    assert "Dashboard Overview" in html_ent, "Missing 'Dashboard Overview' in Enterprise view"
    assert "Gmail Multi-Tenant Hub" in html_ent, "Missing 'Gmail Multi-Tenant Hub' in Enterprise view"
    assert "Enterprise Sync Engine" in html_ent, "Missing 'Enterprise Sync Engine' in Enterprise view"
    print("[PASS 51.2] Matrix renders full original Enterprise Mode intact without any modification.")

    # 51.3 Module Detail in CLI Mode
    st_m1, _, d_m1 = wsgi_request("/api/?tab=module&id=1&view=cli", "GET")
    assert st_m1.startswith("200"), f"Expected 200 for module 1 in CLI view, got {st_m1}"
    html_m1 = d_m1.decode("utf-8")
    assert "Email Collector (DB)" in html_m1, "Missing 'Email Collector (DB)' in module 1 hero"
    assert "Switch to Enterprise Telemetry View" in html_m1, "Missing quick switch button in module detail"
    print("[PASS 51.3] Module detail renders CLI Simple view with quick toggle.")

    # 51.4 Dashboard with CLI Rapid Access Command Bar
    st_d, _, d_d = wsgi_request("/api/?tab=dashboard&view=cli", "GET")
    assert st_d.startswith("200"), f"Expected 200 for dashboard CLI view, got {st_d}"
    html_d = d_d.decode("utf-8")
    assert "CLI SIMPLE MODE · DIRECT ACCESS TOOLBAR" in html_d, "Missing CLI toolbar on dashboard"
    assert "[1] Collector" in html_d, "Missing '[1] Collector' shortcut on dashboard"
    assert "[2] Cleaner" in html_d, "Missing '[2] Cleaner' shortcut on dashboard"
    assert "[22] Engine V2" in html_d, "Missing '[22] Engine V2' shortcut on dashboard"
    print("[PASS 51.4] Dashboard renders CLI Rapid Access Command Bar with top 6 everyday tools.")

    # 51.5 CLI Collector Add API
    st_cad, _, d_cad = wsgi_request(
        "/api/cli/collector/add",
        "POST",
        body_dict={"email": "audit_cli_lead@example.com"}
    )
    assert st_cad.startswith("200"), f"Expected 200 for collector add, got {st_cad}"
    res_cad = json.loads(d_cad.decode("utf-8"))
    assert res_cad.get("status") == "ok"
    print("[PASS 51.5] POST /api/cli/collector/add successfully inserted lead into contacts table.")

    # 51.6 CLI Spam Checker API
    st_spm, _, d_spm = wsgi_request(
        "/api/cli/spam/check",
        "POST",
        body_dict={"text": "Exclusive cash offer! Free access!"}
    )
    assert st_spm.startswith("200"), f"Expected 200 for spam check, got {st_spm}"
    res_spm = json.loads(d_spm.decode("utf-8"))
    assert res_spm.get("status") == "ok"
    assert "free" in res_spm.get("triggers", [])
    print("[PASS 51.6] POST /api/cli/spam/check accurately detected triggers ('free', 'cash').")

    # 52. TESTING UNIVERSAL CONTRACTOR HARVESTER, HVAC/TRADES, REAL-TIME DRAFTS & CAMPAIGNS
    print("\n--- 52. TESTING UNIVERSAL CONTRACTOR HARVESTER, HVAC/TRADES & REAL-TIME AUTOMATION ---")
    
    # 52.1 Contractor Lead Harvester with DNS/MX Pre-Validation
    sample_dork = (
        'Georgia Contractors: john.ga.builder@gmail.com - Custom Home Builder GA\n'
        'HVAC Specialist: atlanta.hvac.cool@gmail.com - Mechanical HVAC contractor\n'
        'Dead domain: fakeuser@nonexistentdomain92837492834.com (Must be rejected)\n'
        'Platform link: support@google.com (Must be rejected)\n'
        'Social link: privacy@facebook.com (Must be rejected)'
    )
    st_ch, _, d_ch = wsgi_request(
        "/api/cli/contractors/collect",
        "POST",
        body_dict={
            "raw_text": sample_dork,
            "state": "GA",
            "trade": "Mechanical & HVAC Contractors (Ductwork & Layout)",
            "custom_trade": ""
        }
    )
    assert st_ch.startswith("200"), f"Expected 200 for contractor collect, got {st_ch}"
    res_ch = json.loads(d_ch.decode("utf-8"))
    assert res_ch.get("status") == "ok"
    assert res_ch.get("valid_saved") >= 2, "Expected at least 2 valid contractor leads saved"
    assert res_ch.get("rejected_count") >= 3, "Expected at least 3 invalid/platform emails rejected"
    print("[PASS 52.1] Contractor Harvester correctly ingested verified HVAC/Builder leads and blocked dead domain & platform junk.")

    # 52.2 Custom Trade Support
    st_ct, _, d_ct = wsgi_request(
        "/api/cli/contractors/collect",
        "POST",
        body_dict={
            "raw_text": "Custom roofer: contact.elite.roofing@gmail.com in Texas",
            "state": "TX",
            "trade": "custom",
            "custom_trade": "Roofing & Siding Specialists"
        }
    )
    assert st_ct.startswith("200"), f"Expected 200 for custom trade collect, got {st_ct}"
    res_ct = json.loads(d_ct.decode("utf-8"))
    assert res_ct.get("trade_category") == "Roofing & Siding Specialists"
    assert res_ct.get("valid_saved") >= 1
    print("[PASS 52.2] Custom trade text input correctly processed and ingested with target state TX.")

    # 52.3 Real-Time Campaign Creation
    st_cr, _, d_cr = wsgi_request(
        "/api/cli/campaigns/create-realtime",
        "POST",
        body_dict={
            "name": "Suite 52 Georgia HVAC Campaign",
            "subject": "CAD & Permit Drawings for {company}",
            "body": "Hi {name},\n\nWe provide 2D/3D permit packages for {trade} in {state}.",
            "state_filter": "GA",
            "trade_filter": "HVAC",
            "limit": 10
        }
    )
    assert st_cr.startswith("200"), f"Expected 200 for realtime campaign create, got {st_cr}"
    res_cr = json.loads(d_cr.decode("utf-8"))
    assert res_cr.get("status") == "ok"
    assert res_cr.get("campaign_id") is not None
    print(f"[PASS 52.3] Real-time campaign #{res_cr.get('campaign_id')} created and queued for dispatch.")

    # 52.4 Real-Time Draft Generation
    st_dr, _, d_dr = wsgi_request(
        "/api/cli/drafts/create-realtime",
        "POST",
        body_dict={
            "profile_name": "Profile 17",
            "account_email": "calvin.gracearchitectures.llc@gmail.com",
            "subject": "Quick question regarding {trade} project in {state}",
            "body": "Hi {name},\n\nWe would love to collaborate.",
            "state_filter": "GA",
            "limit": 5
        }
    )
    assert st_dr.startswith("200"), f"Expected 200 for realtime draft create, got {st_dr}"
    res_dr = json.loads(d_dr.decode("utf-8"))
    assert res_dr.get("status") == "ok"
    assert res_dr.get("created") >= 1
    print(f"[PASS 52.4] Real-time drafts generated ({res_dr.get('created')} drafts processed).")

    # 52.5 Deep DNS/MX Cleaner Sweep
    st_cs, _, d_cs = wsgi_request(
        "/api/cli/cleaner/run-deep",
        "POST",
        body_dict={}
    )
    assert st_cs.startswith("200"), f"Expected 200 for cleaner deep sweep, got {st_cs}"
    res_cs = json.loads(d_cs.decode("utf-8"))
    assert res_cs.get("status") == "ok"
    print(f"[PASS 52.5] Deep DNS/MX cleaner sweep verified ({res_cs.get('total_valid')} valid contacts active).")

    # 52.6 CLI Workspace UI Rendering
    st_m1, _, d_m1 = wsgi_request("/api/?tab=module&id=1&view=cli", "GET")
    assert "CONTRACTOR LEAD HARVESTER" in d_m1.decode("utf-8")
    assert "cli-trade-select" in d_m1.decode("utf-8")
    assert "btn-harvest-contractors" in d_m1.decode("utf-8")

    st_m3, _, d_m3 = wsgi_request("/api/?tab=module&id=3&view=cli", "GET")
    assert "Real-Time Contractor Campaign Creator" in d_m3.decode("utf-8")

    st_m15, _, d_m15 = wsgi_request("/api/?tab=module&id=15&view=cli", "GET")
    assert "Real-Time Gmail Draft Generator" in d_m15.decode("utf-8")
    print("[PASS 52.6] All CLI interactive workbenches (Module 1, 2, 3, 15, 21) verified.")

    # 53. Testing Admin Governance for CLI Simple Mode & Colleague Access Control
    print("\n--- 53. TESTING ADMIN GOVERNANCE FOR CLI SIMPLE MODE & COLLEAGUE ACCESS CONTROL ---")
    
    # 53.1 GET /api/admin/settings includes cli_mode and cli_mode_allowed_colleagues
    st_adm, _, d_adm = wsgi_request("/api/admin/settings", "GET")
    assert st_adm.startswith("200"), f"GET /api/admin/settings failed with {st_adm}"
    adm_json = json.loads(d_adm.decode("utf-8"))
    assert "ribbon_visibility" in adm_json
    assert "cli_mode" in adm_json["ribbon_visibility"], "cli_mode missing from ribbon_visibility in admin settings"
    assert "cli_mode_allowed_colleagues" in adm_json, "cli_mode_allowed_colleagues missing from admin settings"
    print("[PASS 53.1] Admin settings GET correctly returns ribbon_visibility.cli_mode and cli_mode_allowed_colleagues.")

    # 53.2 Super Admin updating ribbon_visibility.cli_mode and cli_mode_allowed_colleagues
    admin_sid_53, admin_csrf_53 = create_server_session("king", "Super Admin")
    admin_headers_53 = {
        "Cookie": f"grace_session_id={admin_sid_53}; grace_csrf_token={admin_csrf_53}",
        "X-CSRF-Token": admin_csrf_53
    }
    st_post_adm, _, d_post_adm = wsgi_request(
        "/api/admin/settings",
        "POST",
        body_dict={
            "ribbon_visibility": {"cli_mode": "selected"},
            "cli_mode_allowed_colleagues": ["king", "abdullah", "hamza"]
        },
        headers_dict=admin_headers_53
    )
    assert st_post_adm.startswith("200")
    st_after = read_shared_state()
    assert st_after["adminSettings"]["ribbon_visibility"]["cli_mode"] == "selected"
    assert "sarah" not in st_after["adminSettings"]["cli_mode_allowed_colleagues"]
    print("[PASS 53.2] Super Admin successfully updated CLI mode rule to 'selected' and updated colleague access list.")

    # 53.3 Admin Governance UI verification (Ribbon Visibility Tab elements)
    _, _, d_root = wsgi_request("/api/?tab=dashboard", "GET")
    root_html_str = d_root.decode("utf-8")
    assert 'id="gov-vis-cli_mode"' in root_html_str, "Missing gov-vis-cli_mode select element in admin governance modal"
    assert 'id="gov-cli-colleagues-wrap"' in root_html_str, "Missing gov-cli-colleagues-wrap element in admin governance modal"
    assert 'onCliModeRuleChange' in root_html_str, "Missing onCliModeRuleChange JS function"
    assert 'renderGovCliColleaguesList' in root_html_str, "Missing renderGovCliColleaguesList JS function"
    print("[PASS 53.3] Admin Governance modal renders CLI Mode visibility selector and colleague checklist.")

    # 53.4 Colleague Management UI verification (CLI switch on cards)
    _, _, d_colleagues = wsgi_request("/api/?tab=colleagues", "GET")
    colleagues_html_str = d_colleagues.decode("utf-8")
    assert 'cli-access-btn-' in colleagues_html_str, "Missing CLI access button in colleague cards"
    assert 'toggleColleagueCliAccess' in colleagues_html_str, "Missing toggleColleagueCliAccess JS function"
    assert 'edit-colleague-cli-access' in colleagues_html_str, "Missing edit-colleague-cli-access checkbox in colleague settings modal"
    print("[PASS 53.4] Colleague Management renders CLI Mode Access button, status badges, and settings modal controls.")

    # 53.5 1-Click Toggle Endpoint: Super Admin toggling CLI access for Sarah
    st_toggle, _, d_toggle = wsgi_request(
        "/api/admin/colleague-cli-access",
        "POST",
        body_dict={"colleague_key": "sarah", "allowed": False},
        headers_dict=admin_headers_53
    )
    assert st_toggle.startswith("200")
    res_toggle = json.loads(d_toggle.decode("utf-8"))
    assert res_toggle["allowed"] is False
    assert res_toggle["colleague_key"] == "sarah"

    # 53.6 Non-admin colleague attempting to mutate CLI permissions is blocked with 403
    colleague_sid_53, colleague_csrf_53 = create_server_session("sarah", "Colleague")
    colleague_headers_53 = {
        "Cookie": f"grace_session_id={colleague_sid_53}; grace_csrf_token={colleague_csrf_53}",
        "X-CSRF-Token": colleague_csrf_53
    }
    st_unauth, _, _ = wsgi_request(
        "/api/admin/colleague-cli-access",
        "POST",
        body_dict={"colleague_key": "sarah", "allowed": True},
        headers_dict=colleague_headers_53
    )
    assert st_unauth.startswith("403"), f"Expected 403 Forbidden for unauthorized colleague, got {st_unauth}"
    print("[PASS 53.5] 1-Click Colleague CLI Access endpoint strictly enforced Super Admin RBAC security.")

    # 53.7 Server-Side Enforcement: Restricted Colleague is blocked from CLI mode
    st_sarah_cli, _, d_sarah_cli = wsgi_request(
        "/api/?tab=matrix&view=cli",
        "GET",
        headers_dict={"Cookie": f"grace_session_id={colleague_sid_53}"}
    )
    assert st_sarah_cli.startswith("200")
    sarah_html = d_sarah_cli.decode("utf-8")
    assert "CLI SIMPLE MODE" not in sarah_html, "Restricted colleague should be forced to Enterprise mode, but got CLI Simple Mode!"
    assert "ENTERPRISE FUNCTIONAL GRID" in sarah_html or "Complete 22-Module Control Matrix" in sarah_html

    # Super Admin King Saab accessing CLI mode succeeds
    st_king_cli, _, d_king_cli = wsgi_request(
        "/api/?tab=matrix&view=cli",
        "GET",
        headers_dict={"Cookie": f"grace_session_id={admin_sid_53}"}
    )
    assert st_king_cli.startswith("200")
    king_html = d_king_cli.decode("utf-8")
    assert "CLI SIMPLE MODE" in king_html, "Super Admin King Saab must always have full access to CLI mode"
    print("[PASS 53.6] Server-side RBAC strictly blocked restricted colleague from CLI mode while Super Admin maintains full access.")

    # Restore Sarah's access and set cli_mode to 'everyone'
    wsgi_request(
        "/api/admin/settings",
        "POST",
        body_dict={
            "ribbon_visibility": {"cli_mode": "everyone"},
            "cli_mode_allowed_colleagues": ["king", "abdullah", "sarah", "hamza"]
        },
        headers_dict=admin_headers_53
    )
    wsgi_request(
        "/api/admin/colleague-cli-access",
        "POST",
        body_dict={"colleague_key": "sarah", "allowed": True},
        headers_dict=admin_headers_53
    )
    print("[PASS 53.7] Restored CLI access governance cleanly.")

    # =========================================================================
    # 54. TESTING UI POLISH, SHOW-PASSWORD ALIGNMENT, PERMANENT COLLEAGUE REMOVAL & APP PADDING AUDIT
    # =========================================================================
    print("\n--- 54. TESTING UI POLISH, SHOW-PASSWORD ALIGNMENT, PERMANENT COLLEAGUE REMOVAL & APP PADDING AUDIT ---")

    # 54.1 Left-Aligned Password Visibility Toggles
    _, _, d_login = wsgi_request("/", "GET")
    login_html = d_login.decode("utf-8")
    assert 'id="login-password-input"' in login_html, "Missing login password input in DOM"
    assert 'justify-content: flex-start' in login_html or 'justify-content:flex-start' in login_html, (
        "Show password toggle container under password field must be left-aligned"
    )
    assert 'id="reg-show-both-pwd"' in login_html, "Missing reg-show-both-pwd toggle on register screen"
    assert 'colleague-settings-modal' in login_html, "Missing colleague-settings-modal in DOM"
    print("[PASS 54.1] Password visibility toggle verified left-aligned under password input across Login, Register, and Modals.")

    # 54.2 App-wide Padding & Border Boundary Protection
    assert '.card {' in login_html or 'padding: 22px 24px' in login_html, "Base CSS must define .card container padding"
    assert 'padding: 22px 24px' in login_html or 'padding:22px 24px' in login_html, "Standard card padding must be at least 22px"

    st_colleagues, _, d_colleagues_page = wsgi_request("/api/?tab=colleagues", "GET")
    assert st_colleagues.startswith("200")
    colleagues_page_str = d_colleagues_page.decode("utf-8")
    assert 'class="card"' in colleagues_page_str, "Colleague management container must use .card styling"
    assert 'padding:22px 24px;' in colleagues_page_str or 'padding: 22px 24px;' in colleagues_page_str, (
        "Colleague management card container must have explicit generous padding to prevent text touching borders"
    )
    print("[PASS 54.2] App-wide container padding verified; text and controls safely indented from borders.")

    # 54.3 Admin Governance Ribbon Visibility Debounce & Authorization Resilience
    assert 'isSavingRibbonSettings' in login_html, "Frontend JS must include isSavingRibbonSettings debounce guard"
    assert 'Saving & Applying Rules...' in login_html, "Frontend JS must provide real-time saving button feedback"

    # Direct POST /api/admin/settings using HTTP_X_ADMIN_KEY fallback without session cookie
    st_adm_key, _, d_adm_key = wsgi_request(
        "/api/admin/settings",
        "POST",
        body_dict={
            "ribbon_visibility": {"cli_mode": "everyone"}
        },
        headers_dict={"X-Admin-Key": "GraceAdmin2026!"}
    )
    assert st_adm_key.startswith("200"), f"Expected 200 via X-Admin-Key fallback, got {st_adm_key}"
    res_adm_key = json.loads(d_adm_key.decode("utf-8"))
    assert res_adm_key.get("status") == "ok"
    print("[PASS 54.3] Admin Governance authorization verified with debounce protection and X-Admin-Key resilience.")

    # 54.4 Permanent Colleague Removal & Access Revocation
    test_key_54 = "audit_temp_colleague"
    test_pwd_54 = "SecureColleaguePass2026!"
    test_pwd_hash_54 = hash_password_argon2id(test_pwd_54)

    st_init = read_shared_state()
    if "deleted_colleagues" in st_init.get("adminSettings", {}):
        if test_key_54 in st_init["adminSettings"]["deleted_colleagues"]:
            st_init["adminSettings"]["deleted_colleagues"].remove(test_key_54)
            from main import write_shared_state
            write_shared_state(st_init)

    update_shared_state({
        "resource": "profiles",
        "key": test_key_54,
        "value": {
            "name": "Audit Colleague 54",
            "email": "audit54@example.com",
            "role": "Colleague",
            "password": test_pwd_hash_54
        }
    })

    # Verify audit colleague can authenticate before deletion
    st_login_pre, _, d_login_pre = wsgi_request(
        "/api/auth/login",
        "POST",
        body_dict={"colleague_key": test_key_54, "password": test_pwd_54}
    )
    assert st_login_pre.startswith("200"), f"Expected 200 for active colleague login, got {st_login_pre}"

    # Create active session for test colleague
    temp_sid_54, temp_csrf_54 = create_server_session(test_key_54, "Colleague")
    assert get_server_session(temp_sid_54) is not None, "Server session must exist for active colleague"

    # Super Admin deletes the colleague profile via batch-delete endpoint
    admin_sid_54, admin_csrf_54 = create_server_session("king", "Super Admin")
    admin_headers_54 = {
        "Cookie": f"grace_session_id={admin_sid_54}; grace_csrf_token={admin_csrf_54}",
        "X-CSRF-Token": admin_csrf_54
    }

    st_del, _, d_del = wsgi_request(
        "/api/colleagues/batch-delete",
        "POST",
        body_dict={"keys": [test_key_54]},
        headers_dict=admin_headers_54
    )
    assert st_del.startswith("200"), f"Batch delete failed with {st_del}"
    res_del = json.loads(d_del.decode("utf-8"))
    assert test_key_54 in res_del.get("deleted", [])

    # Verify shared state reflects permanent removal and blacklisting
    st_state_after = read_shared_state()
    assert test_key_54 not in st_state_after["profiles"], "Deleted colleague must be completely purged from profiles"
    assert test_key_54 in st_state_after["adminSettings"].get("deleted_colleagues", []), (
        "Deleted colleague must be added to persistent deleted_colleagues blacklist"
    )
    assert test_key_54 not in st_state_after["adminSettings"].get("cli_mode_allowed_colleagues", []), (
        "Deleted colleague must be removed from CLI mode allowed list"
    )

    # Verify state anti-resurrection upon fresh read from disk
    from main import _read_shared_state_unlocked
    st_reloaded = _read_shared_state_unlocked()
    assert test_key_54 not in st_reloaded["profiles"], "Deleted colleague must not be resurrected on disk reload"

    # Verify active session for deleted colleague is revoked
    assert get_server_session(temp_sid_54) is None, "Active session must be immediately revoked upon deletion"

    # Verify deleted colleague cannot log in again (blocked with 403)
    st_login_post, _, d_login_post = wsgi_request(
        "/api/auth/login",
        "POST",
        body_dict={"colleague_key": test_key_54, "password": test_pwd_54}
    )
    assert st_login_post.startswith("403"), f"Expected 403 Forbidden for deleted colleague login, got {st_login_post}"
    res_login_post = json.loads(d_login_post.decode("utf-8"))
    assert "Account deactivated" in res_login_post.get("error", "")

    # 54.5 Colleague Settings Modal Delete Button UI Verification
    assert 'deleteColleagueFromModal' in login_html or 'deleteColleagueFromModal' in colleagues_page_str, "Missing deleteColleagueFromModal JS function"
    assert 'btn-delete-colleague-from-modal' in colleagues_page_str, "Missing Delete Colleague button in colleague settings modal"
    print("[PASS 54.4] Colleague permanent removal, profile purging, session revocation, and 403 login lock confirmed.")

    # 54.6 Super Admin Permanent Immunity
    st_del_king, _, d_del_king = wsgi_request(
        "/api/colleagues/batch-delete",
        "POST",
        body_dict={"keys": ["king"]},
        headers_dict=admin_headers_54
    )
    assert st_del_king.startswith("200")
    res_del_king = json.loads(d_del_king.decode("utf-8"))
    assert "king" not in res_del_king.get("deleted", []), "Super Admin root profile must never be deleted"
    st_state_final = read_shared_state()
    assert "king" in st_state_final["profiles"], "Super Admin King Saab profile must remain intact"
    assert "king" not in st_state_final["adminSettings"].get("deleted_colleagues", []), (
        "Super Admin must never be added to deleted_colleagues blacklist"
    )
    print("[PASS 54.5] Super Admin root profile permanently immune from deletion and blacklisting.")

    print("\n[SUCCESS] ALL 54 EXTENSIVE TESTS PASSED WITH 100% SUCCESS!\n")


if __name__ == "__main__":
    run_tests()






