# ai/spam_analyzer.py

from ai.template_rules import SPAM_WORDS


def analyze_spam(subject, body):

    score = 100
    issues = []

    text = (subject + " " + body).lower()

    for word in SPAM_WORDS:

        if word in text:

            issues.append(f"Spam word detected: {word}")
            score -= 8

    exclamation_count = text.count("!")

    if exclamation_count > 2:
        issues.append("Too many exclamation marks")
        score -= 10

    link_count = text.count("http")

    if link_count > 3:
        issues.append("Too many links")
        score -= 10

    if score < 0:
        score = 0

    if score >= 90:
        risk = "Very Low"

    elif score >= 75:
        risk = "Low"

    elif score >= 60:
        risk = "Medium"

    elif score >= 40:
        risk = "High"

    else:
        risk = "Very High"

    return {
        "score": score,
        "risk": risk,
        "issues": issues
    }