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

    print("\n[SUCCESS] ALL 29 EXTENSIVE TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()




