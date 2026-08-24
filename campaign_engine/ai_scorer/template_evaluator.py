import re

SPAM_KEYWORDS = {
    "100% free": 3, "act now": 3, "apply now": 3, "buy direct": 3, "cash bonus": 3,
    "clearance": 3, "click here": 3, "click now": 3, "consolidate debt": 3, "cost": 2,
    "credit card": 3, "cures": 3, "dear friend": 3, "direct marketing": 2, "discount": 2,
    "double your": 3, "earn extra cash": 3, "earn money": 3, "eliminate debt": 3,
    "exclusive deal": 3, "expect to earn": 3, "extra income": 3, "fast cash": 3,
    "financial freedom": 3, "free gift": 3, "free info": 3, "free membership": 3,
    "free preview": 2, "free sample": 2, "free trial": 2, "full refund": 2, "get out of debt": 3,
    "get paid": 3, "giveaway": 3, "guaranteed": 3, "income from home": 3, "increase sales": 2,
    "instant": 2, "investment": 2, "limited time": 3, "lowest price": 3, "make money": 3,
    "million dollars": 3, "miracle": 3, "money back": 3, "no catch": 3, "no cost": 3,
    "no credit check": 3, "no experience": 3, "no fees": 3, "no gimmick": 3, "no hidden": 3,
    "no obligation": 2, "no purchase necessary": 3, "no risk": 3, "no strings attached": 3,
    "not spam": 3, "once in a lifetime": 3, "one time": 2, "online marketing": 2,
    "open immediately": 3, "opportunity": 2, "opt in": 2, "order now": 3, "passwords": 3,
    "pennies a day": 3, "potential earnings": 3, "prize": 3, "promise": 2, "pure profit": 3,
    "refund": 2, "risk free": 3, "save big": 3, "save money": 2, "special promotion": 2,
    "supplies are limited": 3, "take action": 2, "terms and conditions": 2, "unlimited": 2,
    "unsolicited": 3, "urgent": 3, "valuable": 2, "viagra": 3, "vicodin": 3,
    "warranty": 2, "weight loss": 3, "while supplies last": 3, "win": 3, "winner": 3,
    "winning": 3, "work from home": 3, "you have been selected": 3, "your income": 3
}


def analyze_spam_triggers(subject, body):
    text = f"{subject} {body}".lower()
    found_triggers = []
    total_spam_weight = 0

    for word, weight in SPAM_KEYWORDS.items():
        pattern = r'\b' + re.escape(word) + r'\b'
        matches = re.findall(pattern, text)
        if matches:
            count = len(matches)
            found_triggers.append({
                "keyword": word,
                "count": count,
                "weight": weight,
                "points": count * weight
            })
            total_spam_weight += count * weight

    return found_triggers, total_spam_weight


def analyze_subject_line(subject):
    issues = []
    suggestions = []
    score_deductions = 0

    if not subject:
        return {"score": 0, "issues": ["Subject line is empty."], "suggestions": ["Provide a concise subject."]}

    subj_len = len(subject)
    words = subject.split()

    if subj_len < 10:
        issues.append("Subject is too short (< 10 chars).")
        suggestions.append("Aim for 30-55 characters for optimal open rates.")
        score_deductions += 10
    elif subj_len > 60:
        issues.append("Subject may be truncated on mobile devices (> 60 chars).")
        suggestions.append("Keep subject under 60 characters.")
        score_deductions += 10

    caps_words = [w for w in words if w.isupper() and len(w) > 1 and w.isalpha()]
    if caps_words:
        issues.append(f"Excessive ALL CAPS detected ({', '.join(caps_words)}).")
        suggestions.append("Use title case or sentence case instead of ALL CAPS.")
        score_deductions += len(caps_words) * 10

    if "!" in subject or "?" in subject:
        punc_count = subject.count("!") + subject.count("?")
        if punc_count > 1:
            issues.append("Multiple exclamation/question marks in subject.")
            suggestions.append("Avoid hype punctuation (! or ??) in cold outreach subjects.")
            score_deductions += 15

    has_merge_tag = "{" in subject and "}" in subject
    if has_merge_tag:
        suggestions.append("Good: Subject includes personalization tags.")

    subject_score = max(0, 100 - score_deductions)
    return {
        "score": subject_score,
        "length": subj_len,
        "word_count": len(words),
        "issues": issues,
        "suggestions": suggestions
    }


def calculate_health_score(subject, body):
    triggers, spam_weight = analyze_spam_triggers(subject, body)
    subj_meta = analyze_subject_line(subject)
    body_words = len(body.split())

    score = 100
    deductions = []
    recommendations = []

    if spam_weight > 0:
        penalty = min(40, spam_weight * 5)
        score -= penalty
        deductions.append(f"-{penalty} pts: {len(triggers)} spam trigger phrase(s) found.")
        recommendations.append("Replace high-risk commercial buzzwords with conversational language.")

    if subj_meta["score"] < 80:
        subj_penalty = (100 - subj_meta["score"]) // 3
        score -= subj_penalty
        deductions.append(f"-{subj_penalty} pts: Subject line optimization flaws.")

    if body_words < 20:
        score -= 15
        deductions.append("-15 pts: Body copy too short (< 20 words).")
        recommendations.append("Provide sufficient context about your offering.")
    elif body_words > 250:
        score -= 10
        deductions.append("-10 pts: Body copy quite lengthy (> 250 words).")
        recommendations.append("Cold outreach emails perform best between 50 and 150 words.")

    url_count = len(re.findall(r'https?://[^\s]+', body))
    if url_count > 2:
        penalty = (url_count - 2) * 8
        score -= penalty
        deductions.append(f"-{penalty} pts: Too many links ({url_count} found).")
        recommendations.append("Limit links to 1 or 2 to avoid spam filters.")

    health_score = max(0, min(100, score))

    if health_score >= 85:
        tier = "EXCELLENT (Inbox Ready)"
        color_indicator = "🟢"
    elif health_score >= 70:
        tier = "GOOD (Minor Improvements Recommended)"
        color_indicator = "🟡"
    elif health_score >= 50:
        tier = "FAIR (Spam Filter Risk)"
        color_indicator = "🟠"
    else:
        tier = "POOR (High Risk of Spam Folder)"
        color_indicator = "🔴"

    return {
        "health_score": health_score,
        "tier": tier,
        "color_indicator": color_indicator,
        "spam_weight": spam_weight,
        "triggers": triggers,
        "subject_meta": subj_meta,
        "deductions": deductions,
        "recommendations": recommendations + subj_meta["suggestions"]
    }


def evaluate_campaign_template(subject, body):
    res = calculate_health_score(subject, body)

    print("\n" + "=" * 70)
    print("           AI EMAIL TEMPLATE & HEALTH SCORE ANALYSIS")
    print("=" * 70)
    print(f"Health Score     : {res['health_score']}/100 {res['color_indicator']}")
    print(f"Deliverability   : {res['tier']}")
    print(f"Spam Risk Weight : {res['spam_weight']} (0 = Perfect)")
    print("-" * 70)

    subj = res["subject_meta"]
    print(f"Subject Analysis : Score {subj['score']}/100 ({subj['length']} chars, {subj['word_count']} words)")
    if subj["issues"]:
        for issue in subj["issues"]:
            print(f"  [!] Subject Issue: {issue}")

    if res["triggers"]:
        print("\nSpam Triggers Detected:")
        for t in res["triggers"]:
            print(f"  • \"{t['keyword']}\" (Count: {t['count']}, Risk: {t['points']} pts)")
    else:
        print("\nSpam Triggers    : None detected (Clean)")

    if res["deductions"]:
        print("\nScore Deductions:")
        for d in res["deductions"]:
            print(f"  {d}")

    if res["recommendations"]:
        print("\nAI Deliverability Suggestions:")
        for rec in set(res["recommendations"]):
            print(f"  -> {rec}")

    print("=" * 70 + "\n")
    return res
