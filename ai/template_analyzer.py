# ai/template_analyzer.py

from ai.scoring import calculate_health
from ai.ai_suggestions import get_suggestions
from ai.spam_analyzer import analyze_spam


def analyze_template(subject, body):

    result = calculate_health(subject, body)

    spam = analyze_spam(subject, body)

    suggestions = get_suggestions(subject, body)

    print("\n========================================")
    print("         AI TEMPLATE ANALYZER")
    print("========================================\n")

    print(f"Health Score : {result['health']}/100")
    print(f"Grade        : {result['grade']}")
    print(f"Subject      : {result['subject']['score']}/100")
    print(f"Readability  : {result['body']['score']}/100")
    print(f"Spam Score   : {spam['score']}/100")
    print(f"Spam Risk    : {spam['risk']}")

    print("\nSubject Issues")

    if result["subject"]["issues"]:

        for issue in result["subject"]["issues"]:

            print(f"• {issue}")

    else:

        print("• None")

    print("\nBody Issues")

    if result["body"]["issues"]:

        for issue in result["body"]["issues"]:

            print(f"• {issue}")

    else:

        print("• None")

    print("\nSpam Issues")

    if spam["issues"]:

        for issue in spam["issues"]:

            print(f"• {issue}")

    else:

        print("• None")

    print("\nAI Suggestions")

    for suggestion in suggestions:

        print(f"✓ {suggestion}")

    print("\n========================================")

    if result["health"] >= 80:

        print("STATUS : READY TO CREATE DRAFT")

    else:

        print("STATUS : REVIEW TEMPLATE FIRST")

    print("========================================\n")

    return {

        "health": result,

        "spam": spam,

        "suggestions": suggestions

    }