# ai/ai_suggestions.py

from ai.template_rules import SPAM_WORDS


def get_suggestions(subject, body):

    suggestions = []

    text = (subject + " " + body).lower()

    for word in SPAM_WORDS:
        if word in text:
            suggestions.append(
                f"Replace promotional word: '{word}'"
            )

    if len(subject) < 10:
        suggestions.append(
            "Subject is too short."
        )

    if len(subject) > 60:
        suggestions.append(
            "Subject should be under 60 characters."
        )

    if "{{company}}" not in body:
        suggestions.append(
            "Consider adding company personalization."
        )

    if "thank you" not in body.lower():
        suggestions.append(
            "Consider ending the email politely."
        )

    if not suggestions:
        suggestions.append(
            "No major improvements required."
        )

    return suggestions