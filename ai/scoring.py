# ai/scoring.py

from ai.subject_analyzer import analyze_subject
from ai.readability import readability_score


def calculate_health(subject, body):

    subject_data = analyze_subject(subject)

    body_data = readability_score(body)

    health = int(
        (subject_data["score"] + body_data["score"]) / 2
    )

    if health >= 90:
        grade = "A+"

    elif health >= 80:
        grade = "A"

    elif health >= 70:
        grade = "B"

    elif health >= 60:
        grade = "C"

    else:
        grade = "D"

    return {

        "health": health,

        "grade": grade,

        "subject": subject_data,

        "body": body_data

    }