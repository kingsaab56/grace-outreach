from config.database import get_connection



def get_database_contacts(limit=None):

    conn = get_connection()
    cursor = conn.cursor()


    query = """
        SELECT
            email,
            name,
            company,
            city
        FROM contacts
        WHERE status='clean'
    """


    if limit:

        query += f" LIMIT {limit}"


    cursor.execute(query)


    contacts = cursor.fetchall()


    conn.close()


    return contacts