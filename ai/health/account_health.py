from datetime import datetime


def calculate_health(profile):

    health = profile["health_score"]

    sent = profile["sent_today"]

    limit = profile["daily_limit"]

    if sent >= limit:

        health -= 30

    elif sent >= limit * 0.80:

        health -= 15

    if health >= 90:

        status = "Healthy"

    elif health >= 75:

        status = "Warm"

    elif health >= 60:

        status = "Cooling"

    else:

        status = "Rest Required"

    return {

        "health": max(0, health),

        "status": status,

        "recommended_min": profile["recommended_min"],

        "recommended_max": profile["recommended_max"],

        "rest_until": profile["rest_until"]

    }