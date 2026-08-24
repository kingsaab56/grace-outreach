from pathlib import Path
import csv


EXPORT_FOLDER = Path("cleaner/exports")

EXPORT_FOLDER.mkdir(exist_ok=True)


def export_txt(emails):

    path = EXPORT_FOLDER / "cleaned_emails.txt"

    with open(path, "w", encoding="utf-8") as f:

        for email in emails:
            f.write(email + "\n")

    return path


def export_csv(emails):

    path = EXPORT_FOLDER / "cleaned_emails.csv"

    with open(path, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["Email"])

        for email in emails:
            writer.writerow([email])

    return path