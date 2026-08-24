# ai/subject_analyzer.py


SPAM_SUBJECT_WORDS = [
    "free",
    "urgent",
    "limited",
    "offer",
    "buy now",
    "act now",
    "guaranteed"
]


def analyze_subject(subject):

    issues = []
    score = 100


    lower_subject = subject.lower()


    for word in SPAM_SUBJECT_WORDS:

        if word in lower_subject:
            issues.append(
                f"Avoid promotional word: {word}"
            )
            score -= 10


    length = len(subject)


    if length < 10:
        issues.append(
            "Subject is too short"
        )
        score -= 10


    if length > 70:
        issues.append(
            "Subject is too long"
        )
        score -= 10


    if score < 0:
        score = 0


    if score >= 80:
        rating = "Excellent"

    elif score >= 60:
        rating = "Good"

    else:
        rating = "Needs Improvement"



    return {

        "score": score,

        "rating": rating,

        "issues": issues

    }