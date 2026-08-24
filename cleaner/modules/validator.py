import re


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@gmail\.com$"
)


def is_valid_email(email):

    if not email:
        return False

    email = email.strip().lower()

    if not EMAIL_PATTERN.match(email):
        return False

    return True



def validate_emails(email_list):

    valid = []
    invalid = []

    seen = set()

    for email in email_list:

        email = email.strip().lower()

        if email in seen:
            continue

        seen.add(email)

        if is_valid_email(email):
            valid.append(email)
        else:
            invalid.append(email)

    return {
        "valid": valid,
        "invalid": invalid,
        "total": len(email_list),
        "clean": len(valid)
    }
