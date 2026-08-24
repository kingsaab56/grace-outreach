def remove_duplicates(contacts):

    seen = set()

    unique = []


    for contact in contacts:

        email = contact[0].lower()


        if email not in seen:

            seen.add(email)

            unique.append(contact)


    return unique