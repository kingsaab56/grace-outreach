# ai/readability.py

def readability_score(text):

    score = 100
    issues = []

    words = text.split()

    if len(words) < 30:
        issues.append("Email is too short")
        score -= 10

    if len(words) > 250:
        issues.append("Email is too long")
        score -= 10

    if text.count("!") > 2:
        issues.append("Too many exclamation marks")
        score -= 10

    capital_letters = sum(1 for c in text if c.isupper())
    letters = sum(1 for c in text if c.isalpha())

    if letters > 0:

        percent = (capital_letters / letters) * 100

        if percent > 30:
            issues.append("Too many capital letters")
            score -= 15

    if score < 0:
        score = 0

    return {

        "score": score,

        "issues": issues

    }