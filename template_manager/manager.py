import json
from pathlib import Path

from ai.template_analyzer import analyze_template


BASE_DIR = Path(__file__).resolve().parents[1]

try:
    from config.path_manager import TEMPLATES_DIR
except ImportError:
    TEMPLATES_DIR = BASE_DIR / "templates"


TEMPLATE_FILE = TEMPLATES_DIR / "email_templates.json"


def load_templates():

    if not TEMPLATE_FILE.exists():
        return {}

    try:

        with open(
            TEMPLATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except (
        json.JSONDecodeError,
        OSError
    ):

        return {}


def save_templates(data):

    TEMPLATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        TEMPLATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def view_templates(templates):

    if not templates:

        print("\nNo templates found.")
        input("\nPress Enter...")
        return

    print(
        "\n========== EMAIL TEMPLATES ==========\n"
    )

    for name, template in templates.items():

        subject = template.get(
            "subject",
            ""
        )

        body = template.get(
            "body",
            ""
        )

        print("-" * 50)
        print(f"Name    : {name}")
        print(f"Subject : {subject}")
        print("\nBody:")
        print(body)
        print("-" * 50)

    input("\nPress Enter...")


def add_template(templates):

    print(
        "\n========== ADD TEMPLATE ==========\n"
    )

    name = input(
        "Template Name: "
    ).strip()

    if not name:

        print("\nTemplate name cannot be empty.")
        input("\nPress Enter...")
        return

    if name in templates:

        print(
            "\nA template with this name already exists."
        )

        input("\nPress Enter...")
        return

    subject = input(
        "Subject: "
    ).strip()

    print(
        "\nBody (type END on a new line to finish):"
    )

    lines = []

    while True:

        line = input()

        if line == "END":
            break

        lines.append(line)

    body = "\n".join(lines)

    templates[name] = {
        "subject": subject,
        "body": body
    }

    save_templates(
        templates
    )

    print(
        "\nTemplate Saved Successfully."
    )

    input("\nPress Enter...")


def analyze_selected_template(templates):

    print(
        "\n========== ANALYZE TEMPLATE ==========\n"
    )

    if not templates:

        print("No templates found.")
        input("\nPress Enter...")
        return

    names = list(
        templates.keys()
    )

    for index, name in enumerate(
        names,
        start=1
    ):

        print(
            f"{index}. {name}"
        )

    try:

        choice = int(
            input(
                "\nSelect Template: "
            ).strip()
        )

        if not 1 <= choice <= len(names):
            raise ValueError

    except ValueError:

        print(
            "\nInvalid Selection."
        )

        input("\nPress Enter...")
        return

    name = names[
        choice - 1
    ]

    template = templates[name]

    subject = template.get(
        "subject",
        ""
    )

    body = template.get(
        "body",
        ""
    )

    print(
        f"\nAnalyzing: {name}\n"
    )

    try:

        result = analyze_template(
            subject,
            body
        )

    except Exception as error:

        print(
            "\n[ERROR] Template analysis failed."
        )

        print(
            f"\n{error}"
        )

        input("\nPress Enter...")
        return

    if not isinstance(
        result,
        dict
    ):

        print(
            "\nAnalyzer returned an unexpected result."
        )

        input("\nPress Enter...")
        return

    input(
        "\nPress Enter to return..."
    )


def delete_template(templates):

    print(
        "\n========== DELETE TEMPLATE ==========\n"
    )

    if not templates:

        print("No templates found.")
        input("\nPress Enter...")
        return

    names = list(
        templates.keys()
    )

    for index, name in enumerate(
        names,
        start=1
    ):

        print(
            f"{index}. {name}"
        )

    try:

        choice = int(
            input(
                "\nSelect Template: "
            ).strip()
        )

        if not 1 <= choice <= len(names):
            raise ValueError

    except ValueError:

        print(
            "\nInvalid Selection."
        )

        input("\nPress Enter...")
        return

    name = names[
        choice - 1
    ]

    confirm = input(
        f"\nDelete '{name}'? (Y/N): "
    ).strip().lower()

    if confirm != "y":

        print(
            "\nDelete Cancelled."
        )

        input("\nPress Enter...")
        return

    del templates[name]

    save_templates(
        templates
    )

    print(
        "\nTemplate Deleted Successfully."
    )

    input("\nPress Enter...")


def start_template_manager():

    while True:

        print(
            """
========================================
        TEMPLATE MANAGER
========================================

[1] View Templates
[2] Add Template
[3] Analyze Template
[4] Delete Template
[5] Back

========================================
"""
        )

        choice = input(
            "Select: "
        ).strip()

        templates = load_templates()

        if choice == "1":

            view_templates(
                templates
            )

        elif choice == "2":

            add_template(
                templates
            )

        elif choice == "3":

            analyze_selected_template(
                templates
            )

        elif choice == "4":

            delete_template(
                templates
            )

        elif choice == "5":

            break

        else:

            print(
                "\nInvalid Option."
            )

            input("\nPress Enter...")