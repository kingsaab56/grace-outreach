BUSINESS_KEYWORDS = [

    "gracearchitectures",
    "gracearchitectures.us",
    "gracearchitectures.usa",
    "gracearchitectures.llc",
    "contractor",
    "estimating",
    "architecture"

]


def is_business_email(email):

    email = email.lower()

    for keyword in BUSINESS_KEYWORDS:

        if keyword in email:

            return True

    return False


def filter_business_accounts(accounts):

    return [

        account

        for account in accounts

        if is_business_email(account["email"])

    ]


if __name__ == "__main__":

    sample = [

        {"email": "calvin.gracearchitectures.llc@gmail.com"},

        {"email": "rajpootisnomi@gmail.com"},

        {"email": "waheedpk0302@gmail.com"}

    ]

    print(filter_business_accounts(sample))