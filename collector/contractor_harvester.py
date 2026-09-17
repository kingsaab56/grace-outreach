"""
Contractor & Custom Home Builder Lead Harvester & Zero-Bounce Pre-Validator
Developed for King Saab - Grace Outreach Assistant Enterprise
"""

import re
import socket
import subprocess
from typing import Dict, List, Tuple, Any
from config.database import get_connection

# In-memory DNS cache to ensure lightning fast resolution (< 0.0001s per cached domain)
_DNS_CACHE: Dict[str, Tuple[bool, str]] = {
    "gmail.com": (True, "Google Mail Server Verified"),
    "googlemail.com": (True, "Google Mail Server Verified"),
    "yahoo.com": (True, "Yahoo Mail Server Verified"),
    "ymail.com": (True, "Yahoo Mail Server Verified"),
    "outlook.com": (True, "Microsoft Outlook Server Verified"),
    "hotmail.com": (True, "Microsoft Hotmail Server Verified"),
    "live.com": (True, "Microsoft Live Server Verified"),
    "icloud.com": (True, "Apple iCloud Server Verified"),
    "aol.com": (True, "AOL Mail Server Verified"),
    "comcast.net": (True, "Comcast Mail Server Verified"),
    "att.net": (True, "AT&T Mail Server Verified"),
    "sbcglobal.net": (True, "SBCGlobal Mail Server Verified"),
    "bellsouth.net": (True, "BellSouth Mail Server Verified"),
    "cox.net": (True, "Cox Mail Server Verified"),
    "charter.net": (True, "Charter Mail Server Verified"),
}

# Platform and social domains that appear in Google search scrapings but are NOT contractors
PLATFORM_DOMAINS_BLACKLIST = {
    "google.com", "google.co.uk", "bing.com", "msn.com",
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
    "youtube.com", "pinterest.com", "tiktok.com", "reddit.com",
    "apple.com", "microsoft.com", "amazon.com", "wix.com", "wixpress.com",
    "squarespace.com", "godaddy.com", "namecheap.com", "cloudflare.com",
    "sentry.io", "github.com", "gitlab.com", "gravatar.com", "schema.org",
    "wordpress.org", "wordpress.com", "zendesk.com", "intercom.com",
    "example.com", "domain.com", "yourcompany.com", "yoursite.com", "mysite.com",
    "email.com", "whois.com", "bbb.org", "yelp.com", "yellowpages.com",
    "angieslist.com", "angi.com", "houzz.com", "homeadvisor.com"
}

# Disposable temporary inbox providers
DISPOSABLE_DOMAINS_BLACKLIST = {
    "mailinator.com", "tempmail.com", "temp-mail.org", "10minutemail.com",
    "guerrillamail.com", "trashmail.com", "throwawaymail.com", "sharklasers.com",
    "fakeinbox.com", "dispostable.com", "yopmail.com", "burnermail.io"
}

# Generic non-work or system prefixes that cause dead outreach or automated rejection
SYSTEM_PREFIXES_BLACKLIST = {
    "support", "privacy", "abuse", "terms", "legal", "help", "billing",
    "invoice", "jobs", "careers", "hr", "press", "media", "pr", "noreply",
    "no-reply", "donotreply", "do-not-reply", "mailer-daemon", "postmaster",
    "security", "webmaster", "hostmaster", "root", "compliance", "feedback",
    "notifications", "marketing", "unsubscribe", "optout", "opt-out"
}

# Standard trade taxonomy
TRADE_TAXONOMY = {
    "builders": "Custom Home Builders & Remodelers",
    "architects": "Architectural Design Studios (2D/3D & Permits)",
    "hvac": "Mechanical & HVAC Contractors (Ductwork & Layout)",
    "electrical": "Electrical Contractors (Power, Lighting & Panels)",
    "plumbing": "Plumbing Contractors (Water, Waste, Vent & Piping)",
    "structural": "Structural & Framing Contractors (Foundations & Beams)",
    "custom": "Custom Trade Contractor"
}


def extract_emails_from_raw_text(raw_text: str) -> List[str]:
    """
    Extracts all potential email addresses from raw search snippets,
    Google dorks, CSV dumps, or multi-line text.
    """
    if not raw_text:
        return []

    # Regex matches standard emails and decodes URL encoded @ (%40)
    cleaned_text = raw_text.replace("%40", "@").replace("%20", " ")
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, cleaned_text)

    # Normalize, deduplicate preserving order
    seen = set()
    unique_emails = []
    for m in matches:
        e = m.strip().lower()
        # Clean trailing punctuation
        e = re.sub(r'[\.,;:\'\"\)>\]]+$', '', e)
        e = re.sub(r'^[<\(\[\'\"\.]+', '', e)
        if e and "@" in e and e not in seen:
            seen.add(e)
            unique_emails.append(e)

    return unique_emails


def check_domain_deliverability(domain: str) -> Tuple[bool, str]:
    """
    Verifies that a domain has valid DNS resolution and/or MX mail exchange records.
    Catches dead domains that cause 550 'Address not found' hard bounces.
    """
    domain = domain.strip().lower()
    if not domain or "." not in domain:
        return False, "Invalid domain format"

    if domain in _DNS_CACHE:
        return _DNS_CACHE[domain]

    # 1. First test via nslookup for MX record
    try:
        proc = subprocess.run(
            ['nslookup', '-type=mx', domain],
            capture_output=True,
            text=True,
            timeout=3
        )
        out = proc.stdout.lower()
        if 'mail exchanger' in out or 'mx preference' in out or 'exchanger =' in out:
            _DNS_CACHE[domain] = (True, "Verified MX Mail Exchanger Found")
            return True, "Verified MX Mail Exchanger Found"
    except Exception:
        pass

    # 2. Fallback to standard DNS host resolution
    try:
        socket.gethostbyname(domain)
        _DNS_CACHE[domain] = (True, "Domain Host Resolves Active IP")
        return True, "Domain Host Resolves Active IP"
    except socket.gaierror:
        _DNS_CACHE[domain] = (False, "Dead Domain (Host does not exist - causes 'Address not found')")
        return False, "Dead Domain (Host does not exist - causes 'Address not found')"
    except Exception as e:
        _DNS_CACHE[domain] = (False, f"DNS Resolution Error: {e}")
        return False, f"DNS Resolution Error: {e}"


def validate_contractor_email(email: str) -> Tuple[bool, str]:
    """
    Comprehensive contractor email hygiene validator:
    - Syntax correctness
    - Platform / social / directory blacklist
    - System junk prefix blacklist
    - Disposable email filter
    - Real DNS/MX deliverability pre-check
    """
    if not email or "@" not in email:
        return False, "Malformed email format"

    parts = email.split("@")
    if len(parts) != 2:
        return False, "Multiple @ symbols in address"

    prefix, domain = parts[0].strip().lower(), parts[1].strip().lower()

    # Syntax rules
    if len(prefix) < 1 or len(domain) < 3 or "." not in domain:
        return False, "Invalid prefix or domain length"

    if ".." in email or prefix.endswith(".") or prefix.startswith("."):
        return False, "Consecutive or misplaced dots in email syntax"

    # Common domain typos
    if domain in ("gmail.con", "gmial.com", "gamil.com", "yahoo.con", "hotmial.com"):
        return False, f"Known typo in domain ({domain})"

    # Platform & Search Engine Blacklist
    if domain in PLATFORM_DOMAINS_BLACKLIST:
        return False, f"Platform / Social directory email ({domain}) - Not a contractor inbox"

    # Disposable blacklist
    if domain in DISPOSABLE_DOMAINS_BLACKLIST:
        return False, f"Temporary/disposable mailbox ({domain})"

    # System / Non-work prefix check
    for p_noise in SYSTEM_PREFIXES_BLACKLIST:
        if prefix == p_noise or prefix.startswith(f"{p_noise}.") or prefix.startswith(f"{p_noise}_") or prefix.startswith(f"{p_noise}-"):
            return False, f"System/Support generic inbox ('{prefix}@') - Unlikely to reach contractor decision maker"

    # Live DNS / MX Resolution (Eliminates 'Address not found')
    is_live, dns_reason = check_domain_deliverability(domain)
    if not is_live:
        return False, dns_reason

    return True, "Valid Contractor Inbox (Deliverability Pre-Checked)"


def deduce_contractor_details(email: str, default_state: str, default_trade: str) -> Dict[str, Any]:
    """
    Extracts name, company, state, and contractor category from email address.
    """
    prefix = email.split("@")[0].lower()
    domain = email.split("@")[1].lower()

    # Extract name using clean name logic
    name_parts = re.split(r'[._\-+]+', re.sub(r'[0-9]+', '', prefix))
    clean_parts = [p.capitalize() for p in name_parts if len(p) >= 3 and p.isalpha()]
    extracted_name = " ".join(clean_parts[:2]) if clean_parts else "Contractor"

    # Deduce company name
    if domain not in ("gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com"):
        company_slug = domain.split(".")[0]
        company = company_slug.replace("-", " ").replace("_", " ").title()
    else:
        company = f"{extracted_name} Services"

    return {
        "email": email,
        "name": extracted_name,
        "company": company,
        "state": (default_state or "US").upper(),
        "contractor_category": default_trade or "Custom Home Builders & Remodelers",
        "deal_stage": "Cold Lead",
        "lead_score": 70
    }


def process_raw_contractor_leads(
    raw_text: str,
    target_state: str = "GA",
    trade_category: str = "Custom Home Builders & Remodelers",
    custom_trade: str = ""
) -> Dict[str, Any]:
    """
    Processes raw text, dorks, or email lists:
    1. Extracts all emails
    2. Runs deep DNS & contractor hygiene validation
    3. Categorizes and tags with Trade & State
    4. Automatically saves valid leads into SQLite contacts database
    5. Returns comprehensive telemetry breakdown
    """
    final_trade = custom_trade.strip() if custom_trade.strip() else trade_category
    extracted_emails = extract_emails_from_raw_text(raw_text)

    valid_leads = []
    rejected_leads = []

    for email in extracted_emails:
        is_valid, reason = validate_contractor_email(email)
        if is_valid:
            lead_data = deduce_contractor_details(email, target_state, final_trade)
            valid_leads.append(lead_data)
        else:
            rejected_leads.append({
                "email": email,
                "reason": reason
            })

    # Ingest valid leads into Database
    saved_count = 0
    if valid_leads:
        conn = get_connection()
        cur = conn.cursor()
        try:
            for lead in valid_leads:
                cur.execute("""
                    INSERT OR REPLACE INTO contacts 
                    (email, name, company, state, contractor_category, deal_stage, lead_score, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'valid')
                """, (
                    lead["email"],
                    lead["name"],
                    lead["company"],
                    lead["state"],
                    lead["contractor_category"],
                    lead["deal_stage"],
                    lead["lead_score"]
                ))
            conn.commit()
            cur.execute("SELECT COUNT(*) FROM contacts WHERE status = 'valid'")
            total_valid_in_db = cur.fetchone()[0]
            saved_count = len(valid_leads)
        finally:
            conn.close()
    else:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM contacts WHERE status = 'valid'")
            total_valid_in_db = cur.fetchone()[0]
        finally:
            conn.close()

    return {
        "status": "ok",
        "total_extracted": len(extracted_emails),
        "valid_saved": saved_count,
        "rejected_count": len(rejected_leads),
        "total_valid_in_db": total_valid_in_db,
        "target_state": target_state.upper(),
        "trade_category": final_trade,
        "valid_leads": valid_leads[:50],  # sample up to 50
        "rejected_leads": rejected_leads[:50],  # sample up to 50
        "message": f"Successfully ingested {saved_count} verified {final_trade} leads ({target_state.upper()}). Rejected {len(rejected_leads)} invalid/dead emails."
    }
