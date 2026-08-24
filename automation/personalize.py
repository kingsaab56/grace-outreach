def personalize_template(template, data):

    result = template


    for key, value in data.items():

        result = result.replace(
            "{{" + key + "}}",
            value
        )


    return result