def account_recommendation(data):

    if data["health"] >= 90:

        return "Safe to send."

    if data["health"] >= 75:

        return "Reduce sending speed."

    if data["health"] >= 60:

        return "Take a short rest before continuing."

    return "Stop sending. Let this account rest."