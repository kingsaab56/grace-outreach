from ai.personalization import personalize_template


template = """
Hello {{name}},

We provide architectural drawings and estimating services for {{company}} in {{city}}.

Thank you.
"""


data = {

    "name": "John",

    "company": "ABC Builders",

    "city": "Houston"

}


result = personalize_template(
    template,
    data
)


print("========== PERSONALIZED TEMPLATE ==========")

print(result)