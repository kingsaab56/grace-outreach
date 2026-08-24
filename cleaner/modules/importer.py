from pathlib import Path


def import_from_txt(file_path):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(file_path)

    emails = []

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for line in f:

            line = line.strip()

            if line:
                emails.append(line)

    return emails


def import_from_paste():

    print("\nPaste emails below.")
    print("Type END on a new line.\n")

    emails = []

    while True:

        line = input().strip()

        if line.upper() == "END":
            break

        if line:
            emails.append(line)

    return emails