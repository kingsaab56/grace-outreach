from config.database import get_connection


def show_templates():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, days_after
        FROM followup_templates
        ORDER BY days_after
    """)

    rows = cursor.fetchall()

    conn.close()

    print("\n========== FOLLOW-UP TEMPLATES ==========\n")

    if not rows:
        print("No templates found.")
        return

    for row in rows:
        print(f"{row[0]}. {row[1]} ({row[2]} Days)")