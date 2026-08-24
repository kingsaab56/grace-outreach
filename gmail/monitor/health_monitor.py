from config.gmail_profiles import get_gmail_profiles


def calculate_health(
    sent_today,
    daily_limit,
    bounces=0,
    spam_score=0
):

    health = 100


    # Sending limit usage

    if daily_limit > 0:

        usage = sent_today / daily_limit * 100

        if usage >= 90:
            health -= 20

        elif usage >= 70:
            health -= 10



    # Bounce penalty

    health -= bounces * 5



    # Spam score penalty

    health -= int(spam_score)



    if health < 0:
        health = 0


    return health



def show_health_report():

    print("\n========== GMAIL HEALTH REPORT ==========\n")


    profiles = get_gmail_profiles()


    if not profiles:

        print("No Gmail profiles found.")
        return



    for p in profiles:


        profile_name = p[0]
        gmail = p[1]
        health = p[2]
        status = p[3]
        limit = p[4]
        sent = p[5]


        print(
f"""
Profile : {profile_name}
Gmail   : {gmail}

Health  : {health}%
Status  : {status}

Sent Today : {sent}
Daily Limit: {limit}

------------------------------------
"""
        )



def start_health_monitor():

    show_health_report()

    input("\nPress Enter...")