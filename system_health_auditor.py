"""
Grace Outreach Assistant - Comprehensive System Diagnostic & Integrity Auditor
Tests all 22 menu modules, database tables, directories, and dependencies.
"""

import os
import sys
import importlib

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

print("\n" + CYAN + "═" * 78)
print("       🔍 GRACE OUTREACH ASSISTANT - COMPREHENSIVE INTEGRITY AUDIT")
print("═" * 78 + RESET + "\n")

# 1. Check Directory Tree
required_dirs = [
    "config", "campaign_engine", "campaign_engine/ai_scorer", 
    "campaign_engine/limits", "campaign_engine/logger", 
    "campaign_engine/oauth_vault", "campaign_engine/replies", 
    "campaign_engine/scheduler", "tokens_vault_backup", "accounts", "reports"
]

print(f"{BOLD}[1/4] AUDITING DIRECTORY STRUCTURE:{RESET}")
for d in required_dirs:
    full_path = os.path.join(BASE_DIR, d)
    if os.path.exists(full_path):
        print(f"  {GREEN}✔{RESET} Directory Found : {d:<35}")
    else:
        os.makedirs(full_path, exist_ok=True)
        print(f"  {YELLOW}⚠{RESET} Auto-created     : {d:<35}")

# 2. Check Database Connectivity & Core Tables
print(f"\n{BOLD}[2/4] AUDITING DATABASE SCHEMA & TABLES:{RESET}")
try:
    from config.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    required_tables = [
        "contacts", "campaigns", "campaign_items", "gmail_accounts",
        "account_warmup_profiles", "suppression_list", "replies", 
        "scheduled_campaigns", "activity_logs"
    ]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [r[0] for r in cursor.fetchall()]
    
    for t in required_tables:
        if t in existing_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cursor.fetchone()[0]
            print(f"  {GREEN}✔{RESET} Table Ready     : {t:<28} ({cnt} rows)")
        else:
            print(f"  {RED}✖ Missing Table{RESET}  : {t:<28}")
            
    conn.close()
except Exception as e:
    print(f"  {RED}✖ Database Audit Failed: {e}{RESET}")

# 3. Test All 22 Menu Modules Syntax & Import Integrity
print(f"\n{BOLD}[3/4] AUDITING ALL 22 SYSTEM MENU MODULES:{RESET}")

modules_to_test = [
    (1, "Email Collector", "modules.collector", "collector_menu"),
    (2, "Email Cleaner", "modules.cleaner", "cleaner_menu"),
    (3, "Campaign Manager", "modules.campaign", "campaign_menu"),
    (4, "Spam Checker", "modules.spam_checker", "spam_checker_menu"),
    (5, "CRM Dashboard", "modules.crm", "crm_menu"),
    (6, "Lead Scoring", "modules.lead_scorer", "lead_scorer_menu"),
    (7, "AI Template Analyzer", "modules.template_analyzer", "template_analyzer_menu"),
    (8, "Subject Analyzer", "modules.subject_analyzer", "subject_analyzer_menu"),
    (9, "Template Manager", "modules.templates", "template_menu"),
    (10, "Reports", "modules.reports", "reports_menu"),
    (11, "Activity Logs", "modules.activity_log", "activity_log_menu"),
    (12, "Personalized Campaign", "modules.personalized_campaign", "personalized_campaign_menu"),
    (13, "Campaign Progress", "modules.progress", "progress_menu"),
    (14, "System Settings", "modules.settings", "settings_menu"),
    (15, "Gmail Draft Assistant", "modules.gmail_draft_assistant", "draft_assistant_menu"),
    (16, "Gmail Profile Manager", "modules.profile_manager", "profile_manager_menu"),
    (17, "Follow-up Manager", "modules.followup", "followup_menu"),
    (18, "Suppression Manager", "modules.suppression", "suppression_menu"),
    (19, "Reply Manager", "modules.replies", "replies_menu"),
    (20, "Gmail Account Manager", "modules.account_manager", "account_manager_menu"),
    (21, "Draft Queue Manager", "modules.draft_queue", "draft_queue_menu"),
    (22, "Campaign Engine V2", "campaign_engine.campaign_menu", "campaign_engine_menu"),
]

passed_mods = 0
for opt_num, name, mod_path, func_name in modules_to_test:
    try:
        mod = importlib.import_module(mod_path)
        if hasattr(mod, func_name):
            print(f"  {GREEN}✔ [{opt_num:02d}]{RESET} {name:<26} : {mod_path:<32} (Callable OK)")
            passed_mods += 1
        else:
            print(f"  {YELLOW}⚠ [{opt_num:02d}]{RESET} {name:<26} : {mod_path:<32} (Function `{func_name}` Missing)")
    except Exception as e:
        print(f"  {RED}✖ [{opt_num:02d}]{RESET} {name:<26} : {mod_path:<32} (Import Error: {str(e)[:25]})")

# 4. Engine V2 Subsystem Integrity
print(f"\n{BOLD}[4/4] AUDITING CAMPAIGN ENGINE V2 SUBSYSTEMS:{RESET}")
engine_subs = [
    ("AI Scorer", "campaign_engine.ai_scorer.template_evaluator", "evaluate_campaign_template"),
    ("Account Preflight", "campaign_engine.account_preflight", "display_profile_accounts_categorized"),
    ("Limit Tracker", "campaign_engine.limits.limit_tracker", "display_account_limits_summary"),
    ("Warm-up Profiler", "campaign_engine.limits.warmup_profiler", "display_warmup_summary"),
    ("Daily Maintenance", "campaign_engine.limits.daily_maintenance", "run_daily_maintenance"),
    ("Inbound Replies Sync", "campaign_engine.replies.sync_replies", "display_replies_matrix"),
    ("OAuth Vault Manager", "campaign_engine.oauth_vault.oauth_controller", "oauth_vault_manager_menu"),
    ("Activity Logger", "campaign_engine.logger.activity_logger", "export_campaign_report"),
    ("Scheduler Engine", "campaign_engine.scheduler.scheduler_menu", "scheduler_menu"),
]

engine_passed = 0
for name, mod_path, func_name in engine_subs:
    try:
        mod = importlib.import_module(mod_path)
        if hasattr(mod, func_name):
            print(f"  {GREEN}✔{RESET} {name:<25} : {mod_path:<45} (OK)")
            engine_passed += 1
        else:
            print(f"  {YELLOW}⚠{RESET} {name:<25} : Function `{func_name}` missing")
    except Exception as e:
        print(f"  {RED}✖{RESET} {name:<25} : Error: {e}")

print("\n" + CYAN + "═" * 78)
print(f"  SUMMARY: Modules OK ({passed_mods}/{len(modules_to_test)}) │ Engine Subs OK ({engine_passed}/{len(engine_subs)})")
print("═" * 78 + RESET + "\n")
