# ai/personalization.py


def personalize_template(template, data):

    result = template


    for key, value in data.items():

        placeholder = "{{" + key + "}}"

        result = result.replace(
            placeholder,
            value
        )


    return result