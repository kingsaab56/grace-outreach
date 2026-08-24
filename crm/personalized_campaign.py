# crm/personalized_campaign.py

from ai.personalization import personalize_template


def create_personalized_email(template, contact):

    result = personalize_template(
        template,
        contact
    )

    return result



def show_personalized_email(template, contact):

    print("\n========== PERSONALIZED EMAIL ==========\n")

    email = create_personalized_email(
        template,
        contact
    )

    print(email)